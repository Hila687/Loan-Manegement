import uuid
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Trustee, Borrower, LoanChecks


class EditLoanPutTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Admin user to satisfy IsAdminUser
        self.admin = User.objects.create_user(username="admin", password="x")
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.client.force_authenticate(user=self.admin)

        # Trustee
        t_user = User.objects.create_user(username="trustee1", password="x")
        self.trustee = Trustee.objects.create(
            user=t_user,
            community="Ramot",
            notes="Main trustee",
        )

        # Borrower
        b_user = User.objects.create_user(username="borrower1", password="x")
        self.borrower = Borrower.objects.create(
            user=b_user,
            trustee=self.trustee,
            id_number="123456781",
            address="Jerusalem",
        )

        # Loan (checks) with deterministic UUID
        self.loan_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        self.loan = LoanChecks.objects.create(
            loan_id=self.loan_id,
            borrower=self.borrower,
            trustee=self.trustee,
            amount=Decimal("5000.00"),
            start_date="2025-01-01",
            status="ACTIVE",
            num_payments=10,
            check_details="Demo checks",
            predefined_schedule=True,
        )

        self.url = f"/api/loans/{self.loan_id}/"

    def test_happy_path_updates_db_and_returns_200(self):
        payload = {
            "amount": 6000,
            "start_date": "2025-02-01",
            "number_of_payments": 12,
            "trustee_id": str(self.trustee.trustee_id),
            "status": "CLOSED",
        }
        res = self.client.put(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # DB updated
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.amount, Decimal("6000.00"))
        self.assertEqual(self.loan.num_payments, 12)
        self.assertEqual(str(self.loan.start_date), "2025-02-01")

        # status mapped contract->model ("CLOSED" -> "PAID")
        self.assertEqual(self.loan.status, "PAID")

        # Response JSON exists (per BE1 acceptance)
        self.assertEqual(res.data["loan_id"], str(self.loan_id))
        self.assertEqual(res.data["loan_type"], "checks")
        self.assertEqual(res.data["amount"], "6000.00")
        self.assertEqual(res.data["start_date"], "2025-02-01")
        # Response status is contract value (model->contract mapping)
        self.assertIn(res.data["status"], ["ACTIVE", "CLOSED", "OVERDUE"])

    def test_invalid_amount_returns_400_field_level(self):
        payload = {
            "amount": 0,
            "start_date": "2025-02-01",
            "number_of_payments": 10,
            "trustee_id": str(self.trustee.trustee_id),
            "status": "ACTIVE",
        }
        res = self.client.put(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data.get("amount"), ["Must be greater than 0"])

    def test_invalid_number_of_payments_returns_400_field_level(self):
        payload = {
            "amount": 5000,
            "start_date": "2025-02-01",
            "number_of_payments": 0,
            "trustee_id": str(self.trustee.trustee_id),
            "status": "ACTIVE",
        }
        res = self.client.put(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data.get("number_of_payments"), ["Must be at least 1"])
