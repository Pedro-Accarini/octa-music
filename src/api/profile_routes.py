"""
Profile management API routes.
"""
import logging
from flask import Blueprint, request, jsonify, session

from src.services.auth_service import auth_service
from src.services.email_service import email_service

logger = logging.getLogger(__name__)

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')


def require_authentication(f):
    """Decorator to require authentication for routes."""
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                "success": False,
                "message": "Authentication required"
            }), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@profile_bp.route('/', methods=['GET'])
@require_authentication
def get_profile():
    """
    Get user profile information.
    
    Response:
        {
            "success": bool,
            "data": {
                "username": str,
                "email": str,
                "email_verified": bool,
                "created_at": str,
                "last_login": str
            }
        }
    """
    user_id = session.get('user_id')
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        session.clear()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": user.to_public_dict()
    }), 200


@profile_bp.route('/username', methods=['PUT'])
@require_authentication
def update_username():
    """
    Update user's username.
    
    Request JSON:
        {
            "username": str
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
    
    new_username = data.get('username', '').strip()
    
    if not new_username:
        return jsonify({
            "success": False,
            "message": "Username is required"
        }), 400
    
    user_id = session.get('user_id')
    success, error = auth_service.update_username(user_id, new_username)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400
    
    # Update session
    session['username'] = new_username
    
    return jsonify({
        "success": True,
        "message": "Username updated successfully"
    }), 200


@profile_bp.route('/email', methods=['PUT'])
@require_authentication
def update_email():
    """
    Update user's email (requires re-verification).
    
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
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        }), 400
    
    new_email = data.get('email', '').strip()
    
    if not new_email:
        return jsonify({
            "success": False,
            "message": "Email is required"
        }), 400
    
    user_id = session.get('user_id')
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    
    token, error = auth_service.update_email(user_id, new_email)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400
    
    # Send verification email to new address
    email_service.send_email_change_verification(
        new_email,
        user.username,
        token
    )
    
    # Update session
    session['email'] = new_email
    
    # Note: User will need to verify new email
    return jsonify({
        "success": True,
        "message": "Email updated. Please check your new email to verify it."
    }), 200


@profile_bp.route('/password', methods=['PUT'])
@require_authentication
def change_password():
    """
    Change user's password.
    
    Request JSON:
        {
            "current_password": str,
            "new_password": str,
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
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not all([current_password, new_password, confirm_password]):
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400
    
    if new_password != confirm_password:
        return jsonify({
            "success": False,
            "message": "New passwords do not match"
        }), 400
    
    user_id = session.get('user_id')
    success, error = auth_service.change_password(user_id, current_password, new_password)
    
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400
    
    return jsonify({
        "success": True,
        "message": "Password changed successfully"
    }), 200
