from datetime import datetime, timedelta
from flask import request
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app.models.security import (
    SecurityLog, LoginAttempt, UserSession, 
    SecurityAlert, APIAudit
)
from app import db
import hashlib
import hmac
import ipaddress
from sqlalchemy import func
import json
import logging

# Try to import user_agents, but provide fallback if not available
try:
    import user_agents
    HAS_USER_AGENTS = True
except ImportError:
    HAS_USER_AGENTS = False
    logging.warning("user_agents package not installed. User agent parsing will be limited.")

class SecurityService:
    def __init__(self):
        self.MAX_LOGIN_ATTEMPTS = 5
        self.LOCKOUT_TIME = 15  # minutes
        self.SESSION_TIMEOUT = 60  # minutes
        self.MAX_SESSIONS_PER_USER = 5
    
    def _get_user_id_from_jwt(self):
        """Helper method to get user_id from JWT and convert to int if needed"""
        try:
            user_id = get_jwt_identity()
            if user_id:
                # Convert to int if it's a string representation of a number
                if isinstance(user_id, str) and user_id.isdigit():
                    return int(user_id)
                return user_id
            return None
        except:
            return None
    
    def log_security_event(self, event_type, status='success', severity='info', 
                          details=None, user_id=None):
        """Log a security event"""
        try:
            # Get user_id from JWT if not provided
            if not user_id:
                user_id = self._get_user_id_from_jwt()
            
            # Get request information
            ip_address = request.remote_addr if request else None
            user_agent = request.user_agent.string if request and request.user_agent else None
            
            log = SecurityLog(
                user_id=user_id,
                event_type=event_type,
                severity=severity,
                status=status,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details
            )
            
            db.session.add(log)
            db.session.commit()
            
            # Check if this event triggers an alert
            self._check_for_alerts(event_type, status, user_id, ip_address)
            
            return log
            
        except Exception as e:
            print(f"Error logging security event: {e}")
            db.session.rollback()
            return None
    
    def log_login_attempt(self, username, success):
        """Log a login attempt for rate limiting"""
        try:
            ip_address = request.remote_addr if request else None
            
            attempt = LoginAttempt(
                username=username,
                ip_address=ip_address,
                success=success
            )
            
            db.session.add(attempt)
            db.session.commit()
            
            # Check for multiple failed attempts
            if not success:
                self._check_failed_attempts(username, ip_address)
            
            return attempt
            
        except Exception as e:
            print(f"Error logging login attempt: {e}")
            db.session.rollback()
            return None
    
    def create_session(self, user_id, token, expires_at):
        """Create a new user session"""
        try:
            # Ensure user_id is int for database
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            
            # Clean up old sessions
            self._cleanup_sessions(user_id)
            
            # Check current session count
            active_sessions = UserSession.query.filter_by(
                user_id=user_id, 
                is_active=True
            ).count()
            
            if active_sessions >= self.MAX_SESSIONS_PER_USER:
                # Deactivate oldest session
                oldest = UserSession.query.filter_by(
                    user_id=user_id, 
                    is_active=True
                ).order_by(UserSession.last_activity.asc()).first()
                
                if oldest:
                    oldest.is_active = False
                    db.session.add(oldest)
            
            # Create new session
            ip_address = request.remote_addr if request else None
            user_agent = request.user_agent.string if request and request.user_agent else None
            
            session = UserSession(
                user_id=user_id,
                session_token=token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            
            db.session.add(session)
            db.session.commit()
            
            self.log_security_event(
                'session_created',
                status='success',
                details=f"New session created for user {user_id}",
                user_id=user_id
            )
            
            return session
            
        except Exception as e:
            print(f"Error creating session: {e}")
            db.session.rollback()
            return None
    
    def validate_session(self, token):
        """Validate if a session is active"""
        try:
            session = UserSession.query.filter_by(
                session_token=token,
                is_active=True
            ).first()
            
            if not session:
                return False
            
            # Check if expired
            if session.expires_at and session.expires_at < datetime.utcnow():
                session.is_active = False
                db.session.commit()
                return False
            
            # Update last activity
            session.last_activity = datetime.utcnow()
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"Error validating session: {e}")
            return False
    
    def end_session(self, token):
        """End a user session"""
        try:
            session = UserSession.query.filter_by(session_token=token).first()
            
            if session:
                session.is_active = False
                db.session.commit()
                
                self.log_security_event(
                    'session_ended',
                    status='success',
                    user_id=session.user_id
                )
            
            return True
            
        except Exception as e:
            print(f"Error ending session: {e}")
            return False
    
    def end_all_sessions(self, user_id, exclude_token=None):
        """End all sessions for a user"""
        try:
            # Ensure user_id is int for database
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            
            query = UserSession.query.filter_by(user_id=user_id, is_active=True)
            
            if exclude_token:
                query = query.filter(UserSession.session_token != exclude_token)
            
            sessions = query.all()
            
            for session in sessions:
                session.is_active = False
            
            db.session.commit()
            
            self.log_security_event(
                'all_sessions_ended',
                status='success',
                user_id=user_id,
                details=f"Ended {len(sessions)} sessions"
            )
            
            return True
            
        except Exception as e:
            print(f"Error ending all sessions: {e}")
            return False
    
    def check_rate_limit(self, username=None, ip_address=None):
        """Check if login attempts are rate limited"""
        try:
            if not ip_address and request:
                ip_address = request.remote_addr
            
            # Check by username
            if username:
                recent_attempts = LoginAttempt.query.filter(
                    LoginAttempt.username == username,
                    LoginAttempt.timestamp > datetime.utcnow() - timedelta(minutes=self.LOCKOUT_TIME),
                    LoginAttempt.success == False
                ).count()
                
                if recent_attempts >= self.MAX_LOGIN_ATTEMPTS:
                    return False, f"Too many failed attempts. Try again in {self.LOCKOUT_TIME} minutes."
            
            # Check by IP
            if ip_address:
                recent_ip_attempts = LoginAttempt.query.filter(
                    LoginAttempt.ip_address == ip_address,
                    LoginAttempt.timestamp > datetime.utcnow() - timedelta(minutes=self.LOCKOUT_TIME),
                    LoginAttempt.success == False
                ).count()
                
                if recent_ip_attempts >= self.MAX_LOGIN_ATTEMPTS * 2:
                    return False, "Too many failed attempts from this IP. Try again later."
            
            return True, "OK"
            
        except Exception as e:
            print(f"Error checking rate limit: {e}")
            return True, "OK"  # Fail open
    
    def audit_api_call(self, endpoint, method, status_code, response_time, 
                      request_data=None, user_id=None):
        """Audit API calls"""
        try:
            # Get user_id from JWT if not provided
            if not user_id:
                user_id = self._get_user_id_from_jwt()
            
            # Truncate request data for privacy
            if request_data and len(request_data) > 500:
                request_data = request_data[:500] + "... [truncated]"
            
            ip_address = request.remote_addr if request else None
            user_agent = request.user_agent.string if request and request.user_agent else None
            
            audit = APIAudit(
                user_id=user_id,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                ip_address=ip_address,
                user_agent=user_agent,
                request_data=request_data,
                response_time=response_time,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(audit)
            db.session.commit()
            
        except Exception as e:
            print(f"Error auditing API call: {e}")
            db.session.rollback()
    
    def create_alert(self, alert_type, severity, description, user_id=None):
        """Create a security alert"""
        try:
            # Ensure user_id is int for database if provided
            if user_id and isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            
            alert = SecurityAlert(
                user_id=user_id,
                alert_type=alert_type,
                severity=severity,
                description=description
            )
            
            db.session.add(alert)
            db.session.commit()
            
            # Log the alert creation
            self.log_security_event(
                f"alert_created_{alert_type}",
                status='warning',
                severity=severity,
                details=description,
                user_id=user_id
            )
            
            return alert
            
        except Exception as e:
            print(f"Error creating alert: {e}")
            db.session.rollback()
            return None
    
    def resolve_alert(self, alert_id, resolution_notes=None):
        """Resolve a security alert"""
        try:
            alert = SecurityAlert.query.get(alert_id)
            
            if alert:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                
                # Get current user as resolver
                try:
                    resolver_id = self._get_user_id_from_jwt()
                    alert.resolved_by = resolver_id
                except:
                    pass
                
                db.session.commit()
                
                self.log_security_event(
                    'alert_resolved',
                    status='success',
                    details=f"Alert {alert_id} resolved: {resolution_notes if resolution_notes else 'No notes'}"
                )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error resolving alert: {e}")
            return False
    
    def get_user_security_status(self, user_id):
        """Get security status for a user"""
        try:
            # Ensure user_id is int for database
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            
            # Get active sessions
            active_sessions = UserSession.query.filter_by(
                user_id=user_id, 
                is_active=True
            ).count()
            
            # Get recent failed logins
            user = User.query.get(user_id)
            if user:
                failed_logins = LoginAttempt.query.filter(
                    LoginAttempt.username == user.username,
                    LoginAttempt.timestamp > datetime.utcnow() - timedelta(days=1),
                    LoginAttempt.success == False
                ).count()
            else:
                failed_logins = 0
            
            # Get active alerts
            active_alerts = SecurityAlert.query.filter_by(
                user_id=user_id,
                resolved=False
            ).count()
            
            # Get recent security events
            recent_events = SecurityLog.query.filter_by(
                user_id=user_id
            ).order_by(SecurityLog.timestamp.desc()).limit(10).all()
            
            # Calculate security score
            score = 100
            deductions = []
            
            if active_sessions > 3:
                score -= 10
                deductions.append(f"Multiple active sessions ({active_sessions})")
            
            if failed_logins > 5:
                score -= 20
                deductions.append(f"High number of failed logins ({failed_logins})")
            
            if active_alerts > 0:
                score -= active_alerts * 15
                deductions.append(f"Active security alerts ({active_alerts})")
            
            # Check MFA status
            user = User.query.get(user_id)
            if user and not user.mfa_enabled:
                score -= 15
                deductions.append("MFA not enabled")
            
            score = max(0, min(100, score))
            
            return {
                'user_id': user_id,
                'security_score': score,
                'mfa_enabled': user.mfa_enabled if user else False,
                'active_sessions': active_sessions,
                'failed_logins_24h': failed_logins,
                'active_alerts': active_alerts,
                'deductions': deductions,
                'recent_events': [e.to_dict() for e in recent_events]
            }
            
        except Exception as e:
            print(f"Error getting security status: {e}")
            return {'error': str(e)}
    
    def get_security_report(self, days=30):
        """Generate security report for admin"""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            # Summary statistics
            total_events = SecurityLog.query.filter(
                SecurityLog.timestamp >= since
            ).count()
            
            critical_events = SecurityLog.query.filter(
                SecurityLog.timestamp >= since,
                SecurityLog.severity == 'critical'
            ).count()
            
            failed_logins = LoginAttempt.query.filter(
                LoginAttempt.timestamp >= since,
                LoginAttempt.success == False
            ).count()
            
            successful_logins = LoginAttempt.query.filter(
                LoginAttempt.timestamp >= since,
                LoginAttempt.success == True
            ).count()
            
            active_sessions = UserSession.query.filter_by(is_active=True).count()
            
            active_alerts = SecurityAlert.query.filter_by(resolved=False).count()
            
            # Events by type
            events_by_type = db.session.query(
                SecurityLog.event_type,
                func.count(SecurityLog.id)
            ).filter(
                SecurityLog.timestamp >= since
            ).group_by(SecurityLog.event_type).all()
            
            # Events by severity
            events_by_severity = db.session.query(
                SecurityLog.severity,
                func.count(SecurityLog.id)
            ).filter(
                SecurityLog.timestamp >= since
            ).group_by(SecurityLog.severity).all()
            
            # Top users with security issues
            problem_users = db.session.query(
                SecurityLog.user_id,
                func.count(SecurityLog.id).label('event_count'),
                User.username
            ).join(User, User.id == SecurityLog.user_id).filter(
                SecurityLog.timestamp >= since,
                SecurityLog.severity.in_(['warning', 'critical'])
            ).group_by(SecurityLog.user_id, User.username).order_by(
                func.count(SecurityLog.id).desc()
            ).limit(10).all()
            
            return {
                'period_days': days,
                'summary': {
                    'total_events': total_events,
                    'critical_events': critical_events,
                    'failed_logins': failed_logins,
                    'successful_logins': successful_logins,
                    'login_success_rate': round((successful_logins / (failed_logins + successful_logins) * 100) if (failed_logins + successful_logins) > 0 else 0, 1),
                    'active_sessions': active_sessions,
                    'active_alerts': active_alerts
                },
                'events_by_type': [{'type': t, 'count': c} for t, c in events_by_type],
                'events_by_severity': [{'severity': s, 'count': c} for s, c in events_by_severity],
                'problem_users': [{'user_id': uid, 'username': un, 'events': ec} for uid, ec, un in problem_users],
                'recent_alerts': [a.to_dict() for a in SecurityAlert.query.filter_by(
                    resolved=False
                ).order_by(SecurityAlert.created_at.desc()).limit(20).all()]
            }
            
        except Exception as e:
            print(f"Error generating security report: {e}")
            return {'error': str(e)}
    
    def detect_anomalies(self, user_id=None):
        """Detect security anomalies"""
        try:
            anomalies = []
            
            # Ensure user_id is int for database if provided
            if user_id and isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            
            # Check for multiple sessions from different locations
            if user_id:
                sessions = UserSession.query.filter_by(
                    user_id=user_id,
                    is_active=True
                ).all()
                
                if len(sessions) > 1:
                    # Check if from different IPs
                    ips = set(s.ip_address for s in sessions if s.ip_address)
                    if len(ips) > 1:
                        anomalies.append({
                            'type': 'multiple_locations',
                            'severity': 'medium',
                            'description': f"User has active sessions from {len(ips)} different IP addresses",
                            'user_id': user_id
                        })
            
            # Check for failed login spikes
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_failures = LoginAttempt.query.filter(
                LoginAttempt.timestamp >= one_hour_ago,
                LoginAttempt.success == False
            ).count()
            
            if recent_failures > 20:
                anomalies.append({
                    'type': 'failed_login_spike',
                    'severity': 'high',
                    'description': f"High volume of failed logins ({recent_failures} in last hour)",
                    'user_id': None  # System-wide
                })
            
            # Check for expired sessions
            expired_sessions = UserSession.query.filter(
                UserSession.expires_at < datetime.utcnow(),
                UserSession.is_active == True
            ).count()
            
            if expired_sessions > 10:
                anomalies.append({
                    'type': 'expired_sessions',
                    'severity': 'low',
                    'description': f"Found {expired_sessions} expired but still active sessions",
                    'user_id': None
                })
            
            # Create alerts for anomalies
            for anomaly in anomalies:
                self.create_alert(
                    alert_type=anomaly['type'],
                    severity=anomaly['severity'],
                    description=anomaly['description'],
                    user_id=anomaly['user_id']
                )
            
            return anomalies
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return []
    
    def is_suspicious_ip(self, ip_address):
        """Check if an IP address is suspicious"""
        try:
            # Check if private IP
            if ipaddress.ip_address(ip_address).is_private:
                return False  # Private IPs are not suspicious
            
            # Check for known malicious IPs (simplified - would use a real service)
            # This is a placeholder - in production, use a threat intelligence service
            
            return False
            
        except Exception:
            return False
    
    def get_user_agent_info(self, user_agent_string):
        """Parse user agent for security analysis"""
        try:
            if HAS_USER_AGENTS and user_agent_string:
                ua = user_agents.parse(user_agent_string)
                
                return {
                    'browser': ua.browser.family,
                    'browser_version': ua.browser.version_string,
                    'os': ua.os.family,
                    'os_version': ua.os.version_string,
                    'device': ua.device.family,
                    'is_mobile': ua.is_mobile,
                    'is_tablet': ua.is_tablet,
                    'is_pc': ua.is_pc,
                    'is_bot': ua.is_bot
                }
            else:
                # Basic parsing without user_agents
                return {
                    'browser': 'Unknown',
                    'browser_version': 'Unknown',
                    'os': 'Unknown',
                    'os_version': 'Unknown',
                    'device': 'Unknown',
                    'is_mobile': False,
                    'is_tablet': False,
                    'is_pc': True,
                    'is_bot': False,
                    'raw': user_agent_string[:100] if user_agent_string else None
                }
                
        except Exception as e:
            print(f"Error parsing user agent: {e}")
            return None
    
    # Private helper methods
    def _check_failed_attempts(self, username, ip_address):
        """Check for multiple failed attempts and create alerts"""
        try:
            # Check user-specific failures
            user_failures = LoginAttempt.query.filter(
                LoginAttempt.username == username,
                LoginAttempt.timestamp > datetime.utcnow() - timedelta(minutes=30),
                LoginAttempt.success == False
            ).count()
            
            if user_failures >= self.MAX_LOGIN_ATTEMPTS:
                self.create_alert(
                    alert_type='multiple_failed_logins',
                    severity='medium',
                    description=f"Multiple failed login attempts for user {username} ({user_failures} in 30 minutes)",
                    user_id=None  # We don't know user_id yet
                )
            
            # Check IP-specific failures
            ip_failures = LoginAttempt.query.filter(
                LoginAttempt.ip_address == ip_address,
                LoginAttempt.timestamp > datetime.utcnow() - timedelta(minutes=30),
                LoginAttempt.success == False
            ).count()
            
            if ip_failures >= self.MAX_LOGIN_ATTEMPTS * 2:
                self.create_alert(
                    alert_type='suspicious_ip_activity',
                    severity='high',
                    description=f"Multiple failed login attempts from IP {ip_address} ({ip_failures} in 30 minutes)",
                    user_id=None
                )
                
        except Exception as e:
            print(f"Error checking failed attempts: {e}")
    
    def _check_for_alerts(self, event_type, status, user_id, ip_address):
        """Check if event should trigger an alert"""
        try:
            # Ensure user_id is int for database if provided
            if user_id and isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            
            # Different alert rules based on event type
            if event_type == 'login' and status == 'failure':
                # Check for repeated failures (handled separately)
                pass
                
            elif event_type == 'password_change' and status == 'success':
                # Password changed - log but no alert unless suspicious
                if ip_address and self.is_suspicious_ip(ip_address):
                    self.create_alert(
                        alert_type='suspicious_password_change',
                        severity='high',
                        description=f"Password changed from suspicious IP: {ip_address}",
                        user_id=user_id
                    )
                    
            elif event_type == 'mfa_failure':
                # MFA failures are suspicious
                self.create_alert(
                    alert_type='mfa_failures',
                    severity='high',
                    description="Multiple MFA failures detected",
                    user_id=user_id
                )
                
        except Exception as e:
            print(f"Error checking for alerts: {e}")
    
    def _cleanup_sessions(self, user_id):
        """Clean up old/inactive sessions"""
        try:
            # Ensure user_id is int for database
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            
            # Delete expired sessions
            expired = UserSession.query.filter(
                UserSession.user_id == user_id,
                UserSession.expires_at < datetime.utcnow()
            ).all()
            
            for session in expired:
                db.session.delete(session)
            
            # Mark old inactive sessions as inactive
            old_inactive = UserSession.query.filter(
                UserSession.user_id == user_id,
                UserSession.last_activity < datetime.utcnow() - timedelta(days=7)
            ).all()
            
            for session in old_inactive:
                session.is_active = False
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            db.session.rollback()