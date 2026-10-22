from rest_framework import serializers
from .models import Task, Comment
from projects.models import ProjectMembership
from notifications.models import Notification

class TaskSerializer(serializers.ModelSerializer):
    assignee_name = serializers.CharField(source="assigned_to.username", read_only=True, allow_null=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    class Meta:
        model = Task
        fields = ["id", "title", "description", "project", "project_name", "assigned_to", "assignee_name", "created_by", "created_by_name", "status", "priority", "due_date", "created_at", "updated_at"]
        read_only_fields = ["created_by", "created_at", "updated_at"]
    def validate(self, attrs):
        project = attrs.get("project", getattr(self.instance, "project", None))
        assigned = attrs.get("assigned_to", getattr(self.instance, "assigned_to", None))
        if project and not ProjectMembership.objects.filter(project=project, user=self.context["request"].user).exists():
            raise serializers.ValidationError({"project": "You must belong to this project."})
        if assigned and project and not ProjectMembership.objects.filter(project=project, user=assigned).exists():
            raise serializers.ValidationError({"assigned_to": "Assignee must be a project member."})
        return attrs

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    class Meta:
        model = Comment
        fields = ["id", "task", "author", "author_name", "content", "created_at", "updated_at"]
        read_only_fields = ["task", "author", "created_at", "updated_at"]
    def validate_content(self, value):
        if not value.strip(): raise serializers.ValidationError("Comment cannot be empty.")
        return value.strip()
