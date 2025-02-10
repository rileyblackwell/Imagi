from django.contrib.auth import login, logout, get_user_model
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class AuthenticationService:
    @staticmethod
    def register_user(request, serializer):
        """Handle user registration logic."""
        try:
            user = serializer.save(request)
            token, _ = Token.objects.get_or_create(user=user)
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            return user, token
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise

    @staticmethod
    def login_user(request, user):
        """Handle user login logic."""
        try:
            token, _ = Token.objects.get_or_create(user=user)
            login(request, user)
            return token
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise

    @staticmethod
    def logout_user(request):
        """Handle user logout logic."""
        try:
            Token.objects.filter(user=request.user).delete()
            request.session.flush()
            logout(request)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            raise

class SessionService:
    @staticmethod
    def get_session_data(request):
        """Get current session data."""
        return {
            'isAuthenticated': bool(request.user and request.user.is_authenticated),
            'user': request.user if request.user.is_authenticated else None
        }
