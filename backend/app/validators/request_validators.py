from functools import wraps
from flask import request, jsonify
import re
from datetime import datetime

def validate_request(schema):
    """Decorator to validate request data against a schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get request data based on content type
            if request.is_json:
                data = request.get_json()
            elif request.form:
                data = request.form.to_dict()
            else:
                data = request.args.to_dict()
            
            # Validate against schema
            errors = validate_schema(data, schema)
            
            if errors:
                return jsonify({
                    'error': 'Validation Error',
                    'details': errors
                }), 400
            
            # Store validated data in request
            request.validated_data = data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_schema(data, schema):
    """Validate data against a schema"""
    errors = []
    
    for field, rules in schema.items():
        # Check required fields
        if rules.get('required', False) and field not in data:
            errors.append(f"{field} is required")
            continue
        
        # Skip validation if field not present and not required
        if field not in data:
            continue
        
        value = data[field]
        
        # Type validation
        if 'type' in rules:
            type_valid, type_error = validate_type(value, rules['type'], field)
            if not type_valid:
                errors.append(type_error)
                continue
        
        # Format validation
        if 'format' in rules:
            format_valid, format_error = validate_format(value, rules['format'], field)
            if not format_valid:
                errors.append(format_error)
        
        # Range validation for numbers
        if 'min' in rules and isinstance(value, (int, float)):
            if value < rules['min']:
                errors.append(f"{field} must be at least {rules['min']}")
        
        if 'max' in rules and isinstance(value, (int, float)):
            if value > rules['max']:
                errors.append(f"{field} must be at most {rules['max']}")
        
        # Length validation for strings
        if 'min_length' in rules and isinstance(value, str):
            if len(value) < rules['min_length']:
                errors.append(f"{field} must be at least {rules['min_length']} characters")
        
        if 'max_length' in rules and isinstance(value, str):
            if len(value) > rules['max_length']:
                errors.append(f"{field} must be at most {rules['max_length']} characters")
        
        # Pattern validation
        if 'pattern' in rules and isinstance(value, str):
            if not re.match(rules['pattern'], value):
                errors.append(f"{field} format is invalid")
        
        # Enum validation
        if 'enum' in rules and value not in rules['enum']:
            errors.append(f"{field} must be one of: {', '.join(rules['enum'])}")
    
    return errors

def validate_type(value, expected_type, field_name):
    """Validate value type"""
    try:
        if expected_type == 'string':
            return isinstance(value, str), None
        elif expected_type == 'number':
            float(value)
            return True, None
        elif expected_type == 'integer':
            int(value)
            return True, None
        elif expected_type == 'boolean':
            if isinstance(value, bool):
                return True, None
            if value.lower() in ['true', 'false']:
                return True, None
            return False, f"{field_name} must be a boolean"
        elif expected_type == 'date':
            datetime.strptime(value, '%Y-%m-%d')
            return True, None
        elif expected_type == 'email':
            if re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
                return True, None
            return False, f"{field_name} must be a valid email"
        else:
            return True, None
    except:
        return False, f"{field_name} must be of type {expected_type}"

def validate_format(value, format_type, field_name):
    """Validate value format"""
    if format_type == 'email':
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
            return False, f"{field_name} must be a valid email"
    
    elif format_type == 'date':
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except:
            return False, f"{field_name} must be in YYYY-MM-DD format"
    
    elif format_type == 'datetime':
        try:
            datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except:
            return False, f"{field_name} must be in YYYY-MM-DD HH:MM:SS format"
    
    elif format_type == 'phone':
        if not re.match(r'^\+?[0-9]{10,15}$', value):
            return False, f"{field_name} must be a valid phone number"
    
    elif format_type == 'password':
        if len(value) < 8:
            return False, f"{field_name} must be at least 8 characters"
        if not re.search(r'[A-Z]', value):
            return False, f"{field_name} must contain at least one uppercase letter"
        if not re.search(r'[a-z]', value):
            return False, f"{field_name} must contain at least one lowercase letter"
        if not re.search(r'[0-9]', value):
            return False, f"{field_name} must contain at least one number"
    
    return True, None

# Common validation schemas
auth_schemas = {
    'register': {
        'username': {'type': 'string', 'required': True, 'min_length': 3, 'max_length': 50},
        'email': {'type': 'email', 'required': True},
        'password': {'type': 'string', 'required': True, 'format': 'password'},
        'full_name': {'type': 'string', 'max_length': 100}
    },
    'login': {
        'username': {'type': 'string', 'required': True},
        'password': {'type': 'string', 'required': True}
    },
    'mfa_verify': {
        'token': {'type': 'string', 'required': True, 'pattern': r'^[0-9]{6}$'}
    }
}

transaction_schemas = {
    'create': {
        'amount': {'type': 'number', 'required': True, 'min': 0.01},
        'category': {'type': 'string', 'required': True},
        'description': {'type': 'string', 'max_length': 200},
        'date': {'type': 'date', 'required': True}
    },
    'update': {
        'amount': {'type': 'number', 'min': 0.01},
        'category': {'type': 'string'},
        'description': {'type': 'string', 'max_length': 200},
        'date': {'type': 'date'}
    }
}

profile_schemas = {
    'update': {
        'full_name': {'type': 'string', 'max_length': 100},
        'monthly_salary': {'type': 'number', 'min': 0},
        'savings_goal': {'type': 'number', 'min': 0}
    }
}

budget_schemas = {
    'smart_budget': {
        'target_savings_rate': {'type': 'number', 'min': 5, 'max': 50}
    }
}