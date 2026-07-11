"""
URL patterns for the Agents app API.
"""

from django.urls import path
from .views import (
    chat,
    agent,
    conversations_list_create,
    conversation_detail,
    conversation_messages,
)

urlpatterns = [
    path('chat/', chat, name='chat'),
    path('agent/', agent, name='agent'),
    path('conversations/', conversations_list_create, name='conversations_list_create'),
    path('conversations/<int:conversation_id>/', conversation_detail, name='conversation_detail'),
    path('conversations/<int:conversation_id>/messages/', conversation_messages, name='conversation_messages'),
]