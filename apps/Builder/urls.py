# builder/urls.py

from django.urls import path
from . import views

app_name = 'builder'  # Define a namespace for the app

urlpatterns = [
    path('', views.index, name='index'),
    path('process-input/', views.process_input, name='process_input'),
    path('undo-last-action/', views.undo_last_action_view, name='undo_last_action'),  # Corrected view name here
    path('clear-conversation-history/', views.clear_conversation_history, name='clear_conversation_history'),
]
