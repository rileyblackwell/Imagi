"""
URL patterns for the Builder app API.
"""

from django.urls import path

from .views import (
   AIModelsView, CreateFileView, DeleteFileView,
    DirectoryView, FileContentView, 
    PreviewView, ProjectDetailsView, 
    StaticFilesView, TemplateFilesView,
    VersionControlHistoryView, VersionControlResetView
)

urlpatterns = [
    # Builder workspace endpoints
    path('<int:project_id>/preview/', PreviewView.as_view(), name='api-preview'),
    
    # File management endpoints
    path('<int:project_id>/files/create/', CreateFileView.as_view(), name='api-create-file'),
    path('<int:project_id>/files/<path:file_path>/content/', FileContentView.as_view(), name='api-file-content'),
    path('<int:project_id>/files/<path:file_path>/delete/', DeleteFileView.as_view(), name='api-delete-file'),
    
    # Directory management endpoints
    path('<int:project_id>/directories/', DirectoryView.as_view(), name='api-directories'),
    
    # New endpoints for separate file type management
    path('<int:project_id>/templates/', TemplateFilesView.as_view(), name='api-templates'),
    path('<int:project_id>/static/', StaticFilesView.as_view(), name='api-static'),
    path('<int:project_id>/details/', ProjectDetailsView.as_view(), name='api-project-details'),
    
    # Model selection endpoint
    path('models/', AIModelsView.as_view(), name='api-ai-models'),
    
    # Version control endpoints
    path('<int:project_id>/versions/', VersionControlHistoryView.as_view(), name='api-version-history'),
    path('<int:project_id>/versions/reset/', VersionControlResetView.as_view(), name='api-version-reset'),
]