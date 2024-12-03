from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import ProjectGenerationService
from .models import UserProject
from .serializers import UserProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = UserProjectSerializer
    
    def get_queryset(self):
        return UserProject.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        service = ProjectGenerationService(self.request.user)
        project = service.create_project(serializer.validated_data['name'])
        serializer.instance = project