from decimal import Decimal, InvalidOperation

from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from rest_framework import serializers

from .models import (
    Borrower,
    Donation,
    Donor,
    LoanChecks,
    LoanStandingOrder,
    Payment,
    ReminderSettings,
    Role,
    Trustee,
    UserProfile,
)


class RoleSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Role
        fields = [
            "role_id",
            "name",
            "description",
            "created_at",
        ]

        read_only_fields = fields


class UserSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
        ]

        read_only_fields = [
            "id",
            "username",
        ]


class UserProfileSerializer(
    serializers.ModelSerializer
):
    user_details = UserSerializer(
        source="user",
        read_only=True,
    )

    role_name = serializers.CharField(
        source="role.name",
        read_only=True,
    )

    class Meta:
        model = UserProfile

        fields = [
            "id",
            "user_details",
            "role_name",
            "phone",
            "must_change_password",
        ]

        read_only_fields = fields


class TrusteeSerializer(
    serializers.ModelSerializer
):
    user_details = UserSerializer(
        source="user",
        read_only=True,
    )

    phone = serializers.CharField(
        source="user.profile.phone",
        read_only=True,
        allow_blank=True,
    )

    is_active = serializers.BooleanField(
        source="user.is_active",
        read_only=True,
    )

    borrower_count = serializers.IntegerField(
        source="borrowers.count",
        read_only=True,
    )

    class Meta:
        model = Trustee

        fields = [
            "trustee_id",
            "user_details",
            "phone",
            "is_active",
            "community",
            "notes",
            "borrower_count",
        ]

        read_only_fields = [
            "trustee_id",
            "user_details",
            "phone",
            "is_active",
            "borrower_count",
        ]


class TrusteeCreateSerializer(
    serializers.Serializer
):
    first_name = serializers.CharField(
        max_length=150
    )

    last_name = serializers.CharField(
        max_length=150
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )

    community = serializers.CharField(
        max_length=100
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )


class TrusteeUpdateSerializer(
    TrusteeCreateSerializer
):
    first_name = serializers.CharField(
        max_length=150,
        required=False,
    )

    last_name = serializers.CharField(
        max_length=150,
        required=False,
    )

    community = serializers.CharField(
        max_length=100,
        required=False,
    )


class BorrowerSerializer(
    serializers.ModelSerializer
):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    trustee_name = (
        serializers.SerializerMethodField()
    )

    trustee_community = (
        serializers.CharField(
            source="trustee.community",
            read_only=True,
            allow_null=True,
        )
    )

    loans_count = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Borrower

        fields = [
            "borrower_id",
            "username",
            "id_number",
            "first_name",
            "last_name",
            "phone",
            "email",
            "address",
            "trustee",
            "trustee_name",
            "trustee_community",
            "loans_count",
            "created_at",
        ]

        read_only_fields = [
            "borrower_id",
            "username",
            "created_at",
            "loans_count",
            "trustee_name",
            "trustee_community",
        ]

    def get_trustee_name(
        self,
        obj,
    ):
        if (
            not obj.trustee
            or not obj.trustee.user
        ):
            return ""

        return (
            obj.trustee.user.get_full_name()
            or obj.trustee.user.username
        )

    def get_loans_count(
        self,
        obj,
    ):
        return (
            obj.loanchecks_loans.count()
            + obj.loanstandingorder_loans.count()
        )


class DonorSerializer(
    serializers.ModelSerializer
):
    user_details = UserSerializer(
        source="user",
        read_only=True,
    )

    is_active = serializers.BooleanField(
        source="user.is_active",
        read_only=True,
    )

    total_donated = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Donor

        fields = [
            "donor_id",
            "user_details",
            "phone",
            "is_active",
            "notes",
            "total_donated",
            "created_at",
        ]

        read_only_fields = [
            "donor_id",
            "user_details",
            "is_active",
            "total_donated",
            "created_at",
        ]

    def get_total_donated(
        self,
        obj,
    ):
        annotated = getattr(
            obj,
            "total_donated",
            None,
        )

        if annotated is not None:
            return annotated

        return (
            obj.donations.aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )


class DonorCreateSerializer(
    serializers.Serializer
):
    first_name = serializers.CharField(
        max_length=150
    )

    last_name = serializers.CharField(
        max_length=150
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )


class DonorUpdateSerializer(
    DonorCreateSerializer
):
    first_name = serializers.CharField(
        max_length=150,
        required=False,
    )

    last_name = serializers.CharField(
        max_length=150,
        required=False,
    )


class DonationSerializer(
    serializers.ModelSerializer
):
    donor_name = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Donation

        fields = [
            "donation_id",
            "donor",
            "donor_name",
            "amount",
            "donation_date",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "donation_id",
            "donor_name",
            "created_at",
        ]

    def get_donor_name(
        self,
        obj,
    ):
        return (
            obj.donor.user.get_full_name()
            or obj.donor.user.username
        )

    def validate_amount(
        self,
        value,
    ):
        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than 0."
            )

        return value


