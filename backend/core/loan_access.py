from .models import (
    LoanChecks,
    LoanStandingOrder,
)
from .permissions import (
    ROLE_ADMIN,
    ROLE_BORROWER,
    ROLE_TRUSTEE,
    get_role_name,
)


def scoped_loan_querysets(
    user,
    active_only=False,
):
    checks = (
        LoanChecks.objects
        .select_related(
            "borrower__user",
            "trustee__user",
        )
        .all()
    )

    standing = (
        LoanStandingOrder.objects
        .select_related(
            "borrower__user",
            "trustee__user",
        )
        .all()
    )

    role = get_role_name(user)

    if role == ROLE_ADMIN:
        pass

    elif role == ROLE_TRUSTEE:
        trustee = getattr(
            user,
            "trustee_profile",
            None,
        )

        if not trustee:
            return (
                checks.none(),
                standing.none(),
            )

        checks = checks.filter(
            trustee__community=
                trustee.community
        )

        standing = standing.filter(
            trustee__community=
                trustee.community
        )

    elif role == ROLE_BORROWER:
        borrower = getattr(
            user,
            "borrower_profile",
            None,
        )

        if not borrower:
            return (
                checks.none(),
                standing.none(),
            )

        checks = checks.filter(
            borrower=borrower
        )

        standing = standing.filter(
            borrower=borrower
        )

    else:
        return (
            checks.none(),
            standing.none(),
        )

    if active_only:
        checks = checks.filter(
            status__in=[
                "ACTIVE",
                "OVERDUE",
            ]
        )

        standing = standing.filter(
            status__in=[
                "ACTIVE",
                "OVERDUE",
            ]
        )

    return checks, standing


def find_any_loan(
    loan_id,
):
    loan = (
        LoanChecks.objects
        .select_related(
            "borrower__user",
            "trustee__user",
        )
        .filter(
            loan_id=loan_id
        )
        .first()
    )

    if loan:
        return loan

    return (
        LoanStandingOrder.objects
        .select_related(
            "borrower__user",
            "trustee__user",
        )
        .filter(
            loan_id=loan_id
        )
        .first()
    )


def find_scoped_loan(
    user,
    loan_id,
):
    checks, standing = (
        scoped_loan_querysets(user)
    )

    loan = checks.filter(
        loan_id=loan_id
    ).first()

    if loan:
        return loan

    return standing.filter(
        loan_id=loan_id
    ).first()