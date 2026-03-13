from app import create_app, db
from app.models.user import User, UserProfile, Transaction
from app.models.security import SecurityLog, LoginAttempt, UserSession, SecurityAlert, APIAudit

def init_database():
    """Initialize database with proper table creation order"""
    print("Creating database tables...")
    
    app = create_app()
    with app.app_context():
        # Drop all tables first (clean slate)
        db.drop_all()
        print("Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("Created all tables successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables created: {tables}")

if __name__ == "__main__":
    init_database()