from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('process-input/', views.process_input, name='process_input'),
    path('clear-conversation-history/', views.clear_conversation_history, name='clear_conversation_history'),
    path('undo-last-action/', views.undo_last_action, name='undo_last_action'),
]
