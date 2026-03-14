from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.reporting import ReportGenerator
from datetime import datetime
import json

reporting_bp = Blueprint('reporting', __name__)

@reporting_bp.route('/monthly', methods=['GET'])
@jwt_required()
def monthly_report():
    """Generate monthly financial report"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        # Default to current month
        if not month or not year:
            now = datetime.now()
            month = now.month
            year = now.year
        
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.profile:
            return jsonify({
                'report': {},
                'message': 'User profile not set'
            }), 200
        generator = ReportGenerator(user_id)
        report = generator.generate_monthly_report(month, year)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reporting_bp.route('/yearly', methods=['GET'])
@jwt_required()
def yearly_report():
    """Generate yearly financial report"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        year = request.args.get('year', type=int)
        
        # Default to current year
        if not year:
            year = datetime.now().year
        
        generator = ReportGenerator(user_id)
        report = generator.generate_yearly_report(year)
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reporting_bp.route('/category', methods=['GET'])
@jwt_required()
def category_report():
    """Generate report for specific category"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        category = request.args.get('category')
        months = request.args.get('months', 6, type=int)
        
        if not category:
            return jsonify({'error': 'Category is required'}), 400
        
        if months < 1 or months > 24:
            return jsonify({'error': 'Months must be between 1 and 24'}), 400
        
        generator = ReportGenerator(user_id)
        report = generator.generate_category_report(category, months)
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reporting_bp.route('/compare-years', methods=['GET'])
@jwt_required()
def compare_years():
    """Compare spending between two years"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        year1 = request.args.get('year1', type=int)
        year2 = request.args.get('year2', type=int)
        
        if not year1 or not year2:
            now = datetime.now()
            year1 = now.year - 1
            year2 = now.year
        
        generator = ReportGenerator(user_id)
        comparison = generator.generate_comparison_report(year1, year2)
        
        return jsonify(comparison), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reporting_bp.route('/export', methods=['GET'])
@jwt_required()
def export_data():
    """Export financial data"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        format = request.args.get('format', 'json')
        
        generator = ReportGenerator(user_id)
        data = generator.generate_export_data(format)
        
        if 'error' in data:
            return jsonify(data), 400
        
        if format == 'csv':
            # Return as CSV file
            return Response(
                data,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment;filename=financial_data.csv'}
            )
        else:
            # Return as JSON
            return jsonify(data), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reporting_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get dashboard data for the main view"""
    try:
        user_id = get_jwt_identity()
        
        generator = ReportGenerator(user_id)
        
        # Get current month data
        now = datetime.now()
        
        # Monthly report for current month
        monthly = generator.generate_monthly_report(now.month, now.year)
        
        # Yearly report for current year
        yearly = generator.generate_yearly_report(now.year)
        
        # Get recent transactions
        from app.models.user import Transaction
        recent = Transaction.query.filter_by(user_id=user_id).order_by(
            Transaction.transaction_date.desc()
        ).limit(10).all()
        
        recent_transactions = [{
            'id': t.id,
            'date': t.transaction_date.strftime('%Y-%m-%d'),
            'amount': t.amount,
            'category': t.category,
            'description': t.description,
            'type': 'income' if t.amount > 0 else 'expense'
        } for t in recent]
        
        # Get budget status - handle potential errors
        try:
            budget_status = generator.planner.get_current_budget_status()
            if isinstance(budget_status, dict) and 'error' in budget_status:
                budget_status = None
        except:
            budget_status = None
        
        # Get all transactions count
        all_transactions = Transaction.query.filter_by(user_id=user_id).all()
        transaction_count = len(all_transactions)
        
        # Get unique categories
        categories = set(t.category for t in all_transactions) if all_transactions else set()
        
        # Get oldest transaction
        oldest = None
        if all_transactions:
            oldest_date = min((t.transaction_date for t in all_transactions), default=None)
            oldest = oldest_date.strftime('%Y-%m-%d') if oldest_date else None
        
        # Combine into dashboard
        dashboard = {
            'current_month': {
                'month': now.strftime('%B'),
                'year': now.year,
                'summary': monthly.get('summary') if isinstance(monthly, dict) and 'error' not in monthly else None,
                'top_categories': monthly.get('top_categories') if isinstance(monthly, dict) and 'error' not in monthly else []
            },
            'year_to_date': {
                'summary': yearly.get('summary') if isinstance(yearly, dict) and 'error' not in yearly else None,
                'monthly_data': yearly.get('monthly_breakdown', [])[:3] if isinstance(yearly, dict) and 'error' not in yearly else []  # Last 3 months
            },
            'budget_status': budget_status,
            'recent_transactions': recent_transactions,
            'quick_stats': {
                'total_transactions': transaction_count,
                'categories_used': len(categories),
                'oldest_transaction': oldest
            }
        }
        
        return jsonify(dashboard), 200
        
    except Exception as e:
        print(f"Error in dashboard: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500

@reporting_bp.route('/available-reports', methods=['GET'])
@jwt_required()
def get_available_reports():
    """Get list of available reports"""
    try:
        user_id = get_jwt_identity()
        
        # Get all years with data
        from app.models.user import Transaction
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        
        years = sorted(set(t.transaction_date.year for t in transactions)) if transactions else []
        
        # Get all categories (only expense categories)
        categories = sorted(set(t.category for t in transactions if t.amount < 0)) if transactions else []
        
        # Get months with data for current year
        current_year = datetime.now().year
        months_with_data = sorted(set(
            t.transaction_date.month for t in transactions 
            if t.transaction_date.year == current_year
        )) if transactions else []
        
        # Convert month numbers to names
        month_names = []
        import calendar
        for m in months_with_data:
            month_names.append(calendar.month_name[m])
        
        return jsonify({
            'available_years': years,
            'available_categories': categories,
            'months_with_data_current_year': month_names,
            'report_types': ['monthly', 'yearly', 'category', 'comparison', 'export']
        }), 200
        
    except Exception as e:
        print(f"Error in available-reports: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500