"""
Delete the signed-in account, from inside an app.

Apple requires an app that lets people register to let them delete the
account from inside it, so the iOS app's account screen calls this. It lives
here rather than in apps.Auth because Auth's API is copied verbatim into every
generated app (the prebuilt sign-in template), and deleting an Imagi account
means deleting its projects too.

Served at /api/v1/auth/account/delete/ (see api/urls.py).
"""

from django.contrib.auth import logout
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.Auth.api.throttles import LoginRateThrottle

from ..services.account_deletion import delete_account


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([LoginRateThrottle])
def delete_account_view(request):
    """Delete the account, its projects and their files, for good.

    The password is asked for again so a borrowed, still-signed-in phone
    can't erase someone's work; the sign-in throttle bounds guessing it.
    """
    password = request.data.get('password') or ''
    if not password or not request.user.check_password(password):
        return Response(
            {'detail': 'That password is not right.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = request.user
    logout(request)
    delete_account(user)
    return Response(status=status.HTTP_204_NO_CONTENT)
