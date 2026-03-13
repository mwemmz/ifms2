from functools import wraps
from flask import request, jsonify, g, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.services.security import SecurityService
from app.models.user import User
import time
import re

security_service = SecurityService()

def security_middleware(app):
    """Apply security middleware to all requests"""
    
    @app.before_request
    def before_request():
        """Process request before handling"""
        # Store start time for response time calculation
        g.start_time = time.time()
        
        # Rate limiting for login endpoints
        if request.path == '/api/auth/login' and request.method == 'POST':
            try:
                data = request.get_json()
                username = data.get('username') if data else None
                ip = request.remote_addr
                
                allowed, message = security_service.check_rate_limit(username, ip)
                if not allowed:
                    return jsonify({'error': message}), 429
            except:
                pass  # If we can't parse JSON, let the login handler handle it
        
        # Check for suspicious patterns in input
        if request.is_json and request.get_json():
            data = request.get_json()
            if has_sql_injection(data) or has_xss(data):
                security_service.log_security_event(
                    'suspicious_input',
                    status='blocked',
                    severity='critical',
                    details=f"Suspicious input detected"
                )
                return jsonify({'error': 'Invalid input detected'}), 400
    
    @app.after_request
    def after_request(response):
        """Process response after handling"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        # Calculate response time
        if hasattr(g, 'start_time'):
            response_time = (time.time() - g.start_time) * 1000  # in milliseconds
            
            # Get user_id if available
            user_id = None
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
            except:
                pass
            
            # Audit API call for non-static endpoints
            if not request.path.startswith('/static') and not request.path.startswith('/api/auth/login'):
                try:
                    security_service.audit_api_call(
                        endpoint=request.path,
                        method=request.method,
                        status_code=response.status_code,
                        response_time=response_time,
                        request_data=str(request.get_json()) if request.is_json else None,
                        user_id=user_id
                    )
                except Exception as e:
                    # Don't let audit failures break the response
                    print(f"Audit error: {e}")
                    pass
        
        return response

def require_mfa(fn):
    """Decorator to require MFA for specific endpoints"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if user and not user.mfa_enabled:
                return jsonify({
                    'error': 'MFA required',
                    'message': 'Please enable MFA to access this resource'
                }), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    
    return wrapper

def rate_limit(max_requests=60, window_seconds=60):
    """Rate limiting decorator for specific endpoints"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Get client IP
            ip = request.remote_addr
            
            # Simple in-memory rate limiting (in production, use Redis)
            from collections import defaultdict
            from time import time
            
            if not hasattr(g, 'request_counts'):
                g.request_counts = defaultdict(list)
            
            # Clean old requests
            now = time()
            g.request_counts[ip] = [t for t in g.request_counts[ip] if now - t < window_seconds]
            
            # Check rate limit
            if len(g.request_counts[ip]) >= max_requests:
                security_service.log_security_event(
                    'rate_limit_exceeded',
                    status='blocked',
                    severity='warning',
                    details=f"Rate limit exceeded for IP {ip}"
                )
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Add current request
            g.request_counts[ip].append(now)
            
            return fn(*args, **kwargs)
        
        return wrapper
    
    return decorator

def has_sql_injection(data):
    """Check for SQL injection patterns"""
    if isinstance(data, dict):
        for key, value in data.items():
            if has_sql_injection(key) or has_sql_injection(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if has_sql_injection(item):
                return True
    elif isinstance(data, str):
        # Common SQL injection patterns
        patterns = [
            r'(\bSELECT\b.*\bFROM\b)',
            r'(\bINSERT\b.*\bINTO\b)',
            r'(\bUPDATE\b.*\bSET\b)',
            r'(\bDELETE\b.*\bFROM\b)',
            r'(\bDROP\b.*\bTABLE\b)',
            r'(\bUNION\b.*\bSELECT\b)',
            r'--',
            r';',
            r'/\*',
            r'\*/'
        ]
        
        for pattern in patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
    
    return False

def has_xss(data):
    """Check for XSS patterns"""
    if isinstance(data, dict):
        for key, value in data.items():
            if has_xss(key) or has_xss(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if has_xss(item):
                return True
    elif isinstance(data, str):
        # Common XSS patterns
        patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onload=',
            r'onclick=',
            r'onmouseover=',
            r'alert\(',
            r'<iframe',
            r'<img',
            r'<svg',
            r'&lt;script',
            r'&#'
        ]
        
        for pattern in patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
    
    return False

def sanitize_input(data):
    """Sanitize input data"""
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        # Remove potentially dangerous characters
        # This is a basic sanitization - in production, use a proper library
        data = re.sub(r'[<>"\']', '', data)
        return data
    else:
        return data