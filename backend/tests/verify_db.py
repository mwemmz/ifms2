from app import create_app, db
from sqlalchemy import inspect, text

def verify_database():
    """Verify database setup"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("=" * 50)
        print("🔍 DATABASE VERIFICATION")
        print("=" * 50)
        
        if not tables:
            print("❌ No tables found!")
            return
        
        print(f"✅ Found {len(tables)} tables:\n")
        
        for table in tables:
            # Get column info
            columns = inspector.get_columns(table)
            print(f"📊 Table: {table}")
            print(f"   Columns: {len(columns)}")
            
            # Get row count
            try:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"   Rows: {count}")
            except Exception as e:
                print(f"   Error counting rows: {e}")
            
            # Show first few columns
            col_names = [col['name'] for col in columns[:3]]
            print(f"   Sample columns: {', '.join(col_names)}...")
            print()
        
        print("=" * 50)
        print("✅ Database verification complete!")

if __name__ == "__main__":
    verify_database()