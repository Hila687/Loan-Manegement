from rest_framework.response import Response
from rest_framework.views import APIView

from .notification_service import (
    run_due_payment_reminders,
)
from .permissions import IsAdminRole
from .services import audit


class RunRemindersView(APIView):
    permission_classes = [
        IsAdminRole,
    ]

    def post(self, request):
        result = (
            run_due_payment_reminders()
        )

        audit(
            request.user,
            "RUN_PAYMENT_REMINDERS",
            "ReminderLog",
            "",
            result,
        )

        return Response(
            result
        )