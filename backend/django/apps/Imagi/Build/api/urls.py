"""
URL patterns for the Build app API.

The Build app owns two public URL prefixes, kept from the former Builder
and Agents sub-apps so existing API paths stay stable:

    /api/v1/builder/...  - builder workspace endpoints
    /api/v1/agents/...   - agent chat / conversation endpoints
"""

from django.urls import include, path

from .views import (
    # Builder workspace views
    AIModelsView, CreateFileView, DeleteFileView,
    FileContentView,
    PreviewView,
    VersionControlHistoryView, VersionControlResetView,
    CreateAppView,
    ProjectDirectoriesView,
    ProjectLayoutView,
    CreateDirectoryView,
    DeleteDirectoryView,
    # Agent views
    chat,
    agent,
    conversations_list_create,
    conversation_detail,
    conversation_messages,
)

builder_patterns = [
    # Builder workspace endpoints
    path('<int:project_id>/directories/', ProjectDirectoriesView.as_view(), name='api-project-directories'),
    path('<int:project_id>/directories/create/', CreateDirectoryView.as_view(), name='api-create-directory'),
    path('<int:project_id>/directories/<path:dir_path>/delete/', DeleteDirectoryView.as_view(), name='api-delete-directory'),
    path('<int:project_id>/preview/', PreviewView.as_view(), name='api-preview'),

    # File management endpoints
    path('<int:project_id>/files/create/', CreateFileView.as_view(), name='api-create-file'),
    path('<int:project_id>/files/<path:file_path>/content/', FileContentView.as_view(), name='api-file-content'),
    path('<int:project_id>/files/<path:file_path>/delete/', DeleteFileView.as_view(), name='api-delete-file'),

    # Model selection endpoint
    path('models/', AIModelsView.as_view(), name='api-ai-models'),

    # Version control endpoints
    path('<int:project_id>/versions/', VersionControlHistoryView.as_view(), name='api-version-history'),
    path('<int:project_id>/versions/reset/', VersionControlResetView.as_view(), name='api-version-reset'),

    # App creation endpoint
    path('<int:project_id>/apps/create/', CreateAppView.as_view(), name='api-create-app'),

    # Layout management endpoint
    path('<int:project_id>/layout/', ProjectLayoutView.as_view(), name='api-project-layout'),
]

agents_patterns = [
    path('chat/', chat, name='chat'),
    path('agent/', agent, name='agent'),
    path('conversations/', conversations_list_create, name='conversations_list_create'),
    path('conversations/<int:conversation_id>/', conversation_detail, name='conversation_detail'),
    path('conversations/<int:conversation_id>/messages/', conversation_messages, name='conversation_messages'),
]

urlpatterns = [
    path('builder/', include(builder_patterns)),
    path('agents/', include(agents_patterns)),
]
