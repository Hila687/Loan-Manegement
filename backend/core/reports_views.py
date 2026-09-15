from datetime import date
from decimal import Decimal

from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Donation,
    LoanChecks,
    LoanStandingOrder,
)
from .permissions import IsAdminRole
from .services import sync_loan_querysets

def parse_date_parameter(
    value,
    field_name,
):
    if not value:
        return None

    try:
        return date.fromisoformat(value)

    except ValueError:
        raise ValueError(
            f"{field_name} must use YYYY-MM-DD format."
        )


class ManagementReportView(APIView):
    permission_classes = [
        IsAdminRole,
    ]

    def get(self, request):
        trustee_id = request.GET.get(
            "trustee_id"
        )

        borrower_id = request.GET.get(
            "borrower_id"
        )

        try:
            start_date = (
                parse_date_parameter(
                    request.GET.get(
                        "start_date"
                    ),
                    "start_date",
                )
            )

            end_date = (
                parse_date_parameter(
                    request.GET.get(
                        "end_date"
                    ),
                    "end_date",
                )
            )

        except ValueError as exc:
            return Response(
                {
                    "detail":
                        str(exc)
                },
                status=
                    status.HTTP_400_BAD_REQUEST,
            )

        if (
            start_date
            and end_date
            and start_date > end_date
        ):
            return Response(
                {
                    "detail":
                        "start_date cannot be after end_date."
                },
                status=
                    status.HTTP_400_BAD_REQUEST,
            )

        checks = (
            LoanChecks.objects
            .select_related(
                "borrower",
                "trustee__user",
            )
            .all()
        )

        standing = (
            LoanStandingOrder.objects
            .select_related(
                "borrower",
                "trustee__user",
            )
            .all()
        )

        sync_loan_querysets(
            checks,
            standing,
        )

        donations = (
            Donation.objects
            .select_related(
                "donor__user"
            )
            .all()
        )

        if trustee_id:
            checks = checks.filter(
                trustee_id=trustee_id
            )

            standing = standing.filter(
                trustee_id=trustee_id
            )

        if borrower_id:
            checks = checks.filter(
                borrower_id=borrower_id
            )

            standing = standing.filter(
                borrower_id=borrower_id
            )

        if start_date:
            checks = checks.filter(
                start_date__gte=start_date
            )

            standing = standing.filter(
                start_date__gte=start_date
            )

            donations = donations.filter(
                donation_date__gte=start_date
            )

        if end_date:
            checks = checks.filter(
                start_date__lte=end_date
            )

            standing = standing.filter(
                start_date__lte=end_date
            )

            donations = donations.filter(
                donation_date__lte=end_date
            )

        def loan_row(
            loan,
            loan_type,
        ):
            borrower_name = (
                f"{loan.borrower.first_name or ''} "
                f"{loan.borrower.last_name or ''}"
            ).strip()

            trustee_name = ""

            if loan.trustee:
                trustee_name = (
                    loan.trustee.user.get_full_name()
                    or loan.trustee.user.username
                )

            return {
                "loan_id":
                    str(loan.loan_id),

                "loan_type":
                    loan_type,

                "borrower_id":
                    str(loan.borrower_id),

                "borrower_name":
                    borrower_name,

                "trustee_id":
                    (
                        str(loan.trustee_id)
                        if loan.trustee_id
                        else None
                    ),

                "trustee_name":
                    trustee_name,

                "community":
                    (
                        loan.trustee.community
                        if loan.trustee
                        else ""
                    ),

                "amount":
                    loan.amount,

                "start_date":
                    loan.start_date,

                "status":
                    loan.status,
            }

        rows = [
            loan_row(
                loan,
                "checks",
            )
            for loan in checks
        ]

        rows.extend(
            loan_row(
                loan,
                "standing_order",
            )
            for loan in standing
        )

        rows.sort(
            key=lambda item: (
                item["start_date"],
                item["loan_id"],
            ),
            reverse=True,
        )

        total_loan_amount = sum(
            (
                row["amount"]
                for row in rows
            ),
            Decimal("0.00"),
        )

        donation_total = (
            donations.aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        return Response(
            {
                "filters": {
                    "trustee_id":
                        trustee_id,

                    "borrower_id":
                        borrower_id,

                    "start_date":
                        (
                            start_date.isoformat()
                            if start_date
                            else None
                        ),

                    "end_date":
                        (
                            end_date.isoformat()
                            if end_date
                            else None
                        ),
                },

                "summary": {
                    "loans_count":
                        len(rows),

                    "loans_amount":
                        total_loan_amount,

                    "donations_amount":
                        donation_total,
                },

                "loans":
                    rows,
            },
            status=status.HTTP_200_OK,
        )