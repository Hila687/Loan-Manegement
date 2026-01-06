from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import LoanChecks, LoanStandingOrder, Payment
from .serializers import PaymentSerializer
from datetime import date


class LoanPaymentsView(APIView):
    def get(self, request, loan_id):

        # Finding the loan (checks or direct debit)
        loan_checks = LoanChecks.objects.filter(loan_id=loan_id).first()
        loan_standing = LoanStandingOrder.objects.filter(loan_id=loan_id).first()

        if not loan_checks and not loan_standing:
            return Response(
                {"detail": "Loan not found"},
                status=404
            )

        # Retrieving payments
        if loan_checks:
            payments = Payment.objects.filter(
                loan_checks=loan_checks
            ).order_by("due_date")
        else:
            payments = Payment.objects.filter(
                loan_standing_order=loan_standing
            ).order_by("due_date")
        
        # Update the status of payments that were supposed to be made to date
        today = date.today()
        for payment in payments:
            if payment.status == "PENDING" and payment.due_date <= today:
                payment.status = "PAID"
                payment.amount_paid = payment.amount
                payment.save()

        # Summary calculations
        total_payments = payments.count()
        paid_payments = payments.filter(status="PAID").count()

        total_amount = sum(p.amount for p in payments)
        paid_amount = sum(p.amount_paid for p in payments)
        summary = {
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "total_payments": total_payments,
            "paid_payments": paid_payments,
        }


        # Serializer
        serializer = PaymentSerializer(payments, many=True)

        # Response
        return Response({
            "loan_id": loan_id,
            "summary": summary,
            "payments": serializer.data
        })



