from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import Project, ProjectMembership

class ProjectPermissionTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="password")
        self.other = User.objects.create_user("other", password="password")
        self.project = Project.objects.create(name="Private", owner=self.owner)
        ProjectMembership.objects.create(project=self.project, user=self.owner, role="owner")
    def test_create_project_and_owner_membership(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post("/api/projects/", {"name": "New"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ProjectMembership.objects.filter(project_id=response.data["id"], user=self.owner, role="owner").exists())
    def test_nonmember_cannot_read_project(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/projects/{self.project.id}/").status_code, 404)
    def test_owner_edits_and_manages_members(self):
        self.client.force_authenticate(self.owner)
        updated = self.client.patch(f"/api/projects/{self.project.id}/", {"name": "Renamed"}, format="json")
        added = self.client.post(f"/api/projects/{self.project.id}/members/", {"user_id": self.other.id}, format="json")
        removed = self.client.delete(f"/api/projects/{self.project.id}/members/{self.other.id}/")
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(added.status_code, 201)
        self.assertEqual(removed.status_code, 204)
    def test_nonowner_cannot_change_project(self):
        ProjectMembership.objects.create(project=self.project, user=self.other)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(f"/api/projects/{self.project.id}/", {"name": "No"}, format="json").status_code, 403)
