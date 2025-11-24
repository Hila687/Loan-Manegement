from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import BorrowerViewSet, LoanViewSet, TrusteeViewSet


router = DefaultRouter()
router.register(r'borrowers', BorrowerViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'trustees', TrusteeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    

    path('api/', include(router.urls)),
]