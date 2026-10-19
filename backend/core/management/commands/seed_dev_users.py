"""
Create one ready-to-use user of each role for local development.

    python manage.py seed_dev_users

Safe to run again: it resets the same four users to the same passwords.
Refuses to run unless DJANGO_DEBUG=true, so it never touches production.
"""

from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import (
    Borrower,
    Donation,
    Donor,
    LoanChecks,
    LoanStandingOrder,
    Role,
    Trustee,
    UserProfile,
)
from core.services import generate_payment_schedule


DEV_USERS = [
    # role,      username,       password,         first,   last,     ID number,   phone
    ("admin",    "dev_admin",    "Admin1234!",    "רחל",   "מנהלת",  "100000009", "050-0000001"),
    ("trustee",  "dev_trustee",  "Trustee1234!",  "משה",   "נאמן",   "200000008", "050-0000002"),
    ("borrower", "dev_borrower", "Borrower1234!", "דוד",   "לווה",   "300000007", "050-0000003"),
    # Donors don't sign in; this one only exists so donations have data.
    ("donor",    "dev_donor",    None,            "שרה",   "תורמת",  None,        "050-0000004"),
]

ROLE_NAMES = {
    "admin": "Admin",
    "trustee": "Trustee",
    "borrower": "Borrower",
    "donor": "Donor",
}


class Command(BaseCommand):
    help = "Create one development user per role (admin, trustee, borrower, donor)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "seed_dev_users only runs with DJANGO_DEBUG=true "
                "(it creates users with known passwords)."
            )

        with transaction.atomic():
            users = {}

            for role_key, username, password, first, last, id_number, phone in DEV_USERS:
                role, _ = Role.objects.get_or_create(name=ROLE_NAMES[role_key])

                user, _ = User.objects.get_or_create(username=username)
                user.first_name = first
                user.last_name = last
                user.is_active = True
                user.is_staff = role_key == "admin"
                user.is_superuser = role_key == "admin"
                if password:
                    user.set_password(password)
                else:
                    user.set_unusable_password()
                user.save()

                UserProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        "role": role,
                        "phone": phone,
                        # Borrowers keep their ID on Borrower.id_number.
                        "id_number": None if role_key == "borrower" else id_number,
                        "must_change_password": False,
                    },
                )

                users[role_key] = (user, id_number, phone)

            trustee_user = users["trustee"][0]
            trustee, _ = Trustee.objects.update_or_create(
                user=trustee_user,
                defaults={"community": "רמות"},
            )

            borrower_user, borrower_id, borrower_phone = users["borrower"]
            borrower = Borrower.objects.filter(user=borrower_user).first()

            if borrower is None:
                borrower = Borrower.objects.filter(id_number=borrower_id).first()

            if borrower is None:
                borrower = Borrower(user=borrower_user, id_number=borrower_id)

            borrower.user = borrower_user
            borrower.trustee = trustee
            borrower.first_name = borrower_user.first_name
            borrower.last_name = borrower_user.last_name
            borrower.phone = borrower_phone
            borrower.address = "ירושלים"
            borrower.save()

            donor_user, _, donor_phone = users["donor"]
            donor, _ = Donor.objects.update_or_create(
                user=donor_user,
                defaults={"phone": donor_phone},
            )

            self._sample_data(borrower, trustee, donor)

        self.stdout.write(self.style.SUCCESS("Development users are ready:\n"))
        self.stdout.write(f"  {'role':<9} {'username':<13} {'password':<14} {'ID number':<10} phone")
        for role_key, username, password, _f, _l, id_number, phone in DEV_USERS:
            if not password:
                continue
            self.stdout.write(f"  {role_key:<9} {username:<13} {password:<14} {id_number:<10} {phone}")
        self.stdout.write(
            "\nSign in at /login with username + password, "
            "or with ID number + phone (the SMS code is shown on screen in DEBUG)."
        )

    def _sample_data(self, borrower, trustee, donor):
        """A couple of loans and donations so every screen has something to show."""
        has_loans = (
            LoanChecks.objects.filter(borrower=borrower).exists()
            or LoanStandingOrder.objects.filter(borrower=borrower).exists()
        )

        if not has_loans:
            start = date.today().replace(day=1) - relativedelta(months=3)

            checks = LoanChecks.objects.create(
                borrower=borrower,
                trustee=trustee,
                amount=Decimal("12000.00"),
                start_date=start,
                num_payments=12,
            )
            payments = generate_payment_schedule(checks, 12)

            # One bounced check, so the "problem loans" view has an example.
            bounced = payments[1]
            bounced.status = "LATE"
            bounced.amount_paid = Decimal("0.00")
            bounced.is_manual_exception = True
            bounced.exception_note = "צ'ק חזר"
            bounced.save()

            standing = LoanStandingOrder.objects.create(
                borrower=borrower,
                trustee=trustee,
                amount=Decimal("6000.00"),
                start_date=start + relativedelta(months=1),
                num_payments=10,
                monthly_amount=Decimal("600.00"),
                charge_day=10,
            )
            generate_payment_schedule(standing, 10)

        if not donor.donations.exists():
            Donation.objects.create(
                donor=donor,
                amount=Decimal("1800.00"),
                donation_date=date.today() - relativedelta(months=2),
                notes="תרומת דוגמה",
            )
            Donation.objects.create(
                donor=donor,
                amount=Decimal("500.00"),
                donation_date=date.today() - relativedelta(days=10),
                notes="תרומת דוגמה",
            )
