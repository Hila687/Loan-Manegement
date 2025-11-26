from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Trustee, Borrower, LoanChecks, LoanStandingOrder

# --- User & Trustee ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class TrusteeSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    class Meta:
        model = Trustee
        fields = '__all__'

# --- Borrower ---
class BorrowerSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    class Meta:
        model = Borrower
        fields = '__all__'

# --- Loan Serializers (Checks & Standing Order) ---
# עכשיו יש לנו סירליאייזר נפרד לכל סוג

class LoanChecksSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanChecks
        fields = '__all__'

class LoanStandingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanStandingOrder
        fields = '__all__'