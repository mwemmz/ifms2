from datetime import datetime, timedelta
from app.models.user import User, UserProfile, Transaction
from app.services.analysis import SpendingAnalyzer
from app.services.prediction import ExpensePredictor
from sqlalchemy import func
import numpy as np

class FinancialAdvisor:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(user_id)
        self.analyzer = SpendingAnalyzer(user_id)
        self.predictor = ExpensePredictor(user_id)
        
        # Financial rules
        self.SAVINGS_RULE = 0.20  # Should save at least 20% of income
        self.ESSENTIALS_RULE = 0.50  # Essentials should be ≤50% of income
        self.WANTS_RULE = 0.30  # Wants should be ≤30% of income
        self.EMERGENCY_FUND_MONTHS = 6  # Emergency fund should cover 6 months
        
        # Category classifications
        self.ESSENTIAL_CATEGORIES = [
            'Rent/Mortgage',
            'Bills & Utilities',
            'Healthcare',
            'Insurance',
            'Groceries'  # Note: We'll need to map 'Food & Dining' to Groceries partially
        ]
        
        self.WANTS_CATEGORIES = [
            'Entertainment',
            'Shopping',
            'Travel',
            'Dining Out',
            'Gifts & Donations',
            'Personal Care'
        ]

    def get_financial_health_score(self):
        """Calculate overall financial health score (0-100)"""
        try:
            scores = []
            weights = []
            
            # Get user profile
            profile = self.user.profile
            
            # 1. Savings rate score (30% weight)
            savings_rate = self._calculate_savings_rate()
            if savings_rate is not None:
                if savings_rate >= 0.20:
                    savings_score = 100
                elif savings_rate >= 0.15:
                    savings_score = 75
                elif savings_rate >= 0.10:
                    savings_score = 50
                elif savings_rate >= 0.05:
                    savings_score = 25
                else:
                    savings_score = 0
                scores.append(savings_score)
                weights.append(30)
            
            # 2. Essentials ratio score (25% weight)
            essentials_ratio = self._calculate_essentials_ratio()
            if essentials_ratio is not None:
                if essentials_ratio <= 0.50:
                    essentials_score = 100
                elif essentials_ratio <= 0.60:
                    essentials_score = 75
                elif essentials_ratio <= 0.70:
                    essentials_score = 50
                elif essentials_ratio <= 0.80:
                    essentials_score = 25
                else:
                    essentials_score = 0
                scores.append(essentials_score)
                weights.append(25)
            
            # 3. Emergency fund score (20% weight)
            if profile and profile.monthly_salary > 0:
                emergency_fund = self._calculate_emergency_fund()
                target = profile.monthly_salary * self.EMERGENCY_FUND_MONTHS
                
                if emergency_fund >= target:
                    emergency_score = 100
                elif emergency_fund >= target * 0.75:
                    emergency_score = 75
                elif emergency_fund >= target * 0.50:
                    emergency_score = 50
                elif emergency_fund >= target * 0.25:
                    emergency_score = 25
                else:
                    emergency_score = 0
                
                scores.append(emergency_score)
                weights.append(20)
            
            # 4. Spending consistency score (15% weight)
            consistency_score = self._calculate_spending_consistency()
            if consistency_score is not None:
                scores.append(consistency_score)
                weights.append(15)
            
            # 5. Goal progress score (10% weight)
            if profile and profile.savings_goal > 0:
                goal_progress = self._calculate_goal_progress()
                goal_score = min(100, goal_progress * 100)
                scores.append(goal_score)
                weights.append(10)
            
            # Calculate weighted average
            if scores and weights:
                weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
                return round(weighted_score, 1)
            
            return 50  # Default if not enough data
            
        except Exception as e:
            print(f"Error calculating health score: {e}")
            return 50

    def detect_overspending(self):
        """Detect categories with overspending"""
        try:
            # Get current month spending
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
            
            # Get last month for comparison
            if now.month == 1:
                prev_start = datetime(now.year - 1, 12, 1)
            else:
                prev_start = datetime(now.year, now.month - 1, 1)
            
            # Get category breakdowns
            current = self.analyzer.get_category_breakdown(start_date, now)
            previous = self.analyzer.get_category_breakdown(prev_start, start_date - timedelta(days=1))
            
            overspending = []
            
            # Check each category
            for category, data in current.items():
                if category in previous:
                    prev_amount = previous[category]['total']
                    curr_amount = data['total']
                    
                    # If spending increased by more than 20%
                    if prev_amount > 0 and curr_amount > prev_amount * 1.2:
                        increase_pct = ((curr_amount - prev_amount) / prev_amount) * 100
                        overspending.append({
                            'category': category,
                            'current': round(curr_amount, 2),
                            'previous': round(prev_amount, 2),
                            'increase_percentage': round(increase_pct, 1),
                            'excess_amount': round(curr_amount - prev_amount, 2),
                            'severity': 'high' if increase_pct > 50 else 'medium'
                        })
            
            return sorted(overspending, key=lambda x: x['excess_amount'], reverse=True)
            
        except Exception as e:
            print(f"Error detecting overspending: {e}")
            return []

    def generate_recommendations(self):
        """Generate personalized financial recommendations"""
        recommendations = []
        
        # Get user profile and data
        profile = self.user.profile
        
        # 1. Savings rate recommendation
        savings_rate = self._calculate_savings_rate()
        if savings_rate is not None:
            if savings_rate < 0.10:
                recommendations.append({
                    'type': 'warning',
                    'category': 'savings',
                    'priority': 'high',
                    'title': 'Low Savings Rate',
                    'message': f'You are only saving {savings_rate*100:.1f}% of your income.',
                    'suggestion': 'Try to save at least 20% of your income. Consider automating transfers to a savings account.',
                    'actionable': True,
                    'action': 'Set up automatic savings transfer'
                })
            elif savings_rate < 0.20:
                recommendations.append({
                    'type': 'info',
                    'category': 'savings',
                    'priority': 'medium',
                    'title': 'Good Savings Rate',
                    'message': f'You are saving {savings_rate*100:.1f}% of your income.',
                    'suggestion': 'You\'re doing well! Try to increase to 20% by reducing non-essential spending.',
                    'actionable': True,
                    'action': 'Review wants categories for savings opportunities'
                })
        
        # 2. Essentials ratio recommendation
        essentials_ratio = self._calculate_essentials_ratio()
        if essentials_ratio is not None:
            if essentials_ratio > 0.60:
                recommendations.append({
                    'type': 'warning',
                    'category': 'budgeting',
                    'priority': 'high',
                    'title': 'High Essential Expenses',
                    'message': f'Essentials are consuming {essentials_ratio*100:.1f}% of your income.',
                    'suggestion': 'Look for ways to reduce fixed costs like utilities, insurance, or consider refinancing.',
                    'actionable': True,
                    'action': 'Review essential expenses for savings'
                })
        
        # 3. Emergency fund recommendation
        if profile and profile.monthly_salary > 0:
            emergency_fund = self._calculate_emergency_fund()
            target = profile.monthly_salary * self.EMERGENCY_FUND_MONTHS
            
            if emergency_fund < target:
                months_covered = emergency_fund / profile.monthly_salary if profile.monthly_salary > 0 else 0
                recommendations.append({
                    'type': 'warning',
                    'category': 'emergency_fund',
                    'priority': 'high' if months_covered < 3 else 'medium',
                    'title': 'Incomplete Emergency Fund',
                    'message': f'Your emergency fund covers only {months_covered:.1f} months of expenses.',
                    'suggestion': f'Aim for {self.EMERGENCY_FUND_MONTHS} months of expenses. Target: ${target:,.2f}',
                    'actionable': True,
                    'action': 'Increase emergency fund contributions'
                })
        
        # 4. Category-specific overspending
        overspending = self.detect_overspending()
        for item in overspending[:3]:  # Top 3
            recommendations.append({
                'type': 'warning',
                'category': 'overspending',
                'priority': item['severity'],
                'title': f'Overspending in {item["category"]}',
                'message': f'You spent ${item["excess_amount"]} more than last month ({item["increase_percentage"]}% increase).',
                'suggestion': f'Set a monthly budget for {item["category"]} and track your spending.',
                'actionable': True,
                'action': f'Create {item["category"]} budget'
            })
        
        # 5. Wants vs Needs analysis
        wants_ratio = self._calculate_wants_ratio()
        if wants_ratio is not None and wants_ratio > 0.35:
            recommendations.append({
                'type': 'info',
                'category': 'wants',
                'priority': 'medium',
                'title': 'High Discretionary Spending',
                'message': f'You spend {wants_ratio*100:.1f}% on non-essential items.',
                'suggestion': 'Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.',
                'actionable': True,
                'action': 'Review wants categories'
            })
        
        # 6. Goal progress
        if profile and profile.savings_goal > 0:
            progress = self._calculate_goal_progress()
            if progress < 0.25:
                recommendations.append({
                    'type': 'info',
                    'category': 'goals',
                    'priority': 'medium',
                    'title': 'Savings Goal Progress',
                    'message': f'You\'re {progress*100:.1f}% toward your savings goal of ${profile.savings_goal:,.2f}.',
                    'suggestion': 'Consider increasing monthly savings to reach your goal faster.',
                    'actionable': True,
                    'action': 'Adjust savings target'
                })
            elif progress >= 1.0:
                recommendations.append({
                    'type': 'success',
                    'category': 'goals',
                    'priority': 'low',
                    'title': 'Goal Achieved! 🎉',
                    'message': 'Congratulations! You\'ve reached your savings goal!',
                    'suggestion': 'Set a new savings goal to keep building wealth.',
                    'actionable': True,
                    'action': 'Set new goal'
                })
        
        # 7. Investment suggestion
        if savings_rate is not None and savings_rate > 0.15 and emergency_fund >= target:
            recommendations.append({
                'type': 'success',
                'category': 'investing',
                'priority': 'low',
                'title': 'Ready to Invest',
                'message': 'You have strong savings and emergency fund!',
                'suggestion': 'Consider investing in low-cost index funds for long-term growth.',
                'actionable': True,
                'action': 'Explore investment options'
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations

    def get_budget_suggestions(self):
        """Generate personalized budget suggestions"""
        try:
            profile = self.user.profile
            if not profile or not profile.monthly_salary:
                return {'error': 'Monthly salary not set'}
            
            monthly_income = profile.monthly_salary
            
            # Ideal budget based on 50/30/20 rule
            ideal_budget = {
                'essentials': monthly_income * 0.50,
                'wants': monthly_income * 0.30,
                'savings': monthly_income * 0.20
            }
            
            # Current spending
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
            
            current_spending = self.analyzer.get_category_breakdown(start_date, now)
            
            # Categorize current spending
            current_essentials = 0
            current_wants = 0
            
            for category, data in current_spending.items():
                if category in self.ESSENTIAL_CATEGORIES:
                    current_essentials += data['total']
                elif category in self.WANTS_CATEGORIES:
                    current_wants += data['total']
                elif category == 'Food & Dining':
                    # Split food between essentials (groceries) and wants (dining out)
                    # Assuming 60% groceries, 40% dining out if not specified
                    current_essentials += data['total'] * 0.6
                    current_wants += data['total'] * 0.4
            
            current_savings = max(0, monthly_income - current_essentials - current_wants)
            
            # Generate adjustments
            adjustments = []
            
            if current_essentials > ideal_budget['essentials']:
                excess = current_essentials - ideal_budget['essentials']
                adjustments.append({
                    'category': 'essentials',
                    'current': round(current_essentials, 2),
                    'target': round(ideal_budget['essentials'], 2),
                    'excess': round(excess, 2),
                    'suggestion': 'Look for ways to reduce fixed costs'
                })
            
            if current_wants > ideal_budget['wants']:
                excess = current_wants - ideal_budget['wants']
                adjustments.append({
                    'category': 'wants',
                    'current': round(current_wants, 2),
                    'target': round(ideal_budget['wants'], 2),
                    'excess': round(excess, 2),
                    'suggestion': 'Reduce discretionary spending'
                })
            
            if current_savings < ideal_budget['savings']:
                deficit = ideal_budget['savings'] - current_savings
                adjustments.append({
                    'category': 'savings',
                    'current': round(current_savings, 2),
                    'target': round(ideal_budget['savings'], 2),
                    'deficit': round(deficit, 2),
                    'suggestion': 'Increase savings rate'
                })
            
            return {
                'monthly_income': round(monthly_income, 2),
                'ideal_budget': {
                    'essentials': round(ideal_budget['essentials'], 2),
                    'wants': round(ideal_budget['wants'], 2),
                    'savings': round(ideal_budget['savings'], 2)
                },
                'current_spending': {
                    'essentials': round(current_essentials, 2),
                    'wants': round(current_wants, 2),
                    'savings': round(current_savings, 2)
                },
                'adjustments_needed': adjustments,
                'health_score': self.get_financial_health_score()
            }
            
        except Exception as e:
            return {'error': str(e)}

    def get_savings_opportunities(self):
        """Identify potential savings opportunities"""
        try:
            opportunities = []
            
            # Get last 3 months of transactions
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date.between(start_date, end_date),
                Transaction.amount < 0
            ).all()
            
            if not transactions:
                return []
            
            # Group by description to find recurring expenses
            recurring = {}
            for t in transactions:
                if t.description and len(t.description) > 3:
                    key = t.description.lower().strip()
                    if key not in recurring:
                        recurring[key] = {
                            'description': t.description,
                            'total': 0,
                            'count': 0,
                            'category': t.category
                        }
                    recurring[key]['total'] += abs(t.amount)
                    recurring[key]['count'] += 1
            
            # Find subscription-like expenses (recurring monthly)
            for item in recurring.values():
                if item['count'] >= 2 and item['total'] / item['count'] < 100:
                    monthly_avg = item['total'] / item['count']
                    
                    # Check if it's a subscription service
                    subscription_keywords = ['netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 
                                           'gym', 'subscription', 'membership']
                    
                    is_subscription = any(keyword in item['description'].lower() 
                                         for keyword in subscription_keywords)
                    
                    if is_subscription:
                        opportunities.append({
                            'type': 'subscription',
                            'description': item['description'],
                            'monthly_cost': round(monthly_avg, 2),
                            'annual_cost': round(monthly_avg * 12, 2),
                            'suggestion': 'Review if you\'re actively using this subscription'
                        })
            
            # Find categories with high spending
            breakdown = self.analyzer.get_category_breakdown(start_date, end_date)
            for category, data in breakdown.items():
                if data['total'] > 500 and category in self.WANTS_CATEGORIES:
                    opportunities.append({
                        'type': 'high_spending',
                        'category': category,
                        'monthly_avg': round(data['total'] / 3, 2),  # Over 3 months
                        'suggestion': f'Set a monthly limit for {category}'
                    })
            
            return opportunities
            
        except Exception as e:
            print(f"Error finding savings opportunities: {e}")
            return []

    def get_financial_insights(self):
        """Get comprehensive financial insights"""
        try:
            profile = self.user.profile
            
            insights = {
                'health_score': self.get_financial_health_score(),
                'recommendations': self.generate_recommendations(),
                'budget_suggestions': self.get_budget_suggestions(),
                'savings_opportunities': self.get_savings_opportunities(),
                'overspending': self.detect_overspending()
            }
            
            # Add summary metrics
            if profile:
                insights['summary'] = {
                    'monthly_income': profile.monthly_salary,
                    'savings_goal': profile.savings_goal,
                    'emergency_fund': self._calculate_emergency_fund()
                }
            
            # Add next month prediction
            prediction = self.predictor.predict_next_month_linear()
            if 'error' not in prediction:
                insights['next_month_prediction'] = prediction['prediction']
            
            return insights
            
        except Exception as e:
            return {'error': str(e)}

    # Helper methods
    def _calculate_savings_rate(self):
        """Calculate savings rate as percentage of income"""
        try:
            # Get last 3 months average
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date.between(start_date, end_date)
            ).all()
            
            if not transactions:
                return None
            
            total_income = sum(t.amount for t in transactions if t.amount > 0)
            total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
            
            if total_income > 0:
                savings = total_income - total_expenses
                return savings / total_income
            
            return None
            
        except Exception:
            return None

    def _calculate_essentials_ratio(self):
        """Calculate essentials as percentage of income"""
        try:
            profile = self.user.profile
            if not profile or not profile.monthly_salary:
                return None
            
            # Get current month essentials
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
            
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount < 0
            ).all()
            
            essentials_total = 0
            for t in transactions:
                if t.category in self.ESSENTIAL_CATEGORIES:
                    essentials_total += abs(t.amount)
                elif t.category == 'Food & Dining':
                    # Assume 60% of food is essentials (groceries)
                    essentials_total += abs(t.amount) * 0.6
            
            return essentials_total / profile.monthly_salary if profile.monthly_salary > 0 else None
            
        except Exception:
            return None

    def _calculate_wants_ratio(self):
        """Calculate wants as percentage of income"""
        try:
            profile = self.user.profile
            if not profile or not profile.monthly_salary:
                return None
            
            # Get current month wants
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
            
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount < 0
            ).all()
            
            wants_total = 0
            for t in transactions:
                if t.category in self.WANTS_CATEGORIES:
                    wants_total += abs(t.amount)
                elif t.category == 'Food & Dining':
                    # Assume 40% of food is wants (dining out)
                    wants_total += abs(t.amount) * 0.4
            
            return wants_total / profile.monthly_salary if profile.monthly_salary > 0 else None
            
        except Exception:
            return None

    def _calculate_emergency_fund(self):
        """Calculate current emergency fund"""
        try:
            # Assume savings are cumulative
            end_date = datetime.now()
            start_date = datetime(end_date.year - 2, end_date.month, 1)  # Last 2 years
            
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date.between(start_date, end_date)
            ).all()
            
            total_savings = sum(t.amount for t in transactions if t.amount > 0)
            total_withdrawn = sum(abs(t.amount) for t in transactions 
                                 if t.amount < 0 and t.category == 'Emergency')
            
            return max(0, total_savings - total_withdrawn)
            
        except Exception:
            return 0

    def _calculate_goal_progress(self):
        """Calculate progress toward savings goal"""
        try:
            profile = self.user.profile
            if not profile or not profile.savings_goal or profile.savings_goal <= 0:
                return 0
            
            emergency_fund = self._calculate_emergency_fund()
            return emergency_fund / profile.savings_goal
            
        except Exception:
            return 0

    def _calculate_spending_consistency(self):
        """Calculate spending consistency score"""
        try:
            # Get last 6 months of expenses
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date.between(start_date, end_date),
                Transaction.amount < 0
            ).all()
            
            if len(transactions) < 10:
                return None
            
            # Group by month
            monthly_totals = {}
            for t in transactions:
                month_key = t.transaction_date.strftime('%Y-%m')
                if month_key not in monthly_totals:
                    monthly_totals[month_key] = 0
                monthly_totals[month_key] += abs(t.amount)
            
            amounts = list(monthly_totals.values())
            if len(amounts) < 3:
                return None
            
            # Calculate coefficient of variation
            mean_amount = np.mean(amounts)
            if mean_amount > 0:
                cv = np.std(amounts) / mean_amount
                
                # Convert to score (lower CV = higher score)
                if cv < 0.1:
                    return 100
                elif cv < 0.2:
                    return 80
                elif cv < 0.3:
                    return 60
                elif cv < 0.4:
                    return 40
                else:
                    return 20
            
            return None
            
        except Exception:
            return None