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

from .permissions import get_role_name
from .services import audit

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect


def serialize_authenticated_user(
    user,
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
        "must_change_password": (
            profile.must_change_password
            if profile
            else False
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
                    "detail":
                        "Username and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = login_cache_key(
            request,
            username,
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
            "donor",
        }:
            return Response(
                {
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

        audit(
            user,
            "LOGIN",
            "User",
            user.id,
        )

        return Response(
            serialize_authenticated_user(
                user
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
                request.user
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