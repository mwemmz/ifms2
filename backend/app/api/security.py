from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.security import SecurityService
from app.models.user import User
from app.models.security import SecurityLog, SecurityAlert, UserSession, APIAudit
from app import db
import traceback

security_bp = Blueprint('security', __name__)
security_service = SecurityService()

@security_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_security_logs():
    """Get security logs for the current user"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        if not user_id:
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        event_type = request.args.get('event_type')
        severity = request.args.get('severity')
        
        # Build query
        query = SecurityLog.query.filter_by(user_id=user_id)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        # Paginate
        logs = query.order_by(SecurityLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'page': page,
            'per_page': per_page,
            'pages': logs.pages
        }), 200
        
    except Exception as e:
        print(f"Error in get_security_logs: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@security_bp.route('/logs/all', methods=['GET'])
@jwt_required()
def get_all_logs():
    """Get all security logs (admin only)"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id_filter = request.args.get('user_id', type=int)
        
        query = SecurityLog.query
        
        if user_id_filter:
            query = query.filter_by(user_id=user_id_filter)
        
        logs = query.order_by(SecurityLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'page': page,
            'per_page': per_page,
            'pages': logs.pages
        }), 200
        
    except Exception as e:
        print(f"Error in get_all_logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@security_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get security alerts"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        # Get query parameters
        include_resolved = request.args.get('include_resolved', 'false').lower() == 'true'
        severity = request.args.get('severity')
        
        query = SecurityAlert.query.filter(
            (SecurityAlert.user_id == user_id) | (SecurityAlert.user_id.is_(None))
        )
        
        if not include_resolved:
            query = query.filter_by(resolved=False)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        alerts = query.order_by(SecurityAlert.created_at.desc()).all()
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts],
            'count': len(alerts),
            'unresolved': len([a for a in alerts if not a.resolved])
        }), 200
        
    except Exception as e:
        print(f"Error in get_alerts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@security_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert(alert_id):
    """Resolve a security alert"""
    try:
        data = request.get_json() or {}
        notes = data.get('notes')
        
        success = security_service.resolve_alert(alert_id, notes)
        
        if success:
            return jsonify({'message': 'Alert resolved successfully'}), 200
        else:
            return jsonify({'error': 'Alert not found'}), 404
            
    except Exception as e:
        print(f"Error in resolve_alert: {str(e)}")
        return jsonify({'error': str(e)}), 500

@security_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get active sessions for the current user"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        if not user_id:
            return jsonify({'error': 'Invalid user ID'}), 400
        
        sessions = UserSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(UserSession.last_activity.desc()).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions),
            'max_sessions': security_service.MAX_SESSIONS_PER_USER
        }), 200
        
    except Exception as e:
        print(f"Error in get_sessions: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@security_bp.route('/sessions/current', methods=['DELETE'])
@jwt_required()
def logout_current():
    """Logout current session"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '')
        
        security_service.end_session(token)
        
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        security_service.log_security_event(
            'logout',
            status='success',
            details='User logged out',
            user_id=user_id
        )
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        print(f"Error in logout_current: {str(e)}")
        return jsonify({'error': str(e)}), 500

@security_bp.route('/sessions/all', methods=['DELETE'])
@jwt_required()
def logout_all():
    """Logout from all sessions"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        if not user_id:
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # Get current token to exclude
        auth_header = request.headers.get('Authorization', '')
        current_token = auth_header.replace('Bearer ', '')
        
        security_service.end_all_sessions(user_id, current_token)
        
        security_service.log_security_event(
            'logout_all',
            status='success',
            details='Logged out from all sessions',
            user_id=user_id
        )
        
        return jsonify({'message': 'Logged out from all other sessions'}), 200
        
    except Exception as e:
        print(f"Error in logout_all: {str(e)}")
        return jsonify({'error': str(e)}), 500

@security_bp.route('/status', methods=['GET'])
@jwt_required()
def get_security_status():
    """Get security status for current user"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        if not user_id:
            return jsonify({'error': 'Invalid user ID'}), 400
        
        status = security_service.get_user_security_status(user_id)
        
        return jsonify(status), 200
        
    except Exception as e:
        print(f"Error in get_security_status: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@security_bp.route('/report', methods=['GET'])
@jwt_required()
def get_security_report():
    """Get security report (admin only)"""
    try:
        days = request.args.get('days', 30, type=int)
        
        report = security_service.get_security_report(days)
        
        return jsonify(report), 200
        
    except Exception as e:
        print(f"Error in get_security_report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@security_bp.route('/anomalies/detect', methods=['POST'])
@jwt_required()
def detect_anomalies():
    """Manually trigger anomaly detection"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        # Check specific user or all
        target_user = request.args.get('user_id', type=int)
        
        anomalies = security_service.detect_anomalies(target_user)
        
        return jsonify({
            'anomalies_detected': len(anomalies),
            'anomalies': anomalies
        }), 200
        
    except Exception as e:
        print(f"Error in detect_anomalies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@security_bp.route('/mfa/status', methods=['GET'])
@jwt_required()
def mfa_status():
    """Get MFA status"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        if not user_id:
            return jsonify({'error': 'Invalid user ID'}), 400
        
        user = User.query.get(user_id)
        
        return jsonify({
            'mfa_enabled': user.mfa_enabled if user else False,
            'message': 'MFA is enabled' if user and user.mfa_enabled else 'MFA is disabled'
        }), 200
        
    except Exception as e:
        print(f"Error in mfa_status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@security_bp.route('/audit/recent', methods=['GET'])
@jwt_required()
def recent_audit():
    """Get recent API audit logs"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
        
        if not user_id:
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # Get recent API calls by this user
        audits = APIAudit.query.filter_by(
            user_id=user_id
        ).order_by(APIAudit.timestamp.desc()).limit(50).all()
        
        return jsonify({
            'audits': [audit.to_dict() for audit in audits],
            'count': len(audits)
        }), 200
        
    except Exception as e:
        print(f"Error in recent_audit: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500