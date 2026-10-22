from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import Notification

class NotificationOwnershipTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="password")
        self.other = User.objects.create_user("other", password="password")
        self.notification = Notification.objects.create(recipient=self.owner, notification_type="test", message="Update")
    def test_recipient_can_mark_read(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(f"/api/notifications/{self.notification.id}/", {"is_read":True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
    def test_other_user_cannot_read_or_update_notification(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get("/api/notifications/").data["count"], 0)
        self.assertEqual(self.client.patch(f"/api/notifications/{self.notification.id}/", {"is_read":True}, format="json").status_code, 404)
