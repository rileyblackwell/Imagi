"""
URL patterns for the Agents app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('agents/build/template/', views.build_template, name='build_template'),

    path('agents/build/stylesheet/', views.build_stylesheet, name='build_stylesheet'),

    path('agents/chat/', views.chat, name='chat'),
] 