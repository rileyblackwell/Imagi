from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from ..services import ProjectCreationService, ProjectManagementService
from .serializers import (
    ProjectSerializer, 
    ProjectCreateSerializer
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
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Initialize request received for project {pk}")
        
        service = ProjectCreationService(request.user)
        management_service = ProjectManagementService(request.user)
        project = management_service.get_project(pk)
        
        if not project:
            logger.error(f"Project not found: {pk}")
            raise NotFound('Project not found')
        
        logger.info(f"Found project {project.name} (ID: {project.id})")
        
        # Check if project is already initialized
        if project.is_initialized:
            logger.info(f"Project {project.name} (ID: {project.id}) is already initialized")
            return Response({
                'success': True, 
                'already_initialized': True,
                'project_id': project.id,
                'name': project.name,
                'is_initialized': project.is_initialized
            }, status=status.HTTP_200_OK)
            
        # Add a check for partially initialized projects
        # Make sure the path exists
        if not hasattr(project, 'project_path') or not project.project_path:
            logger.error(f"Project {project.name} (ID: {project.id}) has no project_path set")
            
            # Try to assign a default path
            try:
                from django.conf import settings
                import os
                from datetime import datetime
                
                # Create a default path based on user ID and project name
                sanitized_name = ''.join(c if c.isalnum() else '_' for c in project.name)
                if not sanitized_name[0].isalpha():
                    sanitized_name = 'project_' + sanitized_name
                    
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                unique_name = f"{sanitized_name}_{timestamp}"
                
                base_directory = os.path.join(settings.PROJECTS_ROOT, str(request.user.id))
                os.makedirs(base_directory, exist_ok=True)
                
                project_path = os.path.join(base_directory, unique_name)
                
                # Set and save the path
                project.project_path = project_path
                project.save()
                logger.info(f"Assigned default project path: {project_path}")
            except Exception as path_err:
                logger.error(f"Failed to assign default project path: {str(path_err)}")
                return Response({
                    'error': f"Project has no valid path: {str(path_err)}",
                    'project_id': project.id,
                    'name': project.name
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Initialize the project
        try:
            logger.info(f"Starting initialization for project {project.name} (ID: {project.id})")
            project = service.initialize_project(project)
            logger.info(f"Project {project.name} (ID: {project.id}) successfully initialized")
            
            return Response({
                'success': True,
                'project_id': project.id,
                'name': project.name,
                'is_initialized': project.is_initialized
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to initialize project {project.name} (ID: {project.id}): {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            
            # Check if project exists but initialization failed
            if project and hasattr(project, 'id'):
                # Don't mark the project as failed - just return the error
                return Response({
                    'error': str(e),
                    'project_id': project.id,
                    'name': project.name
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProjectStatusView(APIView):
    """
    Check the status of a project.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        management_service = ProjectManagementService(request.user)
        project = management_service.get_project(pk)
        
        if not project:
            raise NotFound('Project not found')
            
        return Response({
            'id': project.id,
            'name': project.name,
            'is_initialized': project.is_initialized,
            'generation_status': project.generation_status,
            'project_path': project.project_path,
            'created_at': project.created_at,
            'updated_at': project.updated_at
        }, status=status.HTTP_200_OK)