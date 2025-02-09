"""
Core business logic for the Auth app.
All API endpoints are handled in the api/ directory.
This file contains shared business logic that might be needed across different parts of the app.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.conf import settings
from allauth.account.utils import send_email_confirmation

import logging
logger = logging.getLogger(__name__)

User = get_user_model()

def send_password_reset_email(user, domain, protocol):
    """
    Sends password reset email to user.
    This is a utility function that can be used by both API and other parts of the system.
    
    Args:
        user: The user requesting password reset
        domain: The domain name for reset link
        protocol: The protocol (http/https) for reset link
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        context = {
            "user": user,
            "domain": domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
            "protocol": protocol,
            "site_name": "Imagi"
        }
        
        subject = "Password Reset Requested"
        email_body = render_to_string('auth/password_reset_email.html', context)
        
        send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending password reset email to {user.email}: {str(e)}")
        return False

def validate_reset_token(user, token):
    """
    Validates a password reset token for a user.
    
    Args:
        user: The user attempting to reset password
        token: The reset token to validate
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        is_valid = default_token_generator.check_token(user, token)
        if not is_valid:
            logger.warning(f"Invalid reset token attempt for user {user.email}")
        return is_valid
    except Exception as e:
        logger.error(f"Error validating reset token for {user.email}: {str(e)}")
        return False

def send_verification_email(request, user):
    """Send email verification using allauth."""
    try:
        send_email_confirmation(request, user)
        return True
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        return False
