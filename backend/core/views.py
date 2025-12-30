from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum

from .models import (
    Borrower,
    Trustee,
    LoanChecks,
    LoanStandingOrder,
    Role,
    UserProfile
)
from .serializers import (
    BorrowerSerializer,
    TrusteeSerializer,
    LoanChecksSerializer,
    LoanStandingOrderSerializer,
    RoleSerializer,
    UserProfileSerializer
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


class DashboardLoanSummaryView(APIView):
    """
    GET /api/dashboard/loan-summary/
    Returns aggregated data for the Home dashboard.
    """

    def get(self, request):
        active_checks = LoanChecks.objects.filter(status="ACTIVE")
        active_standing_orders = LoanStandingOrder.objects.filter(status="ACTIVE")

        active_loans_count = (
            active_checks.count() +
            active_standing_orders.count()
        )

        total_active_loans_amount = (
            (active_checks.aggregate(total=Sum("amount"))["total"] or 0) +
            (active_standing_orders.aggregate(total=Sum("amount"))["total"] or 0)
        )

        return Response({
            "active_loans_count": active_loans_count,
            "total_active_loans_amount": total_active_loans_amount
        })
