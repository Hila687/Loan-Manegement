from django.contrib import admin
import os

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from core.auth_views import (
    AuthConfigView,
    ChangePasswordView,
    CsrfView,
    LoginView,
    LogoutView,
    MeView,
    OtpRequestView,
    OtpVerifyView,
    SendCredentialsView,
)
from core.loans_views import (
    LoanDetailView,
    LoanListView,
    LoanSignedFormView,
    LoanStandingOrderFormView,
)
from core.payments_views import (
    LoanPaymentsView,
    PaymentExceptionView,
)
from core.reminders_views import RunRemindersView
from core.spa_views import health, spa_index
from core.reports_views import ManagementReportView
from core.views import (
    AdminUserViewSet,
    BorrowerViewSet,
    DashboardLoanSummaryView,
    DashboardOverviewView,
    DonationViewSet,
    DonorViewSet,
    ReminderSettingsView,
    RoleViewSet,
    TrusteeViewSet,
    UserProfileViewSet,
)


router = DefaultRouter()

router.register(
    r"roles",
    RoleViewSet,
    basename="roles",
)

router.register(
    r"user-profiles",
    UserProfileViewSet,
    basename="user-profiles",
)

router.register(
    r"borrowers",
    BorrowerViewSet,
    basename="borrowers",
)

router.register(
    r"trustees",
    TrusteeViewSet,
    basename="trustees",
)

router.register(
    r"donors",
    DonorViewSet,
    basename="donors",
)

router.register(
    r"donations",
    DonationViewSet,
    basename="donations",
)

router.register(
    r"admin-users",
    AdminUserViewSet,
    basename="admin-users",
)


urlpatterns = [
    # Django's own admin; the path can be moved with DJANGO_ADMIN_URL.
    path(
        os.getenv("DJANGO_ADMIN_URL", "admin/"),
        admin.site.urls,
    ),

    path(
        "api/health/",
        health,
        name="health",
    ),

    path(
        "api/",
        include(router.urls),
    ),

    path(
        "api/auth/config/",
        AuthConfigView.as_view(),
        name="auth-config",
    ),

    path(
        "api/auth/csrf/",
        CsrfView.as_view(),
        name="auth-csrf",
    ),

    path(
        "api/auth/login/",
        LoginView.as_view(),
        name="auth-login",
    ),

    path(
        "api/auth/logout/",
        LogoutView.as_view(),
        name="auth-logout",
    ),

    path(
        "api/auth/me/",
        MeView.as_view(),
        name="auth-me",
    ),

    path(
        "api/auth/change-password/",
        ChangePasswordView.as_view(),
        name="auth-change-password",
    ),

    path(
        "api/auth/otp/request/",
        OtpRequestView.as_view(),
        name="auth-otp-request",
    ),

    path(
        "api/auth/otp/verify/",
        OtpVerifyView.as_view(),
        name="auth-otp-verify",
    ),

    path(
        "api/auth/send-credentials/",
        SendCredentialsView.as_view(),
        name="auth-send-credentials",
    ),

    path(
        "api/loans/",
        LoanListView.as_view(),
        name="loan-list",
    ),

    path(
        "api/loans/<uuid:loan_id>/",
        LoanDetailView.as_view(),
        name="loan-detail",
    ),

    path(
        "api/loans/<uuid:loan_id>/signed-form/",
        LoanSignedFormView.as_view(),
        name="loan-signed-form",
    ),

    path(
        "api/loans/<uuid:loan_id>/standing-order-form/",
        LoanStandingOrderFormView.as_view(),
        name="loan-standing-order-form",
    ),

    path(
        "api/loans/<uuid:loan_id>/payments/",
        LoanPaymentsView.as_view(),
        name="loan-payments",
    ),

    path(
        "api/payments/<uuid:payment_id>/exception/",
        PaymentExceptionView.as_view(),
        name="payment-exception",
    ),

    path(
        "api/dashboard/loan-summary/",
        DashboardLoanSummaryView.as_view(),
        name="dashboard-loan-summary",
    ),

    path(
        "api/dashboard/overview/",
        DashboardOverviewView.as_view(),
        name="dashboard-overview",
    ),

    path(
        "api/reports/summary/",
        ManagementReportView.as_view(),
        name="management-report",
    ),

    path(
        "api/reminders/settings/",
        ReminderSettingsView.as_view(),
        name="reminder-settings",
    ),

    path(
        "api/reminders/run/",
        RunRemindersView.as_view(),
        name="reminders-run",
    ),

    # Everything else is a page of the Vue app (must stay last).
    re_path(
        r"^(?!api/|static/|assets/|"
        + os.getenv("DJANGO_ADMIN_URL", "admin/").rstrip("/")
        + r"(/|$)).*$",
        spa_index,
        name="spa",
    ),
]
