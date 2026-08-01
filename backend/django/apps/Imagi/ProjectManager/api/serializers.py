from rest_framework import serializers
from ..models import Project


def validate_project_name(value):
    """Reject names that could steer a filesystem path.

    The services keyed their sidecar files on the project id rather than the
    name, so a crafted name no longer escapes anything; this keeps such a name
    out of the database in the first place, and out of the log lines and
    directory basenames the name still reaches.
    """
    value = (value or '').strip()
    if not value:
        raise serializers.ValidationError("Project name cannot be blank.")
    if '/' in value or '\\' in value or '\x00' in value:
        raise serializers.ValidationError("Project name cannot contain path separators.")
    if value == '..' or value.startswith('../') or value.startswith('..\\'):
        raise serializers.ValidationError("Project name cannot be a relative path.")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise serializers.ValidationError("Project name cannot contain control characters.")
    return value


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for reading project data.

    The slug is exposed because the frontend routes on it (/imagi/workspace/
    <slug> and the sibling module workspaces). It is the authoritative one the
    model generates and disambiguates, so two projects whose names collapse to
    the same slug still address distinctly; deriving it on the client instead
    would collide.
    """
    class Meta:
        model = Project
        fields = ['id', 'name', 'slug', 'description', 'design_preferences', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Applies on the writable update path (PATCH /projects/<pk>/)."""
        return validate_project_name(value)

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
        """Validate project name is safe and unique for user."""
        value = validate_project_name(value)
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