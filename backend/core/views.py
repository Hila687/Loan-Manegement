from rest_framework import viewsets
from .models import Borrower, Loan, Trustee
from .serializers import BorrowerSerializer, LoanSerializer, TrusteeSerializer

class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

class TrusteeViewSet(viewsets.ModelViewSet):
    queryset = Trustee.objects.all()
    serializer_class = TrusteeSerializer