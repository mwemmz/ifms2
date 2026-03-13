import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime, timedelta
from app.models.user import Transaction
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class ExpensePredictor:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def prepare_time_series_data(self, category=None, months=12):
        """Prepare time series data for prediction"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)
        
        # Query transactions
        query = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_date.between(start_date, end_date),
            Transaction.amount < 0  # Only expenses
        )
        
        if category:
            query = query.filter_by(category=category)
        
        transactions = query.all()
        
        if len(transactions) < 5:
            return None, None
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'date': t.transaction_date,
            'amount': abs(t.amount),
            'category': t.category,
            'month': t.transaction_date.month,
            'year': t.transaction_date.year
        } for t in transactions])
        
        # Group by month
        df['year_month'] = df['date'].dt.to_period('M')
        monthly_data = df.groupby('year_month').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        
        monthly_data.columns = ['total', 'count', 'average']
        monthly_data = monthly_data.reset_index()
        
        # Convert period to numeric for model
        monthly_data['period_num'] = range(len(monthly_data))
        
        return monthly_data, df
    
    def predict_next_month_linear(self, category=None):
        """Predict next month's expenses using linear regression"""
        
        monthly_data, raw_data = self.prepare_time_series_data(category, months=12)
        
        if monthly_data is None or len(monthly_data) < 3:
            return {
                'error': 'Insufficient data for prediction',
                'required_months': 3,
                'available_months': len(monthly_data) if monthly_data is not None else 0
            }
        
        # Prepare features and target
        X = monthly_data['period_num'].values.reshape(-1, 1)
        y_total = monthly_data['total'].values
        y_count = monthly_data['count'].values
        y_avg = monthly_data['average'].values
        
        # Train models
        model_total = LinearRegression()
        model_count = LinearRegression()
        model_avg = LinearRegression()
        
        model_total.fit(X, y_total)
        model_count.fit(X, y_count)
        model_avg.fit(X, y_avg)
        
        # Predict next month
        next_period = np.array([[len(monthly_data)]])
        predicted_total = max(0, model_total.predict(next_period)[0])
        predicted_count = max(1, round(model_count.predict(next_period)[0]))
        predicted_avg = max(0, model_avg.predict(next_period)[0])
        
        # Calculate confidence metrics
        confidence = self._calculate_confidence(monthly_data, model_total, X, y_total)
        
        # Get recent trend
        recent_trend = self._get_recent_trend(monthly_data)
        
        # Get seasonal factors if enough data
        seasonal_factors = self._get_seasonal_factors(raw_data) if raw_data is not None else {}
        
        result = {
            'prediction': {
                'total': round(float(predicted_total), 2),
                'transaction_count': int(predicted_count),
                'average_per_transaction': round(float(predicted_avg), 2)
            },
            'confidence': confidence,
            'trend': recent_trend,
            'based_on_months': len(monthly_data),
            'historical_data': {
                'months': monthly_data['year_month'].astype(str).tolist(),
                'totals': monthly_data['total'].tolist()
            }
        }
        
        if seasonal_factors:
            result['seasonal_factors'] = seasonal_factors
        
        if category:
            result['category'] = category
        else:
            result['category'] = 'all_expenses'
        
        return result
    
    def predict_next_month_polynomial(self, degree=2, category=None):
        """Predict using polynomial regression for non-linear trends"""
        
        monthly_data, _ = self.prepare_time_series_data(category, months=12)
        
        if monthly_data is None or len(monthly_data) < degree + 1:
            return self.predict_next_month_linear(category)  # Fallback to linear
        
        X = monthly_data['period_num'].values.reshape(-1, 1)
        y = monthly_data['total'].values
        
        # Create polynomial features
        poly = PolynomialFeatures(degree=min(degree, len(monthly_data)-1))
        X_poly = poly.fit_transform(X)
        
        # Train model
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # Predict next month
        next_period = np.array([[len(monthly_data)]])
        next_period_poly = poly.transform(next_period)
        predicted_total = max(0, model.predict(next_period_poly)[0])
        
        # Calculate R-squared for confidence
        r2 = r2_score(y, model.predict(X_poly))
        
        return {
            'prediction': {
                'total': round(float(predicted_total), 2),
                'method': f'polynomial_degree_{degree}'
            },
            'confidence': self._confidence_from_r2(r2),
            'r2_score': round(float(r2), 3),
            'based_on_months': len(monthly_data)
        }
    
    def predict_by_category(self):
        """Predict next month's expenses broken down by category"""
        
        # Get all unique categories
        transactions = Transaction.query.filter_by(
            user_id=self.user_id
        ).filter(Transaction.amount < 0).all()
        
        categories = set(t.category for t in transactions)
        
        category_predictions = {}
        total_predicted = 0
        
        for category in categories:
            pred = self.predict_next_month_linear(category)
            if 'error' not in pred:
                category_predictions[category] = {
                    'predicted': pred['prediction']['total'],
                    'confidence': pred['confidence'],
                    'trend': pred['trend']
                }
                total_predicted += pred['prediction']['total']
        
        # Sort by predicted amount
        category_predictions = dict(sorted(
            category_predictions.items(),
            key=lambda x: x[1]['predicted'],
            reverse=True
        ))
        
        return {
            'total_predicted': round(total_predicted, 2),
            'by_category': category_predictions,
            'categories_analyzed': len(category_predictions)
        }
    
    def moving_average_prediction(self, window=3):
        """Simple moving average prediction"""
        
        monthly_data, _ = self.prepare_time_series_data(months=12)
        
        if monthly_data is None or len(monthly_data) < window:
            return {'error': f'Need at least {window} months of data'}
        
        # Calculate moving average
        moving_avgs = monthly_data['total'].rolling(window=window).mean()
        
        # Use last moving average as prediction
        predicted_total = moving_avgs.iloc[-1]
        
        # Calculate trend
        if len(monthly_data) >= window * 2:
            first_avg = monthly_data['total'].iloc[:window].mean()
            last_avg = monthly_data['total'].iloc[-window:].mean()
            trend_pct = ((last_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
        else:
            trend_pct = 0
        
        return {
            'prediction': {
                'total': round(float(predicted_total), 2),
                'method': f'{window}_month_moving_average'
            },
            'trend': {
                'direction': 'increasing' if trend_pct > 5 else ('decreasing' if trend_pct < -5 else 'stable'),
                'percentage_change': round(float(trend_pct), 2)
            },
            'window_months': window,
            'based_on_months': len(monthly_data)
        }
    
    def ensemble_prediction(self):
        """Combine multiple prediction methods for better accuracy"""
        
        predictions = []
        weights = []
        
        # Linear regression
        linear = self.predict_next_month_linear()
        if 'error' not in linear:
            predictions.append(linear['prediction']['total'])
            weights.append(linear['confidence']['score'] / 100 if linear['confidence']['score'] > 0 else 0.5)
        
        # Moving average (3-month)
        ma3 = self.moving_average_prediction(3)
        if 'error' not in ma3:
            predictions.append(ma3['prediction']['total'])
            weights.append(0.6)  # Medium confidence
        
        # Moving average (6-month)
        ma6 = self.moving_average_prediction(6)
        if 'error' not in ma6:
            predictions.append(ma6['prediction']['total'])
            weights.append(0.4)  # Lower confidence for longer window
        
        if not predictions:
            return {'error': 'Could not generate any predictions'}
        
        # Weighted average
        weighted_avg = sum(p * w for p, w in zip(predictions, weights)) / sum(weights)
        
        # Calculate confidence based on agreement between methods
        if len(predictions) > 1:
            std_dev = np.std(predictions)
            mean_pred = np.mean(predictions)
            cv = std_dev / mean_pred if mean_pred > 0 else 1  # Coefficient of variation
            
            if cv < 0.1:
                ensemble_confidence = 'High'
            elif cv < 0.2:
                ensemble_confidence = 'Medium'
            else:
                ensemble_confidence = 'Low'
        else:
            ensemble_confidence = linear['confidence']['level'] if 'linear' in locals() else 'Medium'
        
        return {
            'prediction': {
                'total': round(float(weighted_avg), 2),
                'method': 'ensemble'
            },
            'individual_predictions': {
                'linear': linear.get('prediction', {}).get('total') if 'linear' in locals() else None,
                'moving_avg_3m': ma3.get('prediction', {}).get('total') if 'ma3' in locals() else None,
                'moving_avg_6m': ma6.get('prediction', {}).get('total') if 'ma6' in locals() else None
            },
            'confidence': ensemble_confidence,
            'methods_used': len(predictions)
        }
    
    def predict_future_months(self, months_ahead=3):
        """Predict expenses for multiple months ahead"""
        
        monthly_data, _ = self.prepare_time_series_data(months=12)
        
        if monthly_data is None or len(monthly_data) < 3:
            return {'error': 'Insufficient data for prediction'}
        
        X = monthly_data['period_num'].values.reshape(-1, 1)
        y = monthly_data['total'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        predictions = []
        last_period = len(monthly_data)
        
        for i in range(1, months_ahead + 1):
            next_period = np.array([[last_period + i - 1]])
            pred = max(0, model.predict(next_period)[0])
            
            # Add confidence decreases as we predict further
            confidence_factor = max(0.3, 1 - (i * 0.15))
            
            predictions.append({
                'month': (datetime.now() + timedelta(days=30*i)).strftime('%B %Y'),
                'predicted_total': round(float(pred), 2),
                'confidence_factor': round(confidence_factor * 100, 1)
            })
        
        return {
            'predictions': predictions,
            'based_on_months': len(monthly_data),
            'method': 'linear_trend_extrapolation'
        }
    
    def _calculate_confidence(self, monthly_data, model, X, y):
        """Calculate confidence level for prediction"""
        
        # R-squared score
        r2 = r2_score(y, model.predict(X))
        
        # Data volume factor
        data_points = len(monthly_data)
        if data_points >= 12:
            volume_factor = 1.0
        elif data_points >= 6:
            volume_factor = 0.8
        elif data_points >= 3:
            volume_factor = 0.5
        else:
            volume_factor = 0.3
        
        # Volatility factor (lower volatility = higher confidence)
        volatility = y.std() / y.mean() if y.mean() > 0 else 1
        if volatility < 0.2:
            volatility_factor = 1.0
        elif volatility < 0.4:
            volatility_factor = 0.7
        elif volatility < 0.6:
            volatility_factor = 0.4
        else:
            volatility_factor = 0.2
        
        # Combined confidence score
        confidence_score = (r2 * 0.4 + volume_factor * 0.3 + volatility_factor * 0.3) * 100
        
        # Determine confidence level
        if confidence_score >= 70:
            level = 'High'
        elif confidence_score >= 40:
            level = 'Medium'
        else:
            level = 'Low'
        
        return {
            'score': round(float(confidence_score), 1),
            'level': level,
            'r2_score': round(float(r2), 3),
            'data_points': data_points,
            'volatility': round(float(volatility), 2)
        }
    
    def _confidence_from_r2(self, r2):
        """Convert R² score to confidence level"""
        if r2 >= 0.7:
            return 'High'
        elif r2 >= 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_recent_trend(self, monthly_data):
        """Determine recent spending trend"""
        if len(monthly_data) < 3:
            return {'direction': 'unknown'}
        
        recent = monthly_data.tail(3)['total'].values
        older = monthly_data.head(3)['total'].values if len(monthly_data) >= 6 else None
        
        if older is not None:
            recent_avg = np.mean(recent)
            older_avg = np.mean(older)
            
            if recent_avg > older_avg * 1.1:
                direction = 'increasing'
                strength = 'strong' if recent_avg > older_avg * 1.2 else 'moderate'
            elif recent_avg < older_avg * 0.9:
                direction = 'decreasing'
                strength = 'strong' if recent_avg < older_avg * 0.8 else 'moderate'
            else:
                direction = 'stable'
                strength = 'stable'
        else:
            # Simple trend from linear regression
            x = np.arange(len(recent))
            slope = np.polyfit(x, recent, 1)[0]
            
            if slope > recent.mean() * 0.1:
                direction = 'increasing'
                strength = 'moderate'
            elif slope < -recent.mean() * 0.1:
                direction = 'decreasing'
                strength = 'moderate'
            else:
                direction = 'stable'
                strength = 'stable'
        
        return {
            'direction': direction,
            'strength': strength
        }
    
    def _get_seasonal_factors(self, df):
        """Identify seasonal patterns (if enough data)"""
        if df is None or len(df) < 24:  # Need 2 years for seasonal analysis
            return {}
        
        # Add month column
        df['month'] = df['date'].dt.month
        
        # Calculate average by month
        monthly_avg = df.groupby('month')['amount'].mean()
        
        overall_avg = df['amount'].mean()
        
        seasonal_factors = {}
        for month in range(1, 13):
            if month in monthly_avg.index:
                factor = monthly_avg[month] / overall_avg if overall_avg > 0 else 1
                seasonal_factors[datetime(2000, month, 1).strftime('%B')] = round(float(factor), 2)
        
        return seasonal_factors