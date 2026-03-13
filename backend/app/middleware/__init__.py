"""Middleware components for the API Gateway"""

from functools import wraps
from flask import request, jsonify
import time
import hashlib

def cache_response(timeout=300):
    """Cache response for specified timeout (seconds)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key from request
            cache_key = hashlib.md5(
                f"{request.path}{request.query_string}".encode()
            ).hexdigest()
            
            # Check if response is cached (simplified - use Redis in production)
            if hasattr(request, 'cached_responses'):
                if cache_key in request.cached_responses:
                    cached = request.cached_responses[cache_key]
                    if time.time() - cached['timestamp'] < timeout:
                        return cached['response']
            
            # Call the function
            response = f(*args, **kwargs)
            
            # Cache the response
            if not hasattr(request, 'cached_responses'):
                request.cached_responses = {}
            
            request.cached_responses[cache_key] = {
                'response': response,
                'timestamp': time.time()
            }
            
            return response
        return decorated_function
    return decorator

def log_request():
    """Log request details"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Process request
            response = f(*args, **kwargs)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000
            
            # Log request (you can integrate with your logging system)
            print(f"Request: {request.method} {request.path} - {response.status_code} - {duration:.2f}ms")
            
            return response
        return decorated_function
    return decorator

def require_headers(required_headers):
    """Require specific headers in the request"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing_headers = []
            
            for header in required_headers:
                if header not in request.headers:
                    missing_headers.append(header)
            
            if missing_headers:
                return jsonify({
                    'error': 'Missing required headers',
                    'missing': missing_headers
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_content_type(allowed_types):
    """Validate content type of the request"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_type = request.headers.get('Content-Type', '').lower()
            
            if not any(allowed in content_type for allowed in allowed_types):
                return jsonify({
                    'error': 'Unsupported Media Type',
                    'allowed': allowed_types
                }), 415
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_version(version):
    """Specify API version for endpoint"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Add version info to response headers
            response = f(*args, **kwargs)
            
            if isinstance(response, tuple):
                response[0].headers['X-API-Version'] = version
            else:
                response.headers['X-API-Version'] = version
            
            return response
        return decorated_function
    return decorator