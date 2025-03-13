from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from ..services import ProjectCreationService, ProjectManagementService, FileService
from .serializers import (
    ProjectSerializer, 
    ProjectCreateSerializer,
    FileSerializer,
    FileContentSerializer
)

class ProjectListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        service = ProjectManagementService(self.request.user)
        return service.get_active_projects()

class ProjectCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            project = serializer.save()  # Don't pass user here, handle it in serializer
            service = ProjectCreationService(request.user)
            service.create_project(project)
            
            response_serializer = ProjectSerializer(project)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            if project:
                project.delete()
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProjectDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer
    
    def get_object(self):
        service = ProjectManagementService(self.request.user)
        project = service.get_project(self.kwargs['pk'])
        if not project:
            raise NotFound('Project not found')
        return project

class ProjectDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        service = ProjectManagementService(request.user)
        project = service.get_project(self.kwargs['pk'])
        
        if not project:
            raise NotFound('Project not found')
            
        service.delete_project(project)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProjectFilesView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        service = FileService(self.request.user)
        return service.get_project_files(project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        service = FileService(self.request.user)
        return service.create_file(project_id, serializer.validated_data)

class ProjectFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileContentSerializer
    lookup_url_kwarg = 'file_path'

    def get_object(self):
        project_id = self.kwargs['project_id']
        file_path = self.kwargs['file_path']
        service = FileService(self.request.user)
        file_obj = service.get_file(project_id, file_path)
        if not file_obj:
            raise NotFound('File not found')
        return file_obj

    def perform_update(self, serializer):
        project_id = self.kwargs['project_id']
        file_path = self.kwargs['file_path']
        service = FileService(self.request.user)
        return service.update_file(project_id, file_path, serializer.validated_data)

class UndoActionView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id, action_id):
        service = ProjectManagementService(request.user)
        project = service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        service.undo_last_action(project)
        return Response(status=status.HTTP_200_OK)

class ProjectInitializeView(APIView):
    """
    Initialize a project with Django project structure.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        service = ProjectCreationService(request.user)
        management_service = ProjectManagementService(request.user)
        project = management_service.get_project(pk)
        
        if not project:
            raise NotFound('Project not found')
            
        # Check if project is already initialized
        if hasattr(project, 'is_initialized') and project.is_initialized:
            return Response({'detail': 'Project already initialized'}, status=status.HTTP_409_CONFLICT)
            
        # Initialize the project
        try:
            project = service.initialize_project(project)
            return Response({'success': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)