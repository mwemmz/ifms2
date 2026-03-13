import requests
import random
import string

base_url = "http://localhost:5000"

def create_test_user():
    """Create a random test user and return token"""
    
    # Generate random username
    random_suffix = ''.join(random.choices(string.digits, k=4))
    username = f"testuser{random_suffix}"
    email = f"test{random_suffix}@example.com"
    password = "Test123!@#"
    
    print(f"Creating test user: {username}")
    
    # Register
    register_url = f"{base_url}/api/auth/register"
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Test User"
    }
    
    register_response = requests.post(register_url, json=register_data)
    
    if register_response.status_code != 201:
        print(f"Registration failed: {register_response.json()}")
        return None, None
    
    # Login
    login_url = f"{base_url}/api/auth/login"
    login_data = {
        "username": username,
        "password": password
    }
    
    login_response = requests.post(login_url, json=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.json()}")
        return None, None
    
    token = login_response.json().get('access_token')
    print(f"Login successful! Token obtained.")
    
    return token, username

def login_with_credentials(username="testuser", password="Test123!@#"):
    """Try to login with provided credentials"""
    
    login_url = f"{base_url}/api/auth/login"
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(login_url, json=login_data)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def wait_for_server(seconds=2):
    """Wait for server to be ready"""
    import time
    print(f"Waiting {seconds} seconds for server...")
    time.sleep(seconds)