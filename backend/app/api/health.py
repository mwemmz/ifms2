from flask import Blueprint, jsonify
from datetime import datetime
import psutil
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Basic system info
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'IFMS API Gateway',
            'version': '1.0.0',
            'environment': os.getenv('FLASK_ENV', 'development')
        }
        
        # Add system metrics in debug mode
        if os.getenv('FLASK_ENV') == 'development':
            health_status['system'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        
        # Check database connection
        from app import db
        try:
            db.session.execute('SELECT 1')
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['database'] = 'error'
            health_status['status'] = 'degraded'
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check for debugging"""
    import sys
    import platform
    
    health_info = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'working_directory': os.getcwd(),
        'process_id': os.getpid(),
        'environment_variables': {
            k: v for k, v in os.environ.items() 
            if not k.startswith('SECRET') and not k.startswith('PASSWORD')
        }
    }
    
    return jsonify(health_info), 200