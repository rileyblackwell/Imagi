"""
URL patterns for the Builder app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Builder workspace endpoints
    path('builder/<int:project_id>/undo/', views.UndoActionView.as_view(), name='api-undo-action'),
    path('builder/<int:project_id>/preview/', views.PreviewView.as_view(), name='api-preview'),
    
    # File management endpoints
    path('builder/<int:project_id>/files/', views.ProjectFilesView.as_view(), name='api-project-files'),
    path('builder/<int:project_id>/files/<path:file_path>/', views.FileDetailView.as_view(), name='api-file-detail'),
    path('builder/<int:project_id>/files/<path:file_path>/content/', views.FileContentView.as_view(), name='api-file-content'),

    # Model selection endpoint
    path('models/', views.AIModelsView.as_view(), name='api-ai-models'),
]