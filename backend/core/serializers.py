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
