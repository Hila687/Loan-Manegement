import json
from decimal import Decimal
from pathlib import Path

from django.db import transaction
from django.http import FileResponse
from rest_framework import status
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .file_validation import validate_signed_form
from .loan_access import (
    find_any_loan,
    find_scoped_loan,
    scoped_loan_querysets,
)
from .models import (
    Borrower,
    LoanChecks,
    LoanStandingOrder,
    Trustee,
)
from .permissions import IsAdminRole
from .serializers import (
    CreateLoanRequestSerializer,
    LoanDetailSerializer,
    LoanListSerializer,
    LoanUpdateSerializer,
)
from .services import (
    audit,
    create_role_user,
    generate_payment_schedule,
    regenerate_payment_schedule,
    sync_loan_querysets,
    sync_payment_statuses_and_loan,
)


def borrower_summary(
    borrower,
):
    user = borrower.user

    name = (
        f"{borrower.first_name or ''} "
        f"{borrower.last_name or ''}"
    ).strip()

    if not name and user:
        name = (
            user.get_full_name()
            or user.username
        )

    return {
        "name":
            name,

        "phone":
            (
                borrower.phone
                or (
                    getattr(
                        getattr(
                            user,
                            "profile",
                            None,
                        ),
                        "phone",
                        "",
                    )
                    if user
                    else ""
                )
            ),

        "email":
            (
                borrower.email
                or (
                    user.email
                    if user
                    else ""
                )
            ),
    }


def trustee_summary(
    trustee,
):
    if not trustee:
        return None

    return {
        "name":
            (
                trustee.user.get_full_name()
                or trustee.user.username
            ),

        "community":
            trustee.community,
    }


def loan_list_item(
    loan,
    loan_type,
):
    return {
        "loan_id":
            loan.loan_id,

        "loan_type":
            loan_type,

        "amount":
            loan.amount,

        "start_date":
            loan.start_date,

        "status":
            loan.status,

        "borrower":
            borrower_summary(
                loan.borrower
            ),

        "trustee":
            trustee_summary(
                loan.trustee
            ),
    }


