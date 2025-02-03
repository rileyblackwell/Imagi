from rest_framework import serializers
from .models import UserProject, Project

class UserProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProject
        fields = ['id', 'name', 'project_path', 'created_at', 'updated_at']
        read_only_fields = ['project_path', 'created_at', 'updated_at']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'user', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']