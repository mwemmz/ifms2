from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    
    if user:
        print("=" * 50)
        print("TEST USER CREDENTIALS")
        print("=" * 50)
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"MFA Enabled: {user.mfa_enabled}")
        
        # Test common passwords
        from app.utils.security import verify_password
        
        test_passwords = [
            "Test123!@#",
            "password123",
            "testuser",
            "password",
            "admin123"
        ]
        
        print("\nTesting passwords:")
        print("-" * 30)
        for pwd in test_passwords:
            if verify_password(user.password_hash, pwd):
                print(f"✅ Password found: '{pwd}'")
                break
        else:
            print("❌ Could not find matching password from common list")
            print("The password is something else")
    else:
        print("❌ User 'testuser' not found")