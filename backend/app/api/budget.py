from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.budget import BudgetPlanner
from app.models.user import User
from datetime import datetime
from datetime import  timedelta
budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/monthly', methods=['GET'])
@jwt_required()
def get_monthly_budget():
    """Generate monthly budget"""
    try:
        user = User.query.get(user_id)
        if not user or not user.profile or not user.profile.monthly_salary:
            # Return default status object
            return jsonify({
                'period': None,
                'total_budget': 0,
                'spent_so_far': 0,
                'remaining': 0,
                'days_remaining': 0,
                'daily_budget': 0,
                'expected_spent': 0,
                'on_track': False,
                'percent_used': 0,
                'percent_time_passed': 0,
                'category_status': [],
                'message': 'Monthly salary not set. Please update your profile.'
            }), 200
        user_id = get_jwt_identity()
        
        # Get query parameters
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.profile or not user.profile.monthly_salary:
            return jsonify({
                'summary': {},
                'category_budgets': {},
                'message': 'Monthly salary not set or user/profile missing'
            }), 200
        planner = BudgetPlanner(user_id)
        budget = planner.generate_monthly_budget(month, year)
        return jsonify(budget), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/compare', methods=['GET'])
@jwt_required()
def compare_budget_actual():
    """Compare budget vs actual spending"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.profile:
            return jsonify({
                'summary': {},
                'categories_over_budget': [],
                'categories_under_budget': [],
                'message': 'User profile not set'
            }), 200
        planner = BudgetPlanner(user_id)
        comparison = planner.compare_budget_vs_actual(month, year)
        return jsonify(comparison), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/future', methods=['GET'])
@jwt_required()
def get_future_budgets():
    """Generate budgets for future months"""
    try:
        user_id = get_jwt_identity()
        months = request.args.get('months', 3, type=int)
        
        if months < 1 or months > 12:
            return jsonify({'error': 'Months must be between 1 and 12'}), 400
        
        planner = BudgetPlanner(user_id)
        future_budgets = planner.generate_future_budgets(months)
        
        return jsonify(future_budgets), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_budget_recommendations():
    """Get budget optimization recommendations"""
    try:
        user_id = get_jwt_identity()
        
        planner = BudgetPlanner(user_id)
        recommendations = planner.get_budget_recommendations()
        
        return jsonify(recommendations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/smart', methods=['POST'])
@jwt_required()
def create_smart_budget():
    """Create smart budget with target savings rate"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        target_savings_rate = data.get('target_savings_rate')
        if target_savings_rate:
            target_savings_rate = target_savings_rate / 100  # Convert from percentage
        
        planner = BudgetPlanner(user_id)
        smart_budget = planner.create_smart_budget(target_savings_rate)
        
        return jsonify(smart_budget), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/history', methods=['GET'])
@jwt_required()
def get_budget_history():
    """Get budget history for last N months"""
    try:
        user_id = get_jwt_identity()
        months = request.args.get('months', 6, type=int)
        
        if months > 24:
            months = 24
        
        planner = BudgetPlanner(user_id)
        history = []
        
        now = datetime.now()
        for i in range(months):
            # Calculate month/year going backwards
            if now.month - i > 0:
                month = now.month - i
                year = now.year
            else:
                month = now.month - i + 12
                year = now.year - 1
            
            comparison = planner.compare_budget_vs_actual(month, year)
            if 'error' not in comparison:
                history.append({
                    'period': f"{datetime(year, month, 1).strftime('%B %Y')}",
                    'month': month,
                    'year': year,
                    'budgeted': comparison['summary']['total_budgeted'],
                    'actual': comparison['summary']['total_actual'],
                    'difference': comparison['summary']['total_difference'],
                    'categories_over': comparison['categories_over_budget'],
                    'categories_under': comparison['categories_under_budget']
                })
        
        return jsonify({
            'history': history,
            'total_months': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/current-status', methods=['GET'])
@jwt_required()
def get_current_budget_status():
    """Get current month's budget status"""
    try:
        user_id = get_jwt_identity()
        
        planner = BudgetPlanner(user_id)
        
        # Get current date
        user_id = get_jwt_identity()
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.profile or not user.profile.monthly_salary:
            # Return default status object
            return jsonify({
                'period': None,
                'total_budget': 0,
                'spent_so_far': 0,
                'remaining': 0,
                'days_remaining': 0,
                'daily_budget': 0,
                'expected_spent': 0,
                'on_track': False,
                'percent_used': 0,
                'percent_time_passed': 0,
                'category_status': [],
                'message': 'Monthly salary not set. Please update your profile.'
            }), 200

        planner = BudgetPlanner(user_id)
        now = datetime.now()
        budget = planner.generate_monthly_budget(now.month, now.year)
        start_date = datetime(now.year, now.month, 1)
        current_spending = planner.analyzer.get_category_breakdown(start_date, now)
        total_spent_so_far = sum(cat['total'] for cat in current_spending.values())
        days_passed = now.day
        days_in_month = (datetime(now.year, now.month + 1, 1) - timedelta(days=1)).day if now.month < 12 else 31

        if 'error' not in budget:
            daily_budget = budget['summary']['total_budgeted'] / days_in_month
            expected_spent = daily_budget * days_passed
            status = {
                'period': budget['period'],
                'total_budget': budget['summary']['total_budgeted'],
                'spent_so_far': round(total_spent_so_far, 2),
                'remaining': round(budget['summary']['total_budgeted'] - total_spent_so_far, 2),
                'days_remaining': days_in_month - days_passed,
                'daily_budget': round(daily_budget, 2),
                'expected_spent': round(expected_spent, 2),
                'on_track': total_spent_so_far <= expected_spent * 1.1,  # Within 10% of expected
                'percent_used': round((total_spent_so_far / budget['summary']['total_budgeted']) * 100, 1) if budget['summary']['total_budgeted'] > 0 else 0,
                'percent_time_passed': round((days_passed / days_in_month) * 100, 1)
            }
            category_status = []
            for category, budget_data in budget['category_budgets'].items():
                spent = current_spending.get(category, {}).get('total', 0)
                allocated = budget_data['allocated']
                if allocated > 0:
                    percent_used = (spent / allocated) * 100
                    if percent_used > 100:
                        status_flag = 'over_budget'
                    elif percent_used > 75:
                        status_flag = 'caution'
                    else:
                        status_flag = 'good'
                    category_status.append({
                        'category': category,
                        'budgeted': allocated,
                        'spent': round(spent, 2),
                        'remaining': round(allocated - spent, 2),
                        'percent_used': round(percent_used, 1),
                        'status': status_flag
                    })
            status['category_status'] = sorted(category_status, key=lambda x: x['percent_used'], reverse=True)
            return jsonify(status), 200
        return jsonify({'error': 'Could not generate budget status'}), 400
            return jsonify(status), 200
        
        return jsonify({'error': 'Could not generate budget status'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500