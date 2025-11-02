"""
Authentication service for user management and authentication operations.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from itsdangerous import URLSafeTimedSerializer
from bson import ObjectId
from flask import current_app

from src.user_models.user_model import User
from src.services.database_service import db_service
from src.utils.validators import (
    validate_username,
    validate_email_format,
    validate_password,
    sanitize_input
)

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for handling authentication operations.
    """
    
    def __init__(self):
        self.users_collection = None
    
    def init_app(self, app):
        """Initialize the auth service with Flask app."""
        self.users_collection = db_service.get_users_collection()
    
    def generate_token(self, purpose: str, **kwargs) -> str:
        """
        Generate a secure token for email verification or password reset.
        
        Args:
            purpose: Token purpose (e.g., 'email-verification', 'password-reset')
            **kwargs: Additional data to encode in token
        
        Returns:
            Secure token string
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        data = {'purpose': purpose, **kwargs}
        return serializer.dumps(data, salt=purpose)
    
    def verify_token(self, token: str, purpose: str, max_age: int = 86400) -> Optional[dict]:
        """
        Verify and decode a token.
        
        Args:
            token: Token to verify
            purpose: Expected token purpose
            max_age: Maximum age in seconds (default 24 hours)
        
        Returns:
            Decoded token data or None if invalid
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token, salt=purpose, max_age=max_age)
            if data.get('purpose') == purpose:
                return data
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
        return None
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Create a new user account.
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
        
        Returns:
            Tuple of (User object, error_message)
        """
        if self.users_collection is None:
            return None, "Database not available"
        
        # Sanitize inputs
        username = sanitize_input(username)
        email = sanitize_input(email.lower())
        
        # Validate inputs
        valid, error = validate_username(username)
        if not valid:
            return None, error
        
        valid, error, normalized_email = validate_email_format(email)
        if not valid:
            return None, error
        
        # Use normalized email
        email = normalized_email
        
        valid, error = validate_password(password)
        if not valid:
            return None, error
        
        # Check if username already exists
        if self.users_collection.find_one({"username": username}):
            return None, "Username already exists"
        
        # Check if email already exists
        if self.users_collection.find_one({"email": email}):
            return None, "Email already exists"
        
        # Create user
        password_hash = User.hash_password(password)
        verification_token = self.generate_token('email-verification', email=email)
        
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            verification_token=verification_token,
            verification_token_expires=datetime.utcnow() + timedelta(hours=24)
        )
        
        # Insert into database
        try:
            result = self.users_collection.insert_one(user.to_dict())
            user._id = result.inserted_id
            logger.info(f"User created: {username} ({email})")
            return user, None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None, "Failed to create user account"
    
    def authenticate_user(
        self,
        login: str,
        password: str
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate a user with email/username and password.
        
        Args:
            login: Email or username
            password: Plain text password
        
        Returns:
            Tuple of (User object, error_message)
        """
        if self.users_collection is None:
            return None, "Database not available"
        
        login = sanitize_input(login.lower())
        
        # Find user by email or username
        user_data = self.users_collection.find_one({
            "$or": [
                {"email": login},
                {"username": login}
            ]
        })
        
        if not user_data:
            return None, "Invalid credentials"
        
        user = User.from_dict(user_data)
        
        # Check if account is locked
        if user.is_locked_out():
            return None, "Account is temporarily locked. Please try again later."
        
        # Verify password
        if not User.verify_password(password, user.password_hash):
            # Increment failed attempts
            user.increment_failed_attempts()
            self.users_collection.update_one(
                {"_id": user._id},
                {
                    "$set": {
                        "failed_login_attempts": user.failed_login_attempts,
                        "lockout_until": user.lockout_until
                    }
                }
            )
            return None, "Invalid credentials"
        
        # Check if email is verified
        if not user.email_verified:
            return None, "Please verify your email address before logging in."
        
        # Reset failed attempts on successful login
        user.reset_failed_attempts()
        user.last_login = datetime.utcnow()
        
        self.users_collection.update_one(
            {"_id": user._id},
            {
                "$set": {
                    "failed_login_attempts": 0,
                    "lockout_until": None,
                    "last_login": user.last_login
                }
            }
        )
        
        logger.info(f"User authenticated: {user.username}")
        return user, None
    
    def verify_email(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Verify user email with token.
        
        Args:
            token: Verification token
        
        Returns:
            Tuple of (success, error_message)
        """
        if self.users_collection is None:
            return False, "Database not available"
        
        # Verify token (24 hours expiry)
        data = self.verify_token(token, 'email-verification', max_age=86400)
        if not data:
            return False, "Invalid or expired verification link"
        
        email = data.get('email')
        if not email:
            return False, "Invalid verification link"
        
        # Update user
        result = self.users_collection.update_one(
            {"email": email, "email_verified": False},
            {
                "$set": {
                    "email_verified": True,
                    "verification_token": None,
                    "verification_token_expires": None
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Email verified: {email}")
            return True, None
        
        return False, "Email already verified or user not found"
    
    def request_password_reset(self, email: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Request a password reset token.
        
        Args:
            email: User email address
        
        Returns:
            Tuple of (reset_token, error_message)
        """
        if self.users_collection is None:
            return None, "Database not available"
        
        email = sanitize_input(email.lower())
        
        # Find user
        user_data = self.users_collection.find_one({"email": email})
        if not user_data:
            # Don't reveal if email exists - security best practice
            return "token_generated", None
        
        # Generate reset token
        reset_token = self.generate_token('password-reset', email=email)
        reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        
        # Update user with reset token
        self.users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "reset_token": reset_token,
                    "reset_token_expires": reset_token_expires
                }
            }
        )
        
        logger.info(f"Password reset requested: {email}")
        return reset_token, None
    
    def reset_password(self, token: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Reset user password with token.
        
        Args:
            token: Reset token
            new_password: New password
        
        Returns:
            Tuple of (success, error_message)
        """
        if self.users_collection is None:
            return False, "Database not available"
        
        # Verify token (1 hour expiry)
        data = self.verify_token(token, 'password-reset', max_age=3600)
        if not data:
            return False, "Invalid or expired reset link"
        
        email = data.get('email')
        if not email:
            return False, "Invalid reset link"
        
        # Validate new password
        valid, error = validate_password(new_password)
        if not valid:
            return False, error
        
        # Hash new password
        password_hash = User.hash_password(new_password)
        
        # Update user password and clear reset token
        result = self.users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "password_hash": password_hash,
                    "reset_token": None,
                    "reset_token_expires": None,
                    "failed_login_attempts": 0,
                    "lockout_until": None
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Password reset: {email}")
            return True, None
        
        return False, "User not found or password already reset"
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID string
        
        Returns:
            User object or None
        """
        if self.users_collection is None:
            return None
        
        try:
            user_data = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User.from_dict(user_data)
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
        
        return None
    
    def update_username(self, user_id: str, new_username: str) -> Tuple[bool, Optional[str]]:
        """
        Update user's username.
        
        Args:
            user_id: User ID
            new_username: New username
        
        Returns:
            Tuple of (success, error_message)
        """
        if self.users_collection is None:
            return False, "Database not available"
        
        new_username = sanitize_input(new_username)
        
        # Validate username
        valid, error = validate_username(new_username)
        if not valid:
            return False, error
        
        # Check if username already exists
        existing = self.users_collection.find_one({
            "username": new_username,
            "_id": {"$ne": ObjectId(user_id)}
        })
        if existing:
            return False, "Username already exists"
        
        # Update username
        result = self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"username": new_username}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Username updated for user: {user_id}")
            return True, None
        
        return False, "Failed to update username"
    
    def update_email(self, user_id: str, new_email: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Update user's email (requires re-verification).
        
        Args:
            user_id: User ID
            new_email: New email address
        
        Returns:
            Tuple of (verification_token, error_message)
        """
        if self.users_collection is None:
            return None, "Database not available"
        
        new_email = sanitize_input(new_email.lower())
        
        # Validate email
        valid, error, normalized_email = validate_email_format(new_email)
        if not valid:
            return None, error
        
        # Use normalized email
        new_email = normalized_email
        
        # Check if email already exists
        existing = self.users_collection.find_one({
            "email": new_email,
            "_id": {"$ne": ObjectId(user_id)}
        })
        if existing:
            return None, "Email already exists"
        
        # Generate verification token
        verification_token = self.generate_token('email-verification', email=new_email)
        
        # Update email (set as unverified)
        result = self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "email": new_email,
                    "email_verified": False,
                    "verification_token": verification_token,
                    "verification_token_expires": datetime.utcnow() + timedelta(hours=24)
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Email updated for user: {user_id}")
            return verification_token, None
        
        return None, "Failed to update email"
    
    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user's password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
        
        Returns:
            Tuple of (success, error_message)
        """
        if self.users_collection is None:
            return False, "Database not available"
        
        # Get user
        user_data = self.users_collection.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            return False, "User not found"
        
        user = User.from_dict(user_data)
        
        # Verify current password
        if not User.verify_password(current_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Validate new password
        valid, error = validate_password(new_password)
        if not valid:
            return False, error
        
        # Hash new password
        password_hash = User.hash_password(new_password)
        
        # Update password
        result = self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": password_hash}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Password changed for user: {user_id}")
            return True, None
        
        return False, "Failed to change password"


# Global auth service instance
auth_service = AuthService()
