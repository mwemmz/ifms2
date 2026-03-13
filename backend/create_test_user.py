import requests
import json

base_url = "http://localhost:5000"

def create_test_user():
    """Create a test user for development"""
    url = f"{base_url}/api/auth/register"
    
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!@#",
        "full_name": "Test User"
    }
    
    print("Creating test user...")
    response = requests.post(url, json=test_user)
    
    if response.status_code == 201:
        print("✅ Test user created successfully!")
        print(json.dumps(response.json(), indent=2))
        return True
    elif response.status_code == 400:
        error_data = response.json()
        if "Username already exists" in str(error_data):
            print("ℹ️ Test user already exists")
            return True
        else:
            print(f"❌ Error: {error_data}")
            return False
    else:
        print(f"❌ Failed with status code: {response.status_code}")
        print(response.text)
        return False

def verify_user_exists():
    """Try to login to verify user exists"""
    url = f"{base_url}/api/auth/login"
    
    credentials = {
        "username": "testuser",
        "password": "Test123!@#"
    }
    
    print("\nVerifying user can login...")
    response = requests.post(url, json=credentials)
    
    if response.status_code == 200:
        print("✅ Login successful!")
        return True
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.json())
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Test User Setup")
    print("=" * 50)
    
    # Make sure Flask app is running
    try:
        requests.get(f"{base_url}/api/auth/health", timeout=2)
    except:
        print("❌ Cannot connect to Flask server. Make sure it's running on port 5000")
        print("Run 'python run.py' in another terminal first")
        exit(1)
    
    # Create test user
    if create_test_user():
        # Verify login works
        verify_user_exists()
    
    print("\n" + "=" * 50)
    print("Setup complete!")