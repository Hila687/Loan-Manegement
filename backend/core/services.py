import secrets
import string
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from .models import (
    AuditLog,
    Payment,
    Role,
    UserProfile,
)
from .payment_schedule import (
    calculate_payment_dates,
    split_amount_exactly,
)


ROLE_NAMES = {
    "admin": "Admin",
    "trustee": "Trustee",
    "borrower": "Borrower",
    "donor": "Donor",
}


def audit(
    actor,
    action: str,
    entity_type: str,
    entity_id="",
    metadata=None,
):
    AuditLog.objects.create(
        actor=(
            actor
            if actor
            and actor.is_authenticated
            else None
        ),
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id or ""),
        metadata=metadata or {},
    )


def _random_password(
    length: int = 16,
) -> str:
    alphabet = (
        string.ascii_letters
        + string.digits
        + "!@#$%"
    )

    while True:
        password = "".join(
            secrets.choice(alphabet)
            for _ in range(length)
        )

        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(
                c in "!@#$%"
                for c in password
            )
        ):
            return password


def _unique_username(
    seed: str,
    role_key: str,
) -> str:
    normalized = "".join(
        ch.lower()
        for ch in seed
        if ch.isalnum()
    )[:18]

    if not normalized:
        normalized = secrets.token_hex(4)

    prefix = {
        "borrower": "b",
        "trustee": "t",
        "donor": "d",
        "admin": "a",
    }.get(
        role_key,
        "u",
    )

    base = f"{prefix}_{normalized}"[:25]
    candidate = base
    counter = 1

    while User.objects.filter(
        username=candidate
    ).exists():
        candidate = (
            f"{base[:21]}_{counter}"
        )
        counter += 1

    return candidate


@transaction.atomic
def create_role_user(
    role_key: str,
    username_seed: str,
    first_name: str = "",
    last_name: str = "",
    email: str = "",
    phone: str = "",
):
    if role_key not in ROLE_NAMES:
        raise ValueError("Invalid role.")

    role, _ = Role.objects.get_or_create(
        name=ROLE_NAMES[role_key],
    )

    username = _unique_username(
        username_seed,
        role_key,
    )

    temporary_password = _random_password()

    user = User(
        username=username,
        first_name=(first_name or "").strip(),
        last_name=(last_name or "").strip(),
        email=(email or "").strip(),
        is_active=True,
        is_staff=role_key == "admin",
    )

    user.set_password(
        temporary_password
    )

    user.save()

    UserProfile.objects.create(
        user=user,
        role=role,
        phone=(phone or "").strip(),
        must_change_password=True,
    )

    return user, temporary_password


def reset_user_password(
    user: User,
) -> str:
    temporary_password = _random_password()

    user.set_password(
        temporary_password
    )

    user.save(
        update_fields=[
            "password",
        ]
    )

    profile = getattr(
        user,
        "profile",
        None,
    )

    if profile:
        profile.must_change_password = True

        profile.save(
            update_fields=[
                "must_change_password",
            ]
        )

    return temporary_password


def get_payment_queryset_for_loan(
    loan,
):
    content_type = (
        ContentType.objects
        .get_for_model(loan)
    )

    return Payment.objects.filter(
        content_type=content_type,
        object_id=loan.loan_id,
    )


def generate_payment_schedule(
    loan,
    num_payments: int,
):
    content_type = (
        ContentType.objects
        .get_for_model(loan)
    )

    due_dates = calculate_payment_dates(
        loan.start_date,
        num_payments,
    )

    amounts = split_amount_exactly(
        Decimal(loan.amount),
        num_payments,
    )

    created = []

    for due_date, amount in zip(
        due_dates,
        amounts,
    ):
        payment, was_created = (
            Payment.objects.get_or_create(
                content_type=content_type,
                object_id=loan.loan_id,
                due_date=due_date,
                defaults={
                    "amount": amount,
                    "amount_paid":
                        Decimal("0.00"),
                    "status":
                        Payment.STATUS_PENDING,
                },
            )
        )

        if not was_created:
            raise ValueError(
                "Duplicate payment schedule detected."
            )

        created.append(payment)

    return created


def regenerate_payment_schedule(
    loan,
    num_payments: int,
):
    payments = (
        get_payment_queryset_for_loan(
            loan
        )
    )

    if payments.filter(
        is_manual_exception=True
    ).exists():
        raise ValueError(
            "Payment schedule cannot be regenerated "
            "while manual exceptions exist."
        )

    payments.delete()

    return generate_payment_schedule(
        loan,
        num_payments,
    )


@transaction.atomic
def sync_payment_statuses_and_loan(
    loan,
):
    today = timezone.localdate()

    payments = list(
        get_payment_queryset_for_loan(
            loan
        ).order_by(
            "due_date"
        )
    )

    changed = []

    for payment in payments:
        if payment.is_manual_exception:
            continue

        if payment.due_date <= today:
            desired_status = (
                Payment.STATUS_PAID
            )

            desired_amount_paid = (
                payment.amount
            )

        else:
            desired_status = (
                Payment.STATUS_PENDING
            )

            desired_amount_paid = (
                Decimal("0.00")
            )

        if (
            payment.status
            != desired_status
            or payment.amount_paid
            != desired_amount_paid
        ):
            payment.status = (
                desired_status
            )

            payment.amount_paid = (
                desired_amount_paid
            )

            changed.append(
                payment
            )

    if changed:
        Payment.objects.bulk_update(
            changed,
            [
                "status",
                "amount_paid",
            ],
        )

    if not payments:
        desired_loan_status = (
            loan.STATUS_ACTIVE
        )

    elif any(
        payment.status
        == Payment.STATUS_LATE
        for payment in payments
    ):
        desired_loan_status = (
            loan.STATUS_OVERDUE
        )

    elif all(
        payment.status
        == Payment.STATUS_PAID
        for payment in payments
    ):
        desired_loan_status = (
            loan.STATUS_CLOSED
        )

    else:
        desired_loan_status = (
            loan.STATUS_ACTIVE
        )

    if (
        loan.status
        != desired_loan_status
    ):
        loan.status = (
            desired_loan_status
        )

        loan.save(
            update_fields=[
                "status",
            ]
        )

    return payments

def sync_loan_querysets(
    *querysets,
):
    for queryset in querysets:
        for loan in queryset.iterator():
            sync_payment_statuses_and_loan(
                loan
            )