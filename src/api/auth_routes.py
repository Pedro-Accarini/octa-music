"""
Authentication API routes for user registration, login, logout, and password reset.
"""
import logging
from datetime import timedelta, datetime
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.services.auth_service import auth_service
from src.services.email_service import email_service
from src.services.database_service import db_service

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Rate limiter will be initialized in main.py
limiter = None


def init_limiter(app_limiter):
    """Initialize rate limiter for auth routes."""
    global limiter
    limiter = app_limiter


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request JSON:
        {
            "username": str,
            "email": str,
            "password": str,
            "confirm_password": str
        }
    
    Response:
        {
            "success": bool,
            "message": str,
            "data": {...} (optional)
        }
    """
    # Apply rate limiting: 5 registrations per hour per IP
    if limiter:
        try:
            limiter.check_limit("5 per hour")
        except Exception:
            return jsonify({
                "success": False,
                "message": "Too many registration attempts. Please try again later."
            }), 429
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        }), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    # Validate required fields
    if not all([username, email, password, confirm_password]):
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400
    
    # Check password match
    if password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match"
        }), 400
    
    # Create user
    user, error = auth_service.create_user(username, email, password)
    
    # Note: error messages from auth_service are always user-safe strings,
    # never raw exception messages
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400
    
    # Send verification email
    email_sent = email_service.send_verification_email(
        user.email,
        user.username,
        user.verification_token
    )
    
    if not email_sent:
        logger.warning(f"Failed to send verification email to {user.email}")
    
    return jsonify({
        "success": True,
        "message": "Registration successful! Please check your email to verify your account.",
        "data": {
            "username": user.username,
            "email": user.email
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and create session.
    
    Request JSON:
        {
            "login": str (email or username),
            "password": str,
            "remember_me": bool (optional)
        }
    
    Response:
        {
            "success": bool,
            "message": str,
            "data": {...} (optional)
        }
    """
    # Apply rate limiting
    if limiter:
        try:
            limiter.check_limit("3 per minute")
            limiter.check_limit("10 per hour")
        except Exception:
            return jsonify({
                "success": False,
                "message": "Too many login attempts. Please try again later."
            }), 429
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        }), 400
    
    login_id = data.get('login', '').strip()
    password = data.get('password', '')
    remember_me = data.get('remember_me', False)
    
    if not all([login_id, password]):
        return jsonify({
            "success": False,
            "message": "Email/username and password are required"
        }), 400
    
    # Authenticate user
    user, error = auth_service.authenticate_user(login_id, password)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 401
    
    # Create session
    session.clear()
    session['user_id'] = str(user._id)
    session['username'] = user.username
    session['email'] = user.email
    session['remember_me'] = remember_me
    session['login_time'] = datetime.utcnow().isoformat()
    
    # Set session duration
    from datetime import timedelta
    from flask import current_app
    
    if remember_me:
        # Remember me: 30 days
        session.permanent = True
        remember_duration = current_app.config.get('REMEMBER_ME_DURATION', 2592000)
        current_app.permanent_session_lifetime = timedelta(seconds=remember_duration)
    else:
        # Regular session: 80 minutes
        session.permanent = True
        session_duration = current_app.config.get('PERMANENT_SESSION_LIFETIME', 4800)
        current_app.permanent_session_lifetime = timedelta(seconds=session_duration)
    
    logger.info(f"User logged in: {user.username} (remember_me: {remember_me})")
    
    return jsonify({
        "success": True,
        "message": f"Welcome back, {user.username}!",
        "data": user.to_public_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """
    Logout user and clear session.
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    username = session.get('username', 'User')
    session.clear()
    
    logger.info(f"User logged out: {username}")
    
    return jsonify({
        "success": True,
        "message": "You have been logged out successfully."
    }), 200


@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """
    Verify user email with token.
    
    Args:
        token: Email verification token from URL
    
    Response:
        Renders verification result page or redirects
    """
    success, error = auth_service.verify_email(token)
    
    if success:
        # Render success page or redirect to login
        return render_template(
            'auth/verify_email.html',
            success=True,
            message="Email verified successfully! You can now log in."
        )
    else:
        # Render error page
        return render_template(
            'auth/verify_email.html',
            success=False,
            message=error or "Invalid or expired verification link."
        )


@auth_bp.route('/reset-request', methods=['POST'])
def reset_request():
    """
    Request password reset email.
    
    Request JSON:
        {
            "email": str
        }
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    # Apply rate limiting: 3 per hour per IP
    if limiter:
        try:
            limiter.check_limit("3 per hour")
        except Exception:
            return jsonify({
                "success": False,
                "message": "Too many reset requests. Please try again later."
            }), 429
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        }), 400
    
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required"
        }), 400
    
    # Request password reset
    token, error = auth_service.request_password_reset(email)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400
    
    # Send reset email (if user exists, token will be real; otherwise it's a dummy)
    if token and token != "token_generated":
        # Get user to send email
        users_collection = db_service.get_users_collection()
        if users_collection:
            user_data = users_collection.find_one({"email": email.lower()})
            if user_data:
                email_service.send_password_reset_email(
                    user_data['email'],
                    user_data['username'],
                    token
                )
    
    # Always return generic message for security
    return jsonify({
        "success": True,
        "message": "If the email exists, a reset link has been sent."
    }), 200


@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """
    Reset password with token.
    
    Args:
        token: Reset token from URL
    
    Request JSON:
        {
            "password": str,
            "confirm_password": str
        }
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        }), 400
    
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not all([password, confirm_password]):
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400
    
    if password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match"
        }), 400
    
    # Reset password
    success, error = auth_service.reset_password(token, password)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400
    
    return jsonify({
        "success": True,
        "message": "Password changed successfully. Please login."
    }), 200


@auth_bp.route('/session-check', methods=['GET'])
def session_check():
    """
    Check if user session is valid.
    
    Response:
        {
            "success": bool,
            "authenticated": bool,
            "data": {...} (optional, user data if authenticated)
        }
    """
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            "success": True,
            "authenticated": False
        }), 200
    
    # Verify user still exists and is valid
    user = auth_service.get_user_by_id(user_id)
    
    if not user or user.is_locked_out():
        session.clear()
        return jsonify({
            "success": True,
            "authenticated": False
        }), 200
    
    return jsonify({
        "success": True,
        "authenticated": True,
        "data": {
            "username": session.get('username'),
            "email": session.get('email')
        }
    }), 200


@auth_bp.route('/refresh-session', methods=['POST'])
def refresh_session():
    """
    Refresh session (extend timeout).
    Only works if remember_me was enabled.
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    user_id = session.get('user_id')
    remember_me = session.get('remember_me', False)
    
    if not user_id:
        return jsonify({
            "success": False,
            "message": "No active session"
        }), 401
    
    if not remember_me:
        return jsonify({
            "success": False,
            "message": "Session refresh not available"
        }), 403
    
    # Session is automatically refreshed by Flask on each request
    # when session.permanent = True
    
    return jsonify({
        "success": True,
        "message": "Session refreshed"
    }), 200
