from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from projects.models import Project, ProjectMembership
from notifications.models import Notification
from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = Task.objects.filter(Q(project__owner=self.request.user) | Q(project__memberships__user=self.request.user)).distinct().select_related("project", "assigned_to", "created_by")
        p, s, pr, q = [self.request.query_params.get(k) for k in ("project", "status", "priority", "search")]
        if p: qs = qs.filter(project_id=p)
        if s: qs = qs.filter(status=s)
        if pr: qs = qs.filter(priority=pr)
        if q: qs = qs.filter(title__icontains=q)
        return qs
    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        if task.assigned_to_id and task.assigned_to_id != self.request.user.id:
            Notification.objects.create(recipient=task.assigned_to, actor=self.request.user, notification_type="task_assigned", message=f"You were assigned {task.title}.", related_project=task.project, related_task=task)
    def perform_update(self, serializer):
        obj = serializer.instance
        if obj.project.owner_id != self.request.user.id and not ProjectMembership.objects.filter(project=obj.project, user=self.request.user).exists():
            raise PermissionDenied()
        before_status, before_assignee = obj.status, obj.assigned_to_id
        task = serializer.save()
        if task.status != before_status:
            for member in ProjectMembership.objects.filter(project=task.project).exclude(user=self.request.user).select_related("user"):
                Notification.objects.create(recipient=member.user, actor=self.request.user, notification_type="task_status", message=f"{task.title} moved to {task.get_status_display()}.", related_project=task.project, related_task=task)
        if task.assigned_to_id and task.assigned_to_id != before_assignee:
            Notification.objects.create(recipient=task.assigned_to, actor=self.request.user, notification_type="task_assigned", message=f"You were assigned {task.title}.", related_project=task.project, related_task=task)
    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        task = self.get_object()
        if request.method == "GET": return Response(CommentSerializer(task.comments.select_related("author"), many=True).data)
        serializer = CommentSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        comment = serializer.save(task=task, author=request.user)
        if task.assigned_to_id and task.assigned_to_id != request.user.id:
            Notification.objects.create(recipient=task.assigned_to, actor=request.user, notification_type="task_comment", message=f"{request.user.username} commented on {task.title}.", related_project=task.project, related_task=task)
        return Response(CommentSerializer(comment).data, status=201)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch", "delete", "head", "options"]
    def get_queryset(self): return Comment.objects.filter(task__in=Task.objects.filter(Q(project__owner=self.request.user) | Q(project__memberships__user=self.request.user)))
    def perform_update(self, serializer):
        if serializer.instance.author_id != self.request.user.id: raise PermissionDenied("You can only edit your own comments.")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.author_id != self.request.user.id: raise PermissionDenied("You can only delete your own comments.")
        instance.delete()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    projects = Project.objects.filter(Q(owner=request.user) | Q(memberships__user=request.user)).distinct()
    tasks = Task.objects.filter(Q(project__owner=request.user) | Q(project__memberships__user=request.user), assigned_to=request.user).distinct()
    return Response({"total_projects": projects.count(), "owned_projects": projects.filter(owner=request.user).count(), "participating_projects": projects.exclude(owner=request.user).count(), "total_assigned_tasks": tasks.count(), "pending_tasks": tasks.filter(status="todo").count(), "in_progress_tasks": tasks.filter(status="in_progress").count(), "completed_tasks": tasks.filter(status="completed").count(), "recent_projects": list(projects.order_by("-updated_at").values("id", "name", "status", "updated_at")[:5]), "recent_tasks": list(tasks.order_by("-updated_at").values("id", "title", "status", "updated_at")[:5]), "upcoming_deadlines": list(tasks.filter(due_date__gte=timezone.localdate()).order_by("due_date").values("id", "title", "due_date")[:5])})
