"""
API URL Configuration for the ProjectManager app.
"""

from django.urls import path
from . import views

app_name = 'project_manager'

urlpatterns = [
    # Project Management
    path('projects/', views.ProjectListView.as_view(), name='project-list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('projects/<int:pk>/initialize/', views.ProjectInitializeView.as_view(), name='project-initialize'),
    
    # Component Management
    path('projects/<int:project_id>/components/', views.ComponentTreeView.as_view(), name='component-tree'),
]
    