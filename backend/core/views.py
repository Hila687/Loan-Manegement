from rest_framework import viewsets
from .models import Borrower, Trustee, LoanChecks, LoanStandingOrder, Role, UserProfile
from .serializers import (
    BorrowerSerializer, TrusteeSerializer, LoanChecksSerializer, 
    LoanStandingOrderSerializer, RoleSerializer, UserProfileSerializer
)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer

class TrusteeViewSet(viewsets.ModelViewSet):
    queryset = Trustee.objects.all()
    serializer_class = TrusteeSerializer

class LoanChecksViewSet(viewsets.ModelViewSet):
    queryset = LoanChecks.objects.all()
    serializer_class = LoanChecksSerializer

class LoanStandingOrderViewSet(viewsets.ModelViewSet):
    queryset = LoanStandingOrder.objects.all()
    serializer_class = LoanStandingOrderSerializer