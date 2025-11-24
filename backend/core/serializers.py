from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Trustee, Borrower, Loan, LoanChecks, LoanStandingOrder

# --- 1. User Serializer ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

# --- 2. Trustee Serializer ---
class TrusteeSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Trustee
        fields = '__all__'

# --- 3. Borrower Serializer ---
class BorrowerSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Borrower
        fields = '__all__'

# --- 4. Loan Serializers ---
class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class LoanChecksSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanChecks
        fields = '__all__'

class LoanStandingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanStandingOrder
        fields = '__all__'