"""
URL patterns for the Agents app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Conversation management endpoints
    path('conversations/', views.ConversationListCreateView.as_view(), name='api-conversation-list'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='api-conversation-detail'),
    
    # Message handling endpoints
    path('send-message/', views.send_message, name='api-send-message'),
    path('clear-conversation/', views.clear_conversation, name='api-clear-conversation'),
    
    # System prompt endpoints
    path('update-system-prompt/', views.update_system_prompt, name='api-update-system-prompt'),
] 