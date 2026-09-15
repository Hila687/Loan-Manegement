from django.contrib import admin

from .models import (
    AuditLog,
    Borrower,
    Donation,
    Donor,
    LoanChecks,
    LoanStandingOrder,
    Payment,
    ReminderLog,
    ReminderSettings,
    Role,
    Trustee,
    UserProfile,
)


admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(Trustee)
admin.site.register(Borrower)
admin.site.register(Donor)
admin.site.register(Donation)
admin.site.register(LoanChecks)
admin.site.register(LoanStandingOrder)
admin.site.register(Payment)
admin.site.register(AuditLog)
admin.site.register(ReminderSettings)
admin.site.register(ReminderLog)