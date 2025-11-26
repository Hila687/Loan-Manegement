from django.contrib import admin
from .models import Trustee, Borrower, LoanChecks, LoanStandingOrder

# רישום המודלים לממשק הניהול
admin.site.register(Trustee)
admin.site.register(Borrower)

# אנחנו רושמים רק את המודלים הספציפיים, לא את Loan הכללי (שהוא Abstract)
admin.site.register(LoanChecks)
admin.site.register(LoanStandingOrder)