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