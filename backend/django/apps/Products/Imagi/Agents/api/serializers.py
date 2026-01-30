"""
Serializers for the Agents app API.

This module provides serializers for the Agents app models:
- AgentMessage: For user and assistant messages in a conversation
- SystemPrompt: For system prompts that guide agent behavior
- AgentConversation: For conversations between users and AI agents

These serializers are used by the API views to format data for responses.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import AgentConversation, SystemPrompt, AgentMessage

User = get_user_model()

class AgentMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for agent messages.
    
    This serializer handles messages exchanged in a conversation between
    a user and an AI agent. Messages can have different roles (user, assistant, system).
    """
    
    class Meta:
        model = AgentMessage
        fields = ('id', 'conversation', 'role', 'content', 'created_at')
        read_only_fields = ('id', 'created_at')

class SystemPromptSerializer(serializers.ModelSerializer):
    """
    Serializer for system prompts.
    
    System prompts provide instructions to the AI agent about how to behave
    and respond in a conversation.
    """
    
    class Meta:
        model = SystemPrompt
        fields = ('id', 'conversation', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class AgentConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for agent conversations.
    
    This serializer provides a summary view of a conversation, including
    basic metadata but not the full message history.
    """
    
    messages = AgentMessageSerializer(many=True, read_only=True)
    system_prompt = SystemPromptSerializer(read_only=True)
    
    class Meta:
        model = AgentConversation
        fields = ('id', 'user', 'model_name', 'provider', 'created_at', 'messages', 'system_prompt')
        read_only_fields = ('id', 'created_at')

class ConversationHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving complete conversation history.
    
    This serializer includes all messages in a conversation and detailed
    user information, used for displaying the full conversation history.
    """
    
    messages = AgentMessageSerializer(many=True, read_only=True)
    system_prompt = SystemPromptSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentConversation
        fields = ('id', 'user', 'model_name', 'provider', 'created_at', 'messages', 'system_prompt')
        read_only_fields = fields
    
    def get_user(self, obj):
        """
        Get detailed user information.
        
        Args:
            obj: The AgentConversation instance
            
        Returns:
            dict: User information including id, username, and email
        """
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email
        }

class MessageResponseSerializer(serializers.Serializer):
    """
    Serializer for API responses that include message pairs.
    
    This serializer is used for formatting responses from agent services
    that include both a user message and an assistant message. It supports
    both chat mode and build mode responses.
    """
    
    success = serializers.BooleanField()
    conversation_id = serializers.IntegerField()
    response = serializers.CharField()
    user_message = serializers.DictField()
    assistant_message = serializers.DictField()
    file_path = serializers.CharField(required=False, allow_null=True)
    file_updated = serializers.BooleanField(required=False, default=False)
    
    class Meta:
        fields = ('success', 'conversation_id', 'response', 'user_message', 
                  'assistant_message', 'file_path', 'file_updated')
        read_only_fields = fields 