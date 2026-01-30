"""
URL patterns for the Agents app API.
"""

from django.urls import path
from .views import build_component, build_view, chat

urlpatterns = [
    path('build/component/', build_component, name='build_component'),
    path('build/view/', build_view, name='build_view'),
    path('chat/', chat, name='chat'),
]