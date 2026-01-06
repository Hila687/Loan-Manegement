from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Trustee, Borrower, LoanChecks, LoanStandingOrder, Role, UserProfile
from decimal import Decimal, InvalidOperation
from .models import Payment
from rest_framework import serializers
from .models import Payment
#from .models import Trustee, LoanChecks, LoanStandingOrder


# --- Role & UserProfile ---
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

# --- User, Trustee, Borrower ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class TrusteeSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    class Meta:
        model = Trustee
        fields = '__all__'

class BorrowerSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    class Meta:
        model = Borrower
        fields = '__all__'

# --- Loans ---
class LoanChecksSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanChecks
        fields = '__all__'

class LoanStandingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanStandingOrder
        fields = '__all__'
        

class LoanListSerializer(serializers.Serializer):
    """
    Serializer for unified loan list items.

    This serializer is NOT tied to a specific Django model.
    It is used to return a clean, consistent JSON structure
    for both LoanChecks and LoanStandingOrder records.
    """

    # Basic loan fields (common to both loan types)
    loan_id = serializers.UUIDField()  # Unique identifier of the loan
    loan_type = serializers.CharField()  # "checks" or "standing_order"
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)  # Loan amount
    start_date = serializers.DateField()  # When the loan starts
    status = serializers.CharField()  # Current status (e.g., ACTIVE, PAID)

    # Nested data for related entities (already prepared as dictionaries in the view)
    borrower = serializers.DictField()  # Contains borrower info (name, phone, email, etc.)
    trustee = serializers.DictField()   # Contains trustee info (name, community, etc.)

class LoanDetailSerializer(serializers.Serializer):
    """
    Full loan details serializer used for the Loan Details panel.
    Unifies output for both loan types (Checks / Standing Order).
    """

    loan_id = serializers.UUIDField()
    loan_type = serializers.SerializerMethodField()   # <-- FIXED
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    start_date = serializers.DateField()
    status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    form_file_url = serializers.SerializerMethodField()
    trustee_id = serializers.SerializerMethodField()


    # Borrower full details
    borrower = serializers.SerializerMethodField()

    # Trustee full details
    trustee = serializers.SerializerMethodField()

    # Loan-type-specific fields
    details = serializers.SerializerMethodField()

    # ----------------------------------------------------
    # Loan Type (FIXED: previously caused AttributeError)
    # ----------------------------------------------------
    def get_loan_type(self, obj):
        if obj.__class__.__name__ == "LoanChecks":
            return "checks"
        if obj.__class__.__name__ == "LoanStandingOrder":
            return "standing_order"
        return None
    
    # -------------------------------
    # Status (MODEL -> CONTRACT)
    # -------------------------------
    def get_status(self, obj):
        """
        Map model status to contract status.

        Model: PENDING, ACTIVE, PAID, REJECTED
        Contract: ACTIVE, CLOSED, OVERDUE
        """
        if obj.status == "PAID":
            return "CLOSED"

        if obj.status == "ACTIVE":
            return "ACTIVE"

        if obj.status in ("PENDING", "REJECTED"):
            return "ACTIVE"   # keep FE stable in Sprint 3

        return "ACTIVE"
    
    # ----------------------------------------------------
    # Borrower section
    # ----------------------------------------------------
    def get_borrower(self, obj):
        borrower = obj.borrower
        user = borrower.user if borrower.user else None

        return {
            "id_number": borrower.id_number,
            "address": borrower.address,
            "name": user.get_full_name() if user else "",
            "email": user.email if user else "",
            "phone": user.profile.phone if user and hasattr(user, "profile") else "",
            "created_at": borrower.created_at,   # optional but useful
        }

    # ----------------------------------------------------
    # Trustee section
    # ----------------------------------------------------
    def get_trustee(self, obj):
        trustee = obj.trustee
        user = trustee.user if trustee.user else None

        return {
            "name": user.get_full_name() if user else "",
            "community": trustee.community,
            "phone": user.profile.phone if user and hasattr(user, "profile") else "",
            "notes": trustee.notes,
        }

    # ----------------------------------------------------
    # Trustee ID (for frontend edit support)
    # ----------------------------------------------------
    def get_trustee_id(self, obj):
        return str(obj.trustee_id) if obj.trustee_id else None
    
    # ----------------------------------------------------
    # Dynamic loan-type-specific details
    # ----------------------------------------------------
    def get_details(self, obj):
        if obj.__class__.__name__ == "LoanChecks":
            return {
                "num_payments": obj.num_payments,
                "check_details": obj.check_details,
                "predefined_schedule": obj.predefined_schedule,
            }

        if obj.__class__.__name__ == "LoanStandingOrder":
            return {
                "monthly_amount": obj.monthly_amount,
                "charge_day": obj.charge_day,
                "stop_date": obj.stop_date,
            }

        return {}

    # ----------------------------------------------------
    # Form file URL
    # ----------------------------------------------------
    def get_form_file_url(self, obj):
        if obj.form_file:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.form_file.url) if request else obj.form_file.url
        return None

