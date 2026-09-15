from decimal import Decimal, ROUND_DOWN

from dateutil.relativedelta import relativedelta


def calculate_payment_dates(
    start_date,
    num_payments: int,
):
    return [
        start_date + relativedelta(months=index)
        for index in range(num_payments)
    ]


def split_amount_exactly(
    amount: Decimal,
    num_payments: int,
):
    if num_payments < 1:
        raise ValueError(
            "Number of payments must be at least 1."
        )

    total = Decimal(amount).quantize(
        Decimal("0.01")
    )

    base = (
        total / Decimal(num_payments)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_DOWN,
    )

    amounts = [
        base
        for _ in range(num_payments)
    ]

    remainder = total - sum(
        amounts,
        Decimal("0.00"),
    )

    cents = int(
        (
            remainder
            / Decimal("0.01")
        ).to_integral_value()
    )

    for index in range(cents):
        amounts[index] += Decimal("0.01")

    return amounts