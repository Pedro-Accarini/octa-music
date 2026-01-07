"""
Security middleware for Flask application.
Implements security headers and best practices for production deployment.
"""
import logging
from functools import wraps
from flask import request, make_response

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses.
    
    Implements:
    - Content Security Policy (CSP)
    - HTTP Strict Transport Security (HSTS)
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security headers middleware with Flask app."""
        app.after_request(self.add_security_headers)
        logger.info("Security headers middleware initialized")
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response."""
        # Content Security Policy - Restricts resource loading
        # This policy allows resources from self, inline styles/scripts needed by the app
        # and specific CDNs used by the application
        csp_directives = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "'unsafe-inline'",  # Required for inline scripts in templates
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com"
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",  # Required for inline styles
                "https://fonts.googleapis.com"
            ],
            "img-src": [
                "'self'",
                "data:",
                "https:",  # Allow images from Spotify, YouTube APIs
                "http:"  # Allow HTTP images in development
            ],
            "font-src": [
                "'self'",
                "https://fonts.gstatic.com",
                "data:"
            ],
            "connect-src": [
                "'self'",
                "https://api.spotify.com",
                "https://www.googleapis.com"
            ],
            "frame-ancestors": ["'none'"],  # Prevent clickjacking
            "base-uri": ["'self'"],
            "form-action": ["'self'"]
        }
        
        csp_string = "; ".join([
            f"{directive} {' '.join(sources)}"
            for directive, sources in csp_directives.items()
        ])
        response.headers['Content-Security-Policy'] = csp_string
        
        # Strict Transport Security - Force HTTPS
        # max-age=31536000 (1 year), includeSubDomains, preload
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # X-Frame-Options - Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options - Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection - Enable XSS filter (legacy browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy - Control referrer information
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy - Control browser features
        permissions = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()"
        ]
        response.headers['Permissions-Policy'] = ", ".join(permissions)
        
        # Cache-Control for security-sensitive responses
        if request.path.startswith('/api/auth'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'
        
        return response


def rate_limit_error_handler(e):
    """Custom error handler for rate limit exceeded."""
    logger.warning(f"Rate limit exceeded: {request.remote_addr} - {request.path}")
    return make_response({
        "success": False,
        "error": "Rate limit exceeded. Please try again later.",
        "retry_after": getattr(e, 'retry_after', None)
    }, 429)


def sanitize_input(data):
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        data: String or dict to sanitize
        
    Returns:
        Sanitized data
    """
    if isinstance(data, str):
        # Remove potential script tags and dangerous characters
        dangerous_patterns = ['<script', '</script', 'javascript:', 'onerror=', 'onload=']
        sanitized = data
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, '')
        return sanitized.strip()
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data


def require_auth(f):
    """
    Decorator to require authentication for routes.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            return 'This is protected'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session, redirect, url_for, jsonify
        
        if not session.get('user_id'):
            if request.is_json:
                return jsonify({
                    "success": False,
                    "error": "Authentication required"
                }), 401
            return redirect(url_for('login_page'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_content_type(required_type='application/json'):
    """
    Decorator to validate request content type.
    
    Args:
        required_type: Expected content type (default: 'application/json')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            if not request.content_type or required_type not in request.content_type:
                return jsonify({
                    "success": False,
                    "error": f"Content-Type must be {required_type}"
                }), 415
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


class RequestValidationMiddleware:
    """Middleware for validating and sanitizing incoming requests."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize request validation middleware with Flask app."""
        app.before_request(self.validate_request)
        logger.info("Request validation middleware initialized")
    
    @staticmethod
    def validate_request():
        """Validate incoming requests for security issues."""
        # Validate request size
        max_content_length = 10 * 1024 * 1024  # 10MB
        if request.content_length and request.content_length > max_content_length:
            logger.warning(f"Request too large: {request.content_length} bytes from {request.remote_addr}")
            return make_response({
                "success": False,
                "error": "Request entity too large"
            }, 413)
        
        # Check for suspicious patterns in URL
        suspicious_patterns = ['../', '..\\', '<script', 'javascript:']
        url = request.url.lower()
        if any(pattern in url for pattern in suspicious_patterns):
            logger.warning(f"Suspicious URL pattern detected: {request.url} from {request.remote_addr}")
            return make_response({
                "success": False,
                "error": "Invalid request"
            }, 400)
        
        return None
