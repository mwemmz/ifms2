from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.prediction import ExpensePredictor
from datetime import datetime

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/next-month', methods=['GET'])
@jwt_required()
def predict_next_month():
    """Predict expenses for next month using linear regression"""
    try:
        user_id = get_jwt_identity()
        category = request.args.get('category')
        
        predictor = ExpensePredictor(user_id)
        prediction = predictor.predict_next_month_linear(category)
        
        return jsonify(prediction), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/by-category', methods=['GET'])
@jwt_required()
def predict_by_category():
    """Get predictions broken down by category"""
    try:
        user_id = get_jwt_identity()
        
        predictor = ExpensePredictor(user_id)
        predictions = predictor.predict_by_category()
        
        return jsonify(predictions), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/moving-average', methods=['GET'])
@jwt_required()
def moving_average():
    """Predict using moving average"""
    try:
        user_id = get_jwt_identity()
        window = request.args.get('window', 3, type=int)
        
        if window < 2 or window > 12:
            return jsonify({'error': 'Window must be between 2 and 12'}), 400
        
        predictor = ExpensePredictor(user_id)
        prediction = predictor.moving_average_prediction(window)
        
        return jsonify(prediction), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/polynomial', methods=['GET'])
@jwt_required()
def polynomial_prediction():
    """Predict using polynomial regression"""
    try:
        user_id = get_jwt_identity()
        degree = request.args.get('degree', 2, type=int)
        category = request.args.get('category')
        
        if degree < 2 or degree > 4:
            return jsonify({'error': 'Degree must be between 2 and 4'}), 400
        
        predictor = ExpensePredictor(user_id)
        prediction = predictor.predict_next_month_polynomial(degree, category)
        
        return jsonify(prediction), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/ensemble', methods=['GET'])
@jwt_required()
def ensemble_prediction():
    """Combine multiple prediction methods"""
    try:
        user_id = get_jwt_identity()
        
        predictor = ExpensePredictor(user_id)
        prediction = predictor.ensemble_prediction()
        
        return jsonify(prediction), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/multi-month', methods=['GET'])
@jwt_required()
def multi_month_prediction():
    """Predict for multiple months ahead"""
    try:
        user_id = get_jwt_identity()
        months = request.args.get('months', 3, type=int)
        
        if months < 1 or months > 6:
            return jsonify({'error': 'Months must be between 1 and 6'}), 400
        
        predictor = ExpensePredictor(user_id)
        predictions = predictor.predict_future_months(months)
        
        return jsonify(predictions), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/insights', methods=['GET'])
@jwt_required()
def prediction_insights():
    """Get comprehensive prediction insights"""
    try:
        user_id = get_jwt_identity()
        
        predictor = ExpensePredictor(user_id)
        
        # Gather all predictions
        insights = {
            'next_month': predictor.predict_next_month_linear(),
            'by_category': predictor.predict_by_category(),
            'ensemble': predictor.ensemble_prediction(),
            'three_month_outlook': predictor.predict_future_months(3)
        }
        
        # Add comparison of methods
        methods = ['linear', 'moving_avg', 'ensemble']
        predictions = []
        
        if 'error' not in insights['next_month']:
            predictions.append({
                'method': 'Linear Regression',
                'predicted': insights['next_month']['prediction']['total'],
                'confidence': insights['next_month']['confidence']['level']
            })
        
        ma = predictor.moving_average_prediction(3)
        if 'error' not in ma:
            predictions.append({
                'method': '3-Month Moving Average',
                'predicted': ma['prediction']['total'],
                'confidence': 'Medium'
            })
        
        if 'error' not in insights['ensemble']:
            predictions.append({
                'method': 'Ensemble',
                'predicted': insights['ensemble']['prediction']['total'],
                'confidence': insights['ensemble']['confidence']
            })
        
        insights['method_comparison'] = predictions
        
        # Calculate average of predictions
        if predictions:
            avg_prediction = sum(p['predicted'] for p in predictions) / len(predictions)
            insights['average_prediction'] = round(avg_prediction, 2)
        
        return jsonify(insights), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/health', methods=['GET'])
@jwt_required()
def prediction_health():
    """Check if we have enough data for predictions"""
    try:
        user_id = get_jwt_identity()
        
        # Get transaction count
        from app.models.user import Transaction
        transaction_count = Transaction.query.filter_by(user_id=user_id).count()
        
        # Get monthly data availability
        predictor = ExpensePredictor(user_id)
        monthly_data, _ = predictor.prepare_time_series_data(months=12)
        
        status = {
            'has_enough_data': False,
            'transaction_count': transaction_count,
            'months_of_data': len(monthly_data) if monthly_data is not None else 0,
            'can_predict': False,
            'available_methods': []
        }
        
        if monthly_data is not None and len(monthly_data) >= 3:
            status['has_enough_data'] = True
            
            if len(monthly_data) >= 3:
                status['available_methods'].append('linear_regression')
                status['available_methods'].append('moving_average')
            
            if len(monthly_data) >= 6:
                status['available_methods'].append('polynomial_regression')
                status['available_methods'].append('ensemble')
            
            if len(monthly_data) >= 12:
                status['available_methods'].append('seasonal_analysis')
            
            status['can_predict'] = len(status['available_methods']) > 0
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500