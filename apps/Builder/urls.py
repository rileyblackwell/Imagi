# builder/urls.py

from django.urls import path
from . import views

app_name = 'builder'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing_page'),
    
    # API endpoints - Put these BEFORE the catch-all patterns
    path('get-page/', views.get_page, name='get_page'),
    path('process-input/', views.process_input, name='process_input'),
    path('get-conversation-history/', views.get_conversation_history, name='get_conversation_history'),
    path('clear-conversation-history/', views.clear_conversation_history, name='clear_conversation_history'),
    path('undo-last-action/', views.undo_last_action_view, name='undo_last_action'),
    path('chat/', views.process_chat, name='process_chat'),
    
    # Project management
    path('create-project/', views.create_project, name='create_project'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    
    # Dynamic project URLs - Put these LAST
    path('oasis/<str:project_name>/', views.project_workspace, name='project_workspace'),
    path('oasis/<path:path>', views.serve_website_file, name='serve_website_file'),
]
