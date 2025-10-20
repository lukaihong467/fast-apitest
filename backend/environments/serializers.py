from rest_framework import serializers

from .models import Environment


class EnvironmentSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Environment
        fields = [
            "id",
            "project",
            "project_name",
            "name",
            "base_url",
            "description",
            "variables",
            "headers",
            "is_default",
            "created_at",
            "updated_at",
        ]
