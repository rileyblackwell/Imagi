"""
API views for the Auth app.
Handles all authentication-related API endpoints.
"""

# Django REST Framework
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework import serializers

# Django and Allauth
from django.contrib.auth import get_user_model

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
from .services import AuthenticationService, SessionService

# Logging
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class LoginRateThrottle(AnonRateThrottle):
    rate = '5/minute'  # Limit to 5 login attempts per minute

class RegistrationRateThrottle(AnonRateThrottle):
    rate = '20/hour'  # Increased from 3/hour to 20/hour

class CSRFTokenView(APIView):
    """Get CSRF token for the frontend - Railway optimized."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def options(self, request, *args, **kwargs):
        """Handle CORS preflight requests for CSRF token endpoint."""
        logger.info("🔧 CSRF OPTIONS preflight request received")
        logger.info(f"📍 Origin: {request.headers.get('Origin', 'No Origin')}")
        logger.info(f"🏠 Host: {request.headers.get('Host', 'No Host')}")
        return Response(status=200)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """
        Provide CSRF token for frontend authentication.
        Enhanced for Railway debugging.
        """
        try:
            # Enhanced logging for Railway debugging
            origin = request.headers.get('Origin', 'No Origin')
            host = request.headers.get('Host', 'No Host')
            x_forwarded_for = request.headers.get('X-Forwarded-For', 'No X-Forwarded-For')
            user_agent = request.headers.get('User-Agent', 'No User-Agent')[:100]
            
            logger.info("🔑 CSRF Token Request Details:")
            logger.info(f"  📍 Origin: {origin}")
            logger.info(f"  🏠 Host: {host}")
            logger.info(f"  🔄 X-Forwarded-For: {x_forwarded_for}")
            logger.info(f"  🖥️ User-Agent: {user_agent}")
            logger.info(f"  🌐 Method: {request.method}")
            logger.info(f"  📄 Path: {request.path}")
            
            csrf_token = get_token(request)
            remote_addr = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            
            logger.info(f"✅ CSRF token generated successfully from {remote_addr}")
            logger.info(f"🔑 Token length: {len(csrf_token) if csrf_token else 0}")
            
            # Check if we're in Railway environment
            from django.conf import settings
            if getattr(settings, 'IS_RAILWAY_PRODUCTION', False):
                logger.info("🚂 Running in Railway production environment")
            
            response_data = {
                'csrfToken': csrf_token,
                'details': 'CSRF cookie set',
                'environment': 'railway' if getattr(settings, 'IS_RAILWAY_PRODUCTION', False) else 'development',
                'debug_info': {
                    'origin': origin,
                    'host': host,
                    'remote_addr': remote_addr,
                    'token_length': len(csrf_token) if csrf_token else 0,
                }
            }
            
            logger.info(f"📤 Sending CSRF response: {response_data}")
            return Response(response_data, status=200)
            
        except Exception as e:
            logger.error(f"❌ Error generating CSRF token: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            return Response({
                'error': 'Unable to generate CSRF token',
                'detail': str(e),
                'environment': 'railway' if getattr(settings, 'IS_RAILWAY_PRODUCTION', False) else 'development',
            }, status=500)

class InitView(APIView):
    """Initialize session and CSRF token."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """Initialize session and return authentication status."""
        session_data = SessionService.get_session_data(request)
        return Response({
            'isAuthenticated': session_data['isAuthenticated'],
            'user': UserSerializer(session_data['user']).data if session_data['isAuthenticated'] else None,
            'csrfToken': get_token(request)
        })

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    throttle_classes = [RegistrationRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        Handle user registration with enhanced error handling for CSRF and proxy issues.
        """
        # Log registration attempt for debugging
        logger.info(f"Registration attempt from {request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user, token = AuthenticationService.register_user(request, serializer)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            # Get specific validation errors
            error_msg = 'Registration failed'
            error_details = {}
            
            if hasattr(e, 'detail'):
                if isinstance(e.detail, dict):
                    for field, errors in e.detail.items():
                        if isinstance(errors, list) and errors:
                            error_details[field] = errors[0]
                        else:
                            error_details[field] = errors
                elif isinstance(e.detail, list) and e.detail:
                    error_msg = str(e.detail[0])
                else:
                    error_msg = str(e.detail)
            
            logger.error(f"Registration validation error: {error_details or error_msg}")
            return Response({
                'error': error_msg,
                'detail': error_details or error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'error': 'Registration failed',
                'detail': 'An unexpected error occurred. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token = AuthenticationService.login_user(request, user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        except serializers.ValidationError as e:
            # Extract validation error details
            error_msg = 'Invalid login credentials'
            error_details = {}
            
            if hasattr(e, 'detail'):
                if isinstance(e.detail, dict):
                    if 'error' in e.detail:
                        error_msg = e.detail['error']
                    
                    for field, errors in e.detail.items():
                        if isinstance(errors, list) and errors:
                            error_details[field] = errors[0]
                        else:
                            error_details[field] = errors
                            
                elif isinstance(e.detail, list) and e.detail:
                    error_msg = str(e.detail[0])
                else:
                    error_msg = str(e.detail)
            
            logger.error(f"Login validation error: {error_details or error_msg}")
            return Response({
                'error': error_msg,
                'detail': error_details
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({
                'error': 'Login failed',
                'detail': 'An unexpected error occurred. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """User logout endpoint."""
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            AuthenticationService.logout_user(request)
            response = Response({'message': 'Logout successful'})
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            return response
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'error': 'Logout failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserView(generics.RetrieveUpdateAPIView):
    """Get or update user details."""
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

class HealthCheckView(APIView):
    """Health check endpoint for Railway debugging."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Health check endpoint with Railway environment details."""
        from django.conf import settings
        import os
        
        # Enhanced health check for Railway debugging
        origin = request.headers.get('Origin', 'No Origin')
        host = request.headers.get('Host', 'No Host')
        x_forwarded_for = request.headers.get('X-Forwarded-For', 'No X-Forwarded-For')
        
        logger.info("🏥 Health check requested:")
        logger.info(f"  📍 Origin: {origin}")
        logger.info(f"  🏠 Host: {host}")
        logger.info(f"  🔄 X-Forwarded-For: {x_forwarded_for}")
        
        health_data = {
            'status': 'healthy',
            'message': 'Auth API is running',
            'timestamp': str(__import__('datetime').datetime.now()),
            'environment': 'railway' if getattr(settings, 'IS_RAILWAY_PRODUCTION', False) else 'development',
            'debug_info': {
                'origin': origin,
                'host': host,
                'remote_addr': x_forwarded_for,
                'django_version': __import__('django').get_version(),
                'python_version': __import__('sys').version.split()[0],
                'cors_allowed_origins': getattr(settings, 'CORS_ALLOWED_ORIGINS', []),
                'csrf_trusted_origins': getattr(settings, 'CSRF_TRUSTED_ORIGINS', []),
                'database_engine': settings.DATABASES['default']['ENGINE'],
                'railway_environment': os.environ.get('RAILWAY_ENVIRONMENT', 'not-set'),
                'allowed_hosts': settings.ALLOWED_HOSTS,
            }
        }
        
        logger.info(f"📤 Health check response: {health_data}")
        return Response(health_data, status=200)
