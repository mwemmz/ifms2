from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='chola_mwamba').first()
    if user:
        print(f"✅ User found: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password hash: {user.password_hash[:50]}...")
        print(f"   MFA enabled: {user.mfa_enabled}")
    else:
        print("❌ User 'chola_mwamba' not found!")
        
    # List all users
    print("\n📋 All users in database:")
    for u in User.query.all():
        print(f"   - {u.username}")