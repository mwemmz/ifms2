import requests
import json
from datetime import datetime
import time

base_url = "http://localhost:5000"

def create_test_user():
    """Create a test user"""
    url = f"{base_url}/api/auth/register"
    timestamp = int(time.time())
    data = {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "Test123!@#",
        "full_name": "Test User"
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print(f"✓ User created successfully: {data['username']}")
        return data['username'], "Test123!@#"
    return None, None

def login(username, password):
    """Login to get token"""
    url = f"{base_url}/api/auth/login"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("✓ Login successful")
        return response.json().get('access_token')
    print(f"✗ Login failed: {response.text}")
    return None

def clear_existing_transactions(token):
    """Clear existing transactions"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}/api/transactions"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        transactions = response.json().get('transactions', [])
        for t in transactions:
            requests.delete(f"{base_url}/api/transactions/{t['id']}", headers=headers)
        print(f"✓ Cleared {len(transactions)} existing transactions")

def add_sample_transactions(token):
    """Add sample transactions for testing"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    sample_data = [
        # January expenses
        {"amount": 450.00, "category": "Rent/Mortgage", "description": "January rent", "date": "2024-01-05"},
        {"amount": 85.50, "category": "Food & Dining", "description": "Groceries", "date": "2024-01-10"},
        {"amount": 45.00, "category": "Transportation", "description": "Gas", "date": "2024-01-15"},
        {"amount": 120.00, "category": "Bills & Utilities", "description": "Electric bill", "date": "2024-01-20"},
        {"amount": 60.00, "category": "Entertainment", "description": "Movie night", "date": "2024-01-25"},
        {"amount": 40.00, "category": "Food & Dining", "description": "Lunch", "date": "2024-01-12"},
        
        # February expenses
        {"amount": 450.00, "category": "Rent/Mortgage", "description": "February rent", "date": "2024-02-05"},
        {"amount": 95.00, "category": "Food & Dining", "description": "Groceries", "date": "2024-02-10"},
        {"amount": 55.00, "category": "Transportation", "description": "Gas", "date": "2024-02-15"},
        {"amount": 115.00, "category": "Bills & Utilities", "description": "Electric bill", "date": "2024-02-20"},
        {"amount": 80.00, "category": "Entertainment", "description": "Dinner out", "date": "2024-02-25"},
        {"amount": 50.00, "category": "Food & Dining", "description": "Coffee runs", "date": "2024-02-18"},
        
        # March expenses
        {"amount": 450.00, "category": "Rent/Mortgage", "description": "March rent", "date": "2024-03-05"},
        {"amount": 110.00, "category": "Food & Dining", "description": "Groceries", "date": "2024-03-10"},
        {"amount": 65.00, "category": "Transportation", "description": "Gas", "date": "2024-03-15"},
        {"amount": 125.00, "category": "Bills & Utilities", "description": "Electric bill", "date": "2024-03-20"},
        {"amount": 95.00, "category": "Entertainment", "description": "Concert", "date": "2024-03-25"},
        {"amount": 75.00, "category": "Food & Dining", "description": "Restaurant", "date": "2024-03-22"},
        
        # Income
        {"amount": 3000.00, "category": "Salary", "description": "January salary", "date": "2024-01-01"},
        {"amount": 3000.00, "category": "Salary", "description": "February salary", "date": "2024-02-01"},
        {"amount": 3000.00, "category": "Salary", "description": "March salary", "date": "2024-03-01"},
    ]
    
    added = 0
    for transaction in sample_data:
        response = requests.post(f"{base_url}/api/transactions", json=transaction, headers=headers)
        if response.status_code == 201:
            added += 1
    
    print(f"✓ Added {added} sample transactions")
    return added

def test_category_breakdown(token):
    print("\n📊 CATEGORY BREAKDOWN")
    print("-" * 50)
    
    # Test February
    url = f"{base_url}/api/analysis/category-breakdown?month=2&year=2024"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Period: {data.get('period', {}).get('month', 'N/A')}")
        print(f"Total Spent: ${data.get('total_spent', 0):.2f}")
        print("\nCategories:")
        for category, details in data.get('categories', {}).items():
            print(f"  • {category}: ${details['total']:.2f} ({details['percentage']}%) - {details['transaction_count']} transactions")
    else:
        print(f"Error: {response.text}")

