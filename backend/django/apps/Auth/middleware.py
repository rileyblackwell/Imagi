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

class CORSErrorMiddleware:
    """
    Middleware to ensure CORS headers are added to all responses, especially error responses.
    This helps prevent CORS issues when the server returns an error response.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            
            # If it's an HTTP response (not a WebSocket or something else)
            if hasattr(response, '__setitem__'):  # Check if we can add headers (more generic)
                # Check if this is an API request (to avoid adding CORS headers to non-API responses)
                if request.path.startswith('/api/'):
                    # Add CORS headers to all responses regardless of status code
                    response['Access-Control-Allow-Origin'] = 'http://localhost:5174'
                    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
                    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
                    response['Access-Control-Allow-Credentials'] = 'true'
                    
                    # If this is an error response (4xx or 5xx), ensure CORS headers are present
                    if hasattr(response, 'status_code') and response.status_code >= 400:
                        # Log this for debugging
                        print(f"CORSErrorMiddleware: Adding CORS headers to error response with status {response.status_code}")
            
            return response
        except Exception as e:
            # If an exception occurs during processing, ensure we still return a response with CORS headers
            import traceback
            print(f"CORSErrorMiddleware caught an exception: {str(e)}")
            print(traceback.format_exc())
            
            # Create a new response for the exception with CORS headers
            from rest_framework.response import Response
            from rest_framework import status
            
            error_response = Response(
                {'error': 'An internal server error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            # Add CORS headers
            error_response['Access-Control-Allow-Origin'] = 'http://localhost:5174'
            error_response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
            error_response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            error_response['Access-Control-Allow-Credentials'] = 'true'
            
            return error_response

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