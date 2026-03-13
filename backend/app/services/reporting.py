import calendar
from datetime import datetime, timedelta
from app.models.user import User, Transaction
from app.services.analysis import SpendingAnalyzer
from app.services.prediction import ExpensePredictor
from app.services.advisor import FinancialAdvisor
from app.services.budget import BudgetPlanner
from collections import defaultdict
import json
from app.utils.currency import CurrencyFormatter

class ReportGenerator:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(user_id)
        self.analyzer = SpendingAnalyzer(user_id)
        self.predictor = ExpensePredictor(user_id)
        self.advisor = FinancialAdvisor(user_id)
        self.planner = BudgetPlanner(user_id)
    
    def generate_monthly_report(self, month=None, year=None):
        """Generate comprehensive monthly financial report"""
        try:
            # Set date
            if not month or not year:
                now = datetime.now()
                month = now.month
                year = now.year
            
            # Date ranges
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Previous month for comparison
            if month == 1:
                prev_month = 12
                prev_year = year - 1
            else:
                prev_month = month - 1
                prev_year = year
            
            prev_start = datetime(prev_year, prev_month, 1)
            if prev_month == 12:
                prev_end = datetime(prev_year + 1, 1, 1) - timedelta(days=1)
            else:
                prev_end = datetime(prev_year, prev_month + 1, 1) - timedelta(days=1)
            
            # Get data
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date.between(start_date, end_date)
            ).all()
            
            # Calculate metrics
            total_income = sum(t.amount for t in transactions if t.amount > 0)
            total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
            net_savings = total_income - total_expenses

            # Format currency values
            total_income_formatted = CurrencyFormatter.format(total_income)
            total_expenses_formatted = CurrencyFormatter.format(total_expenses)
            net_savings_formatted = CurrencyFormatter.format(net_savings)
            
            # Category breakdown
            category_breakdown = self.analyzer.get_category_breakdown(start_date, end_date)
            
            # Daily spending pattern
            daily_spending = self._get_daily_spending(start_date, end_date)
            
            # Comparison with previous month
            prev_metrics = self._get_month_metrics(prev_start, prev_end)
            comparison = self._calculate_comparison(
                total_expenses, prev_metrics['total_expenses'],
                total_income, prev_metrics['total_income']
            )
            
            # Get budget comparison
            budget_comparison = self.planner.compare_budget_vs_actual(month, year)
            
            # Get predictions for next month
            predictions = self.predictor.predict_next_month_linear()
            
            # Get financial advice
            recommendations = self.advisor.generate_recommendations()
            
            # Build report
            report = {
                'report_id': f"monthly_{year}_{month}_{self.user_id}",
                'report_type': 'monthly',
                'generated_at': datetime.now().isoformat(),
                'period': {
                    'month': calendar.month_name[month],
                    'year': year,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days_in_month': (end_date - start_date).days + 1
                },
                'summary': {
                    'total_income': round(total_income, 2),
                    'total_expenses': round(total_expenses, 2),
                    'net_savings': round(net_savings, 2),
                    'savings_rate': round((net_savings / total_income * 100) if total_income > 0 else 0, 1),
                    'transaction_count': len(transactions),
                    'avg_daily_expense': round(total_expenses / (end_date - start_date).days, 2) if (end_date - start_date).days > 0 else 0
                },
                'comparison_vs_previous': comparison,
                'category_breakdown': category_breakdown,
                'daily_spending': daily_spending,
                'budget_comparison': budget_comparison if 'error' not in budget_comparison else None,
                'top_categories': self._get_top_categories(category_breakdown, 5),
                'predictions': {
                    'next_month': predictions.get('prediction') if 'error' not in predictions else None,
                    'confidence': predictions.get('confidence') if 'error' not in predictions else None
                },
                'recommendations': recommendations[:3] if recommendations else [],  # Top 3
                'charts': self._generate_chart_data(category_breakdown, daily_spending, total_income, total_expenses)
            }
            
            # Add insights
            report['insights'] = self._generate_insights(report)
            
            return report
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_yearly_report(self, year):
        """Generate yearly financial report"""
        try:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            
            # Get all transactions for the year
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date.between(start_date, end_date)
            ).all()
            
            # Monthly breakdown
            monthly_data = []
            monthly_totals = []
            
            for month in range(1, 13):
                month_start = datetime(year, month, 1)
                if month == 12:
                    month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = datetime(year, month + 1, 1) - timedelta(days=1)
                
                month_transactions = [t for t in transactions 
                                    if month_start <= t.transaction_date <= month_end]
                
                month_income = sum(t.amount for t in month_transactions if t.amount > 0)
                month_expenses = sum(abs(t.amount) for t in month_transactions if t.amount < 0)
                
                monthly_data.append({
                    'month': calendar.month_name[month],
                    'month_num': month,
                    'income': round(month_income, 2),
                    'expenses': round(month_expenses, 2),
                    'savings': round(month_income - month_expenses, 2),
                    'transaction_count': len(month_transactions)
                })
                
                monthly_totals.append(month_expenses)
            
            # Yearly totals
            total_income = sum(t.amount for t in transactions if t.amount > 0)
            total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
            
            # Category breakdown for the year
            category_breakdown = self.analyzer.get_category_breakdown(start_date, end_date)
            
            # Calculate averages and trends
            avg_monthly_expense = total_expenses / 12 if total_expenses > 0 else 0
            
            # Seasonal patterns
            seasonal_patterns = self._analyze_seasonal_patterns(monthly_data)
            
            # Year-over-year comparison if previous year data exists
            prev_year_data = self._get_yearly_comparison(year)
            
            # Build report
            report = {
                'report_id': f"yearly_{year}_{self.user_id}",
                'report_type': 'yearly',
                'generated_at': datetime.now().isoformat(),
                'period': {
                    'year': year,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                },
                'summary': {
                    'total_income': round(total_income, 2),
                    'total_expenses': round(total_expenses, 2),
                    'total_savings': round(total_income - total_expenses, 2),
                    'avg_monthly_expense': round(avg_monthly_expense, 2),
                    'avg_monthly_income': round(total_income / 12, 2),
                    'transaction_count': len(transactions),
                    'months_with_data': len([m for m in monthly_data if m['transaction_count'] > 0])
                },
                'monthly_breakdown': monthly_data,
                'category_breakdown': category_breakdown,
                'top_categories': self._get_top_categories(category_breakdown, 10),
                'seasonal_patterns': seasonal_patterns,
                'year_over_year': prev_year_data,
                'charts': self._generate_yearly_charts(monthly_data, category_breakdown)
            }
            
            # Add insights
            report['insights'] = self._generate_yearly_insights(report)
            
            return report
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_category_report(self, category, months=6):
        """Generate detailed report for a specific category"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30 * months)
            
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.category == category,
                Transaction.transaction_date.between(start_date, end_date),
                Transaction.amount < 0
            ).all()
            
            if not transactions:
                return {'error': f'No transactions found for category: {category}'}
            
            # Monthly breakdown
            monthly_data = defaultdict(lambda: {'total': 0, 'count': 0, 'transactions': []})
            
            for t in transactions:
                month_key = t.transaction_date.strftime('%Y-%m')
                monthly_data[month_key]['total'] += abs(t.amount)
                monthly_data[month_key]['count'] += 1
                monthly_data[month_key]['transactions'].append({
                    'date': t.transaction_date.strftime('%Y-%m-%d'),
                    'amount': abs(t.amount),
                    'description': t.description
                })
            
            # Convert to list and sort
            monthly_list = []
            for month, data in monthly_data.items():
                monthly_list.append({
                    'month': month,
                    'total': round(data['total'], 2),
                    'count': data['count'],
                    'average': round(data['total'] / data['count'], 2) if data['count'] > 0 else 0,
                    'transactions': data['transactions'][-5:]  # Last 5 transactions
                })
            
            monthly_list.sort(key=lambda x: x['month'])
            
            # Calculate trends
            totals = [m['total'] for m in monthly_list]
            trend = 'increasing' if len(totals) > 1 and totals[-1] > totals[0] else 'decreasing' if len(totals) > 1 and totals[-1] < totals[0] else 'stable'
            
            # Predict next month
            predictor = ExpensePredictor(self.user_id)
            prediction = predictor.predict_next_month_linear(category)
            
            # Get advice for this category
            advice = self._get_category_advice(category, monthly_list)
            
            return {
                'category': category,
                'period_months': months,
                'summary': {
                    'total_spent': round(sum(m['total'] for m in monthly_list), 2),
                    'average_monthly': round(sum(m['total'] for m in monthly_list) / len(monthly_list), 2),
                    'total_transactions': sum(m['count'] for m in monthly_list),
                    'average_per_transaction': round(sum(m['total'] for m in monthly_list) / sum(m['count'] for m in monthly_list), 2) if sum(m['count'] for m in monthly_list) > 0 else 0,
                    'trend': trend
                },
                'monthly_breakdown': monthly_list,
                'prediction': prediction.get('prediction') if 'error' not in prediction else None,
                'advice': advice,
                'charts': {
                    'monthly_totals': {
                        'labels': [m['month'] for m in monthly_list],
                        'data': [m['total'] for m in monthly_list]
                    }
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_comparison_report(self, year1, year2):
        """Compare spending between two years"""
        try:
            report1 = self.generate_yearly_report(year1)
            report2 = self.generate_yearly_report(year2)
            
            if 'error' in report1 or 'error' in report2:
                return {'error': 'Could not generate comparison'}
            
            # Calculate differences
            diff_income = report2['summary']['total_income'] - report1['summary']['total_income']
            diff_expenses = report2['summary']['total_expenses'] - report1['summary']['total_expenses']
            diff_savings = report2['summary']['total_savings'] - report1['summary']['total_savings']
            
            # Category comparison
            category_comparison = []
            all_categories = set(report1['category_breakdown'].keys()) | set(report2['category_breakdown'].keys())
            
            for category in all_categories:
                amount1 = report1['category_breakdown'].get(category, {}).get('total', 0)
                amount2 = report2['category_breakdown'].get(category, {}).get('total', 0)
                
                if amount1 > 0 or amount2 > 0:
                    change = amount2 - amount1
                    change_pct = (change / amount1 * 100) if amount1 > 0 else 100
                    
                    category_comparison.append({
                        'category': category,
                        'year1': round(amount1, 2),
                        'year2': round(amount2, 2),
                        'change': round(change, 2),
                        'change_percentage': round(change_pct, 1),
                        'trend': 'up' if change > 0 else 'down' if change < 0 else 'stable'
                    })
            
            # Monthly comparison
            monthly_comparison = []
            for i in range(12):
                month_data1 = next((m for m in report1['monthly_breakdown'] if m['month_num'] == i+1), None)
                month_data2 = next((m for m in report2['monthly_breakdown'] if m['month_num'] == i+1), None)
                
                monthly_comparison.append({
                    'month': calendar.month_name[i+1],
                    'year1_expenses': month_data1['expenses'] if month_data1 else 0,
                    'year2_expenses': month_data2['expenses'] if month_data2 else 0,
                    'year1_income': month_data1['income'] if month_data1 else 0,
                    'year2_income': month_data2['income'] if month_data2 else 0
                })
            
            return {
                'comparison': {
                    'years': f"{year1} vs {year2}",
                    'income_change': {
                        'absolute': round(diff_income, 2),
                        'percentage': round((diff_income / report1['summary']['total_income']) * 100 if report1['summary']['total_income'] > 0 else 0, 1)
                    },
                    'expenses_change': {
                        'absolute': round(diff_expenses, 2),
                        'percentage': round((diff_expenses / report1['summary']['total_expenses']) * 100 if report1['summary']['total_expenses'] > 0 else 0, 1)
                    },
                    'savings_change': {
                        'absolute': round(diff_savings, 2),
                        'percentage': round((diff_savings / report1['summary']['total_savings']) * 100 if report1['summary']['total_savings'] > 0 else 0, 1)
                    }
                },
                'category_comparison': sorted(category_comparison, key=lambda x: abs(x['change']), reverse=True),
                'monthly_comparison': monthly_comparison
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_export_data(self, format='json'):
        """Generate exportable financial data"""
        try:
            # Get all transactions
            transactions = Transaction.query.filter_by(user_id=self.user_id).all()
            
            # Basic user info
            user_data = {
                'username': self.user.username,
                'email': self.user.email,
                'member_since': self.user.created_at.strftime('%Y-%m-%d')
            }
            
            if self.user.profile:
                user_data['profile'] = {
                    'full_name': self.user.profile.full_name,
                    'monthly_salary': self.user.profile.monthly_salary,
                    'savings_goal': self.user.profile.savings_goal
                }
            
            # Transaction data
            transaction_data = []
            for t in transactions:
                transaction_data.append({
                    'id': t.id,
                    'date': t.transaction_date.strftime('%Y-%m-%d'),
                    'amount': t.amount,
                    'category': t.category,
                    'description': t.description,
                    'type': 'income' if t.amount > 0 else 'expense'
                })
            
            # Summary statistics
            total_income = sum(t.amount for t in transactions if t.amount > 0)
            total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
            
            # Category summaries
            category_summary = {}
            for t in transactions:
                if t.amount < 0:
                    cat = t.category
                    if cat not in category_summary:
                        category_summary[cat] = {
                            'total': 0,
                            'count': 0,
                            'average': 0
                        }
                    category_summary[cat]['total'] += abs(t.amount)
                    category_summary[cat]['count'] += 1
            
            for cat in category_summary:
                category_summary[cat]['average'] = category_summary[cat]['total'] / category_summary[cat]['count']
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'user': user_data,
                'summary': {
                    'total_transactions': len(transactions),
                    'total_income': round(total_income, 2),
                    'total_expenses': round(total_expenses, 2),
                    'net_savings': round(total_income - total_expenses, 2),
                    'date_range': {
                        'first_transaction': min((t.transaction_date for t in transactions), default=None).strftime('%Y-%m-%d') if transactions else None,
                        'last_transaction': max((t.transaction_date for t in transactions), default=None).strftime('%Y-%m-%d') if transactions else None
                    }
                },
                'category_summary': category_summary,
                'transactions': transaction_data
            }
            
            if format == 'json':
                return export_data
            elif format == 'csv':
                return self._convert_to_csv(transaction_data)
            else:
                return export_data
                
        except Exception as e:
            return {'error': str(e)}
    
    # Helper methods
    def _get_month_metrics(self, start_date, end_date):
        """Get metrics for a specific month"""
        transactions = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_date.between(start_date, end_date)
        ).all()
        
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': total_income - total_expenses
        }
    
    def _calculate_comparison(self, current_expenses, prev_expenses, current_income, prev_income):
        """Calculate period-over-period comparison"""
        comparison = {}
        
        if prev_expenses > 0:
            expense_change = ((current_expenses - prev_expenses) / prev_expenses) * 100
            comparison['expenses'] = {
                'current': round(current_expenses, 2),
                'previous': round(prev_expenses, 2),
                'change': round(current_expenses - prev_expenses, 2),
                'change_percentage': round(expense_change, 1),
                'trend': 'up' if expense_change > 0 else 'down' if expense_change < 0 else 'stable'
            }
        
        if prev_income > 0:
            income_change = ((current_income - prev_income) / prev_income) * 100
            comparison['income'] = {
                'current': round(current_income, 2),
                'previous': round(prev_income, 2),
                'change': round(current_income - prev_income, 2),
                'change_percentage': round(income_change, 1),
                'trend': 'up' if income_change > 0 else 'down' if income_change < 0 else 'stable'
            }
        
        return comparison
    
    def _get_daily_spending(self, start_date, end_date):
        """Get daily spending pattern"""
        transactions = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_date.between(start_date, end_date),
            Transaction.amount < 0
        ).all()
        
        daily = defaultdict(float)
        for t in transactions:
            day = t.transaction_date.day
            daily[day] += abs(t.amount)
        
        # Create array for all days of month
        days_in_month = (end_date - start_date).days + 1
        daily_spending = []
        
        for day in range(1, days_in_month + 1):
            daily_spending.append({
                'day': day,
                'amount': round(daily.get(day, 0), 2)
            })
        
        return daily_spending
    
    def _get_top_categories(self, category_breakdown, limit):
        """Get top categories by spending"""
        categories = []
        for category, data in category_breakdown.items():
            categories.append({
                'category': category,
                'amount': data['total'],
                'percentage': data['percentage']
            })
        
        categories.sort(key=lambda x: x['amount'], reverse=True)
        return categories[:limit]
    
    def _generate_chart_data(self, category_breakdown, daily_spending, total_income, total_expenses):
        """Generate chart-ready data"""
        # ...existing code...
        # The report definition should be at this indentation level
        # If you need to use report, define it here
        # ...existing code...
        
        # Income vs Expenses
        charts['income_vs_expenses'] = {
            'labels': ['Income', 'Expenses', 'Savings'],
            'datasets': [{
                'data': [total_income, total_expenses, total_income - total_expenses],
                'backgroundColor': ['rgba(75, 192, 192, 0.5)', 'rgba(255, 99, 132, 0.5)', 'rgba(54, 162, 235, 0.5)']
            }]
        }
        
        return charts
    
    def _generate_yearly_charts(self, monthly_data, category_breakdown):
        """Generate charts for yearly report"""
        charts = {}
        
        # Monthly trend line
        charts['monthly_trend'] = {
            'labels': [m['month'] for m in monthly_data],
            'datasets': [
                {
                    'label': 'Income',
                    'data': [m['income'] for m in monthly_data],
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'fill': False
                },
                {
                    'label': 'Expenses',
                    'data': [m['expenses'] for m in monthly_data],
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'fill': False
                }
            ]
        }
        
        # Category breakdown pie
        charts['category_pie'] = {
            'labels': list(category_breakdown.keys()),
            'datasets': [{
                'data': [c['total'] for c in category_breakdown.values()],
                'backgroundColor': self._generate_colors(len(category_breakdown))
            }]
        }
        
        # Savings by month
        charts['savings_by_month'] = {
            'labels': [m['month'] for m in monthly_data],
            'datasets': [{
                'label': 'Savings',
                'data': [m['savings'] for m in monthly_data],
                'backgroundColor': 'rgba(54, 162, 235, 0.5)'
            }]
        }
        
        return charts
    
    def _generate_colors(self, count):
        """Generate random colors for charts"""
        colors = []
        base_colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF9F40'
        ]
        
        for i in range(count):
            if i < len(base_colors):
                colors.append(base_colors[i])
            else:
                # Generate random color
                import random
                colors.append(f'rgba({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)}, 0.5)')
        
        return colors
    
    def _generate_insights(self, report):
        """Generate textual insights from the report"""
        insights = []
        
        summary = report['summary']
        
        # Savings insight
        if summary['savings_rate'] >= 20:
            insights.append(f"✅ Excellent savings rate of {summary['savings_rate']}%! You're saving well above the recommended 20%.")
        elif summary['savings_rate'] >= 15:
            insights.append(f"👍 Good savings rate of {summary['savings_rate']}%. You're close to the 20% target.")
        elif summary['savings_rate'] >= 10:
            insights.append(f"📈 Your savings rate is {summary['savings_rate']}%. Consider reducing expenses to reach 20%.")
        else:
            insights.append(f"⚠️ Low savings rate of {summary['savings_rate']}%. Review your spending to increase savings.")
        
        # Comparison insight
        if 'expenses' in report['comparison_vs_previous']:
            exp_change = report['comparison_vs_previous']['expenses']['change_percentage']
            if exp_change > 10:
                insights.append(f"📊 Expenses increased by {exp_change}% compared to last month. Review your spending in top categories.")
            elif exp_change < -10:
                insights.append(f"📉 Great job! Expenses decreased by {abs(exp_change)}% compared to last month.")
        
        # Top category insight
        if report['top_categories']:
            top_cat = report['top_categories'][0]
            insights.append(f"💰 Your highest spending category is {top_cat['category']} at ${top_cat['amount']} ({top_cat['percentage']}% of total).")
        
        # Daily average insight
        insights.append(f"📅 You spent an average of ${summary['avg_daily_expense']} per day this month.")
        
        return insights
    
    def _generate_yearly_insights(self, report):
        """Generate insights for yearly report"""
        insights = []
        
        summary = report['summary']
        
        # Overall insight
        insights.append(f"📊 In {report['period']['year']}, you {'saved' if summary['total_savings'] > 0 else 'lost'} ${abs(summary['total_savings']):,.2f} overall.")
        
        # Best and worst months
        if report['monthly_breakdown']:
            best_month = min(report['monthly_breakdown'], key=lambda x: x['expenses'])
            worst_month = max(report['monthly_breakdown'], key=lambda x: x['expenses'])
            
            insights.append(f"🌟 Your lowest spending month was {best_month['month']} (${best_month['expenses']:,.2f})")
            insights.append(f"⚠️ Your highest spending month was {worst_month['month']} (${worst_month['expenses']:,.2f})")
        
        # Seasonal pattern
        if 'seasonal_patterns' in report and report['seasonal_patterns']:
            patterns = report['seasonal_patterns']
            if patterns.get('highest_quarter'):
                insights.append(f"📈 You tend to spend more in {patterns['highest_quarter']}.")
            if patterns.get('lowest_quarter'):
                insights.append(f"📉 You tend to spend less in {patterns['lowest_quarter']}.")
        
        return insights
    
    def _analyze_seasonal_patterns(self, monthly_data):
        """Analyze seasonal spending patterns"""
        if len(monthly_data) < 12:
            return {}
        
        # Group by quarter
        quarters = {
            'Q1 (Jan-Mar)': [m['expenses'] for m in monthly_data[:3]],
            'Q2 (Apr-Jun)': [m['expenses'] for m in monthly_data[3:6]],
            'Q3 (Jul-Sep)': [m['expenses'] for m in monthly_data[6:9]],
            'Q4 (Oct-Dec)': [m['expenses'] for m in monthly_data[9:12]]
        }
        
        quarter_averages = {}
        for quarter, expenses in quarters.items():
            if expenses:
                quarter_averages[quarter] = sum(expenses) / len(expenses)
        
        if quarter_averages:
            highest_quarter = max(quarter_averages, key=quarter_averages.get)
            lowest_quarter = min(quarter_averages, key=quarter_averages.get)
            
            return {
                'highest_quarter': highest_quarter,
                'lowest_quarter': lowest_quarter,
                'quarter_averages': quarter_averages
            }
        
        return {}
    
    def _get_yearly_comparison(self, year):
        """Get data from previous year for comparison"""
        prev_year = year - 1
        
        prev_year_data = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_date.between(
                datetime(prev_year, 1, 1),
                datetime(prev_year, 12, 31)
            )
        ).all()
        
        if not prev_year_data:
            return None
        
        total_income = sum(t.amount for t in prev_year_data if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in prev_year_data if t.amount < 0)
        
        return {
            'year': prev_year,
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'total_savings': round(total_income - total_expenses, 2)
        }
    
    def _get_category_advice(self, category, monthly_data):
        """Get advice for a specific category"""
        if not monthly_data:
            return "No data available for this category."
        
        recent = monthly_data[-1]['total'] if monthly_data else 0
        average = sum(m['total'] for m in monthly_data) / len(monthly_data)
        
        if recent > average * 1.2:
            return f"⚠️ Spending in {category} is {((recent/average)-1)*100:.1f}% above your average. Consider if this is necessary."
        elif recent < average * 0.8:
            return f"👍 Great job! Spending in {category} is {((1 - recent/average)*100):.1f}% below your average."
        else:
            return f"✓ Spending in {category} is consistent with your historical average."
    
    def _convert_to_csv(self, transactions):
        """Convert transaction data to CSV format"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Amount', 'Category', 'Description', 'Type'])
        
        # Write data
        for t in transactions:
            writer.writerow([
                t['date'],
                t['amount'],
                t['category'],
                t['description'],
                t['type']
            ])
        
        return output.getvalue()