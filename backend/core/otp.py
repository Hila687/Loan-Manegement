"""
Password-free sign-in: ID number + phone number + one-time SMS code.

1. The user types their ID number and phone number.
2. If both belong to the same active account, a 6-digit code is sent to
   that phone (the phone already on file, so a stranger who only knows
   someone's ID cannot receive it).
3. The user types the code and is signed in with their role.

Responses never reveal whether an ID / phone pair exists.
"""

import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

from .auth_backends import phone_digits
from .models import Borrower, LoginCode, UserProfile
from .notification_service import mask_phone, normalize_phone, send_twilio
from .permissions import get_role_name

logger = logging.getLogger(__name__)

# Donors are records only; they do not sign in.
ALLOWED_ROLES = {"admin", "trustee", "borrower"}


class OtpError(Exception):
    def __init__(self, code: str, retry_after: int = 0):
        super().__init__(code)
        self.code = code
        self.retry_after = retry_after


def clean_id_number(value) -> str:
    """Digits only, without leading zeros, so 012345678 == 12345678."""
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    return digits.lstrip("0")


def all_phones(user) -> set:
    phones = set()

    borrower = getattr(user, "borrower_profile", None)
    if borrower and borrower.phone:
        phones.add(phone_digits(borrower.phone))

    donor = getattr(user, "donor_profile", None)
    if donor and donor.phone:
        phones.add(phone_digits(donor.phone))

    profile = getattr(user, "profile", None)
    if profile and profile.phone:
        phones.add(phone_digits(profile.phone))

    phones.discard("")
    return phones


def all_emails(user) -> set:
    emails = set()

    if user.email:
        emails.add(user.email.strip().lower())

    borrower = getattr(user, "borrower_profile", None)
    if borrower and borrower.email:
        emails.add(borrower.email.strip().lower())

    emails.discard("")
    return emails


def users_with_id_number(id_number: str):
    wanted = clean_id_number(id_number)

    if not wanted:
        return []

    user_ids = set()

    for user_id, value in Borrower.objects.filter(
        user__isnull=False
    ).values_list("user_id", "id_number"):
        if clean_id_number(value) == wanted:
            user_ids.add(user_id)

    for user_id, value in UserProfile.objects.exclude(
        id_number__isnull=True
    ).exclude(id_number="").values_list("user_id", "id_number"):
        if clean_id_number(value) == wanted:
            user_ids.add(user_id)

    return list(
        User.objects.filter(id__in=user_ids, is_active=True)
    )


def find_user(id_number: str, contact: str, channel: str = "SMS"):
    """
    The one active account with this ID number AND this contact detail
    (the phone for SMS, the email address for EMAIL), or None.
    """
    if channel == "EMAIL":
        wanted = (contact or "").strip().lower()
        owns = lambda user: wanted in all_emails(user)
    else:
        wanted = phone_digits(contact)
        owns = lambda user: wanted in all_phones(user)

    if not wanted:
        return None

    matches = [
        user
        for user in users_with_id_number(id_number)
        if owns(user) and get_role_name(user) in ALLOWED_ROLES
    ]

    if len(matches) != 1:
        if len(matches) > 1:
            logger.warning(
                "OTP login: %s accounts share ID and contact", len(matches)
            )
        return None

    return matches[0]


def _rate_limit(key: str, limit: int, window: int) -> None:
    count = cache.get(key, 0) or 0

    if count >= limit:
        raise OtpError("rate_limited", retry_after=window)

    cache.set(key, count + 1, window)


