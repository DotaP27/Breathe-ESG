from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tenants.models import Tenant
from records.models import EmissionRecord

User = get_user_model()


class RecordsWorkflowTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(name="TestCo", slug="testco")
        self.user = User.objects.create_user(username="analyst", password="pass")
        # create analyst group and add user
        from django.contrib.auth.models import Group
        g, _ = Group.objects.get_or_create(name="analyst")
        self.user.groups.add(g)
        self.user.save()

        self.other = User.objects.create_user(username="other", password="pass")

        self.record = EmissionRecord.objects.create(
            tenant=self.tenant,
            source_type="UTILITY",
            raw_data={"sample": 1},
            scope=2,
            status="PENDING",
        )

    def test_approve_requires_auth(self):
        # unauthenticated
        resp = self.client.post(f"/api/records/{self.record.id}/approve/")
        self.assertEqual(resp.status_code, 401)

    def test_approve_by_authenticated(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f"/api/records/{self.record.id}/approve/")
        self.assertEqual(resp.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, "APPROVED")

    def test_flag_by_analyst(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f"/api/records/{self.record.id}/flag/", {"reason": "suspicious"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, "FLAGGED")
        self.assertTrue(any(h.get("action") == "FLAGGED" for h in self.record.edit_history))

    def test_flag_forbidden_for_non_analyst(self):
        self.client.force_authenticate(user=self.other)
        resp = self.client.post(f"/api/records/{self.record.id}/flag/", {"reason": "suspicious"}, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_reject_by_analyst(self):
        # first flag to change status
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f"/api/records/{self.record.id}/flag/", {"reason": "bad"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.record.refresh_from_db()
        # now reject (puts back to PENDING with REJECTED history)
        resp = self.client.post(f"/api/records/{self.record.id}/reject/", {"reason": "fix"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, "PENDING")
        self.assertTrue(any(h.get("action") == "REJECTED" for h in self.record.edit_history))
