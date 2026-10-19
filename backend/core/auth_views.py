from django.conf import settings
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth_backends import resolve_login_user
from .credentials import send_credentials
from .otp import OtpError, request_code, verify_code
from .permissions import IsAdminRole, get_role_name
from .services import audit

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect


def serialize_authenticated_user(
    user,
    request=None,
):
    profile = getattr(
        user,
        "profile",
        None,
    )

    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": get_role_name(user),
        # Someone who signed in with an SMS code has no password to
        # change, so never send them to the change-password screen.
        "must_change_password": (
            profile.must_change_password
            if profile
            and not (
                request is not None
                and request.session.get("login_method") == "otp"
            )
            else False
        ),
        "login_method": (
            request.session.get("login_method", "password")
            if request is not None
            else "password"
        ),
        "is_superuser":
            user.is_superuser,
    }


def client_address(
    request,
):
    forwarded = request.META.get(
        "HTTP_X_FORWARDED_FOR",
        "",
    )

    if forwarded:
        return (
            forwarded
            .split(",")[0]
            .strip()
        )

    return request.META.get(
        "REMOTE_ADDR",
        "unknown",
    )


def login_cache_key(
    request,
    username,
):
    ip = client_address(request)

    safe_username = (
        str(username)
        .strip()
        .lower()[:100]
    )

    return (
        f"login-attempts:"
        f"{ip}:"
        f"{safe_username}"
    )


class CsrfView(APIView):
    permission_classes = [
        AllowAny,
    ]

    def get(self, request):
        return Response({
            "csrfToken":
                get_token(request),
        })

