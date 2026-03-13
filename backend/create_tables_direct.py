import sqlite3
import os

def create_tables_direct():
    """Create tables directly using SQLite"""
    db_path = 'ifms.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Removed existing database: {db_path}")
    
    # Connect to database (this creates it)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    print("🚀 Creating tables in correct order...")
    
    # 1. Create users table first
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(200) NOT NULL,
        mfa_secret VARCHAR(32),
        mfa_enabled BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ Created users table")
    
    # 2. Create user_profiles table
    cursor.execute('''
    CREATE TABLE user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        full_name VARCHAR(100),
        monthly_salary FLOAT DEFAULT 0,
        savings_goal FLOAT DEFAULT 0,
        emergency_fund_target FLOAT DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    print("✅ Created user_profiles table")
    
    # 3. Create transactions table
    cursor.execute('''
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount FLOAT NOT NULL,
        category VARCHAR(50) NOT NULL,
        description VARCHAR(200),
        transaction_date TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    print("✅ Created transactions table")
    
    # 4. Create security_logs table
    cursor.execute('''
    CREATE TABLE security_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_type VARCHAR(50) NOT NULL,
        severity VARCHAR(20) NOT NULL,
        status VARCHAR(20) NOT NULL,
        ip_address VARCHAR(45),
        user_agent VARCHAR(200),
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    print("✅ Created security_logs table")
    
    # 5. Create login_attempts table
    cursor.execute('''
    CREATE TABLE login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) NOT NULL,
        ip_address VARCHAR(45) NOT NULL,
        success BOOLEAN DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ Created login_attempts table")
    
    # 6. Create user_sessions table
    cursor.execute('''
    CREATE TABLE user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_token VARCHAR(500) UNIQUE NOT NULL,
        ip_address VARCHAR(45),
        user_agent VARCHAR(200),
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    print("✅ Created user_sessions table")
    
    # 7. Create security_alerts table
    cursor.execute('''
    CREATE TABLE security_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        alert_type VARCHAR(50) NOT NULL,
        severity VARCHAR(20) NOT NULL,
        description TEXT,
        resolved BOOLEAN DEFAULT 0,
        resolved_at TIMESTAMP,
        resolved_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (resolved_by) REFERENCES users (id)
    )
    ''')
    print("✅ Created security_alerts table")
    
    # 8. Create api_audit table
    cursor.execute('''
    CREATE TABLE api_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        endpoint VARCHAR(200) NOT NULL,
        method VARCHAR(10) NOT NULL,
        status_code INTEGER,
        ip_address VARCHAR(45),
        user_agent VARCHAR(200),
        request_data TEXT,
        response_time FLOAT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    print("✅ Created api_audit table")
    
    # Commit changes
    conn.commit()
    
    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n📊 Tables in database ({len(tables)}):")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   - {table[0]}: {count} rows")
    
    # Close connection
    conn.close()
    print("\n🎉 Database created successfully!")

if __name__ == "__main__":
    create_tables_direct()