from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring and Railway health checks."""
    try:
        User = get_user_model()
        User.objects.exists()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'

    return Response({
        'status': 'healthy',
        'service': 'imagi-backend',
        'database': db_status,
    })
