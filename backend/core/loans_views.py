from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import LoanChecks, LoanStandingOrder
from .serializers import LoanListSerializer


class LoanListView(APIView):
    """
    GET /loans

    This endpoint returns ONLY ACTIVE loans (for the main loan list screen).
    It pulls data from BOTH loan tables:
        - LoanChecks
        - LoanStandingOrder

    and unifies the output into a single consistent JSON structure.

    Supported filters:
        ?type=checks / standing_orders / all
    (Status is NOT a filter here — always ACTIVE.)

    Steps performed:
    1. Fetch active loans from both tables
    2. Apply optional loan-type filter
    3. Convert each loan into a unified dictionary format
    4. Serialize and return final JSON list
    """

    def get(self, request):

        # Optional type filter
        type_param = request.GET.get("type", None)

        unified_loans = []  # final combined loan list

        # -----------------------------
        #   1. Fetch ACTIVE LoanChecks
        # -----------------------------
        checks_qs = LoanChecks.objects.filter(status="ACTIVE")

        # Apply type filter: include only checks OR all
        if type_param and type_param not in ["all", "checks"]:
            checks_qs = []

        for loan in checks_qs:
            unified_loans.append({
                "loan_id": loan.loan_id,
                "loan_type": "checks",
                "amount": loan.amount,
                "start_date": loan.start_date,
                "status": loan.status,
                "borrower": {
                    "name": loan.borrower.user.first_name if loan.borrower.user else None,
                    "phone": getattr(loan.borrower.user.profile, "phone", None) if loan.borrower.user else None,
                    "email": loan.borrower.user.email if loan.borrower.user else None,
                },
                "trustee": {
                    "name": loan.trustee.user.first_name if loan.trustee else None,
                    "community": loan.trustee.community if loan.trustee else None,
                }
            })

        # ---------------------------------------
        #   2. Fetch ACTIVE LoanStandingOrder
        # ---------------------------------------
        standing_qs = LoanStandingOrder.objects.filter(status="ACTIVE")

        # Apply type filter: include only standing orders OR all
        if type_param and type_param not in ["all", "standing_orders"]:
            standing_qs = []

        for loan in standing_qs:
            unified_loans.append({
                "loan_id": loan.loan_id,
                "loan_type": "standing_order",
                "amount": loan.amount,
                "start_date": loan.start_date,
                "status": loan.status,
                "borrower": {
                    "name": loan.borrower.user.first_name if loan.borrower.user else None,
                    "phone": getattr(loan.borrower.user.profile, "phone", None) if loan.borrower.user else None,
                    "email": loan.borrower.user.email if loan.borrower.user else None,
                },
                "trustee": {
                    "name": loan.trustee.user.first_name if loan.trustee else None,
                    "community": loan.trustee.community if loan.trustee else None,
                }
            })

        # ------------------------
        #   3. Serialize + Return
        # ------------------------
        serializer = LoanListSerializer(unified_loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
