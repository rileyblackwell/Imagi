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
    Middleware to handle caching and security headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if isinstance(response, (HttpResponse, Response)):
            # Allow caching for static files
            if request.path.startswith('/static/'):
                response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            # For everything else, use standard cache control
            else:
                response['Cache-Control'] = 'private, no-cache'
            
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
                    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
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
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # For web pages, redirect to login
            return redirect(settings.LOGIN_URL + f'?next={request.path}')
        
        return self.get_response(request) 