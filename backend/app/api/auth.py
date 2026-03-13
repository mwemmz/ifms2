from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import db, User, UserProfile
from app.utils.security import hash_password, verify_password, validate_email, validate_password_strength
from app.services.security import SecurityService
import pyotp
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
security_service = SecurityService()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_strong, message = validate_password_strength(data['password'])
        if not is_strong:
            return jsonify({'error': message}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password'])
        )
        
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Create user profile
        profile = UserProfile(
            user_id=user.id,
            full_name=data.get('full_name', '')
        )
        db.session.add(profile)
        
        db.session.commit()
        
        # Log successful registration
        security_service.log_security_event(
            'user_registered',
            status='success',
            user_id=user.id,
            details=f"User {user.username} registered successfully"
        )
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        security_service.log_security_event(
            'registration_error',
            status='error',
            severity='warning',
            details=str(e)
        )
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Log login attempt
        security_service.log_login_attempt(data['username'], False)
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not verify_password(user.password_hash, data['password']):
            # Log failed login
            security_service.log_security_event(
                'login_failed',
                status='failure',
                severity='warning',
                details=f"Failed login attempt for username: {data['username']}"
            )
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Log successful login
        security_service.log_security_event(
            'login_success',
            status='success',
            user_id=user.id,
            details="Successful login"
        )
        
        # Update login attempt as success
        from app.models.security import LoginAttempt
        latest_attempt = LoginAttempt.query.filter_by(
            username=data['username']
        ).order_by(LoginAttempt.timestamp.desc()).first()
        
        if latest_attempt:
            latest_attempt.success = True
            db.session.commit()
        
        # Check if MFA is enabled
        if user.mfa_enabled:
            # Create temporary token for MFA verification
            temp_token = create_access_token(
                identity=str(user.id),  # FIXED: Convert to string
                additional_claims={'temp': True, 'mfa_required': True},
                expires_delta=timedelta(minutes=5)
            )
            
            # Log MFA required
            security_service.log_security_event(
                'mfa_required',
                status='info',
                user_id=user.id,
                details="MFA verification required"
            )
            
            return jsonify({
                'mfa_required': True,
                'temp_token': temp_token,
                'message': 'MFA verification required'
            })
        
        # Create access token
        access_token = create_access_token(
            identity=str(user.id),  # FIXED: Convert to string
            additional_claims={'mfa_verified': True}
        )
        
        # Create session
        expires_at = datetime.utcnow() + timedelta(hours=1)
        security_service.create_session(user.id, access_token, expires_at)
        
        # Get user profile
        profile = None
        if user.profile:
            profile = {
                'full_name': user.profile.full_name,
                'monthly_salary': user.profile.monthly_salary,
                'savings_goal': user.profile.savings_goal
            }
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'mfa_enabled': user.mfa_enabled,
                'profile': profile,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        security_service.log_security_event(
            'login_error',
            status='error',
            severity='warning',
            details=str(e)
        )
        return jsonify({'error': str(e)}), 500
@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if 'current_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not verify_password(user.password_hash, data['current_password']):
            # Log failed password change attempt
            security_service.log_security_event(
                'password_change',
                status='failure',
                severity='warning',
                user_id=user_id,
                details='Failed password change attempt - incorrect current password'
            )
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password strength
        from app.utils.security import validate_password_strength
        is_strong, message = validate_password_strength(data['new_password'])
        if not is_strong:
            return jsonify({'error': message}), 400
        
        # Update password
        user.password_hash = hash_password(data['new_password'])
        db.session.commit()
        
        # Log successful password change
        security_service.log_security_event(
            'password_change',
            status='success',
            severity='info',
            user_id=user_id,
            details='Password changed successfully'
        )
        
        # Optionally: Invalidate all other sessions for security
        from app.services.security import SecurityService
        security_service.end_all_sessions(user_id, request.headers.get('Authorization', '').replace('Bearer ', ''))
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        # Convert back to int for database query
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile_data = None
        if user.profile:
            profile_data = {
                'full_name': user.profile.full_name,
                'monthly_salary': user.profile.monthly_salary,
                'savings_goal': user.profile.savings_goal
            }
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'mfa_enabled': user.mfa_enabled,
            'profile': profile_data,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }), 200
        
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update profile
        if user.profile:
            profile = user.profile
        else:
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
        
        if 'full_name' in data:
            profile.full_name = data['full_name']
        if 'monthly_salary' in data:
            profile.monthly_salary = float(data['monthly_salary'])
        if 'savings_goal' in data:
            profile.savings_goal = float(data['savings_goal'])
        
        db.session.commit()
        
        security_service.log_security_event(
            'profile_updated',
            status='success',
            user_id=user.id,
            details="Profile updated successfully"
        )
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/setup-mfa', methods=['POST'])
@jwt_required()
def setup_mfa():
    """Setup MFA for user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate MFA secret
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        db.session.commit()
        
        # Generate TOTP URI - using username instead of email for better compatibility
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.username,  # Changed from email to username
            issuer_name="IFMS"
        )
        
        # Generate QR code with higher quality
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4,  # Increased border
            error_correction=qrcode.constants.ERROR_CORRECT_H  # Higher error correction
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Create image with better contrast
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 with proper formatting
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Also return the secret for manual entry
        return jsonify({
            'secret': secret,
            'qr_code': f"data:image/png;base64,{img_str}",
            'manual_entry_key': secret,  # Added for clarity
            'account': user.username,    # Added for manual entry
            'message': 'Scan QR code or enter the secret key manually in Google Authenticator'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-mfa', methods=['POST'])
@jwt_required()
def verify_mfa():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'token' not in data:
            return jsonify({'error': 'MFA token required'}), 400
        
        user = User.query.get(int(user_id))
        
        if not user or not user.mfa_secret:
            return jsonify({'error': 'MFA not set up'}), 400
        
        # Verify token
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(data['token']):
            # Log MFA failure
            security_service.log_security_event(
                'mfa_verification_failed',
                status='failure',
                severity='warning',
                user_id=user.id,
                details="Invalid MFA token"
            )
            return jsonify({'error': 'Invalid MFA token'}), 401
        
        # Log MFA success
        security_service.log_security_event(
            'mfa_verification_success',
            status='success',
            user_id=user.id,
            details="MFA verified successfully"
        )
        
        # Enable MFA if not already enabled
        if not user.mfa_enabled:
            user.mfa_enabled = True
            db.session.commit()
        
        # Create full access token
        access_token = create_access_token(
            identity=str(user.id),  # FIXED: Convert to string
            additional_claims={'mfa_verified': True}
        )
        
        # Create session
        expires_at = datetime.utcnow() + timedelta(hours=1)
        security_service.create_session(user.id, access_token, expires_at)
        
        return jsonify({
            'access_token': access_token,
            'message': 'MFA verified successfully'
        }), 200
        
    except Exception as e:
        print(f"MFA verification error: {e}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/disable-mfa', methods=['POST'])
@jwt_required()
def disable_mfa():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.mfa_enabled = False
        user.mfa_secret = None
        db.session.commit()
        
        security_service.log_security_event(
            'mfa_disabled',
            status='success',
            user_id=user.id,
            details="MFA disabled successfully"
        )
        
        return jsonify({'message': 'MFA disabled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500