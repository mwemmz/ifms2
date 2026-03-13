import requests
import json
import time

base_url = "http://localhost:5000"

def login(username="testuser2916", password="Test123!@#"):
    """Login to get token"""
    url = f"{base_url}/api/auth/login"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_failed_logins():
    print("\n=== Testing Failed Login Tracking ===")
    
    # Try multiple failed logins
    for i in range(3):
        url = f"{base_url}/api/auth/login"
        data = {
            "username": "nonexistent_user",
            "password": "wrong_password"
        }
        response = requests.post(url, json=data)
        print(f"Attempt {i+1}: Status {response.status_code}")
        time.sleep(1)

def test_security_status(token):
    print("\n=== Testing Security Status ===")
    url = f"{base_url}/api/security/status"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_security_logs(token):
    print("\n=== Testing Security Logs ===")
    url = f"{base_url}/api/security/logs"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total logs: {data.get('total')}")
    print(f"Recent logs: {len(data.get('logs', []))}")

def test_sessions(token):
    print("\n=== Testing Active Sessions ===")
    url = f"{base_url}/api/security/sessions"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Active sessions: {data.get('count')}")
    print(f"Max sessions: {data.get('max_sessions')}")

def test_alerts(token):
    print("\n=== Testing Security Alerts ===")
    url = f"{base_url}/api/security/alerts"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total alerts: {data.get('count')}")
    print(f"Unresolved: {data.get('unresolved')}")

def test_mfa_status(token):
    print("\n=== Testing MFA Status ===")
    url = f"{base_url}/api/security/mfa/status"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_recent_audit(token):
    print("\n=== Testing Recent Audit Logs ===")
    url = f"{base_url}/api/security/audit/recent"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Recent API calls: {data.get('count')}")

def test_detect_anomalies(token):
    print("\n=== Testing Anomaly Detection ===")
    url = f"{base_url}/api/security/anomalies/detect"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_logout(token):
    print("\n=== Testing Logout ===")
    url = f"{base_url}/api/security/sessions/current"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Starting Security Module Tests...")
    print("=" * 50)
    
    # Test failed logins first
    test_failed_logins()
    
    # Login normally
    print("\n=== Logging in normally ===")
    token = login()
    if not token:
        print("Failed to login. Make sure you have a test user registered.")
        exit(1)
    
    print(f"Token obtained: {token[:20]}...")
    
    # Run tests
    test_security_status(token)
    test_security_logs(token)
    test_sessions(token)
    test_alerts(token)
    test_mfa_status(token)
    test_recent_audit(token)
    test_detect_anomalies(token)
    
    # Test logout
    test_logout(token)
    
    print("\n" + "=" * 50)
    print("Tests Complete!")