from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.analysis import SpendingAnalyzer
from datetime import datetime, timedelta
from calendar import monthrange

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/category-breakdown', methods=['GET'], endpoint='category_breakdown')
@jwt_required()
def category_breakdown():
    """Get category-wise spending breakdown"""
    try:
        user_id = get_jwt_identity()
        
        # Get date parameters
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if month and year:
            # Specific month
            start_date = datetime(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = datetime(year, month, last_day, 23, 59, 59)
        else:
            # Default to current month
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
            _, last_day = monthrange(now.year, now.month)
            end_date = datetime(now.year, now.month, last_day, 23, 59, 59)
        
        analyzer = SpendingAnalyzer(user_id)
        breakdown = analyzer.get_category_breakdown(start_date, end_date)
        
        # Calculate totals
        total_spent = sum(cat['total'] for cat in breakdown.values())
        
        return jsonify({
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'month': start_date.strftime('%B %Y')
            },
            'total_spent': round(total_spent, 2),
            'categories': breakdown,
            'category_count': len(breakdown)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/monthly-summary', methods=['GET'], endpoint='monthly_summary')
@jwt_required()
def monthly_summary():
    """Get monthly spending summary"""
    try:
        user_id = get_jwt_identity()
        months = request.args.get('months', 6, type=int)
        
        if months > 24:
            months = 24  # Limit to 24 months
        
        analyzer = SpendingAnalyzer(user_id)
        summary = analyzer.get_monthly_summary(months)
        
        # Calculate averages
        if summary:
            avg_expenses = sum(m['expenses'] for m in summary) / len(summary)
            avg_income = sum(m['income'] for m in summary) / len(summary)
            avg_savings = sum(m['savings'] for m in summary) / len(summary)
        else:
            avg_expenses = avg_income = avg_savings = 0
        
        return jsonify({
            'months_analyzed': len(summary),
            'averages': {
                'monthly_expenses': round(avg_expenses, 2),
                'monthly_income': round(avg_income, 2),
                'monthly_savings': round(avg_savings, 2)
            },
            'monthly_data': summary
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/trends', methods=['GET'])
@jwt_required()
def spending_trends():
    """Detect spending trends"""
    try:
        user_id = get_jwt_identity()
        months = request.args.get('months', 3, type=int)
        
        analyzer = SpendingAnalyzer(user_id)
        result = analyzer.detect_trends(months)
        
        trends = result.get('trends', {})
        
        # Categorize trends
        increasing = []
        decreasing = []
        stable = []
        
        for category, data in trends.items():
            trend_item = {'category': category, **data}
            if data['direction'] == 'increasing':
                increasing.append(trend_item)
            elif data['direction'] == 'decreasing':
                decreasing.append(trend_item)
            else:
                stable.append(trend_item)
        
        return jsonify({
            'analysis_period_months': months,
            'message': result.get('message', ''),
            'trends': trends,
            'summary': {
                'increasing_categories': increasing,
                'decreasing_categories': decreasing,
                'stable_categories': stable,
                'total_categories_analyzed': len(trends)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@analysis_bp.route('/top-categories', methods=['GET'], endpoint='top_categories')
@jwt_required()
def top_categories():
    """Get top spending categories"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 5, type=int)
        
        analyzer = SpendingAnalyzer(user_id)
        top = analyzer.get_top_categories(limit)
        
        return jsonify({
            'top_categories': top,
            'total_categories': len(top)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/compare', methods=['GET'], endpoint='compare_periods')
@jwt_required()
def compare_periods():
    """Compare spending between two periods"""
    try:
        user_id = get_jwt_identity()
        
        # Get parameters
        current_month = request.args.get('current_month', type=int)
        current_year = request.args.get('current_year', type=int)
        previous_month = request.args.get('previous_month', type=int)
        previous_year = request.args.get('previous_year', type=int)
        
        now = datetime.now()
        
        # Set current period
        if current_month and current_year:
            current_start = datetime(current_year, current_month, 1)
            _, last_day = monthrange(current_year, current_month)
            current_end = datetime(current_year, current_month, last_day, 23, 59, 59)
        else:
            current_start = datetime(now.year, now.month, 1)
            _, last_day = monthrange(now.year, now.month)
            current_end = datetime(now.year, now.month, last_day, 23, 59, 59)
        
        # Set previous period
        if previous_month and previous_year:
            previous_start = datetime(previous_year, previous_month, 1)
            _, last_day = monthrange(previous_year, previous_month)
            previous_end = datetime(previous_year, previous_month, last_day, 23, 59, 59)
        else:
            # Default to previous month
            if current_start.month == 1:
                previous_start = datetime(current_start.year - 1, 12, 1)
            else:
                previous_start = datetime(current_start.year, current_start.month - 1, 1)
            _, last_day = monthrange(previous_start.year, previous_start.month)
            previous_end = datetime(previous_start.year, previous_start.month, last_day, 23, 59, 59)
        
        analyzer = SpendingAnalyzer(user_id)
        comparison = analyzer.compare_periods(
            current_start, current_end,
            previous_start, previous_end
        )
        
        return jsonify(comparison), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/patterns', methods=['GET'], endpoint='spending_patterns')
@jwt_required()
def spending_patterns():
    """Analyze spending patterns"""
    try:
        user_id = get_jwt_identity()
        
        analyzer = SpendingAnalyzer(user_id)
        patterns = analyzer.get_spending_patterns()
        
        return jsonify(patterns), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/insights', methods=['GET'], endpoint='comprehensive_insights')
@jwt_required()
def comprehensive_insights():
    """Get comprehensive spending insights"""
    try:
        user_id = get_jwt_identity()
        analyzer = SpendingAnalyzer(user_id)
        
        # Get current month breakdown
        now = datetime.now()
        current_start = datetime(now.year, now.month, 1)
        _, last_day = monthrange(now.year, now.month)
        current_end = datetime(now.year, now.month, last_day, 23, 59, 59)
        
        # Get previous month for comparison
        if now.month == 1:
            prev_start = datetime(now.year - 1, 12, 1)
        else:
            prev_start = datetime(now.year, now.month - 1, 1)
        _, last_day = monthrange(prev_start.year, prev_start.month)
        prev_end = datetime(prev_start.year, prev_start.month, last_day, 23, 59, 59)
        
        # Gather all insights
        insights = {
            'current_month': {
                'breakdown': analyzer.get_category_breakdown(current_start, current_end),
                'total': 0
            },
            'comparison': analyzer.compare_periods(current_start, current_end, prev_start, prev_end),
            'trends': analyzer.detect_trends(6),
            'patterns': analyzer.get_spending_patterns(),
            'top_categories': analyzer.get_top_categories(5)
        }
        
        # Calculate current month total
        current_total = sum(c['total'] for c in insights['current_month']['breakdown'].values())
        insights['current_month']['total'] = round(current_total, 2)
        
        # Add summary
        insights['summary'] = {
            'total_categories': len(insights['current_month']['breakdown']),
            'has_trends': len(insights['trends'].get('trends', {})) > 0,
            'comparison_with_last_month': insights['comparison'].get('overall_change', {}),
            'top_spending_category': insights['top_categories'][0] if insights['top_categories'] else None
        }
        
        return jsonify(insights), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500