import requests
import json
from datetime import datetime, timedelta
import random
from test_utils import create_test_user, login_with_credentials, wait_for_server

base_url = "http://localhost:5000"

def add_historical_transactions(token):
    """Add historical transactions for better predictions"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\nAdding 24 months of historical data...")
    
    # Add 2 years of historical data
    sample_data = []
    
    # Generate data for last 24 months
    for i in range(24, 0, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        year = month_date.year
        month = month_date.month
        
        # Rent - consistent with slight increase over time
        rent_amount = 450 + (i * 2)  # Increases slightly over time
        sample_data.append({
            "amount": rent_amount,
            "category": "Rent/Mortgage",
            "description": f"Rent {month}/{year}",
            "date": f"{year}-{month:02d}-05"
        })
        
        # Food - gradually increasing
        food_amount = 80 + (i * 1.5)  # Increases over time
        sample_data.append({
            "amount": food_amount,
            "category": "Food & Dining",
            "description": f"Groceries {month}/{year}",
            "date": f"{year}-{month:02d}-10"
        })
        
        # Utilities - seasonal variation
        if month in [12, 1, 2]:  # Winter
            util_amount = 150 + random.randint(-10, 10)
        elif month in [6, 7, 8]:  # Summer
            util_amount = 120 + random.randint(-10, 10)
        else:
            util_amount = 100 + random.randint(-10, 10)
            
        sample_data.append({
            "amount": util_amount,
            "category": "Bills & Utilities",
            "description": f"Utilities {month}/{year}",
            "date": f"{year}-{month:02d}-15"
        })
        
        # Entertainment - random variation
        ent_amount = 50 + random.randint(-20, 40)
        sample_data.append({
            "amount": ent_amount,
            "category": "Entertainment",
            "description": f"Entertainment {month}/{year}",
            "date": f"{year}-{month:02d}-20" if i % 2 == 0 else f"{year}-{month:02d}-25"
        })
        
        # Transportation
        transport_amount = 45 + random.randint(-10, 30)
        sample_data.append({
            "amount": transport_amount,
            "category": "Transportation",
            "description": f"Transport {month}/{year}",
            "date": f"{year}-{month:02d}-12" if i % 3 == 0 else f"{year}-{month:02d}-18"
        })
    
    # Add income for each month
    for i in range(24, 0, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        year = month_date.year
        month = month_date.month
        
        sample_data.append({
            "amount": 3000.00,
            "category": "Salary",
            "description": f"Salary {month}/{year}",
            "date": f"{year}-{month:02d}-01"
        })
    
    print(f"Adding {len(sample_data)} transactions...")
    
    success_count = 0
    for i, transaction in enumerate(sample_data):
        response = requests.post(f"{base_url}/api/transactions", json=transaction, headers=headers)
        if response.status_code == 201:
            success_count += 1
        if (i + 1) % 50 == 0:
            print(f"Progress: {i + 1}/{len(sample_data)} transactions added...")
    
    print(f"Successfully added {success_count}/{len(sample_data)} transactions")

def test_prediction_health(token):
    print("\n=== Testing Prediction Health ===")
    url = f"{base_url}/api/predict/health"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_next_month_prediction(token):
    print("\n=== Testing Next Month Prediction (Linear Regression) ===")
    url = f"{base_url}/api/predict/next-month"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_category_predictions(token):
    print("\n=== Testing Category-wise Predictions ===")
    url = f"{base_url}/api/predict/by-category"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_moving_average(token):
    print("\n=== Testing Moving Average Prediction ===")
    url = f"{base_url}/api/predict/moving-average?window=3"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_polynomial_prediction(token):
    print("\n=== Testing Polynomial Regression Prediction ===")
    url = f"{base_url}/api/predict/polynomial?degree=2"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_ensemble_prediction(token):
    print("\n=== Testing Ensemble Prediction ===")
    url = f"{base_url}/api/predict/ensemble"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_multi_month_prediction(token):
    print("\n=== Testing Multi-Month Prediction (3 months ahead) ===")
    url = f"{base_url}/api/predict/multi-month?months=3"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_prediction_insights(token):
    print("\n=== Testing Comprehensive Prediction Insights ===")
    url = f"{base_url}/api/predict/insights"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_category_specific(token):
    print("\n=== Testing Category-Specific Prediction (Food & Dining) ===")
    url = f"{base_url}/api/predict/next-month?category=Food & Dining"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def run_all_tests(token):
    """Run all prediction tests"""
    
    print("\n" + "=" * 60)
    print("RUNNING ALL PREDICTION TESTS")
    print("=" * 60)
    
    # Run tests
    test_prediction_health(token)
    test_next_month_prediction(token)
    test_category_predictions(token)
    test_moving_average(token)
    test_polynomial_prediction(token)
    test_ensemble_prediction(token)
    test_multi_month_prediction(token)
    test_category_specific(token)
    test_prediction_insights(token)
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    print("Starting Expense Prediction Tests...")
    print("=" * 60)
    
    # Wait for server
    wait_for_server(2)
    
    # Try multiple approaches to get a token
    token = None
    
    # Approach 1: Try common test user
    print("\nTrying to login with default test user...")
    token = login_with_credentials("testuser", "Test123!@#")
    
    # Approach 2: Try the specific user from your test
    if not token:
        print("Trying with specific test user from previous run...")
        token = login_with_credentials("testuser6807", "Test123!@#")
    
    # Approach 3: Create a brand new test user
    if not token:
        print("Creating new test user...")
        token, username = create_test_user()
        if token:
            print(f"Created new user: {username}")
    
    if not token:
        print("\n❌ FAILED: Could not obtain authentication token.")
        print("\nTroubleshooting steps:")
        print("1. Make sure the Flask server is running (python run.py)")
        print("2. Check if the server is running on port 5000")
        print("3. Try running test_auth.py first to create a user")
        print("4. Check for any error messages in the server console")
        exit(1)
    
    print("\n✅ Successfully authenticated!")
    print(f"Token: {token[:20]}...")
    
    # Ask if user wants to add historical data
    print("\n" + "-" * 60)
    response = input("Do you want to add 24 months of historical data for better predictions? (y/n): ")
    
    if response.lower() == 'y':
        add_historical_transactions(token)
        print("\n✅ Historical data added successfully!")
    
    # Run all tests
    run_all_tests(token)