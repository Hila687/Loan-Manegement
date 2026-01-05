from django.db import models
from django.contrib.auth.models import User
import uuid

# --- 1. Role Model ---
class Role(models.Model):
    role_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, verbose_name="שם תפקיד")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name="תיאור")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "תפקיד"
        verbose_name_plural = "תפקידים"

# --- 2. UserProfile Model for extending User ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="משתמש")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="תפקיד")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="טלפון")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "פרופיל משתמש"
        verbose_name_plural = "פרופילי משתמשים"

# --- 3. trustee Model ---
class Trustee(models.Model):
    trustee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trustee_profile', verbose_name="משתמש מקושר")
    community = models.CharField(max_length=100, verbose_name="קהילה")
    notes = models.TextField(blank=True, null=True, verbose_name="הערות")

    def __str__(self):
        return f"Trustee: {self.user.username} - {self.community}"

    class Meta:
        verbose_name = "נאמן"
        verbose_name_plural = "נאמנים"

# --- 4. borrower Model ---
class Borrower(models.Model):
    borrower_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='borrower_profile', verbose_name="משתמש מקושר", null=True, blank=True)
    trustee = models.ForeignKey(Trustee, on_delete=models.SET_NULL, null=True, related_name='borrowers', verbose_name="נאמן מלווה")
    id_number = models.CharField(max_length=20, unique=True, verbose_name="תעודת זהות")
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name="כתובת")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="תאריך יצירה")

    def __str__(self):
        return f"Borrower: {self.id_number}"

    class Meta:
        verbose_name = "לווה"
        verbose_name_plural = "לווים"

# --- 5. base Loan Model ---
class Loan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'ממתין לאישור'),
        ('ACTIVE', 'פעיל'),
        ('PAID', 'שולם'),
        ('REJECTED', 'נדחה'),
    ]

    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='%(class)s_loans', verbose_name="לווה")
    trustee = models.ForeignKey(Trustee, on_delete=models.SET_NULL, null=True, related_name='%(class)s_monitored_loans', verbose_name="נאמן מפקח")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="סכום ההלוואה")
    start_date = models.DateField(verbose_name="תאריך התחלה")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="סטטוס")
    form_file = models.FileField(upload_to='loan_forms/', blank=True, null=True, verbose_name="קובץ טופס חתום")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="תאריך יצירה")

    class Meta:
        abstract = True

# --- 6. Loan Subclasses ---
class LoanChecks(Loan):
    num_payments = models.IntegerField(verbose_name="מספר תשלומים")
    check_details = models.TextField(blank=True, null=True, verbose_name="פרטי צ'קים")
    predefined_schedule = models.BooleanField(default=True, verbose_name="לוח תשלומים מוגדר מראש?")

    class Meta:
        verbose_name = "הלוואה (צ'קים)"
        verbose_name_plural = "הלוואות (צ'קים)"

class LoanStandingOrder(Loan):
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="סכום חודשי")
    charge_day = models.IntegerField(verbose_name="יום חיוב בחודש")
    stop_date = models.DateField(blank=True, null=True, verbose_name="תאריך עצירה")

    class Meta:
        verbose_name = "הלוואה (הוראת קבע)"
        verbose_name_plural = "הלוואות (הוראת קבע)"


# --- 7. Payment Model ---
import uuid

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Payment(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_PAID = "PAID"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # --- Generic relation to Loan (LoanChecks / LoanStandingOrder) ---
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    object_id = models.UUIDField()
    loan = GenericForeignKey("content_type", "object_id")

    # --- Payment details ---
    due_date = models.DateField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
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

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"Payment {self.id} | Loan {self.object_id} | {self.status}"
