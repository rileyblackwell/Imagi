"""
Serializers for the Builder app API.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Conversation, Page, Message
from apps.Products.Imagi.ProjectManager.models import Project as PMProject

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']

class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer using ProjectManager's Project model."""
    class Meta:
        model = PMProject
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'user', 'project_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'conversation', 'filename', 'created_at']
        read_only_fields = ['id', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'page', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class FileSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()
    type = serializers.CharField()
    size = serializers.IntegerField(read_only=True)
    lastModified = serializers.DateTimeField(read_only=True)
    content = serializers.CharField(required=False)

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    path = serializers.CharField(required=False)

class FileContentSerializer(serializers.Serializer):
    content = serializers.CharField() 