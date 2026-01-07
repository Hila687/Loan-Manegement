from datetime import date

from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import LoanChecks, LoanStandingOrder, Payment
from .serializers import PaymentSerializer


class LoanPaymentsView(APIView):
    def get(self, request, loan_id):

        # 1. מציאת ההלוואה (צ'קים או הוראת קבע)
        loan_checks = LoanChecks.objects.filter(loan_id=loan_id).first()
        loan_standing = LoanStandingOrder.objects.filter(loan_id=loan_id).first()

        if not loan_checks and not loan_standing:
            return Response(
                {"detail": "Loan not found"},
                status=404
            )

        loan = loan_checks if loan_checks else loan_standing

        # 2. שליפת התשלומים באמצעות GenericForeignKey
        loan_content_type = ContentType.objects.get_for_model(loan)

        payments = Payment.objects.filter(
            content_type=loan_content_type,
            object_id=loan.loan_id
        ).order_by("due_date")

        # 3. עדכון אוטומטי של סטטוס תשלומים שהיו אמורים להיות משולמים
        today = date.today()
        for payment in payments:
            if payment.status == Payment.STATUS_PENDING and payment.due_date <= today:
                payment.status = Payment.STATUS_PAID
                payment.amount_paid = payment.amount
                payment.save()

        # 4. חישוב סיכום
        total_payments = payments.count()
        paid_payments = payments.filter(status=Payment.STATUS_PAID).count()

        total_amount = sum(p.amount for p in payments)
        paid_amount = sum(p.amount_paid for p in payments)

        summary = {
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "total_payments": total_payments,
            "paid_payments": paid_payments,
        }

        # 5. Serializer + Response
        serializer = PaymentSerializer(payments, many=True)

        return Response({
            "loan_id": loan_id,
            "summary": summary,
            "payments": serializer.data
        })
