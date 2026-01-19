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
    Updated for Railway internal networking.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Log initialization with environment info
        logger.info("CORSErrorMiddleware initialized for Railway environment")
        from django.conf import settings
        if getattr(settings, 'IS_RAILWAY_PRODUCTION', False):
            logger.info("🚂 Running in Railway production environment")

    def __call__(self, request):
        # Store the request in thread-local storage for access in _add_cors_headers
        import threading
        setattr(threading.current_thread(), 'request', request)
        
        # For preflight OPTIONS requests, handle them separately for CORS
        if request.method == 'OPTIONS':
            logger.debug("🔧 Handling OPTIONS preflight request")
            response = HttpResponse()
            response.status_code = 200
            # Add required CORS headers for preflight
            self._add_cors_headers(response)
            # Explicitly add headers needed for OPTIONS preflight
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRFToken, X-API-Client, Accept'
            response['Access-Control-Max-Age'] = '86400'  # 24 hours
            return response
            
        try:
            response = self.get_response(request)
            
            # If it's an HTTP response (not a WebSocket or something else)
            if hasattr(response, '__setitem__'):  # Check if we can add headers (more generic)
                # Add CORS headers to ALL responses, not just API responses
                # This ensures even redirects and other responses have proper CORS headers
                self._add_cors_headers(response)
            
            return response
        except Exception as e:
            # If an exception occurs during processing, ensure we still return a response with CORS headers
            import traceback
            logger.error(f"💥 Caught an exception processing {request.path}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Create a new response for the exception with CORS headers
            from rest_framework.response import Response
            from rest_framework import status
            
            error_response = Response(
                {
                    'error': 'An internal server error occurred',
                    'detail': str(e),
                    'path': request.path,
                    'method': request.method
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            # Add CORS headers
            self._add_cors_headers(error_response)
            
            return error_response
            
    def _add_cors_headers(self, response):
        """Helper method to add CORS headers to a response - Railway optimized"""
        # Get the origin from the request
        import threading
        request = getattr(threading.current_thread(), 'request', None)
        origin = request.headers.get('Origin') if request else None
        
        from django.conf import settings
        
        # Railway-specific origin handling
        allowed_origins = [
            'http://localhost:5174',
            'http://127.0.0.1:5174',
            'https://imagi.up.railway.app',
            'https://frontend.railway.internal',
            'http://frontend.railway.internal',
            'https://frontend.railway.internal:80',
            'http://frontend.railway.internal:80',
        ]
        
        # Set Access-Control-Allow-Origin header
        if getattr(settings, 'IS_RAILWAY_PRODUCTION', False):
            # In Railway production, be more permissive to debug connection issues
            if origin:
                response['Access-Control-Allow-Origin'] = origin
            else:
                # Fallback for requests without Origin header (like direct API calls)
                response['Access-Control-Allow-Origin'] = '*'
        else:
            # Development environment
            if origin and origin in allowed_origins:
                response['Access-Control-Allow-Origin'] = origin
            else:
                response['Access-Control-Allow-Origin'] = 'http://localhost:5174'
            
        # Add streaming-specific headers if this is a streaming response
        content_type = response.get('Content-Type', '')
        if 'text/event-stream' in content_type:
            response['Cache-Control'] = 'no-cache'
            response['Connection'] = 'keep-alive'
            response['X-Accel-Buffering'] = 'no'
        
        # Standard CORS headers
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRFToken, X-API-Client, Accept'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'  # 24 hours
        
        return response

class LoginRequiredMiddleware:
    """Middleware to enforce authentication for specific paths."""
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_paths = [
            '/auth/',
            '/api/auth/',
            '/api/v1/auth/',  # Allow unauthenticated access to auth endpoints (login, register, CSRF)
            '/api/v1/health/',  # Allow health check endpoint
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


class RailwayDebugMiddleware:
    """Middleware to debug Railway internal network connections"""
    def __init__(self, get_response):
        self.get_response = get_response
        from django.conf import settings
        self.is_railway = getattr(settings, 'IS_RAILWAY_PRODUCTION', False)

    def __call__(self, request):
        if self.is_railway and request.path.startswith('/api/'):
            # Log all relevant headers for Railway debugging
            logger.info("🚂 Railway Request Debug:")
            logger.info(f"  Path: {request.path}")
            logger.info(f"  Method: {request.method}")
            logger.info(f"  Host: {request.headers.get('Host', 'N/A')}")
            logger.info(f"  X-Forwarded-Proto: {request.headers.get('X-Forwarded-Proto', 'N/A')}")
            logger.info(f"  X-Forwarded-Host: {request.headers.get('X-Forwarded-Host', 'N/A')}")
            logger.info(f"  X-Forwarded-For: {request.headers.get('X-Forwarded-For', 'N/A')}")
            logger.info(f"  X-Real-IP: {request.headers.get('X-Real-IP', 'N/A')}")
            logger.info(f"  X-Frontend-Service: {request.headers.get('X-Frontend-Service', 'N/A')}")
            logger.info(f"  Origin: {request.headers.get('Origin', 'N/A')}")
            logger.info(f"  Remote Addr: {request.META.get('REMOTE_ADDR', 'N/A')}")
        
        return self.get_response(request)