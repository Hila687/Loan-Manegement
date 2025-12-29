from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from django.db import transaction
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
from datetime import datetime

from .models import LoanChecks, LoanStandingOrder, Borrower, Trustee, UserProfile
from .serializers import LoanListSerializer, LoanDetailSerializer, LoanUpdateSerializer



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
                "status": "CLOSED" if loan.status == "PAID" else "ACTIVE",
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
                "status": "CLOSED" if loan.status == "PAID" else "ACTIVE",
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
    
    
    def post(self, request):
        """
        POST /api/loans/
        
        Creates a new loan based on the contract:
        {
          "loan_type": "checks" | "standing_order",
          "borrower": {
            "id_number": "string",
            "first_name": "string",
            "last_name": "string",
            "phone": "string",
            "email": "string",
            "address": "string"
          },
          "loan": {
            "amount": number,
            "num_payments": number,
            "start_date": "YYYY-MM-DD"
          },
          "trustee_id": "UUID"
        }
        
        Returns 201 Created with:
        {
          "loan_id": "UUID",
          "loan_type": "checks" | "standing_order",
          "status": "ACTIVE"
        }
        """
        try:
            with transaction.atomic():
                # Validate required fields
                loan_type = request.data.get('loan_type')
                borrower_data = request.data.get('borrower', {})
                loan_data = request.data.get('loan', {})
                trustee_id = request.data.get('trustee_id')
                
                # Validate loan_type
                if loan_type not in ['checks', 'standing_order']:
                    return Response(
                        {'loan_type': 'Must be either "checks" or "standing_order"'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate borrower fields
                id_number = borrower_data.get('id_number')
                if not id_number:
                    return Response(
                        {'borrower.id_number': 'This field is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                first_name = borrower_data.get('first_name', '')
                last_name = borrower_data.get('last_name', '')
                phone = borrower_data.get('phone', '')
                email = borrower_data.get('email', '')
                address = borrower_data.get('address', '')
                
                # Validate loan fields
                amount = loan_data.get('amount')
                num_payments = loan_data.get('num_payments')
                start_date = loan_data.get('start_date')
                
                # Validate and convert amount
                try:
                    amount_decimal = Decimal(str(amount))
                    if amount_decimal <= 0:
                        return Response(
                            {'loan.amount': 'Must be greater than 0'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except (InvalidOperation, TypeError, ValueError):
                    return Response(
                        {'loan.amount': 'Invalid amount value'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate and convert num_payments
                try:
                    num_payments_int = int(num_payments)
                    if num_payments_int < 1:
                        return Response(
                            {'loan.num_payments': 'Must be at least 1'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except (TypeError, ValueError):
                    return Response(
                        {'loan.num_payments': 'Invalid number of payments'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate start_date
                if not start_date:
                    return Response(
                        {'loan.start_date': 'This field is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Parse start_date
                try:
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    return Response(
                        {'loan.start_date': 'Invalid date format. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate trustee
                if not trustee_id:
                    return Response(
                        {'trustee_id': 'This field is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    trustee = Trustee.objects.get(trustee_id=trustee_id)
                except Trustee.DoesNotExist:
                    return Response(
                        {'trustee_id': 'Trustee not found'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Find or create Borrower by id_number
                borrower, created = Borrower.objects.get_or_create(
                    id_number=id_number,
                    defaults={
                        'address': address,
                        'trustee': trustee
                    }
                )
                
                # Update borrower details if already exists
                if not created:
                    borrower.address = address
                    borrower.trustee = trustee
                    borrower.save()
                
                # Create or update associated User for borrower
                if borrower.user:
                    user = borrower.user
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.save()
                    
                    # Update phone in user profile if exists
                    if hasattr(user, 'profile'):
                        user.profile.phone = phone
                        user.profile.save()
                else:
                    # Create new user
                    username = f"borrower_{id_number}"
                    user, _ = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email
                        }
                    )
                    borrower.user = user
                    borrower.save()
                    
                    # Create user profile with phone
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.phone = phone
                    profile.save()
                
                # Calculate monthly_amount and charge_day
                monthly_amount = amount_decimal / num_payments_int
                charge_day = start_date_obj.day
                
                # Create loan based on type
                if loan_type == 'checks':
                    loan = LoanChecks.objects.create(
                        borrower=borrower,
                        trustee=trustee,
                        amount=amount_decimal,
                        start_date=start_date_obj,
                        num_payments=num_payments_int,
                        status='ACTIVE'
                    )
                else:  # standing_order
                    loan = LoanStandingOrder.objects.create(
                        borrower=borrower,
                        trustee=trustee,
                        amount=amount_decimal,
                        start_date=start_date_obj,
                        monthly_amount=monthly_amount,
                        charge_day=charge_day,
                        status='ACTIVE'
                    )
                
                return Response({
                    'loan_id': str(loan.loan_id),
                    'loan_type': loan_type,
                    'status': 'ACTIVE'
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            # Log the error for debugging but don't expose details
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating loan: {str(e)}")
            return Response(
                {'detail': 'An error occurred while creating the loan'},
                status=status.HTTP_400_BAD_REQUEST
            )



# ------------------------------------
#   Loan Detail View (unchanged)
# ------------------------------------

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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
    PUT  /api/loans/{loan_id}  - admin only
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
