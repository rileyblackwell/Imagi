from rest_framework import serializers
from django.contrib.auth.models import User
from apps.ProjectManager.models import Project

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'user', 'created_at', 'updated_at', 'is_active', 'project_path')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField() 