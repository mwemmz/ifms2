import requests
import json
import time

base_url = "http://localhost:5000"

def wait_for_server():
    """Wait for server to be ready"""
    print("Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/api/auth/profile", timeout=2)
            print("Server is ready!")
            return True
        except:
            print(f"Attempt {i+1}: Server not ready yet...")
            time.sleep(2)
    return False

def test_registration():
    print("\n=== Testing Registration ===")
    url = f"{base_url}/api/auth/register"
    
    # Generate unique username to avoid conflicts
    import random
    unique_id = random.randint(1000, 9999)
    
    data = {
        "username": f"testuser{unique_id}",
        "email": f"test{unique_id}@example.com",
        "password": "Test123!@#",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure Flask is running on port 5000")
        return None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

def test_login(username, password):
    print("\n=== Testing Login ===")
    url = f"{base_url}/api/auth/login"
    
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

def test_get_profile(token):
    print("\n=== Testing Get Profile ===")
    url = f"{base_url}/api/auth/profile"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    print("Starting Authentication Tests...")
    print("=" * 50)
    
    # First, check if server is running
    if not wait_for_server():
        print("\n❌ ERROR: Cannot connect to server!")
        print("Please make sure:")
        print("1. Flask server is running (python run.py)")
        print("2. Server is on port 5000")
        print("3. No firewall blocking the connection")
        exit(1)
    
    # Test registration
    reg_result = test_registration()
    
    if reg_result and 'user' in reg_result:
        username = reg_result['user']['username']
        password = "Test123!@#"
        
        # Test login
        token = test_login(username, password)
        
        # Test profile (if login successful)
        if token:
            test_get_profile(token)
    else:
        print("\nRegistration failed. Testing with default credentials...")
        # Try with a default user if registration fails
        token = test_login("testuser", "Test123!@#")
        if token:
            test_get_profile(token)
    
    print("\n" + "=" * 50)
    print("Tests Complete!")