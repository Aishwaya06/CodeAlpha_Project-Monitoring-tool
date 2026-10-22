from django.conf import settings
from django.db import models

class Task(models.Model):
    STATUS_CHOICES = [("todo", "To Do"), ("in_progress", "In Progress"), ("in_review", "In Review"), ("completed", "Completed")]
    PRIORITY_CHOICES = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tasks")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_tasks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo", db_index=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["due_date", "-updated_at"]
    def __str__(self): return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_comments")
    content = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["created_at"]

