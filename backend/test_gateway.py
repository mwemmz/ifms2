import requests
import json
import time

base_url = "http://localhost:5000"

def register_test_user():
    """Register a test user if not exists"""
    url = f"{base_url}/api/auth/register"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!@#",
        "full_name": "Test User"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("✅ Test user created")
        return True
    elif response.status_code == 400:
        # User might already exist
        print("ℹ️ Test user may already exist")
        return True
    else:
        print(f"❌ Failed to create test user: {response.status_code}")
        return False

def login():
    """Login to get token"""
    url = f"{base_url}/api/auth/login"
    data = {
        "username": "testuser",
        "password": "Test123!@#"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_health_check():
    print("\n=== Testing Health Check Endpoint ===")
    url = f"{base_url}/api/health"
    
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_rate_limiting():
    print("\n=== Testing Rate Limiting ===")
    url = f"{base_url}/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Make multiple requests quickly
    for i in range(7):  # Try 7 times (limit is 5 per minute)
        data = {
            "username": "testuser",
            "password": "wrong_password"  # Wrong password to trigger failures
        }
        response = requests.post(url, json=data, headers=headers)
        print(f"Attempt {i+1}: Status {response.status_code}")
        if response.status_code == 429:
            print(f"Rate limited: {response.json()}")
        time.sleep(0.5)

def test_successful_login():
    print("\n=== Testing Successful Login ===")
    url = f"{base_url}/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "username": "testuser",
        "password": "Test123!@#"  # Correct password
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Successfully logged in")
        return response.json().get('access_token')
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_authentication_required(token):
    print("\n=== Testing Authentication Required ===")
    
    headers = {"Accept": "application/json"}
    
    # Request without token
    url = f"{base_url}/api/transactions"
    response = requests.get(url, headers=headers)
    print(f"Without token: {response.status_code}")
    
    # Request with token
    if token:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        print(f"With token: {response.status_code}")

def test_invalid_endpoint():
    print("\n=== Testing Invalid Endpoint ===")
    url = f"{base_url}/api/invalid/endpoint"
    headers = {"Accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_cors_headers():
    print("\n=== Testing CORS Headers ===")
    url = f"{base_url}/api/health"
    
    headers = {
        "Origin": "http://localhost:3000"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
    print(f"Access-Control-Allow-Credentials: {response.headers.get('Access-Control-Allow-Credentials')}")

def test_security_headers():
    print("\n=== Testing Security Headers ===")
    url = f"{base_url}/api/health"
    
    response = requests.get(url)
    print(f"X-Content-Type-Options: {response.headers.get('X-Content-Type-Options')}")
    print(f"X-Frame-Options: {response.headers.get('X-Frame-Options')}")
    print(f"X-XSS-Protection: {response.headers.get('X-XSS-Protection')}")
    print(f"Strict-Transport-Security: {response.headers.get('Strict-Transport-Security')}")

def test_create_transaction(token):
    if not token:
        print("\n=== Skipping Transaction Creation (no token) ===")
        return
        
    print("\n=== Testing Transaction Creation ===")
    url = f"{base_url}/api/transactions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    valid_data = {
        "amount": 75.50,
        "category": "Food & Dining",
        "description": "Test transaction",
        "date": "2024-03-15"
    }
    
    response = requests.post(url, json=valid_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("✅ Transaction created successfully")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Transaction creation failed: {response.json()}")

if __name__ == "__main__":
    print("Starting API Gateway Tests...")
    print("=" * 50)
    
    # First, try to register a test user
    register_test_user()
    
    # Test public endpoints
    test_health_check()
    
    # Test rate limiting with wrong password
    test_rate_limiting()
    
    # Test successful login
    token = test_successful_login()
    
    if token:
        test_authentication_required(token)
        test_create_transaction(token)
    else:
        print("\n❌ Could not obtain token - skipping authenticated tests")
    
    # Test headers
    test_cors_headers()
    test_security_headers()
    
    # Test error handling
    test_invalid_endpoint()
    
    print("\n" + "=" * 50)
    print("Tests Complete!")