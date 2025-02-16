from rest_framework import serializers
from ..models import Project

class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for reading project data."""
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new projects."""
    class Meta:
        model = Project
        fields = ['name', 'description']

    def validate_name(self, value):
        """Validate project name is unique for user."""
        user = self.context['request'].user
        if Project.objects.filter(user=user, name=value, is_active=True).exists():
            raise serializers.ValidationError("A project with this name already exists.")
        return value

    def create(self, validated_data):
        """Create a new project for the current user."""
        # Don't get user from validated_data since it's passed directly to save()
        user = self.context['request'].user
        project = Project.objects.create(
            user=user,
            name=validated_data['name'],
            description=validated_data.get('description', '')
        )
        return project

class FileSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()
    type = serializers.CharField()
    size = serializers.IntegerField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

class FileContentSerializer(serializers.Serializer):
    content = serializers.CharField()
    encoding = serializers.CharField(required=False, default='utf-8')