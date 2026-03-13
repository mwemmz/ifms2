import os
from app import create_app, db

def reset_database():
    """Completely reset the database"""
    print("Resetting database...")
    
    # Delete the existing database file
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ifms.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted existing database: {db_path}")
    
    # Create app and tables
    app = create_app()
    with app.app_context():
        # Import models in correct order
        from app.models.user import User, UserProfile, Transaction
        from app.models.security import SecurityLog, LoginAttempt, UserSession, SecurityAlert, APIAudit
        
        # Create all tables
        db.create_all()
        print("All tables created successfully!")
        
        # List all tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")

if __name__ == "__main__":
    reset_database()