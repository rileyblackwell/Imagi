from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...services.model_definitions import get_available_models

class ModelDefinitionsView(APIView):
    """
    API view to provide centralized model definitions to frontend.
    """
    
    def get(self, request):
        """
        Get all available model definitions.
        
        Returns:
            Response: List of model definitions
        """
        models = get_available_models()
        return Response(models) 