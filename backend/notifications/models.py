from django.conf import settings
from django.db import models

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="sent_notifications")
    notification_type = models.CharField(max_length=40)
    message = models.CharField(max_length=240)
    related_project = models.ForeignKey("projects.Project", null=True, blank=True, on_delete=models.CASCADE)
    related_task = models.ForeignKey("tasks.Task", null=True, blank=True, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
