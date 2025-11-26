from rest_framework import viewsets
from .models import Borrower, Trustee, LoanChecks, LoanStandingOrder
from .serializers import BorrowerSerializer, TrusteeSerializer, LoanChecksSerializer, LoanStandingOrderSerializer

# --- ViewSets (מנהלי הבקשות) ---

class BorrowerViewSet(viewsets.ModelViewSet):
    """
    מטפל בלווים (יצירה, צפייה, עדכון)
    כתובת: /api/borrowers/
    """
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer

class TrusteeViewSet(viewsets.ModelViewSet):
    """
    מטפל בנאמנים
    כתובת: /api/trustees/
    """
    queryset = Trustee.objects.all()
    serializer_class = TrusteeSerializer

class LoanChecksViewSet(viewsets.ModelViewSet):
    """
    מטפל בהלוואות בצ'קים
    כתובת: /api/loans/checks/
    """
    queryset = LoanChecks.objects.all()
    serializer_class = LoanChecksSerializer

class LoanStandingOrderViewSet(viewsets.ModelViewSet):
    """
    מטפל בהלוואות בהוראת קבע
    כתובת: /api/loans/standing-order/
    """
    queryset = LoanStandingOrder.objects.all()
    serializer_class = LoanStandingOrderSerializer