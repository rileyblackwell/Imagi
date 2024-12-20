from rest_framework import serializers
from .models import UserProject

class UserProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProject
        fields = ['id', 'name', 'project_path', 'created_at', 'updated_at']
        read_only_fields = ['project_path', 'created_at', 'updated_at']