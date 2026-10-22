from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, ProjectMembership

class MemberSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    class Meta:
        model = ProjectMembership
        fields = ["user_id", "username", "email", "role", "joined_at"]

class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    members = MemberSerializer(source="memberships", many=True, read_only=True)
    class Meta:
        model = Project
        fields = ["id", "name", "description", "owner", "owner_name", "members", "status", "start_date", "due_date", "created_at", "updated_at"]
        read_only_fields = ["owner", "created_at", "updated_at"]
    def validate(self, data):
        start, due = data.get("start_date", getattr(self.instance, "start_date", None)), data.get("due_date", getattr(self.instance, "due_date", None))
        if start and due and due < start: raise serializers.ValidationError({"due_date": "Due date cannot be before start date."})
        return data

class AddMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    def validate_user_id(self, value):
        try: return User.objects.get(pk=value)
        except User.DoesNotExist: raise serializers.ValidationError("User does not exist.")
