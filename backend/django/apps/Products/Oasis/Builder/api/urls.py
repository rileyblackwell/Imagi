"""
URL patterns for the Builder app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Builder workspace endpoints
    path('builder/<int:project_id>/preview/', views.PreviewView.as_view(), name='api-preview'),
    
    # File management endpoints
    path('builder/<int:project_id>/files/create/', views.CreateFileView.as_view(), name='api-create-file'),
    path('builder/<int:project_id>/files/<path:file_path>/content/', views.FileContentView.as_view(), name='api-file-content'),
    path('builder/<int:project_id>/files/<path:file_path>/delete/', views.DeleteFileView.as_view(), name='api-delete-file'),
    path('builder/<int:project_id>/files/<path:file_path>/undo/', views.FileUndoView.as_view(), name='api-file-undo'),
    
    # Directory management endpoints
    path('builder/<int:project_id>/directories/', views.DirectoryView.as_view(), name='api-directories'),
    
    # New endpoints for separate file type management
    path('builder/<int:project_id>/templates/', views.TemplateFilesView.as_view(), name='api-templates'),
    path('builder/<int:project_id>/static/', views.StaticFilesView.as_view(), name='api-static'),
    path('builder/<int:project_id>/details/', views.ProjectDetailsView.as_view(), name='api-project-details'),
    
    # Model selection endpoint
    path('models/', views.AIModelsView.as_view(), name='api-ai-models'),
]