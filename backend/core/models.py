from django.db import models
from django.contrib.auth.models import User
import uuid


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



class Borrower(models.Model):
    borrower_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='borrower_profile', verbose_name="משתמש מקושר")
    
    trustee = models.ForeignKey(Trustee, on_delete=models.SET_NULL, null=True, related_name='borrowers', verbose_name="נאמן מלווה")
    
    id_number = models.CharField(max_length=20, unique=True, verbose_name="תעודת זהות")
    address = models.CharField(max_length=255, verbose_name="כתובת")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="תאריך יצירה")

    def __str__(self):
        return f"Borrower: {self.user.first_name} {self.user.last_name} ({self.id_number})"

    class Meta:
        verbose_name = "לווה"
        verbose_name_plural = "לווים"


class Loan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'ממתין לאישור'),
        ('ACTIVE', 'פעיל'),
        ('PAID', 'שולם'),
        ('REJECTED', 'נדחה'),
    ]

    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='loans', verbose_name="לווה")
    trustee = models.ForeignKey(Trustee, on_delete=models.SET_NULL, null=True, related_name='monitored_loans', verbose_name="נאמן מפקח")
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="סכום ההלוואה")
    start_date = models.DateField(verbose_name="תאריך התחלה")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="סטטוס")
    form_file = models.CharField(max_length=255, blank=True, null=True, verbose_name="קובץ טופס חתום") 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="תאריך יצירה")
    loan_type = models.CharField(max_length=50, verbose_name="סוג הלוואה") 

    def __str__(self):
        return f"Loan {self.loan_id} - {self.amount}"

    class Meta:
        verbose_name = "הלוואה"
        verbose_name_plural = "הלוואות"



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