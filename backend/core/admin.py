from django.contrib import admin
from .models import Trustee, Borrower, Loan, LoanChecks, LoanStandingOrder

admin.site.register(Trustee)
admin.site.register(Borrower)
admin.site.register(Loan)
admin.site.register(LoanChecks)
admin.site.register(LoanStandingOrder)