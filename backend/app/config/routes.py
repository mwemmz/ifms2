"""Route configuration for the API Gateway"""

# Public routes (no authentication required)
PUBLIC_ROUTES = [
    ('GET', '/health'),
    ('POST', '/api/auth/register'),
    ('POST', '/api/auth/login'),
    ('POST', '/api/auth/verify-mfa'),
]

# Protected routes (authentication required)
PROTECTED_ROUTES = [
    # Auth module
    ('GET', '/api/auth/profile'),
    ('PUT', '/api/auth/update-profile'),
    ('POST', '/api/auth/setup-mfa'),
    ('POST', '/api/auth/disable-mfa'),
    
    # Transactions module
    ('GET', '/api/transactions'),
    ('POST', '/api/transactions'),
    ('GET', '/api/transactions/categories'),
    ('GET', '/api/transactions/<int:transaction_id>'),
    ('PUT', '/api/transactions/<int:transaction_id>'),
    ('DELETE', '/api/transactions/<int:transaction_id>'),
    ('GET', '/api/transactions/summary'),
    ('GET', '/api/transactions/recent'),
    
    # Analysis module
    ('GET', '/api/analysis/category-breakdown'),
    ('GET', '/api/analysis/monthly-summary'),
    ('GET', '/api/analysis/trends'),
    ('GET', '/api/analysis/top-categories'),
    ('GET', '/api/analysis/compare'),
    ('GET', '/api/analysis/patterns'),
    ('GET', '/api/analysis/insights'),
    
    # Prediction module
    ('GET', '/api/predict/next-month'),
    ('GET', '/api/predict/by-category'),
    ('GET', '/api/predict/moving-average'),
    ('GET', '/api/predict/polynomial'),
    ('GET', '/api/predict/ensemble'),
    ('GET', '/api/predict/multi-month'),
    ('GET', '/api/predict/insights'),
    ('GET', '/api/predict/health'),
    
    # Advice module
    ('GET', '/api/advice/health-score'),
    ('GET', '/api/advice/recommendations'),
    ('GET', '/api/advice/budget-suggestions'),
    ('GET', '/api/advice/overspending'),
    ('GET', '/api/advice/savings-opportunities'),
    ('GET', '/api/advice/insights'),
    ('GET', '/api/advice/goal-progress'),
    ('GET', '/api/advice/emergency-fund'),
    
    # Budget module
    ('GET', '/api/budget/monthly'),
    ('GET', '/api/budget/compare'),
    ('GET', '/api/budget/future'),
    ('GET', '/api/budget/recommendations'),
    ('POST', '/api/budget/smart'),
    ('GET', '/api/budget/history'),
    ('GET', '/api/budget/current-status'),
    
    # Reporting module
    ('GET', '/api/reports/monthly'),
    ('GET', '/api/reports/yearly'),
    ('GET', '/api/reports/category'),
    ('GET', '/api/reports/compare-years'),
    ('GET', '/api/reports/export'),
    ('GET', '/api/reports/dashboard'),
    ('GET', '/api/reports/available-reports'),
    
    # Security module
    ('GET', '/api/security/status'),
    ('GET', '/api/security/logs'),
    ('GET', '/api/security/sessions'),
    ('DELETE', '/api/security/sessions/current'),
    ('DELETE', '/api/security/sessions/all'),
    ('GET', '/api/security/alerts'),
    ('POST', '/api/security/alerts/<int:alert_id>/resolve'),
    ('GET', '/api/security/mfa/status'),
    ('GET', '/api/security/audit/recent'),
    ('POST', '/api/security/anomalies/detect'),
]

# MFA-protected routes (require MFA)
MFA_PROTECTED_ROUTES = [
    ('GET', '/api/security/logs'),
    ('GET', '/api/security/alerts'),
    ('GET', '/api/security/sessions'),
    ('POST', '/api/budget/smart'),
    ('GET', '/api/reports/export'),
]

# Rate limits per endpoint (requests per minute)
RATE_LIMITS = {
    '/api/auth/login': 5,
    '/api/auth/register': 3,
    '/api/auth/verify-mfa': 10,
    'default': 60
}

# Cache configuration for specific endpoints
CACHE_CONFIG = {
    '/api/analysis/trends': {'ttl': 300},  # 5 minutes
    '/api/analysis/monthly-summary': {'ttl': 600},  # 10 minutes
    '/api/predict/health': {'ttl': 60},  # 1 minute
    '/api/reports/available-reports': {'ttl': 3600},  # 1 hour
}