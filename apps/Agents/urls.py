from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    # Conversation management
    path('conversations/', views.list_conversations, name='list_conversations'),
    path('conversations/create/', views.create_conversation, name='create_conversation'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversations/<int:conversation_id>/send/', views.send_message, name='send_message'),
]
