"""
Authentication and cache control middleware for Imagi.
"""

from django.shortcuts import redirect
from django.urls import resolve
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status

class CacheControlMiddleware:
    """
    Middleware to handle caching, security headers, and bfcache prevention.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if isinstance(response, (HttpResponse, Response)):
            # Set cache-control based on path
            if request.path.startswith('/static/'):
                # Allow caching for static files
                response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            else:
                # Prevent bfcache while preserving auth state
                response['Cache-Control'] = 'private, no-store, no-cache, must-revalidate, proxy-revalidate'
                response['Pragma'] = 'no-cache'
                # Explicitly prevent bfcache
                response['Cache-Control'] = f"{response.get('Cache-Control', '')}, max-age=0, s-maxage=0"
            
            # Add security headers for non-static paths
            if not request.path.startswith('/static/'):
                # Headers to prevent bfcache and extension issues
                response['Service-Worker-Allowed'] = '/'
                # Allow extension communication
                response['Content-Security-Policy'] = (
                    "frame-ancestors 'self'; "
                    "connect-src * 'self' blob: data:; "
                    "default-src * 'self' blob: data:; "
                    "script-src * 'self' 'unsafe-inline' 'unsafe-eval' blob: data:; "
                    "style-src * 'self' 'unsafe-inline' blob: data:; "
                    "img-src * 'self' blob: data:; "
                    "font-src * 'self' blob: data:;"
                )
                # Additional bfcache prevention
                response['Vary'] = '*'
                response['Expires'] = '0'
                
                # Prevent FLoC cohorts
                response['Permissions-Policy'] = (
                    'interest-cohort=(), '
                    'sync-xhr=(self), '
                    'document-domain=()'
                )
                
                response['X-Frame-Options'] = 'SAMEORIGIN'
            
            # Basic security headers
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Handle CORS for API requests
            if request.path.startswith('/api/'):
                origin = request.headers.get('Origin')
                if origin and settings.DEBUG:
                    response['Access-Control-Allow-Origin'] = origin
                    response['Access-Control-Allow-Credentials'] = 'true'
                    
                    # Handle preflight requests
                    if request.method == 'OPTIONS':
                        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                        response['Access-Control-Allow-Headers'] = (
                            'Content-Type, Authorization, X-CSRFToken, '
                            'X-Requested-With, Accept, Origin, Cache-Control'
                        )
                        response['Access-Control-Max-Age'] = '86400'  # 24 hours
        
        return response

class LoginRequiredMiddleware:
    """
    Middleware to enforce authentication for specific paths.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require authentication
        self.public_paths = [
            '/auth/login/',
            '/auth/register/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/',
            '/auth/reset/done/',
            '/',  # Landing page
            '/about/',
            '/contact/',
            '/privacy/',
            '/terms/',
            '/cookie-policy/',
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/csrf/',
            '/api/auth/user/',  # Allow checking user auth status
            '/api/auth/password/reset/',
            '/api/auth/password/reset/confirm/',
            '/favicon.ico',
            '/admin/',  # Django admin
            '/static/',  # Static files
            '/__debug__/',  # Django debug toolbar
        ]

    def is_public_path(self, path):
        """Check if the path is public."""
        return any(path.startswith(public_path) for public_path in self.public_paths)

    def __call__(self, request):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return self.get_response(request)
            
        # Skip authentication for public paths
        if self.is_public_path(request.path):
            return self.get_response(request)
            
        # Require authentication for all other paths
        if not request.user.is_authenticated:
            # If it's an API request, return 401
            if request.path.startswith('/api/'):
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED,
                    headers={
                        'Access-Control-Allow-Origin': request.headers.get('Origin'),
                        'Access-Control-Allow-Credentials': 'true'
                    }
                )
            
            # For web pages, redirect to login
            return redirect(settings.LOGIN_URL + f'?next={request.path}')
        
        return self.get_response(request) 