@method_decorator(
    csrf_protect,
    name="dispatch",
)
class LoginView(APIView):
    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        username = str(
            request.data.get(
                "username",
                "",
            )
        ).strip()

        password = str(
            request.data.get(
                "password",
                "",
            )
        )

        if not username or not password:
            return Response(
                {
                    "code":
                        "missing_fields",
                    "detail":
                        "Username and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        resolved_user, ambiguous = (
            resolve_login_user(username)
        )

        if ambiguous:
            return Response(
                {
                    "code":
                        "ambiguous_identifier",
                    "detail":
                        "More than one account matches. "
                        "Please sign in with your username.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Count failed attempts per account, so typing the same phone
        # in different formats does not reset the counter.
        cache_key = login_cache_key(
            request,
            (
                f"user:{resolved_user.pk}"
                if resolved_user
                else username
            ),
        )

        attempts = int(
            cache.get(
                cache_key,
                0,
            )
            or 0
        )

        if attempts >= settings.LOGIN_MAX_ATTEMPTS:
            return Response(
                {
                    "code":
                        "too_many_attempts",
                    "detail":
                        "Too many failed login attempts. "
                        "Please try again later."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if (
            user is None
            or not user.is_active
        ):
            cache.set(
                cache_key,
                attempts + 1,
                settings.LOGIN_LOCKOUT_SECONDS,
            )

            return Response(
                {
                    "code":
                        "invalid_credentials",
                    "detail":
                        "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        role = get_role_name(user)

        if role not in {
            "admin",
            "trustee",
            "borrower",
        }:  # donors have no sign-in
            return Response(
                {
                    "code":
                        "no_access",
                    "detail":
                        "This account does not have "
                        "system access."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        cache.delete(cache_key)

        login(
            request,
            user,
        )

        request.session["login_method"] = "password"

        audit(
            user,
            "LOGIN",
            "User",
            user.id,
        )

        return Response(
            serialize_authenticated_user(
                user,
                request,
            )
        )


class LogoutView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        user = request.user

        audit(
            user,
            "LOGOUT",
            "User",
            user.id,
        )

        logout(request)

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class MeView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        return Response(
            serialize_authenticated_user(
                request.user,
                request,
            )
        )


class ChangePasswordView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        current_password = str(
            request.data.get(
                "current_password",
                "",
            )
        )

        new_password = str(
            request.data.get(
                "new_password",
                "",
            )
        )

        if not request.user.check_password(
            current_password
        ):
            return Response(
                {
                    "current_password": [
                        "Current password is incorrect."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(
                new_password,
                request.user,
            )

        except ValidationError as exc:
            return Response(
                {
                    "new_password":
                        list(exc.messages)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(
            new_password
        )

        request.user.save(
            update_fields=[
                "password",
            ]
        )

        profile = getattr(
            request.user,
            "profile",
            None,
        )

        if profile:
            profile.must_change_password = False

            profile.save(
                update_fields=[
                    "must_change_password",
                ]
            )

        update_session_auth_hash(
            request,
            request.user,
        )

        audit(
            request.user,
            "CHANGE_PASSWORD",
            "User",
            request.user.id,
        )

        return Response({
            "detail":
                "Password changed successfully."
        })

class SendCredentialsView(APIView):
    """
    Text a user their login details (SMS or WhatsApp).

    The admin sends back the temporary password that was just shown to
    them. It is only sent if it is still the account's valid, unchanged
    temporary password, so this cannot be used to leak a real password.
    """

    permission_classes = [
        IsAdminRole,
    ]

    def post(self, request):
        from django.contrib.auth.models import User

        username = str(request.data.get("username", "")).strip()
        temporary_password = str(
            request.data.get("temporary_password", "")
        )
        channel = str(
            request.data.get("channel", "SMS")
        ).strip().upper()

        if channel not in {"SMS", "EMAIL"}:
            return Response(
                {"code": "bad_channel", "detail": "Invalid channel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(username=username).first()
        profile = getattr(user, "profile", None) if user else None

        if (
            not user
            or not profile
            or not profile.must_change_password
            or not user.check_password(temporary_password)
        ):
            return Response(
                {
                    "code": "not_temporary",
                    "detail":
                        "These are not the user's current "
                        "temporary login details.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            user.is_superuser
            or get_role_name(user) == "admin"
        ) and not request.user.is_superuser and user != request.user:
            return Response(
                {"code": "forbidden", "detail": "Not allowed."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            sent_to = send_credentials(
                user,
                temporary_password,
                channel,
            )
        except ValueError as exc:
            missing_email = str(exc) == "NO_EMAIL"
            return Response(
                {
                    "code": "no_email" if missing_email else "no_phone",
                    "detail": (
                        "No email address on file."
                        if missing_email
                        else "No phone number on file."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:  # Twilio not configured / API error
            audit(
                request.user,
                "SEND_CREDENTIALS_FAILED",
                "User",
                user.id,
                {"channel": channel, "error": exc.__class__.__name__},
            )
            return Response(
                {
                    "code": "send_failed",
                    "detail": str(exc)[:200],
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        audit(
            request.user,
            "SEND_CREDENTIALS",
            "User",
            user.id,
            {"channel": channel, "to": sent_to},
        )

        return Response({"sent_to": sent_to, "channel": channel})


OTP_MESSAGES = {
    "rate_limited": "Too many code requests. Please try again later.",
    "too_soon": "Please wait a minute before requesting another code.",
    "send_failed": "The code could not be sent. Please contact the Gemach.",
    "invalid_code": "The code is incorrect.",
    "expired": "The code has expired. Please request a new one.",
}


def otp_error_response(exc: OtpError):
    http_status = {
        "rate_limited": status.HTTP_429_TOO_MANY_REQUESTS,
        "too_soon": status.HTTP_429_TOO_MANY_REQUESTS,
        "send_failed": status.HTTP_503_SERVICE_UNAVAILABLE,
    }.get(exc.code, status.HTTP_400_BAD_REQUEST)

    body = {
        "code": exc.code,
        "detail": OTP_MESSAGES.get(exc.code, "Error."),
    }

    if exc.retry_after:
        body["retry_after"] = exc.retry_after

    return Response(body, status=http_status)


def otp_identity(request):
    """(ID number, phone-or-email, channel) from an OTP request body."""
    id_number = str(request.data.get("id_number", "")).strip()
    channel = str(request.data.get("channel", "SMS")).strip().upper()

    if channel == "EMAIL":
        contact = str(request.data.get("email", "")).strip()
    else:
        channel = "SMS"
        contact = str(request.data.get("phone", "")).strip()

    return id_number, contact, channel


@method_decorator(
    csrf_protect,
    name="dispatch",
)
class OtpRequestView(APIView):
    """Step 1: ID number + phone -> a code is texted if they match."""

    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        id_number, contact, channel = otp_identity(request)

        if not id_number or not contact:
            return Response(
                {
                    "code": "missing_fields",
                    "detail": "ID number and phone / email are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = request_code(
                id_number,
                contact,
                channel,
                client_address(request),
            )
        except OtpError as exc:
            return otp_error_response(exc)
        except Exception as exc:  # SMS provider error
            return otp_error_response(OtpError("send_failed"))

        return Response(result)


@method_decorator(
    csrf_protect,
    name="dispatch",
)
class OtpVerifyView(APIView):
    """Step 2: ID number + phone + code -> signed in."""

    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        id_number, contact, channel = otp_identity(request)
        code = str(request.data.get("code", "")).strip()

        try:
            user = verify_code(id_number, contact, code, channel)
        except OtpError as exc:
            return otp_error_response(exc)

        login(
            request,
            user,
            backend="core.auth_backends.FlexibleLoginBackend",
        )

        request.session["login_method"] = "otp"

        audit(
            user,
            "LOGIN_OTP",
            "User",
            user.id,
        )

        return Response(
            serialize_authenticated_user(
                user,
                request,
            )
        )
