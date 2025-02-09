from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_password_reset_email(user, domain: str, protocol: str = 'http') -> bool:
    """
    Send password reset email to user.
    
    Args:
        user: User object
        domain: Domain name for reset link
        protocol: Protocol (http/https) for reset link
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Generate token and encoded user ID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construct reset URL
        reset_url = f"{protocol}://{domain}/auth/reset-password/{uid}/{token}/"
        
        # Email content
        subject = "Password Reset Request"
        message = f"""
        Hello {user.username},

        You requested a password reset for your Imagi account.
        Please click the link below to reset your password:

        {reset_url}

        If you did not request this reset, please ignore this email.

        Best regards,
        The Imagi Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        return False
