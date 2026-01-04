from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Borrower, Trustee, LoanChecks, LoanStandingOrder
from .serializers import LoanListSerializer, LoanDetailSerializer, LoanUpdateSerializer,CreateLoanRequestSerializer


# ------------------------------------
#   Loan List View (edited) 
# ------------------------------------
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

        def resolve_borrower_fields(borrower):
            user = borrower.user if borrower else None

            # name
            first = (borrower.first_name or "").strip() if borrower else ""
            last = (borrower.last_name or "").strip() if borrower else ""
            name_from_borrower = f"{first} {last}".strip()
            if name_from_borrower:
                name = name_from_borrower
            elif user:
                name = (user.get_full_name() or "").strip()
            else:
                name = ""

            # phone
            if borrower and borrower.phone:
                phone = borrower.phone
            elif user and hasattr(user, "profile") and getattr(user.profile, "phone", None):
                phone = user.profile.phone
            else:
                phone = ""

            # email
            if borrower and borrower.email:
                email = borrower.email
            elif user and user.email:
                email = user.email
            else:
                email = ""

            return name, phone, email
        
        # -----------------------------
        #   1. Fetch ACTIVE LoanChecks
        # -----------------------------
        checks_qs = LoanChecks.objects.filter(status="ACTIVE")

        # Apply type filter: include only checks OR all
        if type_param and type_param not in ["all", "checks"]:
            checks_qs = []

        for loan in checks_qs:
            b_name, b_phone, b_email = resolve_borrower_fields(loan.borrower)
            unified_loans.append({
                "loan_id": loan.loan_id,
                "loan_type": "checks",
                "amount": loan.amount,
                "start_date": loan.start_date,
                "status": "CLOSED" if loan.status == "PAID" else "ACTIVE",
                "borrower": {
                    "name": b_name,
                    "phone": b_phone,
                    "email": b_email,
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
            b_name, b_phone, b_email = resolve_borrower_fields(loan.borrower)
            unified_loans.append({
                "loan_id": loan.loan_id,
                "loan_type": "standing_order",
                "amount": loan.amount,
                "start_date": loan.start_date,
                "status": "CLOSED" if loan.status == "PAID" else "ACTIVE",
                "borrower": {
                    "name": b_name, 
                    "phone": b_phone,
                    "email": b_email,
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
    
    """
    POST /api/loans/
    Create a new loan (Checks or Standing Order).

    Flow:
    - Validate request payload
    - Locate or create Borrower
    - Create Loan by type
    - Wrap entire flow in a transaction
    - Return success response
    """

    def post(self, request):
        # ----------------------------------------------------
        # Step 1: Validate request data (BE-2)
        # ----------------------------------------------------
        serializer = CreateLoanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # ----------------------------------------------------
        # Step 2: Atomic transaction (BE-5)
        # ----------------------------------------------------
        with transaction.atomic():

            # ------------------------------------------------
            # Step 3: Locate or Create Borrower (BE-3)
            # ------------------------------------------------
            borrower_data = data["borrower"]
            trustee_id = data["trustee_id"]

            borrower = Borrower.objects.filter(
                id_number=borrower_data["id_number"]
            ).first()

            if borrower:
                # Update existing borrower
                borrower.first_name = borrower_data.get("first_name")
                borrower.last_name = borrower_data.get("last_name")
                borrower.phone = borrower_data.get("phone")
                borrower.email = borrower_data.get("email")
                borrower.address = borrower_data.get("address")
            else:
                # Create new borrower
                borrower = Borrower(
                    id_number=borrower_data["id_number"],
                    first_name=borrower_data.get("first_name"),
                    last_name=borrower_data.get("last_name"),
                    phone=borrower_data.get("phone"),
                    email=borrower_data.get("email"),
                    address=borrower_data.get("address"),
                )

            # Update borrower trustee (latest trustee)
            borrower.trustee_id = trustee_id
            borrower.save()


            # ------------------------------------------------
            # Step 4: Validate & fetch Trustee
            # ------------------------------------------------
            try:
                trustee = Trustee.objects.get(trustee_id=trustee_id)
            except Trustee.DoesNotExist:
                return Response(
                    {"detail": "Trustee not found"},
                    status=status.HTTP_404_NOT_FOUND
                )       


            # ------------------------------------------------
            # Step 5: Create Loan by type (BE-4)
            # ------------------------------------------------
            loan_type = data["loan_type"]
            loan_data = data["loan"]

            if loan_type == "checks":
                loan = LoanChecks.objects.create(
                    borrower=borrower,
                    trustee_id=trustee_id,
                    amount=loan_data["amount"],
                    start_date=loan_data["start_date"],
                    num_payments=loan_data["num_payments"],
                    status="ACTIVE",
                )

            elif loan_type == "standing_order":
                monthly_amount = loan_data["amount"] / loan_data["num_payments"]
                charge_day = loan_data["start_date"].day

                loan = LoanStandingOrder.objects.create(
                    borrower=borrower,
                    trustee_id=trustee_id,
                    amount=loan_data["amount"],
                    start_date=loan_data["start_date"],
                    monthly_amount=monthly_amount,
                    charge_day=charge_day,
                    status="ACTIVE",
                )


        # ----------------------------------------------------
        # Step 6: Success response (BE-6)
        # ----------------------------------------------------
        return Response(
            {
                "loan_id": str(loan.loan_id),
                "loan_type": loan_type,
                "status": "ACTIVE",
            },
            status=status.HTTP_201_CREATED
        )




# ------------------------------------
#   Loan Detail View (unchanged)
# ------------------------------------
@method_decorator(csrf_exempt, name="dispatch")
class LoanDetailView(APIView):
    """
    GET  /api/loans/{loan_id}
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
                    {"detail": "Loan not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Serialize full details
        serializer = LoanDetailSerializer(
            loan,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
    


    """
    PUT  /api/loans/{loan_id}  - admin only (currently disabled)
    """
    def get_permissions(self):
        # if self.request.method == "PUT":
        #     return [IsAdminUser()]
        # return [AllowAny()]
        return [AllowAny()]

    def put(self, request, loan_id):
        # Find loan
        try:
            loan = LoanChecks.objects.get(loan_id=loan_id)
        except LoanChecks.DoesNotExist:
            try:
                loan = LoanStandingOrder.objects.get(loan_id=loan_id)
            except LoanStandingOrder.DoesNotExist:
                return Response({"detail": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LoanUpdateSerializer(
            instance=loan,
            data=request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        serializer = LoanDetailSerializer(loan, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
