from flask import request, jsonify, current_app
from functools import wraps
import time
import re
from datetime import datetime
import hashlib
from app.services.security import SecurityService
from app.models.user import User
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

class APIGateway:
    def __init__(self, app=None):
        self.app = app
        self.security_service = SecurityService()
        self.routes = {}
        self.middleware = []
        self.rate_limits = {}
        self.cache_config = {}
        
    def init_app(self, app):
        """Initialize the gateway with Flask app"""
        self.app = app
        
        # Register error handlers
        app.register_error_handler(400, self.handle_bad_request)
        app.register_error_handler(401, self.handle_unauthorized)
        app.register_error_handler(403, self.handle_forbidden)
        app.register_error_handler(404, self.handle_not_found)
        app.register_error_handler(405, self.handle_method_not_allowed)
        app.register_error_handler(429, self.handle_rate_limit)
        app.register_error_handler(500, self.handle_server_error)
        
        # Register before request handlers
        app.before_request(self.before_request)
        
        # Register after request handlers
        app.after_request(self.after_request)
        
        print("API Gateway initialized")
    
    def register_route(self, endpoint, methods=None, auth_required=True, rate_limit=None):
        """Decorator to register a route with the gateway"""
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                return f(*args, **kwargs)
            
            # Store route metadata
            self.routes[endpoint] = {
                'function': wrapped,
                'methods': methods or ['GET'],
                'auth_required': auth_required,
                'rate_limit': rate_limit,
                'name': f.__name__
            }
            
            return wrapped
        return decorator
    
    def add_middleware(self, middleware_func):
        """Add middleware to the pipeline"""
        self.middleware.append(middleware_func)
    
    def before_request(self):
        """Process request before route handler"""
        try:
            # Skip for static files
            if request.path.startswith('/static'):
                return None
            
            # Apply all middleware
            for middleware in self.middleware:
                result = middleware(request)
                if result:  # Middleware returned a response
                    return result
            
            # Check if endpoint exists - if not, let it go to 404 handler
            if request.endpoint is None:
                return None
            
            # Check authentication if required
            auth_required = self._is_auth_required(request.endpoint)
            if auth_required:
                auth_result = self._authenticate_request()
                if auth_result:
                    return auth_result
            
            # Check rate limits
            rate_limit_result = self._check_rate_limit(request)
            if rate_limit_result:
                return rate_limit_result
            
            # Validate request
            validation_result = self._validate_request(request)
            if validation_result:
                return validation_result
            
            # Log request
            self._log_request(request)
            
            return None
            
        except Exception as e:
            return self.handle_server_error(e)
    
    def after_request(self, response):
        """Process response after route handler"""
        try:
            # Add security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Add API info headers
            response.headers['X-API-Version'] = '1.0'
            response.headers['X-API-Gateway'] = 'IFMS-Gateway'
            
            # Add CORS headers for allowed origins
            origin = request.headers.get('Origin')
            if origin and self._is_allowed_origin(origin):
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            
            # Handle OPTIONS requests
            if request.method == 'OPTIONS':
                return response
            
            # Log response for debugging
            if current_app.debug:
                print(f"Response: {response.status_code}")
            
            return response
            
        except Exception as e:
            return self.handle_server_error(e)
    
    def handle_bad_request(self, error):
        """Handle 400 Bad Request"""
        return self._error_response(400, "Bad Request", str(error))
    
    def handle_unauthorized(self, error):
        """Handle 401 Unauthorized"""
        self.security_service.log_security_event(
            'unauthorized_access',
            status='blocked',
            severity='warning',
            details=f"Unauthorized access attempt to {request.path}"
        )
        return self._error_response(401, "Unauthorized", "Authentication required")
    
    def handle_forbidden(self, error):
        """Handle 403 Forbidden"""
        self.security_service.log_security_event(
            'forbidden_access',
            status='blocked',
            severity='warning',
            details=f"Forbidden access attempt to {request.path}"
        )
        return self._error_response(403, "Forbidden", "You don't have permission to access this resource")
    
    def handle_not_found(self, error):
        """Handle 404 Not Found"""
        # Check if it's an API route
        if request.path.startswith('/api/'):
            # For API routes, return 404 with error details
            return self._error_response(404, "Not Found", f"Endpoint {request.path} not found")
        else:
            # For non-API routes
            return self._error_response(404, "Not Found", "The requested URL was not found on this server")
    
    def handle_method_not_allowed(self, error):
        """Handle 405 Method Not Allowed"""
        return self._error_response(405, "Method Not Allowed", f"Method {request.method} not allowed for {request.path}")
    
    def handle_rate_limit(self, error):
        """Handle 429 Too Many Requests"""
        self.security_service.log_security_event(
            'rate_limit_exceeded',
            status='blocked',
            severity='info',
            details=f"Rate limit exceeded for {request.path}"
        )
        return self._error_response(429, "Too Many Requests", "Rate limit exceeded. Please try again later.")
    
    def handle_server_error(self, error):
        """Handle 500 Internal Server Error"""
        self.security_service.log_security_event(
            'server_error',
            status='error',
            severity='critical',
            details=f"Server error on {request.path}: {str(error)}"
        )
        return self._error_response(500, "Internal Server Error", "An unexpected error occurred")
    
    def _is_auth_required(self, endpoint):
        """Check if authentication is required for an endpoint"""
        # If endpoint doesn't exist, it should return 404, not 401
        if endpoint is None:
            return False
        
        # Public endpoints that don't require authentication
        public_endpoints = [
            'auth.register',
            'auth.login',
            'auth.verify_mfa',
            'health.health_check',
            'health.detailed_health',
            'static'
        ]
        
        if endpoint in public_endpoints:
            return False
        
        # Check if endpoint starts with auth. for public auth endpoints
        if endpoint and endpoint.startswith('auth.'):
            if endpoint in ['auth.login', 'auth.register', 'auth.verify_mfa']:
                return False
        
        return True
    
    def _authenticate_request(self):
        """Authenticate the current request"""
        try:
            # Try to verify JWT
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            
            if not user_id:
                return self.handle_unauthorized(None)
            
            # Convert user_id to int if it's a string
            if isinstance(user_id, str):
                try:
                    user_id = int(user_id)
                except ValueError:
                    return self.handle_unauthorized(None)
            
            # Check if user exists and is active
            user = User.query.get(user_id)
            if not user:
                return self.handle_unauthorized(None)
            
            # Check if MFA is required for this endpoint
            claims = get_jwt() or {}
            if self._is_mfa_required(request.endpoint) and not claims.get('mfa_verified'):
                return jsonify({
                    'error': 'MFA Required',
                    'message': 'This endpoint requires MFA verification'
                }), 403
            
            # Store user in request context for later use
            request.user = user
            
            return None
            
        except Exception as e:
            return self.handle_unauthorized(e)
    
    def _is_mfa_required(self, endpoint):
        """Check if MFA is required for an endpoint"""
        if endpoint is None:
            return False
            
        mfa_required_endpoints = [
            'security.get_security_logs',
            'security.get_alerts',
            'security.get_sessions',
            'security.get_security_status',
            'budget.create_smart_budget',
            'reporting.export_data'
        ]
        
        return endpoint in mfa_required_endpoints
    
    def _check_rate_limit(self, request):
        """Check rate limits for the request"""
        try:
            # Skip rate limiting for certain paths
            if request.path.startswith('/static'):
                return None
                
            # Get client identifier (user ID if authenticated, otherwise IP)
            client_id = None
            try:
                verify_jwt_in_request(optional=True)
                client_id = get_jwt_identity()
                if client_id and isinstance(client_id, str):
                    try:
                        client_id = int(client_id)
                    except ValueError:
                        pass
            except:
                pass
            
            if not client_id:
                client_id = request.remote_addr or 'unknown'
            
            # Convert client_id to string for dictionary key
            client_id = str(client_id)
            
            # Define rate limits per endpoint - INCREASED LOGIN LIMIT TO 10
            rate_limits = {
                '/api/auth/login': {'limit': 10, 'window': 60},  # Increased from 5 to 10 per minute
                '/api/auth/register': {'limit': 3, 'window': 3600},  # 3 per hour
                '/api/transactions': {'limit': 100, 'window': 60},  # 100 per minute
                '/api/analysis': {'limit': 60, 'window': 60},  # 60 per minute
                '/api/predict': {'limit': 30, 'window': 60},  # 30 per minute
                '/api/advice': {'limit': 30, 'window': 60},  # 30 per minute
                '/api/budget': {'limit': 30, 'window': 60},  # 30 per minute
                '/api/reports': {'limit': 20, 'window': 60},  # 20 per minute
                '/api/security': {'limit': 20, 'window': 60},  # 20 per minute
            }
            
            # Find matching rate limit rule
            endpoint_rule = {'limit': 60, 'window': 60}  # default
            for path, rule in rate_limits.items():
                if request.path.startswith(path):
                    endpoint_rule = rule
                    break
            
            # In-memory rate limiting (for development)
            from collections import defaultdict
            from time import time
            
            if not hasattr(current_app, 'request_counts'):
                current_app.request_counts = defaultdict(list)
            
            # Clean old requests
            now = time()
            current_app.request_counts[client_id] = [
                t for t in current_app.request_counts[client_id] 
                if now - t < endpoint_rule['window']
            ]
            
            # Check limit
            if len(current_app.request_counts[client_id]) >= endpoint_rule['limit']:
                self.security_service.log_security_event(
                    'rate_limit_exceeded',
                    status='blocked',
                    severity='warning',
                    details=f"Rate limit exceeded for {request.path} by {client_id}"
                )
                return self.handle_rate_limit(None)
            
            # Add current request (but don't count failed logins multiple times)
            if not (request.path == '/api/auth/login' and 
                    hasattr(request, '_login_failed') and 
                    request._login_failed):
                current_app.request_counts[client_id].append(now)
            
            return None
            
        except Exception as e:
            print(f"Error checking rate limit: {e}")
            return None  # Fail open
    
    def _validate_request(self, request):
        """Validate the incoming request"""
        try:
            # Check content type for POST/PUT requests
            if request.method in ['POST', 'PUT']:
                if not request.is_json:
                    return self._error_response(415, "Unsupported Media Type", "Content-Type must be application/json")
            
            # Validate request size
            if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
                return self._error_response(413, "Payload Too Large", "Request entity too large")
            
            # More flexible Accept header validation
            if not request.path.startswith('/static'):
                accept_header = request.headers.get('Accept', '')
                # Allow requests without Accept header or with */*
                if accept_header and accept_header != '*/*':
                    if 'application/json' not in accept_header:
                        # Only reject if they explicitly ask for something we don't support
                        if not any(allowed in accept_header for allowed in ['application/json', '*/*']):
                            return self._error_response(406, "Not Acceptable", 
                                                      "This API only supports JSON responses")
            
            return None
            
        except Exception as e:
            return self.handle_bad_request(e)
    
    def _log_request(self, request):
        """Log the request for debugging/auditing"""
        if current_app.debug:
            print(f"Request: {request.method} {request.path}")
            if request.is_json:
                print(f"JSON: {request.get_json()}")
    
    def _is_allowed_origin(self, origin):
        """Check if origin is allowed for CORS"""
        allowed_origins = [
            'http://localhost:3000',
            'http://localhost:5000',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:5000'
        ]
        return origin in allowed_origins
    
    def _error_response(self, code, error, message):
        """Create a standardized error response"""
        response = jsonify({
            'error': error,
            'message': message,
            'status_code': code,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path
        })
        response.status_code = code
        return response