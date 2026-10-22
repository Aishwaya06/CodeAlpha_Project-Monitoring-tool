from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Notification
from rest_framework import serializers

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "actor", "notification_type", "message", "related_project", "related_task", "is_read", "created_at"]
        read_only_fields = ["actor", "notification_type", "message", "related_project", "related_task", "created_at"]

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]
    def get_queryset(self): return Notification.objects.filter(recipient=self.request.user)
    def perform_update(self, serializer):
        if not serializer.validated_data.keys() <= {"is_read"}: raise PermissionDenied("Only read status can be changed.")
        serializer.save()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({"updated": True})
