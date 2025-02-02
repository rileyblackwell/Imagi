"""
Serializers for the Builder app API.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Project, Conversation, Page, Message

User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    url_safe_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'created_at', 'updated_at', 
                 'is_active', 'url_safe_name', 'project_path')
        read_only_fields = ('id', 'created_at', 'updated_at', 'project_path')
    
    def get_url_safe_name(self, obj):
        return obj.get_url_safe_name()

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'conversation', 'page', 'role', 'content', 'created_at')
        read_only_fields = ('id', 'created_at')

class PageSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Page
        fields = ('id', 'conversation', 'filename', 'created_at', 'messages')
        read_only_fields = ('id', 'created_at')

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    pages = PageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'user', 'project', 'created_at', 'messages', 'pages')
        read_only_fields = ('id', 'created_at')

class ProjectDetailSerializer(ProjectSerializer):
    conversations = ConversationSerializer(many=True, read_only=True)
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ('conversations',) 