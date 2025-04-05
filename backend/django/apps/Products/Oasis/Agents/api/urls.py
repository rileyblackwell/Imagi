"""
URL patterns for the Agents app API.
"""

from django.urls import path
from .views import build_template, build_stylesheet, chat

urlpatterns = [
    path('build/template/', build_template, name='build_template'),
    path('build/stylesheet/', build_stylesheet, name='build_stylesheet'),
    path('chat/', chat, name='chat'),
] 