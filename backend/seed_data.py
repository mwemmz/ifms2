"""
Zambian Kwacha (ZMW) Database Seeding Script
=============================================
This script populates the database with realistic Zambian financial data.
Exchange rate reference: 1 USD ≈ 25 ZMW (approximate)
"""

import random
import numpy as np
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User, UserProfile, Transaction
from app.utils.security import hash_password

# Zambian Kwacha configuration
CURRENCY = "ZMW"
EXCHANGE_RATE = 25  # Approximate USD to ZMW conversion

def seed_zambian_data():
    """Seed database with realistic Zambian financial data in ZMW"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting Zambian Kwacha (ZMW) database seeding...")
        print(f"📊 Using currency: {CURRENCY}")
        print(f"💱 Approximate exchange rate: 1 USD = {EXCHANGE_RATE} ZMW")
        
        # Create test user
        user = create_or_get_zambian_user()
        
        # Clear existing data
        print("Clearing existing transactions...")
        Transaction.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # Generate Zambian data
        print("Generating 2 years of Zambian transaction data...")
        transactions = generate_zambian_transactions(user.id)
        
        # Add to database
        db.session.add_all(transactions)
        db.session.commit()
        
        print(f"✅ Successfully added {len(transactions)} transactions in {CURRENCY}!")
        print_zambian_summary(user.id)

def create_or_get_zambian_user():
    """Create or get test user with Zambian profile"""
    user = User.query.filter_by(username='chola_mwamba').first()
    
    if not user:
        print("Creating test user 'chola_mwamba'...")
        user = User(
            username='chola_mwamba',
            email='chola.mwamba@example.com',
            password_hash=hash_password('Test123!@#'),
            mfa_enabled=False,
            created_at=datetime.now() - timedelta(days=730)
        )
        db.session.add(user)
        db.session.flush()
        
        # Zambian salaries are typically 3,000 - 15,000 ZMW per month
        # Converting from $5,500 USD ≈ 137,500 ZMW (adjusted for local context)
        monthly_salary_zmw = 8500  # More realistic Zambian salary
        
        profile = UserProfile(
            user_id=user.id,
            full_name='Chola Mwamba',
            monthly_salary=monthly_salary_zmw,
            savings_goal=50000.00,  # 50,000 ZMW savings goal
            emergency_fund_target=51000.00  # 6 months of expenses
        )
        db.session.add(profile)
        db.session.commit()
        print("✅ Test user created")
    else:
        print("✅ Test user already exists")
    
    return user

def generate_zambian_transactions(user_id):
    """Generate 2 years of transaction data with Zambian patterns"""
    transactions = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    # Configuration with Zambian amounts (in ZMW)
    # Typical Zambian expenses converted to local context
    patterns = {
        'fixed_expenses': {
            'Rent/Mortgage': {'amount': 3500, 'day': 1, 'trend': 0.05},  # Monthly rent in Lusaka
            'Electricity': {'amount': (350, 600), 'day': 10, 'seasonal': True},  # ZESCO bills
            'Water': {'amount': (80, 150), 'day': 12, 'seasonal': True},  # Water utility
            'Internet': {'amount': 450, 'day': 5, 'trend': 0.02},  # Fiber internet
            'Mobile Data': {'amount': 150, 'day': 8, 'trend': 0.01},  # Airtime/data bundles
            'DSTV/GOtv': {'amount': 280, 'day': 15, 'trend': 0.02},  # TV subscription
            'Gym': {'amount': 250, 'day': 3, 'trend': 0.02},  # Gym membership
        },
        'variable_expenses': {
            'Groceries': {'amount': (800, 1500), 'frequency': 'weekly', 'day': 'saturday', 'trend': 0.03},  # Shoprite/Spar
            'Market Shopping': {'amount': (300, 600), 'frequency': 'weekly', 'day': 'saturday', 'trend': 0.02},  # Open market
            'Restaurants': {'amount': (150, 400), 'frequency': 'weekly', 'day': 'friday', 'trend': 0.04},  # Eating out
            'Transport': {'amount': (200, 500), 'frequency': 'weekly', 'trend': 0.03},  # Fuel/taxis/buses
            'Entertainment': {'amount': (150, 400), 'frequency': 'weekly', 'day': 'weekend', 'trend': 0.03},  # Movies/nightlife
            'Shopping': {'amount': (300, 1000), 'frequency': 'biweekly', 'trend': 0.03},  # Clothing, etc.
            'Personal Care': {'amount': (150, 350), 'frequency': 'biweekly', 'trend': 0.02},  # Salon/barber
            'Home Supplies': {'amount': (200, 500), 'frequency': 'monthly', 'day': 5, 'trend': 0.02},
        },
        'income': {
            'Salary': {'amount': 8500, 'day': 1, 'trend': 0.03},  # Monthly salary
            'Business Income': {'amount': (1000, 3000), 'frequency': 'irregular', 'trend': 0.02},  # Side business
            'Rental Income': {'amount': (2000, 2500), 'day': 5, 'trend': 0.02},  # Property rental
            'Bonus': {'amount': (3000, 8000), 'frequency': 'quarterly', 'trend': 0.02},  # Performance bonus
            'Dividends': {'amount': (200, 500), 'day': 15, 'trend': 0.02},  # Stock dividends
            'Tax Refund': {'amount': (1500, 3000), 'frequency': 'yearly', 'month': 4, 'trend': 0.0},  # ZRA refund
        },
        'irregular': {
            'Medical': {'amount': (300, 1500), 'probability': 0.03},  # Clinic/hospital
            'Car Maintenance': {'amount': (500, 2500), 'probability': 0.02},  # Vehicle service
            'Home Repair': {'amount': (800, 3000), 'probability': 0.01},  # House maintenance
            'School Fees': {'amount': (2000, 5000), 'probability': 0.08, 'months': [1, 8]},  # Term fees (Jan, Aug)
            'Wedding/Gifts': {'amount': (500, 2000), 'probability': 0.1},  # Social obligations
            'Travel': {'amount': (1500, 5000), 'probability': 0.04},  # Upcountry/regional travel
        },
        'zambian_specific': {
            'Chicken Poop': {'amount': (50, 150), 'probability': 0.15},  # Popular snack
            'Mosi Beer': {'amount': (80, 200), 'probability': 0.2},  # Local beer
            'Air Time': {'amount': (30, 100), 'probability': 0.3},  # Mobile top-up
            'Township Taxi': {'amount': (15, 40), 'probability': 0.25},  # Local transport
            'Market Fees': {'amount': (20, 50), 'probability': 0.1},  # Market stall fees
            'Kapani': {'amount': (10, 30), 'probability': 0.3},  # Small purchases
        }
    }
    
    current_date = start_date
    
    while current_date <= end_date:
        # Fixed monthly expenses
        for expense, config in patterns['fixed_expenses'].items():
            if current_date.day == config['day']:
                amount = calculate_fixed_amount_zmw(config, current_date)
                # Cap amounts to reasonable Zambian values
                amount = min(amount, 10000)
                if amount >= 10:  # Skip tiny transactions
                    add_transaction_zmw(transactions, user_id, current_date, -amount, expense, 
                                       f"{expense} - {current_date.strftime('%B %Y')}")
        
        # Saturday expenses
        if current_date.weekday() == 5:  # Saturday
            # Groceries (supermarket)
            amount = random.uniform(*patterns['variable_expenses']['Groceries']['amount'])
            amount = min(amount, 2000)
            if random.random() < 0.8:  # 80% chance
                add_transaction_zmw(transactions, user_id, current_date, -amount, 'Groceries',
                                   f"Shoprite/Spar - {current_date.strftime('%Y-%m-%d')}")
            
            # Market shopping
            if random.random() < 0.6:
                amount = random.uniform(*patterns['variable_expenses']['Market Shopping']['amount'])
                amount = min(amount, 800)
                add_transaction_zmw(transactions, user_id, current_date, -amount, 'Market Shopping',
                                   f"Soweto Market - {current_date.strftime('%Y-%m-%d')}")
            
            # Weekend entertainment
            if random.random() < 0.5:
                amount = random.uniform(*patterns['variable_expenses']['Entertainment']['amount'])
                amount = min(amount, 500)
                add_transaction_zmw(transactions, user_id, current_date, -amount, 'Entertainment',
                                   f"Weekend Outing - {current_date.strftime('%Y-%m-%d')}")
        
        # Friday expenses (pay day fun)
        elif current_date.weekday() == 4:  # Friday
            # Restaurants
            if random.random() < 0.6:
                amount = random.uniform(*patterns['variable_expenses']['Restaurants']['amount'])
                amount = min(amount, 500)
                add_transaction_zmw(transactions, user_id, current_date, -amount, 'Restaurants',
                                   f"Friday Night Out - {current_date.strftime('%Y-%m-%d')}")
            
            # Mosi beer
            if random.random() < 0.4:
                amount = random.uniform(*patterns['zambian_specific']['Mosi Beer']['amount'])
                add_transaction_zmw(transactions, user_id, current_date, -amount, 'Entertainment',
                                   f"Mosi Beer - {current_date.strftime('%Y-%m-%d')}")
        
        # Daily transport
        if current_date.weekday() < 5:  # Weekdays
            # Transport to work
            if random.random() < 0.9:
                amount = random.uniform(30, 80)  # Bus/taxi fare
                add_transaction_zmw(transactions, user_id, current_date, -amount, 'Transport',
                                   f"Transport - {current_date.strftime('%Y-%m-%d')}")
            
            # Air time top-up
            if random.random() < 0.3:
                amount = random.uniform(*patterns['zambian_specific']['Air Time']['amount'])
                add_transaction_zmw(transactions, user_id, current_date, -amount, 'Mobile Data',
                                   f"Airtime - {current_date.strftime('%Y-%m-%d')}")
            
            # Small purchases (kapani)
            if random.random() < 0.2:
                amount = random.uniform(*patterns['zambian_specific']['Kapani']['amount'])
                add_transaction_zmw(transactions, user_id, current_date, -amount, 'Miscellaneous',
                                   f"Kapani - {current_date.strftime('%Y-%m-%d')}")
        
        # Biweekly shopping
        if current_date.day in [1, 15] or abs(current_date.day - 15) <= 2:
            if random.random() < 0.4:
                amount = random.uniform(*patterns['variable_expenses']['Shopping']['amount'])
                amount = min(amount, 1500)
                add_transaction_zmw(transactions, user_id, current_date, -amount, 'Shopping',
                                   f"Shopping - {current_date.strftime('%Y-%m-%d')}")
        
        # INCOME
        if current_date.day == 1:
            # Salary
            years_from_start = (current_date.year - 2024) + (current_date.month / 12)
            trend_factor = 1 + (patterns['income']['Salary']['trend'] * years_from_start)
            amount = patterns['income']['Salary']['amount'] * trend_factor
            amount = min(amount, 12000)  # Cap salary
            add_transaction_zmw(transactions, user_id, current_date, amount, 'Salary',
                               f"Monthly Salary - {current_date.strftime('%B %Y')}")
        
        if current_date.day == 5:
            # Rental income
            if random.random() < 0.7:  # 70% chance (tenant pays)
                amount = random.uniform(*patterns['income']['Rental Income']['amount'])
                amount = min(amount, 3000)
                add_transaction_zmw(transactions, user_id, current_date, amount, 'Rental Income',
                                   f"Rent Payment - {current_date.strftime('%B %Y')}")
        
        if current_date.day == 15:
            # Dividends
            if random.random() < 0.5:
                amount = random.uniform(*patterns['income']['Dividends']['amount'])
                amount = min(amount, 600)
                add_transaction_zmw(transactions, user_id, current_date, amount, 'Dividends',
                                   f"Dividend Payment - {current_date.strftime('%B %Y')}")
        
        # Quarterly bonus (Mar, Jun, Sep, Dec)
        if current_date.month in [3, 6, 9, 12] and current_date.day == 1:
            if random.random() < 0.6:  # 60% chance of bonus
                amount = random.uniform(*patterns['income']['Bonus']['amount'])
                amount = min(amount, 10000)
                add_transaction_zmw(transactions, user_id, current_date, amount, 'Bonus',
                                   f"Quarterly Bonus - Q{current_date.month//3 + 1} {current_date.year}")
        
        # Business income (irregular)
        if random.random() < 0.1:  # 10% chance
            amount = random.uniform(*patterns['income']['Business Income']['amount'])
            amount = min(amount, 4000)
            add_transaction_zmw(transactions, user_id, current_date, amount, 'Business Income',
                               f"Side Business - {current_date.strftime('%Y-%m-%d')}")
        
        # Irregular expenses
        for expense, config in patterns['irregular'].items():
            if 'months' in config:
                if current_date.month not in config['months']:
                    continue
            
            if random.random() < config['probability']:
                amount = random.uniform(*config['amount'])
                # Cap amounts
                if expense == 'School Fees':
                    amount = min(amount, 6000)
                elif expense == 'Travel':
                    amount = min(amount, 6000)
                elif expense == 'Home Repair':
                    amount = min(amount, 3500)
                else:
                    amount = min(amount, 2500)
                add_transaction_zmw(transactions, user_id, current_date, -amount, expense,
                                   f"{expense} - {current_date.strftime('%Y-%m-%d')}")
        
        # Zambian-specific small expenses
        for expense, config in patterns['zambian_specific'].items():
            if expense not in ['Mosi Beer', 'Air Time', 'Kapani']:  # Already handled
                if random.random() < config['probability']:
                    amount = random.uniform(*config['amount'])
                    add_transaction_zmw(transactions, user_id, current_date, -amount, 'Miscellaneous',
                                       f"{expense} - {current_date.strftime('%Y-%m-%d')}")
        
        current_date += timedelta(days=1)
    
    # Sort by date
    transactions.sort(key=lambda x: x.transaction_date)
    
    return transactions

def calculate_fixed_amount_zmw(config, date):
    """Calculate fixed expense amount with trend and seasonality in ZMW"""
    if isinstance(config['amount'], tuple):
        # Seasonal amount (like electricity)
        base = random.uniform(*config['amount'])
        
        # Seasonal adjustment (Zambia seasons)
        month = date.month
        if month in [12, 1, 2]:  # Rainy season - higher electricity (lights, heating)
            base *= 1.25
        elif month in [6, 7, 8]:  # Cold season - higher electricity (heating)
            base *= 1.2
        elif month in [9, 10, 11]:  # Hot season - higher electricity (fans)
            base *= 1.15
        
        return base
    else:
        # Fixed amount with trend
        years_from_start = (date.year - 2024) + (date.month / 12)
        trend_factor = 1 + (config['trend'] * years_from_start)
        return config['amount'] * trend_factor

def add_transaction_zmw(transactions, user_id, date, amount, category, description):
    """Add transaction with Zambian-specific validation"""
    # Round to 2 decimals
    amount = round(amount, 2)
    
    # Validation for ZMW amounts
    if abs(amount) > 50000:
        print(f"⚠️ WARNING: Skipping huge transaction: ZMW {amount:,.2f} for {category}")
        return
    
    # Skip tiny transactions (less than 1 ZMW)
    if abs(amount) < 1:
        return
    
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        category=category,
        description=description,
        transaction_date=date
    )
    
    transactions.append(transaction)

def print_zambian_summary(user_id):
    """Print detailed summary of seeded data in ZMW"""
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    
    # Monthly breakdown
    monthly_stats = {}
    for t in transactions:
        key = t.transaction_date.strftime('%Y-%m')
        if key not in monthly_stats:
            monthly_stats[key] = {'income': 0, 'expenses': 0, 'count': 0}
        
        if t.amount > 0:
            monthly_stats[key]['income'] += t.amount
        else:
            monthly_stats[key]['expenses'] += abs(t.amount)
        monthly_stats[key]['count'] += 1
    
    print("\n" + "=" * 60)
    print("📊 ZAMBIAN KWACHA (ZMW) DATABASE SUMMARY")
    print("=" * 60)
    print(f"Total Transactions: {len(transactions)}")
    print(f"Date Range: {transactions[0].transaction_date.strftime('%Y-%m-%d')} to {transactions[-1].transaction_date.strftime('%Y-%m-%d')}")
    
    print("\n💰 FINANCIAL SUMMARY (ZMW)")
    print("-" * 40)
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    print(f"Total Income:   ZMW {total_income:>14,.2f}")
    print(f"Total Expenses: ZMW {total_expenses:>14,.2f}")
    print(f"Net Savings:    ZMW {total_income - total_expenses:>14,.2f}")
    
    if total_income > 0:
        print(f"Savings Rate:   {((total_income - total_expenses)/total_income*100):>13.1f}%")
    
    print("\n📅 MONTHLY AVERAGES (ZMW)")
    print("-" * 40)
    if monthly_stats:
        avg_monthly_income = sum(m['income'] for m in monthly_stats.values()) / len(monthly_stats)
        avg_monthly_expenses = sum(m['expenses'] for m in monthly_stats.values()) / len(monthly_stats)
        print(f"Avg Monthly Income:  ZMW {avg_monthly_income:>14,.2f}")
        print(f"Avg Monthly Expenses: ZMW {avg_monthly_expenses:>14,.2f}")
        print(f"Avg Monthly Savings:  ZMW {avg_monthly_income - avg_monthly_expenses:>14,.2f}")
    
    print("\n📂 CATEGORY BREAKDOWN (ZMW)")
    print("-" * 40)
    categories = {}
    for t in transactions:
        if t.amount < 0:
            if t.category not in categories:
                categories[t.category] = {'total': 0, 'count': 0}
            categories[t.category]['total'] += abs(t.amount)
            categories[t.category]['count'] += 1
    
    for category, data in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
        print(f"   {category:20} ZMW {data['total']:>12,.2f} ({data['count']} txns)")
    
    print("\n📈 TRENDS")
    print("-" * 40)
    
    # Year over year comparison
    years = sorted(set(t.transaction_date.year for t in transactions))
    if len(years) >= 2:
        year1 = years[0]
        year2 = years[-1]
        
        year1_expenses = sum(abs(t.amount) for t in transactions if t.transaction_date.year == year1 and t.amount < 0)
        year2_expenses = sum(abs(t.amount) for t in transactions if t.transaction_date.year == year2 and t.amount < 0)
        
        if year1_expenses > 0:
            change = ((year2_expenses - year1_expenses) / year1_expenses) * 100
            print(f"Expense growth ({year1} → {year2}): {change:+.1f}%")
    
    print("\n" + "=" * 60)
    print("✅ Zambian data seeding complete!")
    print("=" * 60)

if __name__ == '__main__':
    seed_zambian_data()