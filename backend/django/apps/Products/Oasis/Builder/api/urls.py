"""
URL patterns for the Builder app API.
"""

from django.urls import path

from .views import (
    AIModelsView, CreateFileView, DeleteFileView,
    FileContentView, 
    PreviewView, 
    VersionControlHistoryView, VersionControlResetView,
    CreateAppView, CreatePageView, CreateComponentView
)

urlpatterns = [
    # Builder workspace endpoints
    path('<int:project_id>/preview/', PreviewView.as_view(), name='api-preview'),
    
    # File management endpoints
    path('<int:project_id>/files/create/', CreateFileView.as_view(), name='api-create-file'),
    path('<int:project_id>/files/<path:file_path>/content/', FileContentView.as_view(), name='api-file-content'),
    path('<int:project_id>/files/<path:file_path>/delete/', DeleteFileView.as_view(), name='api-delete-file'),
    
    # Directory and file-type endpoints removed (ProjectService deprecated)
    
    # Model selection endpoint
    path('models/', AIModelsView.as_view(), name='api-ai-models'),
    
    # Version control endpoints
    path('<int:project_id>/versions/', VersionControlHistoryView.as_view(), name='api-version-history'),
    path('<int:project_id>/versions/reset/', VersionControlResetView.as_view(), name='api-version-reset'),
    
    # App, Page, and Component creation endpoints
    path('<int:project_id>/apps/create/', CreateAppView.as_view(), name='api-create-app'),
    path('<int:project_id>/pages/create/', CreatePageView.as_view(), name='api-create-page'),
    path('<int:project_id>/components/create/', CreateComponentView.as_view(), name='api-create-component'),
]