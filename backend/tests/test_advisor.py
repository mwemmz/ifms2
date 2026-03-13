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

def set_user_profile(token):
    """Set user profile with salary and goals"""
    url = f"{base_url}/api/auth/update-profile"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "full_name": "Test User",
        "monthly_salary": 5000.00,
        "savings_goal": 10000.00
    }
    
    response = requests.put(url, json=data, headers=headers)
    print(f"Profile Update Status: {response.status_code}")
    if response.status_code == 200:
        print("Profile updated successfully")

def test_health_score(token):
    print("\n=== Testing Financial Health Score ===")
    url = f"{base_url}/api/advice/health-score"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_recommendations(token):
    print("\n=== Testing Financial Recommendations ===")
    url = f"{base_url}/api/advice/recommendations"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_budget_suggestions(token):
    print("\n=== Testing Budget Suggestions (50/30/20 Rule) ===")
    url = f"{base_url}/api/advice/budget-suggestions"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_overspending(token):
    print("\n=== Testing Overspending Detection ===")
    url = f"{base_url}/api/advice/overspending"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_savings_opportunities(token):
    print("\n=== Testing Savings Opportunities ===")
    url = f"{base_url}/api/advice/savings-opportunities"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_goal_progress(token):
    print("\n=== Testing Goal Progress ===")
    url = f"{base_url}/api/advice/goal-progress"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_emergency_fund(token):
    print("\n=== Testing Emergency Fund Status ===")
    url = f"{base_url}/api/advice/emergency-fund"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_financial_insights(token):
    print("\n=== Testing Comprehensive Financial Insights ===")
    url = f"{base_url}/api/advice/insights"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Starting Financial Advice Module Tests...")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        print("Failed to login. Make sure you have a test user registered.")
        exit(1)
    
    print(f"Token obtained: {token[:20]}...")
    
    # Set user profile
    set_user_profile(token)
    
    # Run tests
    test_health_score(token)
    test_recommendations(token)
    test_budget_suggestions(token)
    test_overspending(token)
    test_savings_opportunities(token)
    test_goal_progress(token)
    test_emergency_fund(token)
    test_financial_insights(token)
    
    print("\n" + "=" * 50)
    print("Tests Complete!")