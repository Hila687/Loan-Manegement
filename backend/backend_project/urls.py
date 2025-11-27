from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    BorrowerViewSet, TrusteeViewSet, LoanChecksViewSet, 
    LoanStandingOrderViewSet, RoleViewSet, UserProfileViewSet
)
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'user-profiles', UserProfileViewSet)
router.register(r'borrowers', BorrowerViewSet)
router.register(r'trustees', TrusteeViewSet)
router.register(r'loans/checks', LoanChecksViewSet, basename='loan-checks')
router.register(r'loans/standing-order', LoanStandingOrderViewSet, basename='loan-standing-order')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)