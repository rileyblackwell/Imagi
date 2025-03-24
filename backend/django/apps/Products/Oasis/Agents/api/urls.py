"""
URL patterns for the Agents app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('build/template/', views.build_template, name='build_template'),

    path('build/stylesheet/', views.build_stylesheet, name='build_stylesheet'),

    path('build/application/', views.build_application, name='build_application'),

    path('chat/', views.chat, name='chat'),
] 