import requests
import json
from datetime import datetime

base_url = "http://localhost:5000"

def login():
    """Login to get token"""
    url = f"{base_url}/api/auth/login"
    data = {
        "username": "testuser2916",
        "password": "Test123!@#"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def ensure_profile_set(token):
    """Ensure user profile has salary set"""
    url = f"{base_url}/api/auth/update-profile"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "monthly_salary": 5000.00,
        "savings_goal": 15000.00
    }
    
    response = requests.put(url, json=data, headers=headers)
    print(f"Profile Update Status: {response.status_code}")

def test_monthly_budget(token):
    print("\n=== Testing Monthly Budget Generation ===")
    now = datetime.now()
    url = f"{base_url}/api/budget/monthly?month={now.month}&year={now.year}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_budget_comparison(token):
    print("\n=== Testing Budget vs Actual Comparison ===")
    now = datetime.now()
    # Use previous month for comparison
    if now.month == 1:
        month = 12
        year = now.year - 1
    else:
        month = now.month - 1
        year = now.year
    
    url = f"{base_url}/api/budget/compare?month={month}&year={year}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_future_budgets(token):
    print("\n=== Testing Future Budgets (3 months) ===")
    url = f"{base_url}/api/budget/future?months=3"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_budget_recommendations(token):
    print("\n=== Testing Budget Recommendations ===")
    url = f"{base_url}/api/budget/recommendations"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_smart_budget(token):
    print("\n=== Testing Smart Budget (15% savings target) ===")
    url = f"{base_url}/api/budget/smart"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "target_savings_rate": 15  # 15%
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_budget_history(token):
    print("\n=== Testing Budget History (6 months) ===")
    url = f"{base_url}/api/budget/history?months=6"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_current_status(token):
    print("\n=== Testing Current Budget Status ===")
    url = f"{base_url}/api/budget/current-status"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Starting Budget Planning Module Tests...")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        print("Failed to login. Make sure you have a test user registered.")
        exit(1)
    
    print(f"Token obtained: {token[:20]}...")
    
    # Ensure profile has salary set
    ensure_profile_set(token)
    
    # Run tests
    test_monthly_budget(token)
    test_budget_comparison(token)
    test_future_budgets(token)
    test_budget_recommendations(token)
    test_smart_budget(token)
    test_budget_history(token)
    test_current_status(token)
    
    print("\n" + "=" * 50)
    print("Tests Complete!")