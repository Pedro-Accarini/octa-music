"""
Input validation utilities for authentication.
"""
import re
from typing import Tuple, Optional
from email_validator import validate_email, EmailNotValidError


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Args:
        username: Username to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return False, "Username must not exceed 30 characters"
    
    # Allow alphanumeric, underscore, and dash
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and dashes"
    
    return True, None


def validate_email_format(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    try:
        # Validate and normalize email
        validated = validate_email(email, check_deliverability=False)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password complexity.
    
    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/`~]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_password_match(password: str, confirm_password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that passwords match.
    
    Args:
        password: Password
        confirm_password: Password confirmation
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if password != confirm_password:
        return False, "Passwords do not match"
    
    return True, None


def get_password_strength(password: str) -> dict:
    """
    Calculate password strength and return score with feedback.
    
    Args:
        password: Password to evaluate
    
    Returns:
        Dictionary with strength score and feedback
    """
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Character variety checks
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Add numbers")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/`~]', password):
        score += 1
    else:
        feedback.append("Add special characters")
    
    # Determine strength level
    if score <= 2:
        strength = "weak"
    elif score <= 4:
        strength = "fair"
    elif score <= 6:
        strength = "good"
    else:
        strength = "strong"
    
    return {
        "score": score,
        "max_score": 7,
        "strength": strength,
        "feedback": feedback
    }


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        input_str: Input string to sanitize
    
    Returns:
        Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = input_str.strip()
    
    # Remove any null bytes
    sanitized = sanitized.replace('\x00', '')
    
    return sanitized
