"""
User model for MongoDB authentication system.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from bson import ObjectId


class User:
    """
    User model for authentication and profile management.
    Represents a user document in MongoDB.
    """
    
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        _id: Optional[ObjectId] = None,
        email_verified: bool = False,
        verification_token: Optional[str] = None,
        verification_token_expires: Optional[datetime] = None,
        reset_token: Optional[str] = None,
        reset_token_expires: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        failed_login_attempts: int = 0,
        lockout_until: Optional[datetime] = None
    ):
        self._id = _id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.email_verified = email_verified
        self.verification_token = verification_token
        self.verification_token_expires = verification_token_expires
        self.reset_token = reset_token
        self.reset_token_expires = reset_token_expires
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        self.failed_login_attempts = failed_login_attempts
        self.lockout_until = lockout_until
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt with salt rounds = 12."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary for MongoDB storage."""
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'email_verified': self.email_verified,
            'verification_token': self.verification_token,
            'verification_token_expires': self.verification_token_expires,
            'reset_token': self.reset_token,
            'reset_token_expires': self.reset_token_expires,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'failed_login_attempts': self.failed_login_attempts,
            'lockout_until': self.lockout_until
        }
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary for public API responses (exclude sensitive data)."""
        return {
            'id': str(self._id) if self._id else None,
            'username': self.username,
            'email': self.email,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User object from a dictionary (MongoDB document)."""
        return cls(
            _id=data.get('_id'),
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            email_verified=data.get('email_verified', False),
            verification_token=data.get('verification_token'),
            verification_token_expires=data.get('verification_token_expires'),
            reset_token=data.get('reset_token'),
            reset_token_expires=data.get('reset_token_expires'),
            created_at=data.get('created_at', datetime.utcnow()),
            last_login=data.get('last_login'),
            failed_login_attempts=data.get('failed_login_attempts', 0),
            lockout_until=data.get('lockout_until')
        )
    
    def is_locked_out(self) -> bool:
        """Check if user account is currently locked out."""
        if self.lockout_until and self.lockout_until > datetime.utcnow():
            return True
        return False
    
    def reset_failed_attempts(self):
        """Reset failed login attempts counter."""
        self.failed_login_attempts = 0
        self.lockout_until = None
    
    def increment_failed_attempts(self):
        """Increment failed login attempts and potentially lock account."""
        self.failed_login_attempts += 1
        # Lock account for 15 minutes after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lockout_until = datetime.utcnow() + timedelta(minutes=15)
    
    def get_id(self) -> str:
        """Get user ID as string (required for Flask-Login)."""
        return str(self._id) if self._id else None
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (required for Flask-Login)."""
        return True
    
    @property
    def is_active(self) -> bool:
        """Check if user is active (required for Flask-Login)."""
        return not self.is_locked_out()
    
    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous (required for Flask-Login)."""
        return False
