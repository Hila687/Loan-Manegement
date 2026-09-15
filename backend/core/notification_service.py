from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import (
    Payment,
    ReminderLog,
    ReminderSettings,
)


def normalize_phone(
    phone: str,
) -> str:
    value = "".join(
        character
        for character in (
            phone or ""
        ).strip()
        if (
            character.isdigit()
            or character == "+"
        )
    )

    if value.startswith("+"):
        return value

    if (
        value.startswith("0")
        and settings.DEFAULT_COUNTRY_CODE
    ):
        return (
            f"{settings.DEFAULT_COUNTRY_CODE}"
            f"{value[1:]}"
        )

    return value


def mask_phone(
    phone: str,
) -> str:
    normalized = normalize_phone(
        phone
    )

    if len(normalized) <= 4:
        return "****"

    return (
        f"***"
        f"{normalized[-4:]}"
    )


def message_for_payment(
    payment: Payment,
) -> str:
    loan = payment.loan
    borrower = loan.borrower

    borrower_name = (
        f"{borrower.first_name or ''} "
        f"{borrower.last_name or ''}"
    ).strip()

    if not borrower_name:
        borrower_name = "Borrower"

    return (
        f"Chasdei Yaakov Gemach reminder: "
        f"{borrower_name}, "
        f"loan {loan.loan_id}, "
        f"payment {payment.amount} ILS "
        f"is due on "
        f"{payment.due_date.isoformat()}."
    )


def send_twilio(
    channel: str,
    to_phone: str,
    message: str,
) -> str:
    if (
        not settings.TWILIO_ACCOUNT_SID
        or not settings.TWILIO_AUTH_TOKEN
    ):
        raise RuntimeError(
            "Twilio credentials are not configured."
        )

    try:
        from twilio.rest import Client

    except ImportError as exc:
        raise RuntimeError(
            "Twilio package is not installed."
        ) from exc

    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    if (
        channel
        == ReminderSettings.CHANNEL_WHATSAPP
    ):
        if not settings.TWILIO_WHATSAPP_FROM:
            raise RuntimeError(
                "TWILIO_WHATSAPP_FROM is not configured."
            )

        from_number = (
            settings.TWILIO_WHATSAPP_FROM
            .replace(
                "whatsapp:",
                "",
            )
        )

        to_number = (
            to_phone.replace(
                "whatsapp:",
                "",
            )
        )

        message_object = (
            client.messages.create(
                from_=(
                    f"whatsapp:"
                    f"{from_number}"
                ),
                to=(
                    f"whatsapp:"
                    f"{to_number}"
                ),
                body=message,
            )
        )

    else:
        if not settings.TWILIO_SMS_FROM:
            raise RuntimeError(
                "TWILIO_SMS_FROM is not configured."
            )

        message_object = (
            client.messages.create(
                from_=
                    settings.TWILIO_SMS_FROM,
                to=to_phone,
                body=message,
            )
        )

    return str(
        message_object.sid
    )


def run_due_payment_reminders():
    config, _ = (
        ReminderSettings.objects
        .get_or_create(
            singleton_id=1
        )
    )

    today = timezone.localdate()

    result = {
        "sent": 0,
        "failed": 0,
        "skipped": 0,
        "target_date": None,
    }

    if not config.enabled:
        result[
            "detail"
        ] = "Reminders are disabled."

        return result

    target_date = (
        today
        + timedelta(
            days=config.days_before
        )
    )

    result[
        "target_date"
    ] = target_date.isoformat()

    payments = (
        Payment.objects
        .filter(
            due_date=target_date,
            status=
                Payment.STATUS_PENDING,
            is_manual_exception=False,
        )
        .select_related(
            "content_type"
        )
    )

    if (
        config.channel
        == ReminderSettings.CHANNEL_BOTH
    ):
        channels = [
            ReminderSettings.CHANNEL_SMS,
            ReminderSettings.CHANNEL_WHATSAPP,
        ]

    else:
        channels = [
            config.channel
        ]

    for payment in payments:
        loan = payment.loan

        if not loan:
            continue

        phone = normalize_phone(
            loan.borrower.phone
            or ""
        )

        message = message_for_payment(
            payment
        )

        for channel in channels:
            already_sent = (
                ReminderLog.objects
                .filter(
                    payment=payment,
                    channel=channel,
                    reminder_date=today,
                )
                .exists()
            )

            if already_sent:
                result["skipped"] += 1
                continue

            if not phone:
                ReminderLog.objects.create(
                    payment=payment,
                    channel=channel,
                    reminder_date=today,
                    status=
                        ReminderLog.STATUS_SKIPPED,
                    recipient_masked="",
                    error_code="NO_PHONE",
                )

                result["skipped"] += 1
                continue

            try:
                provider_id = send_twilio(
                    channel,
                    phone,
                    message,
                )

                ReminderLog.objects.create(
                    payment=payment,
                    channel=channel,
                    reminder_date=today,
                    status=
                        ReminderLog.STATUS_SENT,
                    recipient_masked=
                        mask_phone(phone),
                    provider_message_id=
                        provider_id,
                )

                result["sent"] += 1

            except Exception as exc:
                ReminderLog.objects.create(
                    payment=payment,
                    channel=channel,
                    reminder_date=today,
                    status=
                        ReminderLog.STATUS_FAILED,
                    recipient_masked=
                        mask_phone(phone),
                    error_code=
                        exc.__class__.__name__,
                )

                result["failed"] += 1

    return result