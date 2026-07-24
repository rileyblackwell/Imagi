from rest_framework import serializers
from ..models import Project

class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for reading project data."""
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'design_preferences', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']

# The description seeds the initial AI build, so it has to carry enough
# signal for the agent to work with. Mirrored by the creation form.
MIN_DESCRIPTION_LENGTH = 20

class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new projects."""
    description = serializers.CharField(required=True, allow_blank=False)
    # Optional: extra design/style direction the founder can give to steer the
    # initial AI build. Empty is fine — the build prompt carries strong default
    # UI direction on its own.
    design_preferences = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = Project
        fields = ['name', 'description', 'design_preferences']

    def validate_name(self, value):
        """Validate project name is unique for user."""
        user = self.context['request'].user
        if Project.objects.filter(user=user, name=value, is_active=True).exists():
            raise serializers.ValidationError("A project with this name already exists.")
        return value

    def validate_description(self, value):
        """Require a business description substantial enough to seed the initial AI build."""
        value = value.strip()
        if len(value) < MIN_DESCRIPTION_LENGTH:
            raise serializers.ValidationError(
                "Please describe your business — what it does, who its customers are, "
                "and how it will sell. Imagi uses this to build the first version of your app."
            )
        return value

    def create(self, validated_data):
        """Create a new project for the current user."""
        # Don't get user from validated_data since it's passed directly to save()
        user = self.context['request'].user
        project = Project.objects.create(
            user=user,
            name=validated_data['name'],
            description=validated_data['description'],
            design_preferences=validated_data.get('design_preferences', ''),
        )
        return project