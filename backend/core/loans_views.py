from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import LoanChecks, LoanStandingOrder
from .serializers import LoanListSerializer, LoanDetailSerializer


class LoanListView(APIView):
    """
    GET /loans

    Returns ONLY ACTIVE loans (for the main loan list screen).
    Supports optional filtering by loan type and **text search**.
    """

    def get(self, request):

        # Optional type filter (?type=checks / standing_orders / all)
        type_param = request.GET.get("type", None)

        # Optional search text (?search=yael / 050 / trustee name ...)
        search_param = request.GET.get("search", "").strip().lower()

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
        if type_param and type_param not in ["all", "standing_orders", "standing_order"]:
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

        # ----------------------------------------------------
        #   3. Apply free-text search (if ?search= was given)
        # ----------------------------------------------------
        if search_param:
            def matches(loan):
                """
                Returns True if the search query appears in:
                - borrower name
                - borrower phone
                - borrower email
                - trustee name
                - trustee community
                """
                borrower = loan.get("borrower", {})
                trustee = loan.get("trustee", {})

                fields = [
                    borrower.get("name") or "",
                    borrower.get("phone") or "",
                    borrower.get("email") or "",
                    trustee.get("name") or "",
                    trustee.get("community") or "",
                ]

                # Case-insensitive substring match
                return any(search_param in str(value).lower() for value in fields)

            # keep only loans that match the search
            unified_loans = [loan for loan in unified_loans if matches(loan)]

        # ------------------------
        #   4. Serialize + Return
        # ------------------------
        serializer = LoanListSerializer(unified_loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# ------------------------------------
#   Loan Detail View (unchanged)
# ------------------------------------

class LoanDetailView(APIView):
    """
    Returns full loan details for a given loan_id.
    Supports both LoanChecks and LoanStandingOrder.
    """

    def get(self, request, loan_id):

        loan = None
        loan_type = None  # Set default

        # Try LoanChecks first
        try:
            loan = LoanChecks.objects.get(loan_id=loan_id)
            loan_type = "checks"
        except LoanChecks.DoesNotExist:
            pass

        # Try StandingOrder next
        if loan is None:
            try:
                loan = LoanStandingOrder.objects.get(loan_id=loan_id)
                loan_type = "standing_order"
            except LoanStandingOrder.DoesNotExist:
                return Response(
                    {"detail": "Loan not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Serialize full details
        serializer = LoanDetailSerializer(
            loan,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
