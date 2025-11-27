from django.contrib import admin
from .models import Trustee, Borrower, LoanChecks, LoanStandingOrder, Role, UserProfile

admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(Trustee)
admin.site.register(Borrower)
admin.site.register(LoanChecks)
admin.site.register(LoanStandingOrder)