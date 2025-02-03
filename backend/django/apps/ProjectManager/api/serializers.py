from rest_framework import serializers
from ..models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'user', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description']

    def create(self, validated_data):
        user = self.context['request'].user
        project = Project.objects.create(
            user=user,
            **validated_data
        )
        return project 