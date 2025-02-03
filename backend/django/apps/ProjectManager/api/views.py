from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import Project
from .serializers import ProjectSerializer, ProjectCreateSerializer
from ..services.project_service import ProjectGenerationService

class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        # First create the project record
        project = serializer.save()
        
        try:
            # Then generate the actual project files
            service = ProjectGenerationService(self.request.user)
            service.create_project(project.name)
        except Exception as e:
            # If project generation fails, delete the project record and raise the error
            project.delete()
            raise e

    @action(detail=False, methods=['get'])
    def active_projects(self, request):
        projects = self.get_queryset()
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        try:
            # Delete project files first
            service = ProjectGenerationService(request.user)
            service.delete_project(project.name)
            # Then delete the project record
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 