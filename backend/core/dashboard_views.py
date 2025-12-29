from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count

from .models import LoanChecks, LoanStandingOrder


class LoanSummaryView(APIView):
    """
    GET /api/dashboard/loan-summary/
    
    Returns aggregated statistics for ACTIVE loans only:
    - active_loans_count: Total count of active loans (LoanChecks + LoanStandingOrder)
    - total_active_loans_amount: Total sum of amounts for active loans
    
    Always returns HTTP 200.
    If no active loans exist, returns zeros.
    """
    
    def get(self, request):
        # Count active LoanChecks
        checks_count = LoanChecks.objects.filter(status='ACTIVE').count()
        
        # Count active LoanStandingOrder
        standing_order_count = LoanStandingOrder.objects.filter(status='ACTIVE').count()
        
        # Sum amounts for active LoanChecks
        checks_amount = LoanChecks.objects.filter(status='ACTIVE').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Sum amounts for active LoanStandingOrder
        standing_order_amount = LoanStandingOrder.objects.filter(status='ACTIVE').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Combine counts and amounts
        total_count = checks_count + standing_order_count
        total_amount = checks_amount + standing_order_amount
        
        return Response({
            'active_loans_count': total_count,
            'total_active_loans_amount': float(total_amount)
        }, status=status.HTTP_200_OK)
