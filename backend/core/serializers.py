from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Trustee, Borrower, LoanChecks, LoanStandingOrder, Role, UserProfile

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
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    form_file_url = serializers.SerializerMethodField()

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
