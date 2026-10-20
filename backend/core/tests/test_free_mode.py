"""
"Free mode": no SMS and no email configured. Everyone signs in with a
password; nothing offers to send a code or a message.
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from core.models import Trustee

FREE = dict(
    SMS_ENABLED=False,
    EMAIL_ENABLED=False,
    CODE_LOGIN_SMS=False,
    CODE_LOGIN_EMAIL=False,
)


@override_settings(**FREE)
class FreeModeTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = APIClient()
        self.admin.force_authenticate(
            User.objects.create_superuser("boss", "b@example.com", "Sup3r!Pass")
        )
        self.trustee_id = str(
            Trustee.objects.create(
                user=User.objects.create(username="t1"), community="Ramot"
            ).trustee_id
        )

    def test_config_reports_no_channels(self):
        data = APIClient().get("/api/auth/config/").json()
        self.assertEqual(data["code_login"], {"sms": False, "email": False})
        self.assertEqual(data["send"], {"sms": False, "email": False})

    def test_code_request_is_refused(self):
        r = APIClient().post(
            "/api/auth/otp/request/",
            {"id_number": "123456782", "phone": "054-2222222"},
            format="json",
        )
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data["code"], "disabled")

    def test_new_borrower_gets_password_and_can_sign_in_with_id(self):
        r = self.admin.post(
            "/api/borrowers/",
            {"id_number": "123456782", "first_name": "D", "last_name": "K",
             "address": "x", "phone": "054-2222222", "trustee": self.trustee_id},
            format="json",
        )
        creds = r.data["credentials"]
        self.assertFalse(creds["code_login"])
        self.assertFalse(creds["can_send_sms"])
        self.assertFalse(creds["can_send_email"])

        r = APIClient().post(
            "/api/auth/login/",
            {"username": "123456782", "password": creds["temporary_password"]},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["role"], "borrower")
        self.assertTrue(r.data["must_change_password"])
