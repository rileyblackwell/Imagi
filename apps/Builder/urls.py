# builder/urls.py

from django.urls import path
from . import views

app_name = 'builder'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing_page'),
    
    # Project management
    path('create-project/', views.create_project, name='create_project'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    
    # Dynamic project URLs - Put these LAST
    path('oasis/<str:project_name>/', views.project_workspace, name='project_workspace'),
    path('oasis/<path:path>', views.serve_website_file, name='serve_website_file'),
]
