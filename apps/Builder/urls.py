# builder/urls.py

from django.urls import path
from . import views

app_name = 'builder'  # Define a namespace for the app

urlpatterns = [
    # Main views
    path('', views.index, name='index'),
    path('process-input/', views.process_input, name='process_input'),
    
    # Conversation management
    path('get-conversation-history/', views.get_conversation_history, name='get_conversation_history'),
    path('clear-conversation-history/', views.clear_conversation_history, name='clear_conversation_history'),
    path('undo-last-action/', views.undo_last_action_view, name='undo_last_action'),
    
    # File management
    path('get-page/', views.get_page, name='get_page'),
    path('website/<path:path>', views.serve_website_file, name='serve_website_file'),
]
