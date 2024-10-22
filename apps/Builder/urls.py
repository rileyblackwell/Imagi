from django.urls import path
from . import views

app_name = 'builder'  # Add this line to define a namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('process-input/', views.process_input, name='process_input'),
    path('undo-last-action/', views.undo_last_action, name='undo_last_action'),
    path('clear-conversation-history/', views.clear_conversation_history, name='clear_conversation_history'),
]
