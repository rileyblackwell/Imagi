"""
URL patterns for the Builder app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Project endpoints
    path('projects/', views.ProjectListCreateView.as_view(), name='api-project-list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='api-project-detail'),
    
    # Builder workspace endpoints
    path('projects/<int:project_id>/files/', views.ProjectFilesView.as_view(), name='api-project-files'),
    path('projects/<int:project_id>/generate/', views.GenerateCodeView.as_view(), name='api-generate-code'),
    path('projects/<int:project_id>/undo/', views.UndoActionView.as_view(), name='api-undo-action'),
    
    # Model selection endpoint
    path('models/', views.AIModelsView.as_view(), name='api-ai-models'),
    
    # File management endpoints
    path('projects/<int:project_id>/files/<path:file_path>/', views.FileDetailView.as_view(), name='api-file-detail'),
    path('projects/<int:project_id>/files/<path:file_path>/content/', views.FileContentView.as_view(), name='api-file-content'),
] 