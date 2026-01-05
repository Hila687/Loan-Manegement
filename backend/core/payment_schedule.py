from datetime import date
from dateutil.relativedelta import relativedelta


def calculate_payment_dates(start_date: date, num_payments: int) -> list[date]:
    """
    Calculate payment due dates based on a start date and number of payments.

    Rules (Sprint 5):
    - First payment due date is start_date
    - Each subsequent payment is exactly +1 calendar month
    - No special handling for end-of-month edge cases
    - Year transitions are handled naturally by date arithmetic
    """

    if num_payments <= 0:
        return []

    due_dates = []
    current_date = start_date

    for _ in range(num_payments):
        due_dates.append(current_date)
        current_date = current_date + relativedelta(months=1)

    return due_dates
