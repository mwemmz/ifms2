from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.advisor import FinancialAdvisor

advisor_bp = Blueprint('advisor', __name__)

@advisor_bp.route('/health-score', methods=['GET'])
@jwt_required()
def get_health_score():
    """Get financial health score"""
    try:
        user_id = get_jwt_identity()
        
        advisor = FinancialAdvisor(user_id)
        score = advisor.get_financial_health_score()
        
        # Determine rating based on score
        if score >= 80:
            rating = "Excellent"
        elif score >= 60:
            rating = "Good"
        elif score >= 40:
            rating = "Fair"
        else:
            rating = "Needs Improvement"
        
        return jsonify({
            'score': score,
            'rating': rating,
            'max_score': 100
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advisor_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get personalized financial recommendations"""
    try:
        user_id = get_jwt_identity()
        
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.profile:
            return jsonify({
                'recommendations': [],
                'count': 0,
                'message': 'User profile not set'
            }), 200
        advisor = FinancialAdvisor(user_id)
        recommendations = advisor.generate_recommendations()
        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advisor_bp.route('/budget-suggestions', methods=['GET'])
@jwt_required()
def get_budget_suggestions():
    """Get personalized budget suggestions based on 50/30/20 rule"""
    try:
        user_id = get_jwt_identity()
        
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.profile:
            return jsonify({
                'suggestions': [],
                'message': 'User profile not set'
            }), 200
        advisor = FinancialAdvisor(user_id)
        suggestions = advisor.get_budget_suggestions()
        return jsonify(suggestions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advisor_bp.route('/overspending', methods=['GET'])
@jwt_required()
def get_overspending():
    """Detect categories with overspending"""
    try:
        user_id = get_jwt_identity()
        
        advisor = FinancialAdvisor(user_id)
        overspending = advisor.detect_overspending()
        
        return jsonify({
            'overspending_categories': overspending,
            'count': len(overspending)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advisor_bp.route('/savings-opportunities', methods=['GET'])
@jwt_required()
def get_savings_opportunities():
    """Identify potential savings opportunities"""
    try:
        user_id = get_jwt_identity()
        
        advisor = FinancialAdvisor(user_id)
        opportunities = advisor.get_savings_opportunities()
        
        return jsonify({
            'opportunities': opportunities,
            'count': len(opportunities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advisor_bp.route('/insights', methods=['GET'])
@jwt_required()
def get_financial_insights():
    """Get comprehensive financial insights"""
    try:
        user_id = get_jwt_identity()
        
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.profile:
            return jsonify({
                'insights': {},
                'message': 'User profile not set'
            }), 200
        advisor = FinancialAdvisor(user_id)
        insights = advisor.get_financial_insights()
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advisor_bp.route('/goal-progress', methods=['GET'])
@jwt_required()
def get_goal_progress():
    """Check progress toward savings goal"""
    try:
        user_id = get_jwt_identity()
        
        advisor = FinancialAdvisor(user_id)
        
        # Get user profile
        from app.models.user import User
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not user.profile or not user.profile.savings_goal:
            # Return default progress object
            return jsonify({
                'goal_amount': 0,
                'current_amount': 0,
                'progress_percentage': 0,
                'remaining': 0,
                'on_track': False,
                'message': 'No savings goal set'
            }), 200
        
        emergency_fund = advisor._calculate_emergency_fund()
        progress = advisor._calculate_goal_progress()
        
        return jsonify({
            'goal_amount': user.profile.savings_goal,
            'current_amount': emergency_fund,
            'progress_percentage': round(progress * 100, 1),
            'remaining': round(max(0, user.profile.savings_goal - emergency_fund), 2),
            'on_track': progress >= 0.5  # Example threshold
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advisor_bp.route('/emergency-fund', methods=['GET'])
@jwt_required()
def get_emergency_fund_status():
    """Check emergency fund status"""
    try:
        user_id = get_jwt_identity()
        
        advisor = FinancialAdvisor(user_id)
        
        # Get user profile
        from app.models.user import User
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not user.profile or not user.profile.monthly_salary:
            # Return default emergency fund object
            return jsonify({
                'current_amount': 0,
                'monthly_expenses_estimate': 0,
                'months_covered': 0,
                'target_months': advisor.EMERGENCY_FUND_MONTHS,
                'target_amount': 0,
                'status': 'missing',
                'message': 'Monthly salary not set'
            }), 200
        
        emergency_fund = advisor._calculate_emergency_fund()
        monthly_expenses = user.profile.monthly_salary * 0.7  # Estimate
        
        months_covered = emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
        target_months = advisor.EMERGENCY_FUND_MONTHS
        target_amount = monthly_expenses * target_months
        
        return jsonify({
            'current_amount': round(emergency_fund, 2),
            'monthly_expenses_estimate': round(monthly_expenses, 2),
            'months_covered': round(months_covered, 1),
            'target_months': target_months,
            'target_amount': round(target_amount, 2),
            'status': 'healthy' if months_covered >= target_months else 
                     'adequate' if months_covered >= 3 else 
                     'needs_attention' if months_covered >= 1 else 'critical'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500