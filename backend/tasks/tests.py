from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from projects.models import Project, ProjectMembership
from .models import Task, Comment
from notifications.models import Notification

class TaskAndCommentTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="password")
        self.member = User.objects.create_user("member", password="password")
        self.outsider = User.objects.create_user("outsider", password="password")
        self.project = Project.objects.create(name="Team", owner=self.owner)
        ProjectMembership.objects.create(project=self.project, user=self.owner, role="owner")
        ProjectMembership.objects.create(project=self.project, user=self.member)
        self.task = Task.objects.create(title="Build", project=self.project, created_by=self.owner)
    def test_member_can_assign_only_project_member(self):
        self.client.force_authenticate(self.owner)
        ok = self.client.post("/api/tasks/", {"title":"Assigned", "project":self.project.id, "assigned_to":self.member.id}, format="json")
        bad = self.client.post("/api/tasks/", {"title":"Invalid", "project":self.project.id, "assigned_to":self.outsider.id}, format="json")
        self.assertEqual(ok.status_code, 201)
        self.assertEqual(bad.status_code, 400)
    def test_nonmember_cannot_modify_task(self):
        self.client.force_authenticate(self.outsider)
        self.assertEqual(self.client.patch(f"/api/tasks/{self.task.id}/", {"title":"Changed"}, format="json").status_code, 404)
    def test_comment_author_only_can_edit(self):
        comment = Comment.objects.create(task=self.task, author=self.member, content="Hello")
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.patch(f"/api/comments/{comment.id}/", {"content":"Edited"}, format="json").status_code, 403)
        self.client.force_authenticate(self.member)
        self.assertEqual(self.client.patch(f"/api/comments/{comment.id}/", {"content":"Edited"}, format="json").status_code, 200)
    def test_status_change_notifies_project_member(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(f"/api/tasks/{self.task.id}/", {"status":"in_progress"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Notification.objects.filter(recipient=self.member, notification_type="task_status", related_task=self.task).exists())
