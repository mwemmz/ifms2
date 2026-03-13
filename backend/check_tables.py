from app import create_app, db
from app.models.user import User, Transaction
from app.models.security import SecurityLog, LoginAttempt, UserSession, SecurityAlert, APIAudit

app = create_app()
with app.app_context():
    print("=" * 60)
    print("DATABASE TABLE CHECK")
    print("=" * 60)
    
    # Check Users
    users = User.query.all()
    print(f"\n👤 USERS TABLE: {len(users)} records")
    for user in users:
        print(f"   - ID: {user.id}, Username: {user.username}, Email: {user.email}, MFA: {user.mfa_enabled}")
    
    # Check Transactions for each user
    print(f"\n💳 TRANSACTIONS TABLE:")
    total_tx = 0
    for user in users:
        user_tx = Transaction.query.filter_by(user_id=user.id).all()
        tx_count = len(user_tx)
        total_tx += tx_count
        print(f"   User {user.username} (ID: {user.id}): {tx_count} transactions")
        
        if tx_count > 0:
            # Show sample
            sample = user_tx[0]
            print(f"      Sample: {sample.amount} - {sample.category} - {sample.transaction_date}")
            
            # Calculate totals
            income_sum = sum(t.amount for t in user_tx if t.amount > 0)
            expense_sum = sum(abs(t.amount) for t in user_tx if t.amount < 0)
            print(f"      Income: ${income_sum:,.2f}")
            print(f"      Expenses: ${expense_sum:,.2f}")
            print(f"      Net: ${income_sum - expense_sum:,.2f}")
    
    # Check Security Tables
    print(f"\n🔒 SECURITY TABLES:")
    
    security_logs = SecurityLog.query.all()
    print(f"   SecurityLogs: {len(security_logs)} records")
    
    login_attempts = LoginAttempt.query.all()
    print(f"   LoginAttempts: {len(login_attempts)} records")
    
    user_sessions = UserSession.query.all()
    print(f"   UserSessions: {len(user_sessions)} records")
    
    security_alerts = SecurityAlert.query.all()
    print(f"   SecurityAlerts: {len(security_alerts)} records")
    
    api_audits = APIAudit.query.all()
    print(f"   APIAudits: {len(api_audits)} records")
    
    print("\n" + "=" * 60)
    print(f"TOTAL TRANSACTIONS: {total_tx}")
    print("=" * 60)