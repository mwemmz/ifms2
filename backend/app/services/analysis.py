import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.models.user import Transaction
from sqlalchemy import extract, func
from collections import defaultdict

class SpendingAnalyzer:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def get_category_breakdown(self, start_date, end_date):
        """Get category-wise spending breakdown for a date range"""
        
        transactions = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_date.between(start_date, end_date),
            Transaction.amount < 0  # Only expenses
        ).all()
        
        if not transactions:
            return {}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([{
            'category': t.category,
            'amount': abs(t.amount)
        } for t in transactions])
        
        # Calculate breakdown
        breakdown = df.groupby('category').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        
        total_spent = df['amount'].sum()
        
        result = {}
        for category in breakdown.index:
            result[category] = {
                'total': float(breakdown.loc[category, ('amount', 'sum')]),
                'percentage': round(float(breakdown.loc[category, ('amount', 'sum')] / total_spent * 100), 2),
                'transaction_count': int(breakdown.loc[category, ('amount', 'count')]),
                'average_per_transaction': float(breakdown.loc[category, ('amount', 'mean')])
            }
        
        # Sort by total amount descending
        result = dict(sorted(result.items(), key=lambda x: x[1]['total'], reverse=True))
        
        return result
    
    def get_monthly_summary(self, months=6):
        """Get monthly spending summary for last N months"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)
        
        transactions = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_date.between(start_date, end_date)
        ).all()
        
        if not transactions:
            return []
        
        df = pd.DataFrame([{
            'year': t.transaction_date.year,
            'month': t.transaction_date.month,
            'amount': t.amount,
            'type': 'income' if t.amount > 0 else 'expense'
        } for t in transactions])
        
        # Group by year and month
        summary = []
        for (year, month), group in df.groupby(['year', 'month']):
            income = group[group['type'] == 'income']['amount'].sum()
            expenses = abs(group[group['type'] == 'expense']['amount'].sum())
            
            summary.append({
                'year': int(year),
                'month': int(month),
                'month_name': datetime(int(year), int(month), 1).strftime('%B'),
                'income': float(round(income, 2)),
                'expenses': float(round(expenses, 2)),
                'savings': float(round(income - expenses, 2)),
                'transaction_count': int(len(group))
            })
        
        # Sort by date descending
        summary.sort(key=lambda x: (x['year'], x['month']), reverse=True)
        
        return summary
    
    def detect_trends(self, months=3):
        """Detect spending trends in different categories"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)
        
        transactions = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_date.between(start_date, end_date),
            Transaction.amount < 0
        ).all()
        
        if len(transactions) < 5:
            return {'trends': {}, 'message': 'Insufficient data for trend analysis'}
        
        df = pd.DataFrame([{
            'date': t.transaction_date,
            'category': t.category,
            'amount': abs(t.amount)
        } for t in transactions])
        
        # Add month column
        df['month'] = df['date'].dt.to_period('M')
        
        trends = {}
        
        # Analyze each category
        for category in df['category'].unique():
            cat_data = df[df['category'] == category]
            
            # Group by month
            monthly = cat_data.groupby('month')['amount'].agg(['sum', 'count', 'mean']).reset_index()
            
            if len(monthly) >= 2:
                # Calculate trend using linear regression
                x = np.arange(len(monthly))
                y = monthly['sum'].values
                
                if len(y) >= 2 and y.std() > 0:
                    slope = np.polyfit(x, y, 1)[0]
                    
                    # Determine trend direction
                    if slope > 0:
                        direction = 'increasing'
                    elif slope < 0:
                        direction = 'decreasing'
                    else:
                        direction = 'stable'
                    
                    # Calculate percentage change
                    if len(y) >= 2 and y[0] > 0:
                        pct_change = ((y[-1] - y[0]) / y[0]) * 100
                    else:
                        pct_change = 0
                    
                    trends[category] = {
                        'direction': direction,
                        'slope': float(round(slope, 2)),
                        'percentage_change': float(round(pct_change, 2)),
                        'current_monthly_avg': float(round(monthly['sum'].iloc[-1], 2)),
                        'previous_monthly_avg': float(round(monthly['sum'].iloc[0], 2)) if len(monthly) > 1 else None,
                        'volatility': float(round(y.std(), 2))
                    }
        
        return {'trends': trends}
    
    def get_top_categories(self, limit=5):
        """Get top spending categories"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        breakdown = self.get_category_breakdown(start_date, end_date)
        
        # Sort by total and get top N
        top_categories = sorted(
            [{'category': k, **v} for k, v in breakdown.items()],
            key=lambda x: x['total'],
            reverse=True
        )[:limit]
        
        return top_categories
    
    def compare_periods(self, current_start, current_end, previous_start, previous_end):
        """Compare spending between two periods"""
        
        current = self.get_category_breakdown(current_start, current_end)
        previous = self.get_category_breakdown(previous_start, previous_end)
        
        comparison = {
            'current_period': {
                'start': current_start.strftime('%Y-%m-%d'),
                'end': current_end.strftime('%Y-%m-%d'),
                'total': float(sum(c['total'] for c in current.values())),
                'categories': current
            },
            'previous_period': {
                'start': previous_start.strftime('%Y-%m-%d'),
                'end': previous_end.strftime('%Y-%m-%d'),
                'total': float(sum(c['total'] for c in previous.values())),
                'categories': previous
            },
            'changes': {}
        }
        
        # Calculate changes
        current_total = comparison['current_period']['total']
        previous_total = comparison['previous_period']['total']
        
        if previous_total > 0:
            comparison['overall_change'] = {
                'absolute': float(round(current_total - previous_total, 2)),
                'percentage': float(round(((current_total - previous_total) / previous_total) * 100, 2))
            }
        
        # Category-wise changes
        all_categories = set(current.keys()) | set(previous.keys())
        for category in all_categories:
            current_amount = float(current.get(category, {}).get('total', 0))
            previous_amount = float(previous.get(category, {}).get('total', 0))
            
            if previous_amount > 0 or current_amount > 0:
                change = {
                    'current': current_amount,
                    'previous': previous_amount,
                    'absolute_change': float(round(current_amount - previous_amount, 2))
                }
                
                if previous_amount > 0:
                    change['percentage_change'] = float(round(((current_amount - previous_amount) / previous_amount) * 100, 2))
                else:
                    change['percentage_change'] = 100.0
                
                comparison['changes'][category] = change
        
        return comparison
    
    def get_spending_patterns(self):
        """Identify spending patterns like weekday vs weekend, etc."""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        transactions = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_date.between(start_date, end_date),
            Transaction.amount < 0
        ).all()
        
        if not transactions:
            return {}
        
        df = pd.DataFrame([{
            'date': t.transaction_date,
            'amount': abs(t.amount),
            'category': t.category,
            'weekday': t.transaction_date.strftime('%A'),
            'is_weekend': t.transaction_date.weekday() >= 5,
            'day_of_month': t.transaction_date.day
        } for t in transactions])
        
        patterns = {
            'weekday_vs_weekend': {
                'weekday': {
                    'total': float(df[~df['is_weekend']]['amount'].sum()),
                    'average': float(df[~df['is_weekend']]['amount'].mean()) if len(df[~df['is_weekend']]) > 0 else 0,
                    'count': int(len(df[~df['is_weekend']]))
                },
                'weekend': {
                    'total': float(df[df['is_weekend']]['amount'].sum()),
                    'average': float(df[df['is_weekend']]['amount'].mean()) if len(df[df['is_weekend']]) > 0 else 0,
                    'count': int(len(df[df['is_weekend']]))
                }
            },
            'by_day_of_week': {}
        }
        
        # Spending by day of week
        for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
            day_data = df[df['weekday'] == day]
            if len(day_data) > 0:
                patterns['by_day_of_week'][day] = {
                    'total': float(day_data['amount'].sum()),
                    'average': float(day_data['amount'].mean()),
                    'count': int(len(day_data))
                }
        
        # Peak spending days (first half vs second half of month)
        first_half = df[df['day_of_month'] <= 15]
        second_half = df[df['day_of_month'] > 15]
        
        patterns['month_halves'] = {
            'first_half': {
                'total': float(first_half['amount'].sum()) if len(first_half) > 0 else 0,
                'average': float(first_half['amount'].mean()) if len(first_half) > 0 else 0
            },
            'second_half': {
                'total': float(second_half['amount'].sum()) if len(second_half) > 0 else 0,
                'average': float(second_half['amount'].mean()) if len(second_half) > 0 else 0
            }
        }
        
        return patterns