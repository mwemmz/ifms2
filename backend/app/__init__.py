from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import timedelta
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ifms.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    
    # Configure CORS for local and Render frontend
    CORS(app,
        origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://ifms2-22.onrender.com"
        ],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    # Import models to ensure they're registered
    from app.models.user import User, UserProfile, Transaction
    from app.models.security import SecurityLog, LoginAttempt, UserSession, SecurityAlert, APIAudit
    
    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.transactions import transactions_bp
    from app.api.analysis import analysis_bp
    from app.api.prediction import prediction_bp
    from app.api.advisor import advisor_bp
    from app.api.budget import budget_bp
    from app.api.reporting import reporting_bp
    from app.api.security import security_bp
    from app.api.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(prediction_bp, url_prefix='/api/predict')
    app.register_blueprint(advisor_bp, url_prefix='/api/advice')
    app.register_blueprint(budget_bp, url_prefix='/api/budget')
    app.register_blueprint(reporting_bp, url_prefix='/api/reports')
    app.register_blueprint(security_bp, url_prefix='/api/security')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created!")
        print("CORS configured for: http://localhost:3000")
    
    return app