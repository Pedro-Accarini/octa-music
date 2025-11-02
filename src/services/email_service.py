"""
Email service for sending authentication-related emails.
"""
import logging
from typing import Optional
from flask import current_app, render_template_string
from flask_mail import Mail, Message

logger = logging.getLogger(__name__)

# Email templates as strings (can be moved to HTML files later)
VERIFICATION_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #1db954; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f9f9f9; }
        .button { display: inline-block; padding: 12px 24px; background-color: #1db954; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Octa Music!</h1>
        </div>
        <div class="content">
            <p>Hi {{ username }},</p>
            <p>Thank you for registering with Octa Music. Please verify your email address to complete your registration.</p>
            <p style="text-align: center;">
                <a href="{{ verification_link }}" class="button">Verify Email Address</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{{ verification_link }}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account with Octa Music, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 Octa Music. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

PASSWORD_RESET_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #1db954; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f9f9f9; }
        .button { display: inline-block; padding: 12px 24px; background-color: #1db954; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Password Reset Request</h1>
        </div>
        <div class="content">
            <p>Hi {{ username }},</p>
            <p>We received a request to reset your password for your Octa Music account.</p>
            <p style="text-align: center;">
                <a href="{{ reset_link }}" class="button">Reset Password</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{{ reset_link }}</p>
            <p>This link will expire in 1 hour.</p>
            <p><strong>If you didn't request a password reset, please ignore this email.</strong> Your password will remain unchanged.</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 Octa Music. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

EMAIL_CHANGE_VERIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #1db954; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f9f9f9; }
        .button { display: inline-block; padding: 12px 24px; background-color: #1db954; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Verify Your New Email</h1>
        </div>
        <div class="content">
            <p>Hi {{ username }},</p>
            <p>You recently changed your email address for your Octa Music account. Please verify your new email address.</p>
            <p style="text-align: center;">
                <a href="{{ verification_link }}" class="button">Verify New Email</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{{ verification_link }}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't change your email address, please contact support immediately.</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 Octa Music. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


class EmailService:
    """
    Service for sending authentication-related emails.
    """
    
    def __init__(self):
        self.mail = None
    
    def init_app(self, app):
        """Initialize the email service with Flask app."""
        self.mail = Mail(app)
    
    def send_verification_email(self, email: str, username: str, token: str) -> bool:
        """
        Send email verification email.
        
        Args:
            email: User's email address
            username: User's username
            token: Verification token
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5000')
            verification_link = f"{frontend_url}/api/auth/verify-email/{token}"
            
            html_body = render_template_string(
                VERIFICATION_EMAIL_TEMPLATE,
                username=username,
                verification_link=verification_link
            )
            
            msg = Message(
                subject="Verify Your Octa Music Account",
                recipients=[email],
                html=html_body
            )
            
            # In development mode, log email instead of sending
            if current_app.config.get('MAIL_SUPPRESS_SEND', False):
                logger.info(f"[DEV MODE] Email verification link for {email}: {verification_link}")
                return True
            
            self.mail.send(msg)
            logger.info(f"Verification email sent to: {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            return False
    
    def send_password_reset_email(self, email: str, username: str, token: str) -> bool:
        """
        Send password reset email.
        
        Args:
            email: User's email address
            username: User's username
            token: Reset token
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5000')
            reset_link = f"{frontend_url}/reset-password/{token}"
            
            html_body = render_template_string(
                PASSWORD_RESET_EMAIL_TEMPLATE,
                username=username,
                reset_link=reset_link
            )
            
            msg = Message(
                subject="Reset Your Octa Music Password",
                recipients=[email],
                html=html_body
            )
            
            # In development mode, log email instead of sending
            if current_app.config.get('MAIL_SUPPRESS_SEND', False):
                logger.info(f"[DEV MODE] Password reset link for {email}: {reset_link}")
                return True
            
            self.mail.send(msg)
            logger.info(f"Password reset email sent to: {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
    
    def send_email_change_verification(self, email: str, username: str, token: str) -> bool:
        """
        Send email change verification email.
        
        Args:
            email: New email address
            username: User's username
            token: Verification token
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5000')
            verification_link = f"{frontend_url}/api/auth/verify-email/{token}"
            
            html_body = render_template_string(
                EMAIL_CHANGE_VERIFICATION_TEMPLATE,
                username=username,
                verification_link=verification_link
            )
            
            msg = Message(
                subject="Verify Your New Email Address",
                recipients=[email],
                html=html_body
            )
            
            # In development mode, log email instead of sending
            if current_app.config.get('MAIL_SUPPRESS_SEND', False):
                logger.info(f"[DEV MODE] Email change verification link for {email}: {verification_link}")
                return True
            
            self.mail.send(msg)
            logger.info(f"Email change verification sent to: {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email change verification: {e}")
            return False


# Global email service instance
email_service = EmailService()
