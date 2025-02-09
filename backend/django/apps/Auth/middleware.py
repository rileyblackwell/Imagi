"""
Authentication and cache control middleware for Imagi.
"""

from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status

class CacheControlMiddleware:
    """Middleware to handle caching and security headers."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if isinstance(response, (HttpResponse, Response)):
            # Set security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            
            # Set cache control headers
            if request.path.startswith('/static/'):
                response['Cache-Control'] = 'public, max-age=31536000'
            else:
                response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                response['Pragma'] = 'no-cache'
        
        return response

class LoginRequiredMiddleware:
    """Middleware to enforce authentication for specific paths."""
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_paths = [
            '/auth/',
            '/api/auth/',
            '/',
            '/about/',
            '/contact/',
            '/privacy/',
            '/terms/',
            '/admin/',
            '/static/',
            '/__debug__/',
        ]

    def __call__(self, request):
        if request.method == 'OPTIONS' or any(request.path.startswith(path) for path in self.public_paths):
            return self.get_response(request)
            
        if not request.user.is_authenticated:
            if request.path.startswith('/api/'):
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            return redirect(settings.LOGIN_URL + f'?next={request.path}')
        
        return self.get_response(request)