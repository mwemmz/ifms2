from datetime import datetime, timedelta
from app.models.user import User, UserProfile, Transaction
from app.services.analysis import SpendingAnalyzer
from app.services.prediction import ExpensePredictor
from app.services.advisor import FinancialAdvisor
import numpy as np
from collections import defaultdict

class BudgetPlanner:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(user_id)
        self.analyzer = SpendingAnalyzer(user_id)
        self.predictor = ExpensePredictor(user_id)
        self.advisor = FinancialAdvisor(user_id)
        
        # Budget rules
        self.ESSENTIALS_TARGET = 0.50  # 50% for needs
        self.WANTS_TARGET = 0.30        # 30% for wants
        self.SAVINGS_TARGET = 0.20       # 20% for savings
        
    def generate_monthly_budget(self, month=None, year=None):
        """Generate a complete monthly budget"""
        try:
            # Set date
            if not month or not year:
                now = datetime.now()
                month = now.month
                year = now.year
            
            # Get user profile
            profile = self.user.profile
            if not profile or not profile.monthly_salary:
                return {'error': 'Monthly salary not set. Please update your profile.'}
            
            monthly_income = profile.monthly_salary
            
            # Calculate ideal budget based on 50/30/20 rule
            ideal_budget = {
                'essentials': monthly_income * self.ESSENTIALS_TARGET,
                'wants': monthly_income * self.WANTS_TARGET,
                'savings': monthly_income * self.SAVINGS_TARGET
            }
            
            # Get historical spending patterns
            historical_avg = self._get_historical_averages()
            
            # Get category-specific recommendations
            category_budgets = self._generate_category_budgets(monthly_income, historical_avg)
            
            # Calculate projected savings
            projected_expenses = sum(cat['allocated'] for cat in category_budgets.values())
            projected_savings = monthly_income - projected_expenses
            
            # Check if budget meets savings goal
            savings_goal_met = projected_savings >= ideal_budget['savings']
            
            # Generate budget adjustments if needed
            adjustments = self._generate_budget_adjustments(
                category_budgets, 
                projected_savings, 
                ideal_budget['savings']
            )
            
            # Create budget periods
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            budget = {
                'budget_id': f"budget_{year}_{month}_{self.user_id}",
                'period': {
                    'month': start_date.strftime('%B'),
                    'year': year,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days_in_month': (end_date - start_date).days + 1
                },
                'income': {
                    'monthly_salary': monthly_income,
                    'other_income': 0,  # Could be added later
                    'total_income': monthly_income
                },
                'ideal_budget': ideal_budget,
                'category_budgets': category_budgets,
                'summary': {
                    'total_budgeted': round(projected_expenses, 2),
                    'projected_savings': round(projected_savings, 2),
                    'savings_rate': round((projected_savings / monthly_income) * 100, 1) if monthly_income > 0 else 0,
                    'savings_goal_met': savings_goal_met,
                    'remaining_for_savings': round(max(0, ideal_budget['savings'] - projected_savings), 2) if not savings_goal_met else 0
                },
                'adjustments_needed': adjustments,
                'tips': self._generate_budget_tips(category_budgets, projected_savings, monthly_income)
            }
            
            # Add goal information if exists
            if profile.savings_goal > 0:
                current_savings = self.advisor._calculate_emergency_fund()
                goal_progress = (current_savings / profile.savings_goal) * 100 if profile.savings_goal > 0 else 0
                
                months_to_goal = (profile.savings_goal - current_savings) / projected_savings if projected_savings > 0 else float('inf')
                
                budget['savings_goal'] = {
                    'target': profile.savings_goal,
                    'current': round(current_savings, 2),
                    'progress_percentage': round(goal_progress, 1),
                    'months_to_goal': round(months_to_goal, 1) if months_to_goal != float('inf') else 'N/A',
                    'on_track': projected_savings >= (profile.savings_goal - current_savings) / 12 if profile.savings_goal > current_savings else True
                }
            
            return budget
            
        except Exception as e:
            return {'error': str(e)}
    
    def compare_budget_vs_actual(self, month=None, year=None):
        """Compare budgeted amounts with actual spending"""
        try:
            # Set date
            if not month or not year:
                now = datetime.now()
                month = now.month
                year = now.year
            
            # Get budget
            budget = self.generate_monthly_budget(month, year)
            if 'error' in budget:
                return budget
            
            # Get actual spending
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            actual_spending = self.analyzer.get_category_breakdown(start_date, end_date)
            
            # Calculate totals
            total_actual = sum(cat['total'] for cat in actual_spending.values())
            total_budgeted = budget['summary']['total_budgeted']
            
            # Compare by category
            comparison = []
            for category, budget_data in budget['category_budgets'].items():
                actual = actual_spending.get(category, {}).get('total', 0)
                budgeted = budget_data['allocated']
                
                diff = actual - budgeted
                diff_percentage = (diff / budgeted * 100) if budgeted > 0 else 0
                
                status = 'over' if diff > 0 else 'under' if diff < 0 else 'on track'
                
                comparison.append({
                    'category': category,
                    'budgeted': round(budgeted, 2),
                    'actual': round(actual, 2),
                    'difference': round(diff, 2),
                    'difference_percentage': round(abs(diff_percentage), 1),
                    'status': status,
                    'priority': 'high' if diff > budgeted * 0.2 else 'medium' if diff > 0 else 'low'
                })
            
            # Add categories with actual but no budget
            for category in actual_spending:
                if category not in budget['category_budgets']:
                    comparison.append({
                        'category': category,
                        'budgeted': 0,
                        'actual': round(actual_spending[category]['total'], 2),
                        'difference': round(actual_spending[category]['total'], 2),
                        'difference_percentage': 100,
                        'status': 'unbudgeted',
                        'priority': 'medium'
                    })
            
            # Sort by difference (largest overspend first)
            comparison.sort(key=lambda x: abs(x['difference']), reverse=True)
            
            return {
                'period': budget['period'],
                'income': budget['income'],
                'summary': {
                    'total_budgeted': total_budgeted,
                    'total_actual': round(total_actual, 2),
                    'total_difference': round(total_budgeted - total_actual, 2),
                    'actual_savings': round(budget['income']['total_income'] - total_actual, 2),
                    'budgeted_savings': budget['summary']['projected_savings'],
                    'savings_variance': round((budget['income']['total_income'] - total_actual) - budget['summary']['projected_savings'], 2)
                },
                'category_comparison': comparison,
                'categories_over_budget': len([c for c in comparison if c['status'] == 'over']),
                'categories_under_budget': len([c for c in comparison if c['status'] == 'under'])
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_future_budgets(self, months=3):
        """Generate budgets for future months"""
        try:
            now = datetime.now()
            future_budgets = []
            
            for i in range(months):
                # Calculate future month/year
                future_date = now + timedelta(days=30 * (i + 1))
                month = future_date.month
                year = future_date.year
                
                # Generate budget
                budget = self.generate_monthly_budget(month, year)
                if 'error' not in budget:
                    # Add prediction confidence
                    if i == 0:
                        confidence = 'High'
                    elif i == 1:
                        confidence = 'Medium'
                    else:
                        confidence = 'Low'
                    
                    future_budgets.append({
                        'month': budget['period']['month'],
                        'year': budget['period']['year'],
                        'total_budget': budget['summary']['total_budgeted'],
                        'projected_savings': budget['summary']['projected_savings'],
                        'savings_rate': budget['summary']['savings_rate'],
                        'confidence': confidence,
                        'categories': len(budget['category_budgets'])
                    })
            
            return {
                'future_budgets': future_budgets,
                'total_months': len(future_budgets)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_budget_recommendations(self):
        """Get recommendations for budget optimization"""
        try:
            profile = self.user.profile
            if not profile or not profile.monthly_salary:
                return {'error': 'Monthly salary not set'}
            
            # Get current budget vs actual for last month
            now = datetime.now()
            last_month = now.month - 1 if now.month > 1 else 12
            last_month_year = now.year if now.month > 1 else now.year - 1
            
            comparison = self.compare_budget_vs_actual(last_month, last_month_year)
            
            recommendations = []
            
            if 'error' not in comparison:
                # Analyze overspending patterns
                over_budget_cats = [c for c in comparison['category_comparison'] if c['status'] == 'over']
                
                for cat in over_budget_cats[:3]:  # Top 3
                    if cat['difference_percentage'] > 20:
                        recommendations.append({
                            'type': 'budget_adjustment',
                            'category': cat['category'],
                            'current_budget': cat['budgeted'],
                            'suggested_budget': round(cat['budgeted'] * 1.15, 2),  # Increase by 15%
                            'reason': f'Consistently over budget by {cat["difference_percentage"]}%',
                            'action': 'Consider increasing budget or reducing spending'
                        })
                
                # Find under-budget categories for reallocation
                under_budget_cats = [c for c in comparison['category_comparison'] if c['status'] == 'under' and c['difference'] < -20]
                
                for cat in under_budget_cats[:2]:
                    recommendations.append({
                        'type': 'reallocation',
                        'category': cat['category'],
                        'potential_savings': round(abs(cat['difference']), 2),
                        'suggestion': f'You consistently spend less in {cat["category"]}. Consider reallocating to savings.'
                    })
            
            # Get savings opportunities
            opportunities = self.advisor.get_savings_opportunities()
            for opp in opportunities[:2]:
                recommendations.append({
                    'type': 'savings_opportunity',
                    'description': opp['description'] if 'description' in opp else f"Reduce {opp['category']} spending",
                    'potential_savings': opp.get('monthly_cost', opp.get('monthly_avg', 0)),
                    'suggestion': opp['suggestion']
                })
            
            return {
                'recommendations': recommendations,
                'count': len(recommendations)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def create_smart_budget(self, target_savings_rate=None):
        """Create a smart budget that optimizes for a target savings rate"""
        try:
            profile = self.user.profile
            if not profile or not profile.monthly_salary:
                return {'error': 'Monthly salary not set'}
            
            monthly_income = profile.monthly_salary
            
            # Use provided target or default to 20%
            if target_savings_rate is None:
                target_savings_rate = self.SAVINGS_TARGET
            
            # Ensure reasonable range
            target_savings_rate = max(0.05, min(0.50, target_savings_rate))
            
            # Calculate available for expenses
            available_for_expenses = monthly_income * (1 - target_savings_rate)
            
            # Get historical spending patterns
            historical_avg = self._get_historical_averages()
            
            # Distribute budget based on historical patterns
            smart_budget = {}
            
            if historical_avg and sum(historical_avg.values()) > 0:
                total_historical = sum(historical_avg.values())
                
                for category, avg in historical_avg.items():
                    # Allocate proportionally to historical spending
                    proportion = avg / total_historical
                    smart_budget[category] = {
                        'allocated': round(available_for_expenses * proportion, 2),
                        'historical_avg': round(avg, 2),
                        'change': round((available_for_expenses * proportion) - avg, 2)
                    }
            else:
                # If no historical data, use default distribution
                smart_budget = self._get_default_category_budgets(available_for_expenses)
            
            # Calculate totals
            total_budgeted = sum(cat['allocated'] for cat in smart_budget.values())
            projected_savings = monthly_income - total_budgeted
            
            return {
                'income': monthly_income,
                'target_savings_rate': target_savings_rate * 100,
                'target_savings_amount': round(monthly_income * target_savings_rate, 2),
                'available_for_expenses': round(available_for_expenses, 2),
                'category_budgets': smart_budget,
                'summary': {
                    'total_budgeted': round(total_budgeted, 2),
                    'projected_savings': round(projected_savings, 2),
                    'actual_savings_rate': round((projected_savings / monthly_income) * 100, 1),
                    'on_target': abs(projected_savings - (monthly_income * target_savings_rate)) < 10
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    # Helper methods
    def _get_historical_averages(self):
        """Get average spending by category over last 3 months"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = Transaction.query.filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date.between(start_date, end_date),
                Transaction.amount < 0
            ).all()
            
            if not transactions:
                return {}
            
            # Group by category
            category_totals = defaultdict(float)
            for t in transactions:
                category_totals[t.category] += abs(t.amount)
            
            # Calculate monthly averages
            monthly_averages = {}
            for category, total in category_totals.items():
                monthly_averages[category] = total / 3  # Over 3 months
            
            return monthly_averages
            
        except Exception:
            return {}
    
    def _generate_category_budgets(self, monthly_income, historical_avg):
        """Generate detailed category budgets"""
        try:
            category_budgets = {}
            
            # Define category groups
            essential_categories = self.advisor.ESSENTIAL_CATEGORIES
            wants_categories = self.advisor.WANTS_CATEGORIES
            
            # Calculate target amounts by group
            essentials_target = monthly_income * self.ESSENTIALS_TARGET
            wants_target = monthly_income * self.WANTS_TARGET
            
            if historical_avg:
                # Distribute based on historical patterns
                total_essentials_hist = sum(historical_avg.get(cat, 0) for cat in essential_categories if cat in historical_avg)
                total_wants_hist = sum(historical_avg.get(cat, 0) for cat in wants_categories if cat in historical_avg)
                
                # Process essential categories
                for category in essential_categories:
                    if category in historical_avg:
                        if total_essentials_hist > 0:
                            proportion = historical_avg[category] / total_essentials_hist
                            allocated = essentials_target * proportion
                        else:
                            allocated = essentials_target / len([c for c in essential_categories if c in historical_avg])
                    else:
                        allocated = 0
                    
                    category_budgets[category] = {
                        'allocated': round(allocated, 2),
                        'type': 'essential',
                        'historical_avg': round(historical_avg.get(category, 0), 2),
                        'notes': self._get_category_note(category, allocated, historical_avg.get(category, 0))
                    }
                
                # Process wants categories
                for category in wants_categories:
                    if category in historical_avg:
                        if total_wants_hist > 0:
                            proportion = historical_avg[category] / total_wants_hist
                            allocated = wants_target * proportion
                        else:
                            allocated = wants_target / len([c for c in wants_categories if c in historical_avg])
                    else:
                        allocated = 0
                    
                    category_budgets[category] = {
                        'allocated': round(allocated, 2),
                        'type': 'want',
                        'historical_avg': round(historical_avg.get(category, 0), 2),
                        'notes': self._get_category_note(category, allocated, historical_avg.get(category, 0))
                    }
                
                # Handle Food & Dining specially (split between essentials and wants)
                if 'Food & Dining' in historical_avg:
                    food_total = historical_avg['Food & Dining']
                    # Assume 60% groceries (essential), 40% dining out (want)
                    groceries_part = food_total * 0.6
                    dining_part = food_total * 0.4
                    
                    # Add to existing or create new
                    if 'Groceries' not in category_budgets:
                        category_budgets['Groceries'] = {
                            'allocated': round(groceries_part, 2),
                            'type': 'essential',
                            'historical_avg': round(groceries_part, 2),
                            'notes': 'Based on 60% of food spending'
                        }
                    
                    if 'Dining Out' not in category_budgets:
                        category_budgets['Dining Out'] = {
                            'allocated': round(dining_part, 2),
                            'type': 'want',
                            'historical_avg': round(dining_part, 2),
                            'notes': 'Based on 40% of food spending'
                        }
                    
                    # Remove Food & Dining from budget
                    if 'Food & Dining' in category_budgets:
                        del category_budgets['Food & Dining']
            
            else:
                # No historical data, use default distribution
                category_budgets = self._get_default_category_budgets(essentials_target + wants_target)
            
            return category_budgets
            
        except Exception as e:
            print(f"Error generating category budgets: {e}")
            return {}
    
    def _get_default_category_budgets(self, total_expense_budget):
        """Get default category budgets when no history exists"""
        defaults = {
            'Rent/Mortgage': {'type': 'essential', 'weight': 0.35},
            'Bills & Utilities': {'type': 'essential', 'weight': 0.10},
            'Groceries': {'type': 'essential', 'weight': 0.15},
            'Transportation': {'type': 'essential', 'weight': 0.10},
            'Healthcare': {'type': 'essential', 'weight': 0.05},
            'Insurance': {'type': 'essential', 'weight': 0.05},
            'Dining Out': {'type': 'want', 'weight': 0.08},
            'Entertainment': {'type': 'want', 'weight': 0.05},
            'Shopping': {'type': 'want', 'weight': 0.04},
            'Personal Care': {'type': 'want', 'weight': 0.02},
            'Travel': {'type': 'want', 'weight': 0.01}
        }
        
        category_budgets = {}
        total_weight = sum(item['weight'] for item in defaults.values())
        
        for category, data in defaults.items():
            allocated = (data['weight'] / total_weight) * total_expense_budget
            category_budgets[category] = {
                'allocated': round(allocated, 2),
                'type': data['type'],
                'historical_avg': 0,
                'notes': 'Default budget based on typical spending patterns'
            }
        
        return category_budgets
    
    def _get_category_note(self, category, allocated, historical):
        """Generate note for category budget"""
        if historical == 0:
            return f"New category. Allocated ${allocated:.2f} based on income."
        
        if allocated > historical:
            increase = ((allocated - historical) / historical) * 100
            return f"Increased by {increase:.1f}% from historical average."
        elif allocated < historical:
            decrease = ((historical - allocated) / historical) * 100
            return f"Reduced by {decrease:.1f}% from historical average to meet savings goal."
        else:
            return "Matches historical spending."
    
    def _generate_budget_adjustments(self, category_budgets, projected_savings, target_savings):
        """Generate adjustments needed to meet savings goal"""
        adjustments = []
        
        if projected_savings < target_savings:
            shortfall = target_savings - projected_savings
            
            # Find wants categories to reduce
            wants_categories = [cat for cat, data in category_budgets.items() 
                              if data.get('type') == 'want' and data['allocated'] > 0]
            
            if wants_categories:
                reduction_per_category = shortfall / len(wants_categories)
                
                for category in wants_categories[:3]:  # Suggest for top 3
                    adjustments.append({
                        'type': 'reduction',
                        'category': category,
                        'current': category_budgets[category]['allocated'],
                        'suggested': round(max(0, category_budgets[category]['allocated'] - reduction_per_category), 2),
                        'reason': f'Reduce to meet savings target of ${target_savings:.2f}'
                    })
            
            # If not enough wants, suggest increasing income
            if len(adjustments) < 2:
                adjustments.append({
                    'type': 'income',
                    'suggestion': 'Consider finding additional income sources to meet savings goals',
                    'additional_needed': round(shortfall, 2)
                })
        
        return adjustments
    
    def _generate_budget_tips(self, category_budgets, projected_savings, monthly_income):
        """Generate helpful budget tips"""
        tips = []
        
        savings_rate = (projected_savings / monthly_income) * 100
        
        if savings_rate >= 20:
            tips.append("👍 Excellent! You're saving 20%+ of your income.")
        elif savings_rate >= 15:
            tips.append("✓ Good savings rate. Try to reach 20% for optimal financial health.")
        elif savings_rate >= 10:
            tips.append("📈 You're saving, but consider increasing by 5% for better security.")
        else:
            tips.append("⚠️ Low savings rate. Review wants categories for reduction opportunities.")
        
        # Category-specific tips
        high_wants = [cat for cat, data in category_budgets.items() 
                     if data.get('type') == 'want' and data['allocated'] > monthly_income * 0.1]
        
        for category in high_wants:
            tips.append(f"🎯 Your {category} budget is {category_budgets[category]['allocated']/monthly_income*100:.1f}% of income. Consider if this aligns with your priorities.")
        
        # Emergency fund tip
        emergency_fund = self.advisor._calculate_emergency_fund()
        monthly_expenses = sum(data['allocated'] for data in category_budgets.values())
        
        if emergency_fund < monthly_expenses * 3:
            months_covered = emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
            tips.append(f"🛡️ Emergency fund covers {months_covered:.1f} months. Aim for 3-6 months of expenses.")
        
        return tips