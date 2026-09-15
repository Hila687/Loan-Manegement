from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .loan_access import find_scoped_loan
from .models import Payment
from .permissions import IsAdminRole
from .serializers import (
    PaymentExceptionSerializer,
    PaymentSerializer,
)
from .services import (
    audit,
    get_payment_queryset_for_loan,
    sync_payment_statuses_and_loan,
)


class LoanPaymentsView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        loan_id,
    ):
        loan = find_scoped_loan(
            request.user,
            loan_id,
        )

        if not loan:
            return Response(
                {
                    "detail":
                        "Loan not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        sync_payment_statuses_and_loan(
            loan
        )

        payments = (
            get_payment_queryset_for_loan(
                loan
            ).order_by(
                "due_date"
            )
        )

        total_amount = sum(
            (
                payment.amount
                for payment
                in payments
            ),
            Decimal("0.00"),
        )

        paid_amount = sum(
            (
                payment.amount_paid
                for payment
                in payments
            ),
            Decimal("0.00"),
        )

        return Response({
            "loan_id":
                str(loan.loan_id),

            "loan_status":
                loan.status,

            "summary": {
                "total_amount":
                    total_amount,

                "paid_amount":
                    paid_amount,

                "total_payments":
                    payments.count(),

                "paid_payments":
                    payments.filter(
                        status=
                            Payment.STATUS_PAID
                    ).count(),

                "late_payments":
                    payments.filter(
                        status=
                            Payment.STATUS_LATE
                    ).count(),
            },

            "payments":
                PaymentSerializer(
                    payments,
                    many=True,
                ).data,
        })


class PaymentExceptionView(APIView):
    permission_classes = [
        IsAdminRole,
    ]

    @transaction.atomic
    def patch(
        self,
        request,
        payment_id,
    ):
        payment = (
            Payment.objects
            .select_for_update()
            .filter(
                pk=payment_id
            )
            .first()
        )

        if not payment:
            return Response(
                {
                    "detail":
                        "Payment not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        loan = payment.loan

        serializer = (
            PaymentExceptionSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = (
            serializer.validated_data
        )

        if data.get(
            "clear_exception"
        ):
            payment.is_manual_exception = False
            payment.exception_note = ""

            payment.save(
                update_fields=[
                    "is_manual_exception",
                    "exception_note",
                ]
            )

            sync_payment_statuses_and_loan(
                loan
            )

            audit(
                request.user,
                "CLEAR_PAYMENT_EXCEPTION",
                "Payment",
                payment.id,
            )

            return Response(
                PaymentSerializer(
                    payment
                ).data
            )

        payment.is_manual_exception = True

        payment.exception_note = (
            data["note"].strip()
        )

        payment.status = data[
            "status"
        ]

        if (
            payment.status
            == Payment.STATUS_PAID
        ):
            payment.amount_paid = (
                data.get(
                    "amount_paid",
                    payment.amount,
                )
            )

            payment.paid_at = (
                payment.paid_at
                or timezone.now()
            )

        elif (
            payment.status
            == Payment.STATUS_LATE
        ):
            payment.amount_paid = (
                data.get(
                    "amount_paid",
                    Decimal("0.00"),
                )
            )

            payment.paid_at = None

        else:
            payment.amount_paid = (
                data.get(
                    "amount_paid",
                    Decimal("0.00"),
                )
            )

            payment.paid_at = None

        if (
            payment.amount_paid
            > payment.amount
        ):
            return Response(
                {
                    "amount_paid": [
                        "Amount paid cannot exceed "
                        "the scheduled amount."
                    ]
                },
                status=
                    status.HTTP_400_BAD_REQUEST,
            )

        payment.save()

        sync_payment_statuses_and_loan(
            loan
        )

        audit(
            request.user,
            "SET_PAYMENT_EXCEPTION",
            "Payment",
            payment.id,
            {
                "status":
                    payment.status
            },
        )

        return Response(
            PaymentSerializer(
                payment
            ).data
        )