from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import db, Transaction
from app.utils.validators import validate_transaction
from app.utils.categories import get_expense_categories, get_income_categories, get_category_type
from app.utils.currency import CurrencyFormatter
from datetime import datetime, timedelta
from sqlalchemy import extract, func

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all available categories (for suggestions only)"""
    return jsonify({
        'expense_categories': get_expense_categories(),
        'income_categories': get_income_categories()
    }), 200

@transactions_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get all transactions for the logged-in user with optional filters"""
    try:
        print("--- TRANSACTIONS API DEBUG ---")
        # user_id, month, year, etc. are defined below
        user_id = get_jwt_identity()
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        # Get query parameters
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        category = request.args.get('category')
        transaction_type = request.args.get('type')  # 'income' or 'expense'
        search = request.args.get('search')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = Transaction.query.filter_by(user_id=user_id)
        
        # Apply filters
        if month and year:
            query = query.filter(
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == year
            )
        elif year:
            query = query.filter(extract('year', Transaction.transaction_date) == year)
        
        if category:
            query = query.filter_by(category=category)

        if transaction_type:
            if transaction_type == 'expense':
                query = query.filter(Transaction.amount < 0)
            elif transaction_type == 'income':
                query = query.filter(Transaction.amount > 0)

        if search:
            search_lower = search.lower()
            query = query.filter(
                func.lower(Transaction.description).contains(search_lower) |
                func.lower(Transaction.category).contains(search_lower)
            )
        
        # Get total count for pagination
        total_count = query.count()
        
        # Get paginated results
        transactions = query.order_by(
            Transaction.transaction_date.desc(),
            Transaction.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return jsonify({
            'transactions': [{
                'id': t.id,
                'amount': t.amount,
                'amount_formatted': CurrencyFormatter.format(t.amount),
                'amount_kwacha': CurrencyFormatter.format_kwacha(t.amount),
                'category': t.category,
                'description': t.description,
                'date': t.transaction_date.strftime('%Y-%m-%d'),
                'type': 'income' if t.amount > 0 else 'expense'
            } for t in transactions],
            'pagination': {
                'total': total_count,
                'offset': offset,
                'limit': limit,
                'has_more': (offset + limit) < total_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('', methods=['POST'])
@jwt_required()
def add_transaction():
    """Add a new transaction"""
    try:
        user_id = get_jwt_identity()
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        data = request.get_json()
        
        # Log the received data
        print(f"Received transaction data: {data}")
        
        # Validate transaction data
        is_valid, errors = validate_transaction(data)
        print(f"Validation result: is_valid={is_valid}, errors={errors}")
        
        if not is_valid:
            return jsonify({'errors': errors}), 400
        
        # Rest of your code...
        # Parse amount
        amount = float(data['amount'])
        category = data['category'].strip()  # Trim whitespace
        
        # Determine if it's expense or income based on category
        # Default to expense for unknown categories, or you could check keywords
        category_lower = category.lower()
        
        # Simple rule: if it contains salary, freelance, income, etc. - treat as income
        income_keywords = ['salary', 'freelance', 'income', 'gift', 'refund', 'investment', 'business']
        is_income = any(keyword in category_lower for keyword in income_keywords)
        
        if is_income:
            amount = abs(amount)  # Make positive for income
        else:
            amount = -abs(amount)  # Make negative for expenses
        
        # Create transaction
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            category=category,
            description=data.get('description', ''),
            transaction_date=datetime.strptime(data['date'], '%Y-%m-%d')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction added successfully',
            'transaction': {
                'id': transaction.id,
                'amount': transaction.amount,
                'amount_formatted': CurrencyFormatter.format(transaction.amount),
                'amount_kwacha': CurrencyFormatter.format_kwacha(transaction.amount),
                'category': transaction.category,
                'description': transaction.description,
                'date': transaction.transaction_date.strftime('%Y-%m-%d'),
                'type': 'income' if transaction.amount > 0 else 'expense'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    """Get a specific transaction by ID"""
    try:
        user_id = get_jwt_identity()
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=user_id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        return jsonify({
            'id': transaction.id,
            'amount': transaction.amount,
            'category': transaction.category,
            'description': transaction.description,
            'date': transaction.transaction_date.strftime('%Y-%m-%d'),
            'type': 'income' if transaction.amount > 0 else 'expense'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """Update a transaction"""
    try:
        user_id = get_jwt_identity()
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        data = request.get_json()
        
        # Find transaction
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=user_id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Validate if fields are being updated
        if 'amount' in data:
            amount = float(data['amount'])
            category = data.get('category', transaction.category)
            
            # Determine if it's income or expense based on category
            category_lower = category.lower()
            income_keywords = ['salary', 'freelance', 'income', 'gift', 'refund', 'investment', 'business']
            is_income = any(keyword in category_lower for keyword in income_keywords)
            
            if is_income:
                transaction.amount = abs(amount)
            else:
                transaction.amount = -abs(amount)
        
        if 'category' in data:
            # Just ensure it's not empty
            if not data['category'] or not data['category'].strip():
                return jsonify({'error': 'Category cannot be empty'}), 400
            
            transaction.category = data['category'].strip()
            
            # Update amount sign based on new category if amount wasn't updated
            if 'amount' not in data:
                category_lower = transaction.category.lower()
                income_keywords = ['salary', 'freelance', 'income', 'gift', 'refund', 'investment', 'business']
                is_income = any(keyword in category_lower for keyword in income_keywords)
                
                if is_income:
                    transaction.amount = abs(transaction.amount)
                else:
                    transaction.amount = -abs(transaction.amount)
        
        if 'description' in data:
            if len(data['description']) > 200:
                return jsonify({'error': 'Description must be less than 200 characters'}), 400
            transaction.description = data['description']
        
        if 'date' in data:
            transaction.transaction_date = datetime.strptime(data['date'], '%Y-%m-%d')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction updated successfully',
            'transaction': {
                'id': transaction.id,
                'amount': transaction.amount,
                'category': transaction.category,
                'description': transaction.description,
                'date': transaction.transaction_date.strftime('%Y-%m-%d'),
                'type': 'income' if transaction.amount > 0 else 'expense'
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        user_id = get_jwt_identity()
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=user_id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """Get transaction summary for a period"""
    try:
        user_id = get_jwt_identity()
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        # Get query parameters
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Get transactions for the period
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date.between(start_date, end_date)
        ).all()
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        
        # Category breakdown
        category_breakdown = {}
        for t in transactions:
            if t.amount < 0:  # Only expenses for breakdown
                category = t.category
                amount = abs(t.amount)
                if category not in category_breakdown:
                    category_breakdown[category] = {
                        'amount': 0,
                        'percentage': 0,
                        'count': 0
                    }
                category_breakdown[category]['amount'] += amount
                category_breakdown[category]['count'] += 1
        
        # Calculate percentages
        if total_expenses > 0:
            for category in category_breakdown:
                category_breakdown[category]['percentage'] = round(
                    (category_breakdown[category]['amount'] / total_expenses) * 100, 2
                )
        
        return jsonify({
            'period': f"{year}-{month:02d}",
            'summary': {
                'total_income': round(total_income, 2),
                'total_expenses': round(total_expenses, 2),
                'net_savings': round(total_income - total_expenses, 2),
                'transaction_count': len(transactions)
            },
            'category_breakdown': category_breakdown
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_transactions():
    """Get recent transactions (last 30 days)"""
    try:
        user_id = get_jwt_identity()
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= thirty_days_ago
        ).order_by(Transaction.transaction_date.desc()).limit(10).all()
        
        return jsonify([{
            'id': t.id,
            'amount': t.amount,
            'category': t.category,
            'description': t.description,
            'date': t.transaction_date.strftime('%Y-%m-%d'),
            'type': 'income' if t.amount > 0 else 'expense'
        } for t in transactions]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500