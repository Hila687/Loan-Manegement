from rest_framework.permissions import BasePermission


ROLE_ADMIN = "admin"
ROLE_TRUSTEE = "trustee"
ROLE_BORROWER = "borrower"
ROLE_DONOR = "donor"


def get_role_name(user):
    if not user or not user.is_authenticated:
        return None

    if user.is_superuser:
        return ROLE_ADMIN

    profile = getattr(user, "profile", None)

    if not profile or not profile.role:
        return None

    return profile.role.name.strip().lower()


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and get_role_name(request.user) == ROLE_ADMIN
        )


class IsAuthenticatedReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in {
            "GET",
            "HEAD",
            "OPTIONS",
        }:
            return True

        return (
            get_role_name(request.user)
            == ROLE_ADMIN
        )