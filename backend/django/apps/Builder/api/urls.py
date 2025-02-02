"""
URL patterns for the Builder app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Project endpoints
    path('projects/', views.ProjectListCreateView.as_view(), name='api-project-list'),
    path('projects/<str:project_name>/', views.ProjectDetailView.as_view(), name='api-project-detail'),
    
    # Conversation endpoints
    path('projects/<str:project_name>/conversations/', views.ConversationListView.as_view(), name='api-conversation-list'),
    
    # Page endpoints
    path('conversations/<int:conversation_id>/pages/<str:filename>/', views.PageView.as_view(), name='api-page-detail'),
    
    # Builder functionality endpoints
    path('process-input/', views.process_input, name='api-process-input'),
    path('undo/', views.undo_last_action, name='api-undo-action'),
    path('clear-conversation/', views.clear_conversation, name='api-clear-conversation'),
] 