import requests
import json
import time
from datetime import datetime, timedelta

base_url = "http://localhost:5000"

def wait_for_server():
    """Wait for server to be ready"""
    print("Waiting for server to start...")
    time.sleep(2)
    print("Server is ready!")

def login():
    """Login to get token"""
    url = f"{base_url}/api/auth/login"
    data = {
        "username": "testuser2164",  # Use the username from your registration
        "password": "Test123!@#"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"Login failed: {response.status_code}")
            print(f"Response: {response.json()}")
            return None
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server. Make sure Flask is running on port 5000")
        return None

def test_get_categories(token):
    print("\n=== Testing Get Categories ===")
    url = f"{base_url}/api/transactions/categories"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_add_transaction(token):
    print("\n=== Testing Add Transaction (Expense) ===")
    url = f"{base_url}/api/transactions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Add an expense
    expense_data = {
        "amount": 45.99,
        "category": "Food & Dining",
        "description": "Grocery shopping",
        "date": datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.post(url, json=expense_data, headers=headers)
        print(f"Expense - Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result.get('transaction', {}).get('id')
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_get_transactions(token):
    print("\n=== Testing Get All Transactions ===")
    url = f"{base_url}/api/transactions"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_get_summary(token):
    print("\n=== Testing Get Monthly Summary ===")
    now = datetime.now()
    url = f"{base_url}/api/transactions/summary?month={now.month}&year={now.year}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_get_recent(token):
    print("\n=== Testing Get Recent Transactions ===")
    url = f"{base_url}/api/transactions/recent"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_delete_transaction(token, transaction_id):
    print(f"\n=== Testing Delete Transaction ({transaction_id}) ===")
    url = f"{base_url}/api/transactions/{transaction_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting Transaction Module Tests...")
    print("=" * 50)
    
    wait_for_server()
    
    # Login
    token = login()
    if not token:
        print("\n❌ Failed to login. Make sure:")
        print("1. Flask server is running (python run.py)")
        print("2. You have a test user registered")
        print("3. Using correct username/password")
        exit(1)
    
    print(f"\n✅ Token obtained: {token[:20]}...")
    
    # Run tests
    test_get_categories(token)
    
    transaction_id = test_add_transaction(token)
    
    if transaction_id:
        print(f"\n✅ Transaction created with ID: {transaction_id}")
        test_get_transactions(token)
        test_get_summary(token)
        test_get_recent(token)
        
        # Clean up - delete the test transaction
        test_delete_transaction(token, transaction_id)
        print(f"\n✅ Test transaction deleted")
    else:
        print("\n❌ Failed to create transaction")
    
    print("\n" + "=" * 50)
    print("Tests Complete!")