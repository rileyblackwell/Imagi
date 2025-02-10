"""
API views for the Auth app.
Handles all authentication-related API endpoints.
"""

# Django REST Framework
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle
from rest_framework.decorators import api_view, permission_classes

# Django and Allauth
from django.contrib.auth import login, logout, get_user_model

# Django
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

# Local imports
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
)

# Logging
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class LoginRateThrottle(AnonRateThrottle):
    rate = '5/minute'  # Limit to 5 login attempts per minute

class RegistrationRateThrottle(AnonRateThrottle):
    rate = '20/hour'  # Increased from 3/hour to 20/hour

class CSRFTokenView(APIView):
    """Get CSRF token for the frontend."""
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({
            'csrfToken': get_token(request),
            'details': 'CSRF cookie set'
        })

class InitView(APIView):
    """Initialize session and CSRF token."""
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """Initialize session and return authentication status."""
        return Response({
            'isAuthenticated': bool(request.user and request.user.is_authenticated),
            'user': UserSerializer(request.user).data if request.user.is_authenticated else None,
            'csrfToken': get_token(request)
        })

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    throttle_classes = [RegistrationRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save(request)
            
            # Create auth token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Log the user in directly without using complete_signup
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'error': 'Registration failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        return serializer.save(self.request)

class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            # Create or get token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Perform login
            login(request, user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """User logout endpoint."""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            # Delete the auth token
            Token.objects.filter(user=request.user).delete()

            # Clear session
            request.session.flush()
            logout(request)
            
            response = Response({'message': 'Logout successful'})
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            return response
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'error': 'Logout failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDetailView(generics.RetrieveUpdateAPIView):
    """Get or update user details."""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint."""
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)