class AdminUserSerializer(
    serializers.ModelSerializer
):
    phone = serializers.CharField(
        source="profile.phone",
        read_only=True,
    )

    must_change_password = (
        serializers.BooleanField(
            source="profile.must_change_password",
            read_only=True,
        )
    )

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "is_active",
            "is_superuser",
            "must_change_password",
        ]

        read_only_fields = fields


class AdminCreateSerializer(
    serializers.Serializer
):
    first_name = serializers.CharField(
        max_length=150
    )

    last_name = serializers.CharField(
        max_length=150
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )


class LoanListSerializer(
    serializers.Serializer
):
    loan_id = serializers.UUIDField()
    loan_type = serializers.CharField()

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    start_date = serializers.DateField()
    status = serializers.CharField()

    borrower = serializers.DictField()

    trustee = serializers.DictField(
        allow_null=True
    )


class LoanDetailSerializer(
    serializers.Serializer
):
    loan_id = serializers.UUIDField()

    loan_type = (
        serializers.SerializerMethodField()
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    start_date = serializers.DateField()

    status = serializers.CharField()

    created_at = serializers.DateTimeField()

    form_file_url = (
        serializers.SerializerMethodField()
    )

    standing_order_form_file_url = (
        serializers.SerializerMethodField()
    )

    trustee_id = (
        serializers.SerializerMethodField()
    )

    borrower = (
        serializers.SerializerMethodField()
    )

    trustee = (
        serializers.SerializerMethodField()
    )

    details = (
        serializers.SerializerMethodField()
    )

    def get_loan_type(
        self,
        obj,
    ):
        if isinstance(
            obj,
            LoanChecks,
        ):
            return "checks"

        return "standing_order"

    def get_borrower(
        self,
        obj,
    ):
        borrower = obj.borrower
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
            "id_number":
                borrower.id_number,

            "address":
                borrower.address,

            "name":
                name,

            "email":
                (
                    borrower.email
                    or (
                        user.email
                        if user
                        else ""
                    )
                ),

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

            "created_at":
                borrower.created_at,
        }

    def get_trustee(
        self,
        obj,
    ):
        trustee = obj.trustee

        if not trustee:
            return None

        user = trustee.user

        return {
            "name":
                (
                    user.get_full_name()
                    or user.username
                ),

            "community":
                trustee.community,

            "phone":
                (
                    getattr(
                        getattr(
                            user,
                            "profile",
                            None,
                        ),
                        "phone",
                        "",
                    )
                    or ""
                ),

            "notes":
                trustee.notes,
        }

    def get_trustee_id(
        self,
        obj,
    ):
        if not obj.trustee_id:
            return None

        return str(
            obj.trustee_id
        )

    def get_details(
        self,
        obj,
    ):
        if isinstance(
            obj,
            LoanChecks,
        ):
            return {
                "num_payments":
                    obj.num_payments,

                "check_details":
                    obj.check_details,

                "predefined_schedule":
                    obj.predefined_schedule,
            }

        return {
            "num_payments":
                obj.num_payments,

            "monthly_amount":
                obj.monthly_amount,

            "charge_day":
                obj.charge_day,

            "stop_date":
                obj.stop_date,
        }

    def get_form_file_url(
        self,
        obj,
    ):
        if not obj.form_file:
            return None

        request = self.context.get(
            "request"
        )

        path = reverse(
            "loan-signed-form",
            kwargs={
                "loan_id":
                    obj.loan_id
            },
        )

        if request:
            return (
                request.build_absolute_uri(
                    path
                )
            )

        return path

    def get_standing_order_form_file_url(
        self,
        obj,
    ):
        if not isinstance(
            obj,
            LoanStandingOrder,
        ):
            return None

        if not getattr(
            obj,
            "standing_order_form_file",
            None,
        ):
            return None

        request = self.context.get(
            "request"
        )

        path = reverse(
            "loan-standing-order-form",
            kwargs={
                "loan_id":
                    obj.loan_id
            },
        )

        if request:
            return (
                request.build_absolute_uri(
                    path
                )
            )

        return path


