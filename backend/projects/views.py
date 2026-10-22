from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Project, ProjectMembership
from .serializers import ProjectSerializer, MemberSerializer, AddMemberSerializer
from notifications.models import Notification

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Project.objects.filter(Q(owner=self.request.user) | Q(memberships__user=self.request.user)).distinct().select_related("owner").prefetch_related("memberships__user")
    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        ProjectMembership.objects.get_or_create(project=project, user=self.request.user, defaults={"role": "owner"})
    def perform_update(self, serializer):
        if serializer.instance.owner_id != self.request.user.id: raise PermissionDenied("Only the project owner can edit project settings.")
        serializer.save()
    def destroy(self, request, *args, **kwargs):
        if self.get_object().owner_id != request.user.id: raise PermissionDenied("Only the project owner can delete this project.")
        return super().destroy(request, *args, **kwargs)
    @action(detail=True, methods=["get", "post"], url_path="members")
    def members(self, request, pk=None):
        project = self.get_object()
        if request.method == "GET": return Response(MemberSerializer(project.memberships.select_related("user"), many=True).data)
        if project.owner_id != request.user.id: raise PermissionDenied("Only the project owner can add members.")
        serializer = AddMemberSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user_id"]
        if user.id == project.owner_id: return Response({"detail": "The owner is already a member."}, status=400)
        membership, created = ProjectMembership.objects.get_or_create(project=project, user=user)
        if created: Notification.objects.create(recipient=user, actor=request.user, notification_type="project_added", message=f"You were added to {project.name}.", related_project=project)
        return Response(MemberSerializer(membership).data, status=201 if created else 200)
    @action(detail=True, methods=["delete"], url_path=r"members/(?P<user_id>[^/.]+)")
    def remove_member(self, request, pk=None, user_id=None):
        project = self.get_object()
        if project.owner_id != request.user.id: raise PermissionDenied("Only the project owner can remove members.")
        if str(project.owner_id) == str(user_id): return Response({"detail": "The owner cannot be removed."}, status=400)
        deleted, _ = ProjectMembership.objects.filter(project=project, user_id=user_id).delete()
        if not deleted: return Response(status=404)
        return Response(status=204)
