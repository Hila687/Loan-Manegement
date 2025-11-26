from django.db import models
from django.contrib.auth.models import User
import uuid

# --- 1. מודל הנאמן (Trustee) ---
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


# --- 2. מודל הלווה (Borrower) ---
class Borrower(models.Model):
    borrower_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='borrower_profile', verbose_name="משתמש מקושר", null=True, blank=True)
    trustee = models.ForeignKey(Trustee, on_delete=models.SET_NULL, null=True, related_name='borrowers', verbose_name="נאמן מלווה")
    id_number = models.CharField(max_length=20, unique=True, verbose_name="תעודת זהות")
    address = models.CharField(max_length=255, verbose_name="כתובת")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="תאריך יצירה")

    def __str__(self):
        return f"Borrower: {self.id_number}"

    class Meta:
        verbose_name = "לווה"
        verbose_name_plural = "לווים"


# --- 3. מודל הלוואה בסיסי (Abstract Loan) ---
# מודל אבסטרקטי לא יוצר טבלה בדאטהבייס. הוא משמש רק כתבנית.
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
    # כאן אנחנו שומרים את הקובץ (משימה 97)
    form_file = models.FileField(upload_to='loan_forms/', blank=True, null=True, verbose_name="קובץ טופס חתום")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="תאריך יצירה")

    class Meta:
        abstract = True  # זה הופך את המודל לאבסטרקטי!


# --- 4. הלוואת צ'קים (LoanChecks) ---
# זהו מודל אמיתי שייצור טבלה, והוא יורש את כל השדות של Loan.
class LoanChecks(Loan):
    num_payments = models.IntegerField(verbose_name="מספר תשלומים")
    check_details = models.TextField(blank=True, null=True, verbose_name="פרטי צ'קים")
    predefined_schedule = models.BooleanField(default=True, verbose_name="לוח תשלומים מוגדר מראש?")

    class Meta:
        verbose_name = "הלוואה (צ'קים)"
        verbose_name_plural = "הלוואות (צ'קים)"


# --- 5. הלוואת הוראת קבע (LoanStandingOrder) ---
class LoanStandingOrder(Loan):
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="סכום חודשי")
    charge_day = models.IntegerField(verbose_name="יום חיוב בחודש")
    stop_date = models.DateField(blank=True, null=True, verbose_name="תאריך עצירה")

    class Meta:
        verbose_name = "הלוואה (הוראת קבע)"
        verbose_name_plural = "הלוואות (הוראת קבע)"