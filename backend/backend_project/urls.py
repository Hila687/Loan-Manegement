from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.views import (
    BorrowerViewSet, TrusteeViewSet, LoanChecksViewSet, 
    LoanStandingOrderViewSet, RoleViewSet, UserProfileViewSet
)

# Import Sprint 2 loan views
from core.loans_views import LoanListView, LoanDetailView

# Import dashboard views
from core.dashboard_views import LoanSummaryView

from django.conf import settings
from django.conf.urls.static import static


# -------------------------------
# Router for standard CRUD APIs
# -------------------------------
router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'user-profiles', UserProfileViewSet)
router.register(r'borrowers', BorrowerViewSet)
router.register(r'trustees', TrusteeViewSet)
router.register(r'loans/checks', LoanChecksViewSet, basename='loan-checks')
router.register(r'loans/standing-order', LoanStandingOrderViewSet, basename='loan-standing-order')


# -------------------------------
# URL Patterns
# -------------------------------
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # All router-generated endpoints
    path('api/', include(router.urls)),

    # Unified loan list endpoint
    path('api/loans/', LoanListView.as_view(), name='loan-list'),

    # Full loan detail endpoint
    path('api/loans/<uuid:loan_id>/', LoanDetailView.as_view(), name='loan-detail'),

    # Dashboard loan summary endpoint
    path('api/dashboard/loan-summary/', LoanSummaryView.as_view(), name='loan-summary'),
]


# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
