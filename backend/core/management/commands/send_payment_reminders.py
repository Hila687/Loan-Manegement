from django.core.management.base import BaseCommand

from core.notification_service import (
    run_due_payment_reminders,
)


class Command(BaseCommand):
    help = "Send configured payment reminders."

    def handle(
        self,
        *args,
        **options,
    ):
        result = (
            run_due_payment_reminders()
        )

        self.stdout.write(
            self.style.SUCCESS(
                str(result)
            )
        )