import uuid
from pathlib import Path

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


def signed_form_upload_to(
    instance,
    filename: str,
) -> str:
    extension = Path(filename).suffix.lower()

    return (
        f"loan_forms/"
        f"{timezone.localdate().year}/"
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )


class Role(models.Model):
    role_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=50,
        unique=True,
    )

    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    must_change_password = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.user.username


class Trustee(models.Model):
    trustee_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="trustee_profile",
    )

    community = models.CharField(
        max_length=100,
        db_index=True,
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        name = (
            self.user.get_full_name()
            or self.user.username
        )

        return f"{name} - {self.community}"


class Borrower(models.Model):
    borrower_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="borrower_profile",
        null=True,
        blank=True,
    )

    trustee = models.ForeignKey(
        Trustee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="borrowers",
    )

    id_number = models.CharField(
        max_length=20,
        unique=True,
    )

    first_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    last_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    email = models.EmailField(
        null=True,
        blank=True,
    )

    address = models.CharField(
        max_length=255,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        name = (
            f"{self.first_name or ''} "
            f"{self.last_name or ''}"
        ).strip()

        return name or self.id_number


class Donor(models.Model):
    donor_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="donor_profile",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            self.user.get_full_name()
            or self.user.username
        )


class Donation(models.Model):
    donation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    donor = models.ForeignKey(
        Donor,
        on_delete=models.PROTECT,
        related_name="donations",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    donation_date = models.DateField()

    notes = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-donation_date",
            "-created_at",
        ]

    def __str__(self):
        return (
            f"Donation "
            f"{self.donation_id} - "
            f"{self.amount}"
        )


class Loan(models.Model):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_OVERDUE = "OVERDUE"
    STATUS_CLOSED = "CLOSED"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_OVERDUE, "Overdue"),
        (STATUS_CLOSED, "Closed"),
    ]

    loan_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    borrower = models.ForeignKey(
        Borrower,
        on_delete=models.CASCADE,
        related_name="%(class)s_loans",
    )

    trustee = models.ForeignKey(
        Trustee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_monitored_loans",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    start_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True,
    )

    form_file = models.FileField(
        upload_to=signed_form_upload_to,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class LoanChecks(Loan):
    num_payments = models.PositiveIntegerField()

    check_details = models.TextField(
        blank=True,
        null=True,
    )

    predefined_schedule = models.BooleanField(
        default=True,
    )


class LoanStandingOrder(Loan):
    num_payments = models.PositiveIntegerField(
        default=1,
    )

    monthly_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    charge_day = models.PositiveSmallIntegerField()

    stop_date = models.DateField(
        blank=True,
        null=True,
    )
    standing_order_form_file = models.FileField(
    upload_to="standing_order_forms/",
    blank=True,
    null=True,
    verbose_name="Standing order authorization form",
)


class Payment(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_PAID = "PAID"
    STATUS_LATE = "LATE"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_LATE, "Late"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    object_id = models.UUIDField()

    loan = GenericForeignKey(
        "content_type",
        "object_id",
    )

    due_date = models.DateField(
        db_index=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    check_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    is_manual_exception = models.BooleanField(
        default=False,
    )

    exception_note = models.CharField(
        max_length=500,
        blank=True,
        default="",
    )

    class Meta:
        ordering = [
            "due_date",
            "id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "content_type",
                    "object_id",
                    "due_date",
                ],
                name="unique_payment_due_date_per_loan",
            ),
        ]

    def __str__(self):
        return (
            f"Payment {self.id} | "
            f"Loan {self.object_id} | "
            f"{self.status}"
        )


class AuditLog(models.Model):
    audit_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )

    action = models.CharField(
        max_length=100,
    )

    entity_type = models.CharField(
        max_length=100,
    )

    entity_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]


class ReminderSettings(models.Model):
    CHANNEL_SMS = "SMS"
    CHANNEL_WHATSAPP = "WHATSAPP"
    CHANNEL_BOTH = "BOTH"

    CHANNEL_CHOICES = [
        (CHANNEL_SMS, "SMS"),
        (CHANNEL_WHATSAPP, "WhatsApp"),
        (CHANNEL_BOTH, "SMS + WhatsApp"),
    ]

    singleton_id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False,
    )

    enabled = models.BooleanField(
        default=False,
    )

    days_before = models.PositiveSmallIntegerField(
        default=3,
    )

    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default=CHANNEL_SMS,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        self.singleton_id = 1
        super().save(*args, **kwargs)


class ReminderLog(models.Model):
    STATUS_SENT = "SENT"
    STATUS_FAILED = "FAILED"
    STATUS_SKIPPED = "SKIPPED"

    STATUS_CHOICES = [
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
        (STATUS_SKIPPED, "Skipped"),
    ]

    reminder_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="reminder_logs",
    )

    channel = models.CharField(
        max_length=20,
    )

    reminder_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )

    recipient_masked = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    provider_message_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    error_code = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "payment",
                    "channel",
                    "reminder_date",
                ],
                name="unique_daily_payment_reminder",
            ),
        ]