def _send_email_code(to_email: str, code: str) -> None:
    from django.core.mail import send_mail

    minutes = settings.OTP_TTL_SECONDS // 60
    send_mail(
        subject='קוד כניסה – גמ"ח חסדי יעקב',
        message=(
            f"קוד הכניסה שלך הוא: {code}\n"
            f"הקוד תקף ל-{minutes} דקות.\n"
            "אין למסור אותו לאף אחד. אם לא ביקשת קוד, אפשר להתעלם מהודעה זו."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
    )


def request_code(id_number: str, contact: str, channel: str, client_ip: str):
    """
    Send a code if the ID + phone (SMS) or ID + email (EMAIL) match.
    Returns a dict for the API.

    Always looks the same to the caller, matched or not, except that in
    development (DEBUG without Twilio) the code itself is returned so the
    flow can be tested.
    """
    _rate_limit(
        f"otp-ip:{client_ip}",
        settings.OTP_MAX_REQUESTS_PER_IP,
        3600,
    )

    result = {"resend_in": settings.OTP_RESEND_SECONDS}

    user = find_user(id_number, contact, channel)

    if user is None:
        return result

    cooldown_key = f"otp-cooldown:{user.pk}"

    if cache.get(cooldown_key):
        raise OtpError("too_soon", retry_after=settings.OTP_RESEND_SECONDS)

    _rate_limit(
        f"otp-user:{user.pk}",
        settings.OTP_MAX_CODES_PER_HOUR,
        3600,
    )

    code = f"{secrets.randbelow(10 ** 6):06d}"

    if channel == "EMAIL":
        destination = contact.strip()
        masked = destination[:2] + "***" + destination[destination.find("@"):]
        provider_ready = bool(settings.EMAIL_HOST)
    else:
        destination = normalize_phone(contact)
        masked = mask_phone(destination)
        provider_ready = bool(
            settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN
        )

    # Only one live code per user.
    LoginCode.objects.filter(user=user, used_at__isnull=True).update(
        used_at=timezone.now()
    )

    login_code = LoginCode.objects.create(
        user=user,
        code_hash=make_password(code),
        channel=channel,
        sent_to=masked,
        expires_at=timezone.now()
        + timedelta(seconds=settings.OTP_TTL_SECONDS),
    )

    message = (
        f'גמ"ח חסדי יעקב: קוד הכניסה שלך הוא {code}. '
        f"הקוד תקף ל-{settings.OTP_TTL_SECONDS // 60} דקות. "
        f"אין למסור אותו לאף אחד."
    )

    if provider_ready:
        try:
            if channel == "EMAIL":
                _send_email_code(destination, code)
            else:
                send_twilio("SMS", destination, message)
        except Exception:
            # Not delivered: void the code and let the user retry at once.
            login_code.used_at = timezone.now()
            login_code.save(update_fields=["used_at"])
            raise
    elif settings.DEBUG:
        # Development: no SMS / email provider, so show the code instead.
        logger.warning("DEV login code for %s: %s", user.username, code)
        print(f"\n*** DEV login code for {user.username}: {code} ***\n")
        result["dev_code"] = code
    else:
        login_code.used_at = timezone.now()
        login_code.save(update_fields=["used_at"])
        raise OtpError("send_failed")

    cache.set(cooldown_key, True, settings.OTP_RESEND_SECONDS)

    return result


def verify_code(id_number: str, contact: str, code: str, channel: str = "SMS"):
    """Return the user if the code is right, else raise OtpError."""
    user = find_user(id_number, contact, channel)
    code = "".join(ch for ch in str(code or "") if ch.isdigit())

    if user is None or len(code) != 6:
        raise OtpError("invalid_code")

    login_code = (
        LoginCode.objects.filter(
            user=user,
            used_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
        .order_by("-created_at")
        .first()
    )

    if login_code is None:
        raise OtpError("expired")

    if login_code.attempts >= settings.OTP_MAX_ATTEMPTS:
        login_code.used_at = timezone.now()
        login_code.save(update_fields=["used_at"])
        raise OtpError("expired")

    login_code.attempts += 1

    if not check_password(code, login_code.code_hash):
        login_code.save(update_fields=["attempts"])
        raise OtpError("invalid_code")

    login_code.used_at = timezone.now()
    login_code.save(update_fields=["attempts", "used_at"])

    return user


def set_profile_id_number(user, data) -> None:
    """Save an ID number sent in a create/update request onto the profile."""
    from rest_framework.exceptions import ValidationError

    if "id_number" not in data:
        return

    raw = str(data.get("id_number") or "").strip()
    profile = getattr(user, "profile", None)

    if profile is None:
        return

    if raw:
        digits = "".join(ch for ch in raw if ch.isdigit())

        if not (5 <= len(digits) <= 9) or digits != raw.replace("-", ""):
            raise ValidationError(
                {"id_number": ["ID number must be 5-9 digits."]}
            )

        clash = UserProfile.objects.filter(
            id_number__in=[digits, digits.lstrip("0"), digits.zfill(9)]
        ).exclude(user=user)

        if clash.exists():
            raise ValidationError(
                {"id_number": ["This ID number is already in use."]}
            )

        profile.id_number = digits
    else:
        profile.id_number = None

    profile.save(update_fields=["id_number"])

