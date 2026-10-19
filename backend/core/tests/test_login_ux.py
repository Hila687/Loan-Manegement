from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from core.models import Borrower, Donor, Trustee
from core.services import create_role_user


LOGIN = "/api/auth/login/"


@override_settings(LOGIN_MAX_ATTEMPTS=5, LOGIN_LOCKOUT_SECONDS=60)
class FlexibleLoginTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

        self.admin, self.admin_pw = create_role_user(
            "admin", "manager", "Rivka", "Levi", phone="050-0000000"
        )

        trustee_user, self.trustee_pw = create_role_user(
            "trustee", "cohen", "Moshe", "Cohen", phone="052-1111111"
        )
        self.trustee = Trustee.objects.create(
            user=trustee_user, community="Ramot"
        )

        borrower_user, self.borrower_pw = create_role_user(
            "borrower", "123456782", "Dina", "Katz",
            email="dina@example.com", phone="054-2222222",
        )
        self.borrower = Borrower.objects.create(
            user=borrower_user,
            trustee=self.trustee,
            id_number="123456782",
            first_name="Dina",
            last_name="Katz",
            phone="054-2222222",
            email="dina@example.com",
            address="Jerusalem",
        )

        donor_user, self.donor_pw = create_role_user(
            "donor", "donor", "Avi", "Gold", phone="053-3333333"
        )
        Donor.objects.create(user=donor_user, phone="053-3333333")

    def login(self, identifier, password):
        return self.client.post(
            LOGIN,
            {"username": identifier, "password": password},
            format="json",
        )

    # --- signing in with friendly identifiers -------------------------

    def test_borrower_can_sign_in_with_id_number(self):
        r = self.login("123456782", self.borrower_pw)
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["role"], "borrower")

    def test_phone_in_any_format(self):
        for phone in ["054-2222222", "0542222222", "+972542222222", "+972 54 222 2222"]:
            self.client.logout()
            r = self.login(phone, self.borrower_pw)
            self.assertEqual(r.status_code, 200, (phone, r.data))

    def test_trustee_and_donor_sign_in_with_phone(self):
        self.assertEqual(self.login("052-1111111", self.trustee_pw).data["role"], "trustee")
        self.client.logout()
        # Donors are records only and cannot sign in.
        self.assertEqual(self.login("0533333333", self.donor_pw).status_code, 403)

    def test_email_and_case_insensitive_username(self):
        self.assertEqual(self.login("DINA@example.com", self.borrower_pw).status_code, 200)
        self.client.logout()
        username = self.borrower.user.username.upper()
        self.assertEqual(self.login(username, self.borrower_pw).status_code, 200)

    def test_wrong_password_returns_code(self):
        r = self.login("123456782", "nope")
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data["code"], "invalid_credentials")

    def test_shared_phone_is_refused_as_ambiguous(self):
        user, pw = create_role_user("donor", "other", phone="054-2222222")
        Donor.objects.create(user=user, phone="054-2222222")
        r = self.login("054-2222222", self.borrower_pw)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data["code"], "ambiguous_identifier")
        # The ID number still works.
        self.assertEqual(self.login("123456782", self.borrower_pw).status_code, 200)

    def test_lockout_counts_per_account_across_formats(self):
        for phone in ["054-2222222", "0542222222", "+972542222222", "054 222 2222", "0542222222"]:
            self.login(phone, "bad")
        r = self.login("123456782", self.borrower_pw)
        self.assertEqual(r.status_code, 429)
        self.assertEqual(r.data["code"], "too_many_attempts")

    def test_inactive_user_cannot_sign_in(self):
        self.borrower.user.is_active = False
        self.borrower.user.save()
        self.assertEqual(self.login("123456782", self.borrower_pw).status_code, 401)


class CredentialsManagementTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = User.objects.create_superuser("boss", "b@example.com", "Sup3r!Pass")
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

        trustee_user, _ = create_role_user("trustee", "t", "T", "T", phone="052-1111111")
        self.trustee = Trustee.objects.create(user=trustee_user, community="Ramot")

        self.borrower_user, self.borrower_pw = create_role_user(
            "borrower", "123456782", "Dina", "Katz", phone="054-2222222"
        )
        self.borrower = Borrower.objects.create(
            user=self.borrower_user, trustee=self.trustee, id_number="123456782",
            first_name="Dina", last_name="Katz", phone="054-2222222", address="J",
        )

    def test_create_borrower_returns_hints(self):
        r = self.client.post(
            "/api/borrowers/",
            {"id_number": "000000018", "first_name": "A", "last_name": "B",
             "address": "x", "phone": "050-9999999", "trustee": str(self.trustee.trustee_id)},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)
        creds = r.data["credentials"]
        self.assertEqual(creds["login_hints"]["id_number"], "000000018")
        self.assertTrue(creds["can_send"])

    def test_admin_can_reset_borrower_password(self):
        r = self.client.post(f"/api/borrowers/{self.borrower.borrower_id}/reset-password/")
        self.assertEqual(r.status_code, 200, r.data)
        self.borrower_user.refresh_from_db()
        self.assertTrue(self.borrower_user.check_password(r.data["temporary_password"]))
        self.assertTrue(self.borrower_user.profile.must_change_password)

    def test_reset_creates_account_for_legacy_borrower(self):
        legacy = Borrower.objects.create(
            trustee=self.trustee, id_number="111111118", first_name="L", address="x"
        )
        r = self.client.post(f"/api/borrowers/{legacy.borrower_id}/reset-password/")
        self.assertEqual(r.status_code, 200, r.data)
        legacy.refresh_from_db()
        self.assertIsNotNone(legacy.user)

    def test_trustee_cannot_reset_passwords(self):
        client = APIClient()
        client.force_authenticate(self.trustee.user)
        r = client.post(f"/api/borrowers/{self.borrower.borrower_id}/reset-password/")
        self.assertEqual(r.status_code, 403)

    @mock.patch("core.credentials.send_twilio", return_value="SM123")
    def test_send_credentials_sms(self, send):
        r = self.client.post(
            "/api/auth/send-credentials/",
            {"username": self.borrower_user.username,
             "temporary_password": self.borrower_pw, "channel": "SMS"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        channel, phone, message = send.call_args[0]
        self.assertEqual((channel, phone), ("SMS", "+972542222222"))
        self.assertIn("תעודת זהות", message)
        self.assertNotIn(self.borrower_pw, message)
        self.assertIn("/login", message)

    @mock.patch("core.credentials.send_twilio")
    def test_send_refuses_non_temporary_password(self, send):
        profile = self.borrower_user.profile
        profile.must_change_password = False
        profile.save()
        r = self.client.post(
            "/api/auth/send-credentials/",
            {"username": self.borrower_user.username,
             "temporary_password": self.borrower_pw},
            format="json",
        )
        self.assertEqual(r.data["code"], "not_temporary")
        send.assert_not_called()

    def test_send_without_twilio_reports_failure(self):
        r = self.client.post(
            "/api/auth/send-credentials/",
            {"username": self.borrower_user.username,
             "temporary_password": self.borrower_pw},
            format="json",
        )
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.data["code"], "send_failed")
