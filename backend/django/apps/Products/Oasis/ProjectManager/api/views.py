from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .services import ProjectService, FileService
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
        service = ProjectService(self.request.user)
        return service.get_active_projects()

class ProjectCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            project = serializer.save()  # Don't pass user here, handle it in serializer
            service = ProjectService(request.user)
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
        service = ProjectService(self.request.user)
        project = service.get_project(self.kwargs['pk'])
        if not project:
            raise NotFound('Project not found')
        return project

class ProjectDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        service = ProjectService(request.user)
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

class ComponentTreeView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        service = ProjectService(request.user)
        project = service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        component_tree = service.get_component_tree(project)
        return Response(component_tree)

class UndoActionView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id, action_id):
        service = ProjectService(request.user)
        project = service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        service.undo_action(project, action_id)
        return Response(status=status.HTTP_200_OK)