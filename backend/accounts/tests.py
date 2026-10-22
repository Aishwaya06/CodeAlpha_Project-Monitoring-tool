from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class AuthenticationTests(APITestCase):
    def test_register_login_logout(self):
        response = self.client.post("/api/auth/register/", {"username": "alice", "email": "alice@example.com", "password": "LongPass!739"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data)
        self.client.post("/api/auth/logout/")
        response = self.client.post("/api/auth/login/", {"username": "alice", "password": "LongPass!739"}, format="json")
        self.assertEqual(response.status_code, 200)
    def test_duplicate_registration_rejected(self):
        User.objects.create_user("alice", password="LongPass!739")
        response = self.client.post("/api/auth/register/", {"username": "alice", "email": "a@example.com", "password": "LongPass!739"}, format="json")
        self.assertEqual(response.status_code, 400)
