"""
Login with a friendly identifier.

Users get an auto-generated username (b_123456789, t_cohen ...) that
nobody remembers. This backend lets them sign in with whatever they
actually know about themselves:

    * the username itself (case-insensitive)
    * an Israeli ID number (borrowers)
    * a phone number, in any common format (050-1234567, +972501234567)
    * an email address

If an identifier matches more than one active account, login is refused
rather than guessing, and the user is told to use their username.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Borrower, Donor, UserProfile


def phone_digits(value) -> str:
    """Normalize a phone number to local digits: +972-50-1234567 -> 0501234567."""
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())

    if digits.startswith("972"):
        digits = "0" + digits[3:]

    return digits


def looks_like_phone(value: str) -> bool:
    digits = phone_digits(value)
    return digits.startswith("0") and 9 <= len(digits) <= 10


def candidate_users(identifier: str):
    """Return the set of user ids the identifier could refer to."""
    identifier = (identifier or "").strip()

    if not identifier:
        return set()

    ids = set(
        User.objects.filter(
            username__iexact=identifier
        ).values_list("id", flat=True)
    )

    # An exact username match always wins.
    if ids:
        return ids

    if "@" in identifier:
        ids.update(
            User.objects.filter(
                email__iexact=identifier
            ).values_list("id", flat=True)
        )
        ids.update(
            Borrower.objects.filter(
                email__iexact=identifier,
                user__isnull=False,
            ).values_list("user_id", flat=True)
        )
        return ids

    compact = identifier.replace("-", "").replace(" ", "")

    if compact.isdigit():
        ids.update(
            Borrower.objects.filter(
                Q(id_number=compact) | Q(id_number=compact.lstrip("0")),
                user__isnull=False,
            ).values_list("user_id", flat=True)
        )

    if looks_like_phone(identifier):
        wanted = phone_digits(identifier)

        for user_id, phone in UserProfile.objects.exclude(
            phone__isnull=True
        ).exclude(phone="").values_list("user_id", "phone"):
            if phone_digits(phone) == wanted:
                ids.add(user_id)

        for user_id, phone in Borrower.objects.filter(
            user__isnull=False
        ).exclude(phone__isnull=True).exclude(
            phone=""
        ).values_list("user_id", "phone"):
            if phone_digits(phone) == wanted:
                ids.add(user_id)

        for user_id, phone in Donor.objects.exclude(
            phone__isnull=True
        ).exclude(phone="").values_list("user_id", "phone"):
            if phone_digits(phone) == wanted:
                ids.add(user_id)

    return ids


def resolve_login_user(identifier: str):
    """
    Return (user, ambiguous).

    user is the single active account matching the identifier, or None.
    ambiguous is True when more than one active account matched.
    """
    ids = candidate_users(identifier)

    users = list(
        User.objects.filter(id__in=ids, is_active=True)
    )

    if len(users) == 1:
        return users[0], False

    return None, len(users) > 1


class FlexibleLoginBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        user, _ambiguous = resolve_login_user(username)

        if user is None:
            # Run the hasher anyway so response time does not reveal
            # whether the identifier exists.
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
