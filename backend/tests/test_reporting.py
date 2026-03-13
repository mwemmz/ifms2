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

def test_monthly_report(token):
    print("\n=== Testing Monthly Report ===")
    now = datetime.now()
    url = f"{base_url}/api/reports/monthly?month={now.month}&year={now.year}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Report ID: {data.get('report_id')}")
        print(f"Period: {data.get('period', {}).get('month')} {data.get('period', {}).get('year')}")
        print(f"Summary: {data.get('summary')}")
        print(f"Categories: {len(data.get('category_breakdown', {}))} categories")
        print(f"Insights: {len(data.get('insights', []))} insights")

def test_yearly_report(token):
    print("\n=== Testing Yearly Report ===")
    now = datetime.now()
    url = f"{base_url}/api/reports/yearly?year={now.year}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Report ID: {data.get('report_id')}")
        print(f"Year: {data.get('period', {}).get('year')}")
        print(f"Summary: {data.get('summary')}")
        print(f"Months with data: {data.get('summary', {}).get('months_with_data')}")
        print(f"Insights: {len(data.get('insights', []))} insights")

def test_category_report(token):
    print("\n=== Testing Category Report ===")
    # Try a common category
    url = f"{base_url}/api/reports/category?category=Food%20%26%20Dining&months=6"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Category: {data.get('category')}")
        print(f"Summary: {data.get('summary')}")
        print(f"Monthly breakdown: {len(data.get('monthly_breakdown', []))} months")

def test_compare_years(token):
    print("\n=== Testing Year Comparison ===")
    now = datetime.now()
    url = f"{base_url}/api/reports/compare-years?year1={now.year-1}&year2={now.year}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Comparison: {data.get('comparison')}")
        print(f"Category changes: {len(data.get('category_comparison', []))} categories")

def test_export_json(token):
    print("\n=== Testing Export (JSON) ===")
    url = f"{base_url}/api/reports/export?format=json"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"User: {data.get('user', {}).get('username')}")
        print(f"Total transactions: {data.get('summary', {}).get('total_transactions')}")
        print(f"Total income: ${data.get('summary', {}).get('total_income')}")

def test_export_csv(token):
    print("\n=== Testing Export (CSV) ===")
    url = f"{base_url}/api/reports/export?format=csv"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"CSV Headers: {response.headers.get('Content-Disposition')}")
        print(f"CSV Content Length: {len(response.text)} characters")

def test_dashboard(token):
    print("\n=== Testing Dashboard ===")
    url = f"{base_url}/api/reports/dashboard"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Current Month: {data.get('current_month', {}).get('month')}")
        print(f"Quick Stats: {data.get('quick_stats')}")
        print(f"Recent Transactions: {len(data.get('recent_transactions', []))}")

def test_available_reports(token):
    print("\n=== Testing Available Reports ===")
    url = f"{base_url}/api/reports/available-reports"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Available years: {data.get('available_years')}")
        print(f"Available categories: {len(data.get('available_categories', []))} categories")
        print(f"Report types: {data.get('report_types')}")

if __name__ == "__main__":
    print("Starting Reporting Module Tests...")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        print("Failed to login. Make sure you have a test user registered.")
        exit(1)
    
    print(f"Token obtained: {token[:20]}...")
    
    # Run tests
    test_available_reports(token)
    test_dashboard(token)
    test_monthly_report(token)
    test_yearly_report(token)
    test_category_report(token)
    test_compare_years(token)
    test_export_json(token)
    test_export_csv(token)
    
    print("\n" + "=" * 50)
    print("Tests Complete!")