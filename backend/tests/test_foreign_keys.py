from app import create_app, db
from app.models.user import User
from app.models.security import SecurityLog
from sqlalchemy import text
from datetime import datetime

def test_foreign_keys():
    """Test if foreign keys are working"""
    app = create_app()
    
    with app.app_context():
        # Enable foreign keys
        db.session.execute(text('PRAGMA foreign_keys = ON'))
        db.session.commit()
        
        # Check if foreign keys are enabled
        result = db.session.execute(text('PRAGMA foreign_keys'))
        foreign_keys_enabled = result.scalar()
        print(f"🔑 Foreign keys enabled: {foreign_keys_enabled}")
        
        # Create a test user
        print("\n👤 Creating test user...")
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="test_hash"
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ User created with ID: {user.id}")
        
        # Try to create a security log with valid user_id
        print("\n📝 Creating security log with valid user_id...")
        log = SecurityLog(
            user_id=user.id,
            event_type="test",
            severity="info",
            status="success"
        )
        db.session.add(log)
        db.session.commit()
        print("✅ Security log created successfully")
        
        # Try to create a security log with invalid user_id (should fail)
        print("\n📝 Attempting to create security log with invalid user_id...")
        try:
            invalid_log = SecurityLog(
                user_id=99999,  # This user doesn't exist
                event_type="test",
                severity="info",
                status="failure"
            )
            db.session.add(invalid_log)
            db.session.commit()
            print("❌ ERROR: Should have failed but didn't!")
        except Exception as e:
            print(f"✅ Correctly blocked: {e}")
            db.session.rollback()
        
        # Clean up
        print("\n🧹 Cleaning up...")
        SecurityLog.query.delete()
        User.query.delete()
        db.session.commit()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 TESTING FOREIGN KEY CONSTRAINTS")
    print("=" * 50)
    test_foreign_keys()