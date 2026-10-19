"""
Helpers for handing login details to borrowers and trustees.

The admin creates the account; the system can then text the person their
username, temporary password and the site address, so the admin does not
have to dictate them over the phone.
"""

from django.conf import settings

from .auth_backends import phone_digits
from .notification_service import mask_phone, normalize_phone, send_twilio
from .permissions import get_role_name


def user_phone(user) -> str:
    """Best phone number we have for this user, or ''."""
    borrower = getattr(user, "borrower_profile", None)
    if borrower and borrower.phone:
        return borrower.phone

    donor = getattr(user, "donor_profile", None)
    if donor and donor.phone:
        return donor.phone

    profile = getattr(user, "profile", None)
    if profile and profile.phone:
        return profile.phone

    return ""


def user_email(user) -> str:
    borrower = getattr(user, "borrower_profile", None)
    if borrower and borrower.email:
        return borrower.email

    return user.email or ""


def login_hints(user) -> dict:
    """What, besides the username, this person can type to sign in."""
    hints = {}

    borrower = getattr(user, "borrower_profile", None)
    profile = getattr(user, "profile", None)

    if borrower and borrower.id_number:
        hints["id_number"] = borrower.id_number
    elif profile and profile.id_number:
        hints["id_number"] = profile.id_number

    phone = user_phone(user)
    if phone:
        hints["phone"] = phone

    email = user_email(user)
    if email:
        hints["email"] = email

    return hints


def credentials_payload(user, temporary_password: str) -> dict:
    """The JSON block returned to the admin after create / reset."""
    phone = user_phone(user)

    return {
        "username": user.username,
        "temporary_password": temporary_password,
        "login_hints": login_hints(user),
        "can_send": bool(phone_digits(phone)),
        "can_send_sms": bool(phone_digits(phone)),
        "can_send_email": bool(user_email(user)),
        "phone_masked": mask_phone(phone) if phone else "",
        # ID number + phone on file = can sign in with an SMS code,
        # no password needed.
        "code_login": can_use_code_login(user),
    }


def can_use_code_login(user) -> bool:
    hints = login_hints(user)
    return bool(
        hints.get("id_number")
        and (phone_digits(hints.get("phone")) or hints.get("email"))
    )


def credentials_message(user, temporary_password: str) -> str:
    name = (user.first_name or "").strip()
    greeting = f"שלום {name}," if name else "שלום,"

    if can_use_code_login(user):
        # No password in the message: they sign in with ID + phone + code.
        lines = [
            greeting,
            'נפתח עבורך חשבון במערכת גמ"ח חסדי יעקב.',
            f"כניסה: {settings.SITE_URL}/login",
            "מקלידים תעודת זהות ומספר טלפון (או כתובת מייל), "
            "ומקבלים קוד כניסה ב-SMS או במייל.",
            "אין צורך בסיסמה.",
        ]
        return "\n".join(lines)

    lines = [
        greeting,
        'נפתח עבורך חשבון במערכת גמ"ח חסדי יעקב.',
        f"כניסה: {settings.SITE_URL}/login",
        f"שם משתמש: {user.username}",
        f"סיסמה זמנית: {temporary_password}",
        "בכניסה הראשונה תתבקש/י לבחור סיסמה חדשה.",
    ]

    return "\n".join(lines)


def send_credentials(user, temporary_password: str, channel: str) -> str:
    """Send by SMS or email. Returns the masked address it went to."""
    message = credentials_message(user, temporary_password)

    if channel == "EMAIL":
        from django.core.mail import send_mail

        email = user_email(user)

        if not email:
            raise ValueError("NO_EMAIL")

        if not settings.EMAIL_HOST:
            raise RuntimeError("Email is not configured.")

        send_mail(
            subject='פתיחת חשבון – גמ"ח חסדי יעקב',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return email[:2] + "***" + email[email.find("@"):]

    phone = normalize_phone(user_phone(user))

    if not phone:
        raise ValueError("NO_PHONE")

    send_twilio("SMS", phone, message)

    return mask_phone(phone)


def role_of(user) -> str:
    return get_role_name(user) or ""
