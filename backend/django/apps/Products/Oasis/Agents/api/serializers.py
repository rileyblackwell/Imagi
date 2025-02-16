"""
Serializers for the Agents app API.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import AgentConversation, SystemPrompt, AgentMessage

User = get_user_model()

class AgentMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentMessage
        fields = ('id', 'conversation', 'role', 'content', 'created_at')
        read_only_fields = ('id', 'created_at')

class SystemPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPrompt
        fields = ('id', 'conversation', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class AgentConversationSerializer(serializers.ModelSerializer):
    messages = AgentMessageSerializer(many=True, read_only=True)
    system_prompt = SystemPromptSerializer(read_only=True)
    
    class Meta:
        model = AgentConversation
        fields = ('id', 'user', 'model_name', 'created_at', 'messages', 'system_prompt')
        read_only_fields = ('id', 'created_at')

class ConversationHistorySerializer(serializers.ModelSerializer):
    """Serializer for retrieving conversation history with all messages."""
    messages = AgentMessageSerializer(many=True, read_only=True)
    system_prompt = SystemPromptSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentConversation
        fields = ('id', 'user', 'model_name', 'created_at', 'messages', 'system_prompt')
        read_only_fields = fields
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email
        } 