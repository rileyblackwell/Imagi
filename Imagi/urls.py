from django.contrib import admin
from django.urls import path
from apps.Builder import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface
    path('', views.index, name='index'),  # Home page
    path('process-input/', views.process_input, name='process_input'),  # Handle user input processing
    path('clear-conversation-history/', views.clear_conversation_history, name='clear_conversation_history'),  # Clear session history
    path('undo-last-action/', views.undo_last_action, name='undo_last_action'),  # Add this line for Undo functionality
]