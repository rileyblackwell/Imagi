"""
Authentication and cache control middleware for Imagi.
"""

from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
import logging
import time

logger = logging.getLogger(__name__)
api_logger = logging.getLogger('django.request')

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
        # Log initialization at debug level instead of printing
        logger.debug("CORSErrorMiddleware initialized")

    def __call__(self, request):
        # Log incoming requests at debug level
        logger.debug(f"Processing request to {request.path}")
        
        # Store the request in thread-local storage for access in _add_cors_headers
        import threading
        setattr(threading.current_thread(), 'request', request)
        
        # For preflight OPTIONS requests, handle them separately for CORS
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response.status_code = 200
            # Add required CORS headers for preflight
            self._add_cors_headers(response)
            # Explicitly add headers needed for OPTIONS preflight
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRFToken, X-API-Client'
            response['Access-Control-Max-Age'] = '86400'  # 24 hours
            logger.debug("Handled OPTIONS preflight request")
            return response
            
        try:
            response = self.get_response(request)
            
            # If it's an HTTP response (not a WebSocket or something else)
            if hasattr(response, '__setitem__'):  # Check if we can add headers (more generic)
                # Add CORS headers to ALL responses, not just API responses
                # This ensures even redirects and other responses have proper CORS headers
                self._add_cors_headers(response)
                
                # Debug log responses
                if hasattr(response, 'status_code'):
                    logger.debug(f"Response for {request.path} has status {response.status_code}")
            
            return response
        except Exception as e:
            # If an exception occurs during processing, ensure we still return a response with CORS headers
            import traceback
            logger.error(f"Caught an exception: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Create a new response for the exception with CORS headers
            from rest_framework.response import Response
            from rest_framework import status
            
            error_response = Response(
                {'error': 'An internal server error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            # Add CORS headers
            self._add_cors_headers(error_response)
            
            return error_response
            
    def _add_cors_headers(self, response):
        """Helper method to add CORS headers to a response"""
        # Support multiple origins in development
        ALLOWED_ORIGINS = [
            'http://localhost:5174',
            'http://127.0.0.1:5174',
            'http://localhost:8000',
            'http://127.0.0.1:8000',
        ]
        
        # Get the origin from the request
        import threading
        request = getattr(threading.current_thread(), 'request', None)
        origin = request.headers.get('Origin') if request else None
        
        # Log the request accept header
        if request:
            logger.debug(f"Request Accept header: {request.headers.get('Accept')}")
            logger.debug(f"Response Content-Type: {response.get('Content-Type')}")
        
        # If the origin is in our allowed list, reflect it back
        # Otherwise default to the main development origin
        if origin and origin in ALLOWED_ORIGINS:
            response['Access-Control-Allow-Origin'] = origin
        else:
            # For simplicity and to fix the immediate issue, we'll allow the main development origin
            response['Access-Control-Allow-Origin'] = 'http://localhost:5174'
            
        # Add streaming-specific headers if this is a streaming response
        content_type = response.get('Content-Type', '')
        if 'text/event-stream' in content_type:
            logger.debug("Adding streaming-specific headers")
            response['Cache-Control'] = 'no-cache'
            response['Connection'] = 'keep-alive'
            response['X-Accel-Buffering'] = 'no'
        
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRFToken, X-API-Client, Accept'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'  # 24 hours
        
        # For debugging, log the headers we're setting
        logger.debug(f"Added CORS headers to response with origin: {response.get('Access-Control-Allow-Origin')}")
        
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

class APIRequestLoggingMiddleware:
    """Middleware to log API requests and responses"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip non-API paths
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Record the start time
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate processing time in milliseconds
        duration = (time.time() - start_time) * 1000
        
        # Log the request with method, path, status code, and duration
        api_logger.info(
            f"{request.method} {request.path} - {duration:.2f}ms",
            extra={
                'request': request,
                'status_code': response.status_code
            }
        )
        
        return response