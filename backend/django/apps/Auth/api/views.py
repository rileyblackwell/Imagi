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

# Django
from django.contrib.auth import login, logout, get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.middleware.csrf import get_token
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

# Local imports
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
)
from apps.Auth.utils import send_password_reset_email  # Fix the import path

# Logging
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class LoginRateThrottle(AnonRateThrottle):
    rate = '5/minute'  # Limit to 5 login attempts per minute

class RegistrationRateThrottle(AnonRateThrottle):
    rate = '3/hour'  # Limit to 3 registration attempts per hour

class CSRFTokenView(APIView):
    """Get CSRF token for the frontend."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            # Generate CSRF token
            token = get_token(request)
            
            # Create response
            response = Response({'csrfToken': token})
            
            # Add required headers
            response['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:5174')
            response['Access-Control-Allow-Credentials'] = 'true'
            
            return response
        except Exception as e:
            logger.error(f"Error generating CSRF token: {str(e)}")
            return Response(
                {'error': 'Failed to generate CSRF token'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
    """User registration endpoint."""
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    throttle_classes = [RegistrationRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Check for suspicious registration patterns
            ip = request.META.get('REMOTE_ADDR')
            registrations_key = f'registrations_from_ip_{ip}'
            registrations = cache.get(registrations_key, 0)
            if registrations > 10:  # More than 10 registrations from same IP in 24h
                logger.warning(f"Suspicious registration activity from IP: {ip}")
                return Response({
                    'error': 'Too many registration attempts'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            user = serializer.save()
            login(request, user)
            
            # Create token with expiration
            token = Token.objects.create(user=user)
            
            # Update registration count
            cache.set(registrations_key, registrations + 1, 86400)  # 24h expiry
            
            response = Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
            
            # Add security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            return response
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'error': 'Registration failed',
                'detail': str(e)
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

class PasswordResetRequestView(generics.GenericAPIView):
    """Request password reset email."""
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            success = send_password_reset_email(
                user=user,
                domain=request.get_host(),
                protocol='https' if request.is_secure() else 'http'
            )
            if not success:
                logger.error(f"Failed to send password reset email to {email}")
                
        except User.DoesNotExist:
            # Don't reveal whether a user exists
            pass
        
        # Always return success to prevent email enumeration
        return Response({
            'message': 'Password reset email has been sent if an account exists with this email.'
        })

class PasswordResetConfirmView(generics.GenericAPIView):
    """Confirm password reset and set new password."""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = User.objects.get(pk=uid)
            
            if not default_token_generator.check_token(user, serializer.validated_data['token']):
                return Response(
                    {'error': 'Invalid or expired reset token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'message': 'Password reset successful'})
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response(
                {'error': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(generics.GenericAPIView):
    """Change user password."""
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Invalid current password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Update session auth hash to prevent logout
            login(request, user)
            
            return Response({'message': 'Password changed successfully'})
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return Response(
                {'error': 'Failed to change password'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint."""
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)
