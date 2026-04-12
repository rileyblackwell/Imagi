"""
URL patterns for the Agents app API.
"""

from django.urls import path
from .views import chat, agent

urlpatterns = [
    path('chat/', chat, name='chat'),
    path('agent/', agent, name='agent'),
]