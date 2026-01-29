"""
Custom social account adapter for django-allauth.
Enforces existing-email-only policy for Google SSO.
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter that enforces existing-email-only policy.
    Users can only sign in with Google if their email already exists in the database.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        """
        # If the user is already logged in, allow the connection
        if request.user.is_authenticated:
            return
        
        # Get the email from the social account
        if not sociallogin.is_existing:
            # This is a new social login (not connected to any existing user)
            email = None
            if sociallogin.account.extra_data:
                email = sociallogin.account.extra_data.get('email')
            
            if not email:
                # No email provided by the social provider
                logger.warning("Google SSO attempted without email")
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5174')
                raise ImmediateHttpResponse(
                    redirect(f'{frontend_url}/auth/signin?sso_error=no_email')
                )
            
            # Check if a user with this email exists
            try:
                user = User.objects.get(email__iexact=email)
                # Connect this social account to the existing user
                sociallogin.connect(request, user)
                logger.info(f"Connected Google account to existing user: {email}")
            except User.DoesNotExist:
                # No user with this email exists - reject the login
                logger.warning(f"Google SSO attempted with non-existing email: {email}")
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5174')
                raise ImmediateHttpResponse(
                    redirect(f'{frontend_url}/auth/signin?sso_error=no_account')
                )
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Return False to prevent automatic signup.
        Users must have an existing account to use social login.
        """
        return False
