import hashlib

from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer
from .throttles import LoginRateThrottle, RegisterRateThrottle

# Per-account failure counter, on top of the per-IP throttle: it bounds a
# distributed guessing run against one account, which a per-IP limit cannot
# see. Only failures count and a success clears the counter, so an attacker
# cannot lock a victim out by failing on their behalf — the window simply
# expires.
FAILED_LOGIN_LIMIT = 10
FAILED_LOGIN_WINDOW_SECONDS = 15 * 60


def _failed_login_key(username):
    """Cache key for one account's recent failures.

    The username is hashed so credentials never appear in cache keys (which
    reach logs and cache-inspection tooling).
    """
    digest = hashlib.sha256(username.strip().lower().encode('utf-8')).hexdigest()
    return f"auth:failed-login:{digest}"


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_view(request):
    """Plant the csrftoken cookie for the Vue SPA."""
    get_token(request)
    return Response({'detail': 'CSRF cookie set'})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
@csrf_protect
def signin_view(request):
    """Sign in.

    ``csrf_protect`` restores the check DRF's ``@api_view`` removes: it wraps
    the view in ``csrf_exempt``, and DRF's own check lives in
    ``SessionAuthentication``, which skips it for an anonymous request — so
    without this an attacker's page could sign a visitor's browser into an
    account the attacker controls. The SPA already fetches the token from
    ``/csrf/`` and sends ``X-CSRFToken`` on this call.
    """
    username = (request.data.get('username') or '').strip()
    password = request.data.get('password') or ''
    if not username or not password:
        return Response(
            {'detail': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    failure_key = _failed_login_key(username)
    if (cache.get(failure_key) or 0) >= FAILED_LOGIN_LIMIT:
        return Response(
            {'detail': 'Too many failed sign-in attempts. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        # set() rather than incr() so the first failure creates the key with
        # its expiry; the window slides forward on each failure.
        cache.set(
            failure_key,
            (cache.get(failure_key) or 0) + 1,
            FAILED_LOGIN_WINDOW_SECONDS,
        )
        return Response(
            {'detail': 'Invalid username or password.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    cache.delete(failure_key)
    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterRateThrottle])
@csrf_protect
def register_view(request):
    """Register an account. See signin_view for why csrf_protect is here."""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {'token': token.key, 'user': UserSerializer(user).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except (Token.DoesNotExist, AttributeError):
        pass
    logout(request)
    return Response({'detail': 'Successfully logged out.'})


@api_view(['GET'])
@permission_classes([AllowAny])
def init_view(request):
    if request.user.is_authenticated:
        return Response({
            'isAuthenticated': True,
            'user': UserSerializer(request.user).data,
        })
    return Response({'isAuthenticated': False, 'user': None})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def user_update_view(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)