class LoanListView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAdminRole()
            ]

        return [
            IsAuthenticated()
        ]

    def get(self, request):
        type_param = (
            request.GET.get(
                "type"
            )
            or "all"
        ).strip().lower()

        search_param = (
            request.GET.get(
                "search"
            )
            or ""
        ).strip().lower()

        checks, standing = (
           scoped_loan_querysets(
             request.user
            )
        )
        sync_loan_querysets(
          checks,
          standing,
        )

        checks, standing = (
          scoped_loan_querysets(
             request.user,
             active_only=True,
            )
        )


        items = []

        if type_param in {
            "all",
            "checks",
        }:
            items.extend(
                loan_list_item(
                    loan,
                    "checks",
                )
                for loan in checks
            )

        if type_param in {
            "all",
            "standing_order",
            "standing_orders",
        }:
            items.extend(
                loan_list_item(
                    loan,
                    "standing_order",
                )
                for loan in standing
            )

        if search_param:
            filtered = []

            for item in items:
                borrower = (
                    item.get("borrower")
                    or {}
                )

                trustee = (
                    item.get("trustee")
                    or {}
                )

                values = [
                    borrower.get(
                        "name",
                        "",
                    ),
                    borrower.get(
                        "phone",
                        "",
                    ),
                    borrower.get(
                        "email",
                        "",
                    ),
                    trustee.get(
                        "name",
                        "",
                    ),
                    trustee.get(
                        "community",
                        "",
                    ),
                ]

                if any(
                    search_param
                    in str(value).lower()
                    for value in values
                ):
                    filtered.append(item)

            items = filtered

        items.sort(
            key=lambda item: (
                item["start_date"],
                str(item["loan_id"]),
            ),
            reverse=True,
        )

        serializer = LoanListSerializer(
            items,
            many=True,
        )

        return Response(
            serializer.data
        )

    def post(self, request):
        raw_payload = request.data.get(
            "payload"
        )

        if raw_payload:
            try:
                payload = json.loads(
                    raw_payload
                )

            except (
                TypeError,
                json.JSONDecodeError,
            ):
                return Response(
                    {
                        "payload": [
                            "Invalid JSON payload."
                        ]
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST,
                )

        else:
            payload = request.data

        serializer = (
            CreateLoanRequestSerializer(
                data=payload
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        form_file = request.FILES.get(
            "form_file"
        )

        validate_signed_form(
            form_file
        )

        standing_order_form_file = (
            request.FILES.get(
                "standing_order_form_file"
            )
        )

        if (
            data["loan_type"]
            == "standing_order"
        ):
            if not standing_order_form_file:
                return Response(
                    {
                        "standing_order_form_file": [
                            "Standing order authorization form is required."
                        ]
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST,
                )

            validate_signed_form(
                standing_order_form_file,
                field_name=(
                    "standing_order_form_file"
                ),
            )

        borrower_data = data[
            "borrower"
        ]

        loan_data = data[
            "loan"
        ]

        trustee = (
            Trustee.objects
            .filter(
                trustee_id=
                    data["trustee_id"],
                user__is_active=True,
            )
            .first()
        )

        if not trustee:
            return Response(
                {
                    "trustee_id": [
                        "Trustee not found."
                    ]
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        stored_file_name = ""
        stored_standing_order_file_name = ""
        credentials = None
        loan = None

        try:
            with transaction.atomic():
                borrower = (
                    Borrower.objects
                    .select_for_update()
                    .filter(
                        id_number=
                            borrower_data[
                                "id_number"
                            ]
                    )
                    .first()
                )

                if borrower is None:
                    (
                        user,
                        temporary_password,
                    ) = create_role_user(
                        "borrower",
                        borrower_data[
                            "id_number"
                        ],
                        borrower_data[
                            "first_name"
                        ],
                        borrower_data[
                            "last_name"
                        ],
                        borrower_data.get(
                            "email",
                            "",
                        ),
                        borrower_data.get(
                            "phone",
                            "",
                        ),
                    )

                    borrower = (
                        Borrower.objects.create(
                            user=user,
                            trustee=trustee,
                            id_number=
                                borrower_data[
                                    "id_number"
                                ],
                            first_name=
                                borrower_data[
                                    "first_name"
                                ],
                            last_name=
                                borrower_data[
                                    "last_name"
                                ],
                            phone=
                                borrower_data[
                                    "phone"
                                ],
                            email=
                                borrower_data.get(
                                    "email",
                                    "",
                                ),
                            address=
                                borrower_data[
                                    "address"
                                ],
                        )
                    )

                    credentials = {
                        "username":
                            user.username,

                        "temporary_password":
                            temporary_password,
                    }

                else:
                    borrower.trustee = trustee

                    borrower.first_name = (
                        borrower_data[
                            "first_name"
                        ]
                    )

                    borrower.last_name = (
                        borrower_data[
                            "last_name"
                        ]
                    )

                    borrower.phone = (
                        borrower_data[
                            "phone"
                        ]
                    )

                    borrower.email = (
                        borrower_data.get(
                            "email",
                            "",
                        )
                    )

                    borrower.address = (
                        borrower_data[
                            "address"
                        ]
                    )

                    if borrower.user is None:
                        (
                            user,
                            temporary_password,
                        ) = create_role_user(
                            "borrower",
                            borrower_data[
                                "id_number"
                            ],
                            borrower_data[
                                "first_name"
                            ],
                            borrower_data[
                                "last_name"
                            ],
                            borrower_data.get(
                                "email",
                                "",
                            ),
                            borrower_data.get(
                                "phone",
                                "",
                            ),
                        )

                        borrower.user = user

                        credentials = {
                            "username":
                                user.username,

                            "temporary_password":
                                temporary_password,
                        }

                    else:
                        borrower.user.first_name = (
                            borrower_data[
                                "first_name"
                            ]
                        )

                        borrower.user.last_name = (
                            borrower_data[
                                "last_name"
                            ]
                        )

                        borrower.user.email = (
                            borrower_data.get(
                                "email",
                                "",
                            )
                        )

                        borrower.user.save(
                            update_fields=[
                                "first_name",
                                "last_name",
                                "email",
                            ]
                        )

                        profile = getattr(
                            borrower.user,
                            "profile",
                            None,
                        )

                        if profile:
                            profile.phone = (
                                borrower_data[
                                    "phone"
                                ]
                            )

                            profile.save(
                                update_fields=[
                                    "phone",
                                ]
                            )

                    borrower.save()

                num_payments = (
                    loan_data[
                        "num_payments"
                    ]
                )

                common_fields = {
                    "borrower":
                        borrower,

                    "trustee":
                        trustee,

                    "amount":
                        loan_data[
                            "amount"
                        ],

                    "start_date":
                        loan_data[
                            "start_date"
                        ],

                    "status":
                        "ACTIVE",

                    "form_file":
                        form_file,
                }

                if (
                    data["loan_type"]
                    == "checks"
                ):
                    loan = (
                        LoanChecks.objects.create(
                            num_payments=
                                num_payments,
                            **common_fields,
                        )
                    )

                else:
                    monthly_amount = (
                        Decimal(
                            loan_data[
                                "amount"
                            ]
                        )
                        / Decimal(
                            num_payments
                        )
                    ).quantize(
                        Decimal("0.01")
                    )

                    loan = (
                        LoanStandingOrder.objects
                        .create(
                            num_payments=
                                num_payments,

                            monthly_amount=
                                monthly_amount,

                            charge_day=
                                loan_data[
                                    "start_date"
                                ].day,

                            standing_order_form_file=
                                standing_order_form_file,

                            **common_fields,
                        )
                    )

                if loan.form_file:
                    stored_file_name = (
                        loan.form_file.name
                    )

                if (
                    data["loan_type"]
                    == "standing_order"
                    and
                    getattr(
                        loan,
                        "standing_order_form_file",
                        None,
                    )
                ):
                    stored_standing_order_file_name = (
                        loan
                        .standing_order_form_file
                        .name
                    )

                generate_payment_schedule(
                    loan,
                    num_payments,
                )

                audit(
                    request.user,
                    "CREATE_LOAN",
                    loan.__class__.__name__,
                    loan.loan_id,
                    {
                        "loan_type":
                            data[
                                "loan_type"
                            ]
                    },
                )

        except Exception:
            if (
                loan
                and stored_file_name
            ):
                try:
                    loan.form_file.storage.delete(
                        stored_file_name
                    )

                except Exception:
                    pass

            if (
                loan
                and
                stored_standing_order_file_name
            ):
                try:
                    (
                        loan
                        .standing_order_form_file
                        .storage
                        .delete(
                            stored_standing_order_file_name
                        )
                    )

                except Exception:
                    pass

            raise

        response_data = {
            "loan_id":
                str(loan.loan_id),

            "loan_type":
                data["loan_type"],

            "status":
                loan.status,
        }

        if credentials:
            response_data[
                "borrower_credentials"
            ] = credentials

        return Response(
            response_data,
            status=
                status.HTTP_201_CREATED,
        )

class LoanDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_permissions(self):
        if self.request.method == "PUT":
            return [
                IsAdminRole()
            ]

        return [
            IsAuthenticated()
        ]

    def get(
        self,
        request,
        loan_id,
    ):
        loan = find_scoped_loan(
            request.user,
            loan_id,
        )

        if not loan:
            return Response(
                {
                    "detail":
                        "Loan not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        serializer = LoanDetailSerializer(
            loan,
            context={
                "request":
                    request
            },
        )

        return Response(
            serializer.data
        )

    def put(
        self,
        request,
        loan_id,
    ):
        loan = find_any_loan(
            loan_id
        )

        if not loan:
            return Response(
                {
                    "detail":
                        "Loan not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        old_schedule = (
            loan.amount,
            loan.start_date,
            loan.num_payments,
        )

        serializer = LoanUpdateSerializer(
            instance=loan,
            data=request.data,
            context={
                "request":
                    request
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            with transaction.atomic():
                updated_loan = (
                    serializer.save()
                )

                new_schedule = (
                    updated_loan.amount,
                    updated_loan.start_date,
                    updated_loan.num_payments,
                )

                if (
                    new_schedule
                    != old_schedule
                ):
                    regenerate_payment_schedule(
                        updated_loan,
                        updated_loan.num_payments,
                    )

                audit(
                    request.user,
                    "UPDATE_LOAN",
                    updated_loan
                    .__class__.__name__,
                    updated_loan.loan_id,
                )

        except ValueError as exc:
            return Response(
                {
                    "detail":
                        str(exc)
                },
                status=
                    status.HTTP_409_CONFLICT,
            )

        return Response(
            LoanDetailSerializer(
                updated_loan,
                context={
                    "request":
                        request
                },
            ).data
        )


class LoanSignedFormView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        loan_id,
    ):
        loan = find_scoped_loan(
            request.user,
            loan_id,
        )

        if not loan:
            return Response(
                {
                    "detail":
                        "Loan not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        sync_payment_statuses_and_loan(
         loan
        )

        serializer = LoanDetailSerializer(
            loan,
            context={
                "request":
                request
            },
        )

        if not loan.form_file:
            return Response(
                {
                    "detail":
                        "Signed form not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        extension = Path(
            loan.form_file.name
        ).suffix.lower()

        response = FileResponse(
            loan.form_file.open(
                "rb"
            ),
            as_attachment=False,
            filename=(
                f"signed-form-"
                f"{loan.loan_id}"
                f"{extension}"
            ),
        )

        response[
            "Cache-Control"
        ] = "private, no-store"

        response[
            "X-Content-Type-Options"
        ] = "nosniff"

        return response

class LoanStandingOrderFormView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        loan_id,
    ):
        loan = find_scoped_loan(
            request.user,
            loan_id,
        )

        if not loan:
            return Response(
                {
                    "detail":
                        "Loan not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        if not isinstance(
            loan,
            LoanStandingOrder,
        ):
            return Response(
                {
                    "detail":
                        "Standing order form not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        form_file = getattr(
            loan,
            "standing_order_form_file",
            None,
        )

        if not form_file:
            return Response(
                {
                    "detail":
                        "Standing order form not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        extension = Path(
            form_file.name
        ).suffix.lower()

        response = FileResponse(
            form_file.open(
                "rb"
            ),
            as_attachment=False,
            filename=(
                f"standing-order-form-"
                f"{loan.loan_id}"
                f"{extension}"
            ),
        )

        response[
            "Cache-Control"
        ] = "private, no-store"

        response[
            "X-Content-Type-Options"
        ] = "nosniff"

        return response

