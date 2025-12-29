from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Trustee, Borrower, LoanChecks, LoanStandingOrder


class DashboardLoanSummaryTests(TestCase):
    """Tests for GET /api/dashboard/loan-summary/ endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/dashboard/loan-summary/"

        # Create trustee
        t_user = User.objects.create_user(username="trustee1", password="x")
        self.trustee = Trustee.objects.create(
            user=t_user,
            community="Test Community",
            notes="Test trustee",
        )

        # Create borrower
        b_user = User.objects.create_user(username="borrower1", password="x")
        self.borrower = Borrower.objects.create(
            user=b_user,
            trustee=self.trustee,
            id_number="123456789",
            address="Test Address",
        )

    def test_no_active_loans_returns_zeros(self):
        """When no active loans exist, should return zeros"""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["active_loans_count"], 0)
        self.assertEqual(res.data["total_active_loans_amount"], 0)

    def test_counts_only_active_loan_checks(self):
        """Should count only ACTIVE LoanChecks"""
        # Create ACTIVE loan
        LoanChecks.objects.create(
            borrower=self.borrower,
            trustee=self.trustee,
            amount=Decimal("1000.00"),
            start_date="2025-01-01",
            status="ACTIVE",
            num_payments=10,
        )
        
        # Create PAID loan (should not be counted)
        LoanChecks.objects.create(
            borrower=self.borrower,
            trustee=self.trustee,
            amount=Decimal("2000.00"),
            start_date="2025-01-01",
            status="PAID",
            num_payments=10,
        )

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["active_loans_count"], 1)
        self.assertEqual(res.data["total_active_loans_amount"], 1000.0)

    def test_counts_only_active_standing_order(self):
        """Should count only ACTIVE LoanStandingOrder"""
        # Create ACTIVE loan
        LoanStandingOrder.objects.create(
            borrower=self.borrower,
            trustee=self.trustee,
            amount=Decimal("3000.00"),
            start_date="2025-01-01",
            status="ACTIVE",
            monthly_amount=Decimal("300.00"),
            charge_day=1,
        )
        
        # Create PENDING loan (should not be counted)
        LoanStandingOrder.objects.create(
            borrower=self.borrower,
            trustee=self.trustee,
            amount=Decimal("4000.00"),
            start_date="2025-01-01",
            status="PENDING",
            monthly_amount=Decimal("400.00"),
            charge_day=1,
        )

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["active_loans_count"], 1)
        self.assertEqual(res.data["total_active_loans_amount"], 3000.0)

    def test_aggregates_both_loan_types(self):
        """Should aggregate both LoanChecks and LoanStandingOrder"""
        # Create 2 ACTIVE LoanChecks
        LoanChecks.objects.create(
            borrower=self.borrower,
            trustee=self.trustee,
            amount=Decimal("1000.00"),
            start_date="2025-01-01",
            status="ACTIVE",
            num_payments=10,
        )
        LoanChecks.objects.create(
            borrower=self.borrower,
            trustee=self.trustee,
            amount=Decimal("2000.00"),
            start_date="2025-01-01",
            status="ACTIVE",
            num_payments=10,
        )
        
        # Create 1 ACTIVE LoanStandingOrder
        LoanStandingOrder.objects.create(
            borrower=self.borrower,
            trustee=self.trustee,
            amount=Decimal("3000.00"),
            start_date="2025-01-01",
            status="ACTIVE",
            monthly_amount=Decimal("300.00"),
            charge_day=1,
        )

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["active_loans_count"], 3)
        self.assertEqual(res.data["total_active_loans_amount"], 6000.0)

    def test_response_format(self):
        """Should always return the expected response format"""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("active_loans_count", res.data)
        self.assertIn("total_active_loans_amount", res.data)
        self.assertEqual(len(res.data), 2)  # Only these two fields
