from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .services import ProjectGenerationService
from .models import UserProject, Project
from .serializers import UserProjectSerializer, ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active_projects(self, request):
        projects = self.get_queryset()
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)