class LoanUpdateSerializer(serializers.Serializer):
    """
    Contract-bound serializer for PUT /api/loans/{loan_id}

    Accepts ONLY:
      amount, start_date, number_of_payments, trustee_id, status

    Validations (per contract):
      amount > 0
      number_of_payments >= 1
      start_date ISO date
      trustee_id exists
      status in { ACTIVE, CLOSED, OVERDUE }

    Returns 400 field-level errors:
      { "amount": ["Must be greater than 0"] }
    """

    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    start_date = serializers.DateField()
    number_of_payments = serializers.IntegerField()
    trustee_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=["ACTIVE", "CLOSED", "OVERDUE"])

    # --- Contract messages ---
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0")
        return value

    def validate_number_of_payments(self, value):
        if value < 1:
            raise serializers.ValidationError("Must be at least 1")
        return value

    def validate_trustee_id(self, value):
        if not Trustee.objects.filter(trustee_id=value).exists():
            raise serializers.ValidationError("Trustee not found")
        return value

    def validate(self, attrs):
        """
        Enforce strict payload: reject unexpected fields.
        """
        request = self.context.get("request")
        if request:
            allowed = {"amount", "start_date", "number_of_payments", "trustee_id", "status"}
            extra = set(request.data.keys()) - allowed
            if extra:
                raise serializers.ValidationError({k: ["Unexpected field"] for k in sorted(extra)})
        return attrs

    # --- Internal mapping: contract status -> model status ---
    def _map_status_to_model(self, contract_status: str) -> str:
        """
        Model choices are: PENDING, ACTIVE, PAID, REJECTED.
        Contract expects: ACTIVE, CLOSED, OVERDUE.

        Sprint 3 approach (no DB schema changes):
          ACTIVE  -> ACTIVE
          CLOSED  -> PAID
          OVERDUE -> ACTIVE  (kept ACTIVE until future status expansion)
        """
        mapping = {
            "ACTIVE": "ACTIVE",
            "CLOSED": "PAID",
            "OVERDUE": "ACTIVE",
        }
        return mapping.get(contract_status, "ACTIVE")

    def update(self, instance, validated_data):
        amount = validated_data["amount"]
        num_payments = validated_data["number_of_payments"]
        trustee_uuid = validated_data["trustee_id"]
        contract_status = validated_data["status"]

        # Common updates (loan-level only)
        instance.amount = amount
        instance.start_date = validated_data["start_date"]
        instance.status = self._map_status_to_model(contract_status)
        instance.trustee = Trustee.objects.get(trustee_id=trustee_uuid)

        # Loan-type translation
        if isinstance(instance, LoanChecks):
            instance.num_payments = num_payments

        elif isinstance(instance, LoanStandingOrder):
            try:
                instance.monthly_amount = (Decimal(amount) / Decimal(num_payments))
            except (InvalidOperation, ZeroDivisionError):
                raise serializers.ValidationError({"number_of_payments": ["Invalid value"]})

        instance.save()
        return instance
    
    def create(self, validated_data):
        raise serializers.ValidationError({"detail": ["Create is not supported"]})

# ----------------------------------------------------
# Create Loan Request Serializers
# Responsible for validating and normalizing incoming data
# for the loan creation flow (POST /api/loans).
# ----------------------------------------------------

class BorrowerCreateSerializer(serializers.Serializer):
    id_number = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    address = serializers.CharField(max_length=255)

class LoanDetailsSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    num_payments = serializers.IntegerField()
    start_date = serializers.DateField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def validate_num_payments(self, value):
        if value < 1:
            raise serializers.ValidationError("Number of payments must be at least 1")
        return value

class CreateLoanRequestSerializer(serializers.Serializer):
    loan_type = serializers.ChoiceField(choices=["checks", "standing_order"])
    borrower = BorrowerCreateSerializer()
    loan = LoanDetailsSerializer()
    trustee_id = serializers.UUIDField()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "payment_id",
            "due_date",
            "amount",
            "amount_paid",
            "status",
            "paid_at",
            "check_number",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    amount_due = serializers.DecimalField(
        source="amount",
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        model = Payment
        fields = [
            "payment_id",
            "due_date",
            "amount_due",
            "amount_paid",
            "status",
        ]
