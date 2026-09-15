import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Borrower, LoanChecks, Trustee


class EditLoanPutTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin user for the edit-loan endpoint.
        self.admin = User.objects.create_user(
            username="admin",
            password="x",
        )
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()

        self.client.force_authenticate(
            user=self.admin
        )

        # Create a trustee.
        trustee_user = User.objects.create_user(
            username="trustee1",
            password="x",
        )

        self.trustee = Trustee.objects.create(
            user=trustee_user,
            community="Ramot",
            notes="Main trustee",
        )

        # Create a borrower.
        borrower_user = User.objects.create_user(
            username="borrower1",
            password="x",
        )

        self.borrower = Borrower.objects.create(
            user=borrower_user,
            trustee=self.trustee,
            id_number="123456781",
            address="Jerusalem",
        )

        # Create a deterministic checks loan.
        self.loan_id = uuid.UUID(
            "00000000-0000-0000-0000-000000000001"
        )

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

        self.url = (
            f"/api/loans/{self.loan_id}/"
        )

    def test_happy_path_updates_db_and_returns_200(self):
        payload = {
            "amount": 6000,
            "start_date": "2025-02-01",
            "number_of_payments": 12,
            "trustee_id": str(
                self.trustee.trustee_id
            ),
            "status": "CLOSED",
        }

        response = self.client.put(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.loan.refresh_from_db()

        self.assertEqual(
            self.loan.amount,
            Decimal("6000.00"),
        )

        self.assertEqual(
            self.loan.num_payments,
            12,
        )

        self.assertEqual(
            str(self.loan.start_date),
            "2025-02-01",
        )

        # The current contract stores CLOSED directly.
        self.assertEqual(
            self.loan.status,
            "CLOSED",
        )

        self.assertEqual(
            response.data["loan_id"],
            str(self.loan_id),
        )

        self.assertEqual(
            response.data["loan_type"],
            "checks",
        )

        self.assertEqual(
            response.data["amount"],
            "6000.00",
        )

        self.assertEqual(
            response.data["start_date"],
            "2025-02-01",
        )

        self.assertEqual(
            response.data["status"],
            "CLOSED",
        )

    def test_invalid_amount_returns_400_field_level(self):
        payload = {
            "amount": 0,
            "start_date": "2025-02-01",
            "number_of_payments": 10,
            "trustee_id": str(
                self.trustee.trustee_id
            ),
            "status": "ACTIVE",
        }

        response = self.client.put(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "amount",
            response.data,
        )

        self.assertEqual(
            str(
                response.data[
                    "amount"
                ][0]
            ),
            "Must be greater than 0.",
        )

    def test_invalid_number_of_payments_returns_400_field_level(self):
        payload = {
            "amount": 5000,
            "start_date": "2025-02-01",
            "number_of_payments": 0,
            "trustee_id": str(
                self.trustee.trustee_id
            ),
            "status": "ACTIVE",
        }

        response = self.client.put(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "number_of_payments",
            response.data,
        )

        self.assertEqual(
            str(
                response.data[
                    "number_of_payments"
                ][0]
            ),
            "Must be at least 1.",
        )