class LoanUpdateSerializer(
    serializers.Serializer
):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    start_date = serializers.DateField()

    number_of_payments = (
        serializers.IntegerField()
    )

    trustee_id = serializers.UUIDField()

    status = serializers.ChoiceField(
        choices=[
            "ACTIVE",
            "CLOSED",
            "OVERDUE",
        ]
    )

    def validate_amount(
        self,
        value,
    ):
        if value <= 0:
            raise serializers.ValidationError(
                "Must be greater than 0."
            )

        return value

    def validate_number_of_payments(
        self,
        value,
    ):
        if value < 1:
            raise serializers.ValidationError(
                "Must be at least 1."
            )

        return value

    def validate_trustee_id(
        self,
        value,
    ):
        if not Trustee.objects.filter(
            trustee_id=value,
            user__is_active=True,
        ).exists():
            raise serializers.ValidationError(
                "Trustee not found."
            )

        return value

    def validate(
        self,
        attrs,
    ):
        request = self.context.get(
            "request"
        )

        if request:
            allowed = {
                "amount",
                "start_date",
                "number_of_payments",
                "trustee_id",
                "status",
            }

            extra = (
                set(request.data.keys())
                - allowed
            )

            if extra:
                raise serializers.ValidationError({
                    key: [
                        "Unexpected field."
                    ]
                    for key in sorted(extra)
                })

        return attrs

    def update(
        self,
        instance,
        validated_data,
    ):
        amount = validated_data[
            "amount"
        ]

        num_payments = validated_data[
            "number_of_payments"
        ]

        instance.amount = amount

        instance.start_date = (
            validated_data[
                "start_date"
            ]
        )

        instance.status = (
            validated_data[
                "status"
            ]
        )

        instance.trustee = (
            Trustee.objects.get(
                trustee_id=
                    validated_data[
                        "trustee_id"
                    ]
            )
        )

        instance.num_payments = (
            num_payments
        )

        if isinstance(
            instance,
            LoanStandingOrder,
        ):
            try:
                instance.monthly_amount = (
                    Decimal(amount)
                    / Decimal(num_payments)
                ).quantize(
                    Decimal("0.01")
                )

            except (
                InvalidOperation,
                ZeroDivisionError,
            ):
                raise serializers.ValidationError({
                    "number_of_payments": [
                        "Invalid value."
                    ]
                })

            instance.charge_day = (
                instance.start_date.day
            )

        instance.save()

        return instance

    def create(
        self,
        validated_data,
    ):
        raise serializers.ValidationError({
            "detail": [
                "Create is not supported."
            ]
        })


class BorrowerCreateSerializer(
    serializers.Serializer
):
    id_number = serializers.CharField(
        max_length=20
    )

    first_name = serializers.CharField(
        max_length=100
    )

    last_name = serializers.CharField(
        max_length=100
    )

    phone = serializers.CharField(
        max_length=20
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    address = serializers.CharField(
        max_length=255
    )


class LoanDetailsCreateSerializer(
    serializers.Serializer
):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    num_payments = (
        serializers.IntegerField()
    )

    start_date = serializers.DateField()

    def validate_amount(
        self,
        value,
    ):
        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than 0."
            )

        return value

    def validate_num_payments(
        self,
        value,
    ):
        if value < 1:
            raise serializers.ValidationError(
                "Number of payments must be at least 1."
            )

        return value


class CreateLoanRequestSerializer(
    serializers.Serializer
):
    loan_type = serializers.ChoiceField(
        choices=[
            "checks",
            "standing_order",
        ]
    )

    borrower = BorrowerCreateSerializer()

    loan = LoanDetailsCreateSerializer()

    trustee_id = serializers.UUIDField()

    def validate_trustee_id(
        self,
        value,
    ):
        if not Trustee.objects.filter(
            trustee_id=value,
            user__is_active=True,
        ).exists():
            raise serializers.ValidationError(
                "Trustee not found."
            )

        return value


class PaymentSerializer(
    serializers.ModelSerializer
):
    payment_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    amount_due = serializers.DecimalField(
        source="amount",
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        model = Payment

        fields = [
            "payment_id",
            "due_date",
            "amount_due",
            "amount_paid",
            "status",
            "is_manual_exception",
            "exception_note",
        ]

        read_only_fields = fields


class PaymentExceptionSerializer(
    serializers.Serializer
):
    status = serializers.ChoiceField(
        choices=[
            Payment.STATUS_PENDING,
            Payment.STATUS_PAID,
            Payment.STATUS_LATE,
        ],
        required=False,
    )

    amount_paid = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )

    note = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=False,
    )

    clear_exception = (
        serializers.BooleanField(
            required=False,
            default=False,
        )
    )

    def validate(
        self,
        attrs,
    ):
        if attrs.get(
            "clear_exception"
        ):
            return attrs

        if "status" not in attrs:
            raise serializers.ValidationError({
                "status": [
                    "This field is required."
                ]
            })

        if not attrs.get("note"):
            raise serializers.ValidationError({
                "note": [
                    "A note is required "
                    "for a manual exception."
                ]
            })

        return attrs

    def validate_amount_paid(
        self,
        value,
    ):
        if value < 0:
            raise serializers.ValidationError(
                "Amount paid cannot be negative."
            )

        return value


class ReminderSettingsSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ReminderSettings

        fields = [
            "enabled",
            "days_before",
            "channel",
            "updated_at",
        ]

        read_only_fields = [
            "updated_at",
        ]

    def validate_days_before(
        self,
        value,
    ):
        if value > 30:
            raise serializers.ValidationError(
                "Reminder timing cannot exceed 30 days."
            )

        return value