from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from core.models import Borrower, Donor, LoginCode, Trustee
from core.services import create_role_user


REQUEST = "/api/auth/otp/request/"
VERIFY = "/api/auth/otp/verify/"


@override_settings(DEBUG=True, TWILIO_ACCOUNT_SID="", TWILIO_AUTH_TOKEN="")
class OtpLoginTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

        trustee_user, _ = create_role_user("trustee", "t", "Moshe", "Cohen", phone="052-1111111")
        trustee_user.profile.id_number = "222222226"
        trustee_user.profile.save()
        self.trustee = Trustee.objects.create(user=trustee_user, community="Ramot")

        borrower_user, _ = create_role_user("borrower", "123456782", "Dina", "Katz")
        self.borrower = Borrower.objects.create(
            user=borrower_user, trustee=self.trustee, id_number="123456782",
            first_name="Dina", last_name="Katz", phone="054-2222222", address="J",
        )

    def ask(self, id_number, phone, **extra):
        return self.client.post(
            REQUEST, {"id_number": id_number, "phone": phone, **extra}, format="json"
        )

    def verify(self, id_number, phone, code):
        return self.client.post(
            VERIFY, {"id_number": id_number, "phone": phone, "code": code}, format="json"
        )

    def test_borrower_full_flow(self):
        r = self.ask("123456782", "0542222222")
        self.assertEqual(r.status_code, 200, r.data)
        code = r.data["dev_code"]

        r = self.verify("123456782", "+972-54-2222222", code)
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["role"], "borrower")
        self.assertFalse(r.data["must_change_password"])

        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.data["role"], "borrower")
        self.assertFalse(me.data["must_change_password"])
        self.assertEqual(me.data["login_method"], "otp")

    def test_trustee_with_profile_id_number(self):
        code = self.ask("222222226", "052-1111111").data["dev_code"]
        r = self.verify("222222226", "052-1111111", code)
        self.assertEqual(r.data["role"], "trustee")

    def test_wrong_phone_sends_nothing_and_looks_the_same(self):
        r = self.ask("123456782", "050-9999999")
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("dev_code", r.data)
        self.assertEqual(LoginCode.objects.count(), 0)

    def test_unknown_id_looks_the_same(self):
        r = self.ask("999999999", "054-2222222")
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("dev_code", r.data)

    def test_wrong_code_then_lockout(self):
        code = self.ask("123456782", "0542222222").data["dev_code"]
        wrong = "000000" if code != "000000" else "111111"
        for _ in range(5):
            r = self.verify("123456782", "0542222222", wrong)
            self.assertEqual(r.data["code"], "invalid_code")
        # Even the right code no longer works after 5 failures.
        r = self.verify("123456782", "0542222222", code)
        self.assertEqual(r.data["code"], "expired")

    def test_code_is_single_use(self):
        code = self.ask("123456782", "0542222222").data["dev_code"]
        self.assertEqual(self.verify("123456782", "0542222222", code).status_code, 200)
        self.client.logout()
        self.assertEqual(self.verify("123456782", "0542222222", code).data["code"], "expired")

    def test_resend_cooldown(self):
        self.ask("123456782", "0542222222")
        r = self.ask("123456782", "0542222222")
        self.assertEqual(r.status_code, 429)
        self.assertEqual(r.data["code"], "too_soon")

    def test_code_for_other_phone_is_rejected(self):
        code = self.ask("123456782", "0542222222").data["dev_code"]
        r = self.verify("123456782", "050-9999999", code)
        self.assertEqual(r.data["code"], "invalid_code")

    def test_inactive_user_gets_no_code(self):
        self.borrower.user.is_active = False
        self.borrower.user.save()
        self.assertNotIn("dev_code", self.ask("123456782", "0542222222").data)

    @override_settings(DEBUG=False, TWILIO_ACCOUNT_SID="AC1", TWILIO_AUTH_TOKEN="x")
    def test_production_sends_sms_and_hides_code(self):
        with mock.patch("core.otp.send_twilio", return_value="SM1") as send:
            r = self.ask("123456782", "054-2222222", channel="WHATSAPP")  # unknown -> SMS
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("dev_code", r.data)
        channel, phone, message = send.call_args[0]
        self.assertEqual((channel, phone), ("SMS", "+972542222222"))
        self.assertRegex(message, r"\d{6}")

    @override_settings(DEBUG=False)
    def test_production_without_twilio_reports_failure(self):
        r = self.ask("123456782", "054-2222222")
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.data["code"], "send_failed")


@override_settings(
    DEBUG=False,
    EMAIL_HOST="smtp.example.com",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class EmailCodeTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        trustee_user, _ = create_role_user("trustee", "t")
        trustee = Trustee.objects.create(user=trustee_user, community="R")
        user, _ = create_role_user("borrower", "555555556")
        self.borrower = Borrower.objects.create(
            user=user, trustee=trustee, id_number="555555556",
            first_name="E", email="Eli@Example.com", address="x",
        )

    def test_email_code_flow(self):
        from django.core import mail

        r = self.client.post(REQUEST, {"id_number": "555555556", "email": "eli@example.com",
                                       "channel": "EMAIL"}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertNotIn("dev_code", r.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["eli@example.com"])
        code = __import__("re").search(r"\d{6}", mail.outbox[0].body).group()

        r = self.client.post(VERIFY, {"id_number": "555555556", "email": "ELI@example.com",
                                      "channel": "EMAIL", "code": code}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["role"], "borrower")

    def test_wrong_email_sends_nothing(self):
        from django.core import mail

        r = self.client.post(REQUEST, {"id_number": "555555556", "email": "other@example.com",
                                       "channel": "EMAIL"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)


class DonorsCannotSignInTests(TestCase):
    @override_settings(DEBUG=True, TWILIO_ACCOUNT_SID="", TWILIO_AUTH_TOKEN="")
    def test_donor_gets_no_code(self):
        cache.clear()
        user, _ = create_role_user("donor", "d", phone="053-1231231")
        user.profile.id_number = "666666664"
        user.profile.save()
        Donor.objects.create(user=user, phone="053-1231231")
        r = APIClient().post(REQUEST, {"id_number": "666666664", "phone": "053-1231231"}, format="json")
        self.assertNotIn("dev_code", r.data)


class IdNumberOnProfilesTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.client.force_authenticate(
            User.objects.create_superuser("boss", "b@example.com", "Sup3r!Pass")
        )

    def test_create_trustee_and_donor_with_id_number(self):
        r = self.client.post(
            "/api/trustees/",
            {"first_name": "A", "last_name": "B", "community": "C",
             "phone": "052-0000001", "id_number": "333333334"},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["id_number"] if "id_number" in r.data else
                         Trustee.objects.get().user.profile.id_number, "333333334")

        r = self.client.post(
            "/api/donors/",
            {"first_name": "D", "last_name": "E", "phone": "053-0000001", "id_number": "333333334"},
            format="json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("id_number", r.data)
        self.assertFalse(Donor.objects.exists())  # rolled back

    def test_update_trustee_id_number(self):
        user, _ = create_role_user("trustee", "x", phone="052-0000002")
        trustee = Trustee.objects.create(user=user, community="R")
        r = self.client.patch(
            f"/api/trustees/{trustee.trustee_id}/", {"id_number": "444444442"}, format="json"
        )
        self.assertEqual(r.status_code, 200, r.data)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.id_number, "444444442")