def test_monthly_summary(token):
    print("\n📈 MONTHLY SUMMARY")
    print("-" * 50)
    
    url = f"{base_url}/api/analysis/monthly-summary?months=3"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Months Analyzed: {data.get('months_analyzed', 0)}")
        print(f"Averages - Income: ${data.get('averages', {}).get('monthly_income', 0):.2f}, "
              f"Expenses: ${data.get('averages', {}).get('monthly_expenses', 0):.2f}, "
              f"Savings: ${data.get('averages', {}).get('monthly_savings', 0):.2f}")
        
        print("\nMonthly Data:")
        for month in data.get('monthly_data', []):
            print(f"  • {month['month_name']} {month['year']}: "
                  f"Income: ${month['income']:.2f}, "
                  f"Expenses: ${month['expenses']:.2f}, "
                  f"Savings: ${month['savings']:.2f}")
    else:
        print(f"Error: {response.text}")

def test_trends(token):
    print("\n📉 SPENDING TRENDS")
    print("-" * 50)
    
    url = f"{base_url}/api/analysis/trends?months=3"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        trends = data.get('trends', {})
        
        if trends:
            for category, trend in trends.items():
                print(f"  • {category}: {trend['direction']} "
                      f"(change: {trend['percentage_change']}%, "
                      f"volatility: {trend['volatility']})")
        else:
            print("No significant trends detected")
    else:
        print(f"Error: {response.text}")

def test_top_categories(token):
    print("\n🏆 TOP SPENDING CATEGORIES")
    print("-" * 50)
    
    url = f"{base_url}/api/analysis/top-categories?limit=5"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        for i, cat in enumerate(data.get('top_categories', []), 1):
            print(f"  {i}. {cat['category']}: ${cat['total']:.2f} ({cat['percentage']}%)")
    else:
        print(f"Error: {response.text}")

def test_compare_periods(token):
    print("\n🔄 PERIOD COMPARISON")
    print("-" * 50)
    
    url = f"{base_url}/api/analysis/compare?current_month=2&current_year=2024&previous_month=1&previous_year=2024"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        current = data.get('current_period', {})
        previous = data.get('previous_period', {})
        change = data.get('overall_change', {})
        
        print(f"Current ({current.get('start')} to {current.get('end')}): ${current.get('total', 0):.2f}")
        print(f"Previous ({previous.get('start')} to {previous.get('end')}): ${previous.get('total', 0):.2f}")
        print(f"\nChange: ${change.get('absolute', 0):.2f} ({change.get('percentage', 0)}%)")
    else:
        print(f"Error: {response.text}")

def test_spending_patterns(token):
    print("\n📅 SPENDING PATTERNS")
    print("-" * 50)
    
    url = f"{base_url}/api/analysis/patterns"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        weekday = data.get('weekday_vs_weekend', {}).get('weekday', {})
        weekend = data.get('weekday_vs_weekend', {}).get('weekend', {})
        
        print(f"Weekday spending: ${weekday.get('total', 0):.2f} (avg ${weekday.get('average', 0):.2f})")
        print(f"Weekend spending: ${weekend.get('total', 0):.2f} (avg ${weekend.get('average', 0):.2f})")
    else:
        print(f"Error: {response.text}")

def test_insights(token):
    print("\n🎯 COMPREHENSIVE INSIGHTS")
    print("-" * 50)
    
    url = f"{base_url}/api/analysis/insights"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        current = data.get('current_month', {})
        summary = data.get('summary', {})
        
        print(f"Current Month Total: ${current.get('total', 0):.2f}")
        print(f"Total Categories: {summary.get('total_categories', 0)}")
        
        top = summary.get('top_spending_category', {})
        if top:
            print(f"Top Category: {top.get('category', 'N/A')} (${top.get('total', 0):.2f})")
        
        comparison = summary.get('comparison_with_last_month', {})
        print(f"vs Last Month: {comparison.get('percentage', 0)}%")
    else:
        print(f"Error: {response.text}")

def wait_for_server():
    """Wait for server to be ready"""
    print("Waiting for server to start...")
    for i in range(30):
        try:
            response = requests.get(f"{base_url}/api/auth/login", timeout=2)
            # Server is up (even if 404 is fine)
            print("Server is ready!")
            return True
        except:
            time.sleep(1)
    print("Server not responding. Make sure Flask is running on port 5000")
    return False

if __name__ == "__main__":
    print("Starting Spending Analysis Tests...")
    print("=" * 50)
    
    # Wait for server
    if not wait_for_server():
        exit(1)
    
    # Create test user and login
    username, password = create_test_user()
    if not username:
        print("Failed to create test user")
        exit(1)
    
    token = login(username, password)
    if not token:
        print("Failed to login")
        exit(1)
    
    print(f"✓ Token obtained: {token[:20]}...")
    
    # Clear and add sample data
    clear_existing_transactions(token)
    add_sample_transactions(token)
    
    # Run tests
    test_category_breakdown(token)
    test_monthly_summary(token)
    test_trends(token)
    test_top_categories(token)
    test_compare_periods(token)
    test_spending_patterns(token)
    test_insights(token)
    
    print("\n" + "=" * 50)
    print("✅ All tests complete!")