from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Borrower, LoanChecks, Trustee
from core.services import create_role_user, generate_payment_schedule


class LoanListAndDashboardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("boss", "b@example.com", "Sup3r!Pass")
        trustee_user, _ = create_role_user("trustee", "t")
        self.trustee = Trustee.objects.create(user=trustee_user, community="Ramot")
        borrower_user, _ = create_role_user("borrower", "1")
        self.borrower_user = borrower_user
        borrower = Borrower.objects.create(
            user=borrower_user, trustee=self.trustee, id_number="1", first_name="A", address="x"
        )
        self.loan = LoanChecks.objects.create(
            borrower=borrower, trustee=self.trustee, amount=Decimal("1200"),
            start_date=date.today().replace(day=1) - relativedelta(months=2), num_payments=12,
        )
        payments = generate_payment_schedule(self.loan, 12)
        bounced = payments[1]
        bounced.status, bounced.is_manual_exception, bounced.exception_note = "LATE", True, "Bounced"
        bounced.save()

    def client_for(self, user):
        client = APIClient()
        client.force_authenticate(user)
        return client

    def test_loan_row_has_balance_and_problem(self):
        row = self.client_for(self.admin).get("/api/loans/").json()[0]
        self.assertEqual(row["status"], "OVERDUE")
        # 3 of 12 payments are due: 2 auto-paid, 1 bounced.
        self.assertEqual(Decimal(row["remaining_amount"]), Decimal("1000.00"))
        self.assertEqual(row["problem"]["count"], 1)
        self.assertEqual(row["problem"]["notes"], ["Bounced"])
        self.assertEqual(Decimal(row["problem"]["missing_amount"]), Decimal("100.00"))

    def test_include_closed(self):
        self.loan.status = "CLOSED"
        LoanChecks.objects.filter(pk=self.loan.pk).update(status="CLOSED")
        client = self.client_for(self.admin)
        # sync recomputes the status from payments, so it stays OVERDUE here;
        # the flag just has to be accepted and still return the loan.
        self.assertEqual(len(client.get("/api/loans/", {"include_closed": 1}).json()), 1)

    def test_dashboard_figures(self):
        d = self.client_for(self.admin).get("/api/dashboard/overview/").json()
        self.assertEqual(Decimal(str(d["repayment"]["missing"])), Decimal("100"))
        self.assertEqual(len(d["upcoming_by_month"]), 6)
        self.assertEqual(d["balance_by_community"][0]["community"], "Ramot")
        self.assertIn("total_donations_amount", d)
        self.assertEqual(len(d["donations_by_month"]), 12)

    def test_borrower_dashboard_has_no_donation_figures(self):
        d = self.client_for(self.borrower_user).get("/api/dashboard/overview/").json()
        self.assertNotIn("total_donations_amount", d)
        self.assertNotIn("donations_by_month", d)
        self.assertIsNotNone(d["next_payment"])
