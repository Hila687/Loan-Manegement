from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q, Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .loan_access import scoped_loan_querysets
from .models import (
    Borrower,
    Donation,
    Donor,
    LoanChecks,
    LoanStandingOrder,
    ReminderSettings,
    Role,
    Trustee,
    UserProfile,
)
from .permissions import (
    ROLE_ADMIN,
    ROLE_BORROWER,
    ROLE_DONOR,
    ROLE_TRUSTEE,
    IsAdminRole,
    IsAuthenticatedReadOnlyOrAdmin,
    get_role_name,
)
from .serializers import (
    AdminCreateSerializer,
    AdminUserSerializer,
    BorrowerSerializer,
    DonationSerializer,
    DonorCreateSerializer,
    DonorSerializer,
    DonorUpdateSerializer,
    ReminderSettingsSerializer,
    RoleSerializer,
    TrusteeCreateSerializer,
    TrusteeSerializer,
    TrusteeUpdateSerializer,
    UserProfileSerializer,
)
from .services import (
    audit,
    create_role_user,
    reset_user_password,
    sync_loan_querysets,
)

def user_full_name(user):
    if not user:
        return ""

    return (
        user.get_full_name().strip()
        or user.username
    )


def decimal_zero():
    return Decimal("0.00")


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Role.objects.all().order_by("name")


class UserProfileViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return (
            UserProfile.objects
            .select_related(
                "user",
                "role",
            )
            .all()
            .order_by(
                "user__username"
            )
        )


class BorrowerViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowerSerializer
    permission_classes = [
        IsAuthenticatedReadOnlyOrAdmin
    ]

    def get_queryset(self):
        queryset = (
            Borrower.objects
            .select_related(
                "user",
                "user__profile",
                "trustee",
                "trustee__user",
            )
            .all()
            .order_by(
                "last_name",
                "first_name",
                "id_number",
            )
        )

        role = get_role_name(
            self.request.user
        )

        if role == ROLE_ADMIN:
            return queryset

        if role == ROLE_TRUSTEE:
            trustee = getattr(
                self.request.user,
                "trustee_profile",
                None,
            )

            if not trustee:
                return queryset.none()

            return queryset.filter(
                trustee__community=
                    trustee.community
            )

        if role == ROLE_BORROWER:
            borrower = getattr(
                self.request.user,
                "borrower_profile",
                None,
            )

            if not borrower:
                return queryset.none()

            return queryset.filter(
                borrower_id=
                    borrower.borrower_id
            )

        return queryset.none()

    @transaction.atomic
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        required_fields = {
            "id_number":
                data.get("id_number"),
            "first_name":
                data.get("first_name"),
            "last_name":
                data.get("last_name"),
            "address":
                data.get("address"),
            "trustee":
                data.get("trustee"),
        }

        errors = {}

        for field_name, value in (
            required_fields.items()
        ):
            if value in {
                None,
                "",
            }:
                errors[field_name] = [
                    "This field is required."
                ]

        if errors:
            return Response(
                errors,
                status=
                    status.HTTP_400_BAD_REQUEST,
            )

        if Borrower.objects.filter(
            id_number=data["id_number"]
        ).exists():
            return Response(
                {
                    "id_number": [
                        "A borrower with this ID "
                        "number already exists."
                    ]
                },
                status=
                    status.HTTP_400_BAD_REQUEST,
            )

        user, temporary_password = (
            create_role_user(
                role_key="borrower",
                username_seed=
                    data["id_number"],
                first_name=
                    data["first_name"],
                last_name=
                    data["last_name"],
                email=
                    data.get(
                        "email",
                        "",
                    ),
                phone=
                    data.get(
                        "phone",
                        "",
                    ),
            )
        )

        borrower = Borrower.objects.create(
            user=user,
            trustee=data["trustee"],
            id_number=data["id_number"],
            first_name=
                data["first_name"],
            last_name=
                data["last_name"],
            phone=
                data.get(
                    "phone",
                    "",
                ),
            email=
                data.get(
                    "email",
                    "",
                ),
            address=data["address"],
        )

        audit(
            request.user,
            "CREATE_BORROWER",
            "Borrower",
            borrower.borrower_id,
        )

        response_data = (
            BorrowerSerializer(
                borrower
            ).data
        )

        response_data[
            "credentials"
        ] = {
            "username":
                user.username,
            "temporary_password":
                temporary_password,
        }

        return Response(
            response_data,
            status=
                status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        partial = kwargs.pop(
            "partial",
            False,
        )

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        borrower = serializer.save()

        credentials = None

        if borrower.user is None:
            user, temporary_password = (
                create_role_user(
                    role_key="borrower",
                    username_seed=
                        borrower.id_number,
                    first_name=
                        borrower.first_name
                        or "",
                    last_name=
                        borrower.last_name
                        or "",
                    email=
                        borrower.email
                        or "",
                    phone=
                        borrower.phone
                        or "",
                )
            )

            borrower.user = user

            borrower.save(
                update_fields=[
                    "user",
                ]
            )

            credentials = {
                "username":
                    user.username,
                "temporary_password":
                    temporary_password,
            }

        else:
            user = borrower.user

            user.first_name = (
                borrower.first_name
                or ""
            )

            user.last_name = (
                borrower.last_name
                or ""
            )

            user.email = (
                borrower.email
                or ""
            )

            user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "email",
                ]
            )

            profile = getattr(
                user,
                "profile",
                None,
            )

            if profile:
                profile.phone = (
                    borrower.phone
                    or ""
                )

                profile.save(
                    update_fields=[
                        "phone",
                    ]
                )

        audit(
            request.user,
            "UPDATE_BORROWER",
            "Borrower",
            borrower.borrower_id,
        )

        response_data = (
            BorrowerSerializer(
                borrower
            ).data
        )

        if credentials:
            response_data[
                "credentials"
            ] = credentials

        return Response(
            response_data
        )

    @transaction.atomic
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        borrower = self.get_object()

        loans_exist = (
            borrower
            .loanchecks_loans
            .exists()
            or
            borrower
            .loanstandingorder_loans
            .exists()
        )

        if loans_exist:
            return Response(
                {
                    "detail":
                        "A borrower with existing "
                        "loans cannot be deleted."
                },
                status=
                    status.HTTP_409_CONFLICT,
            )

        borrower_id = (
            borrower.borrower_id
        )

        user = borrower.user

        audit(
            request.user,
            "DELETE_BORROWER",
            "Borrower",
            borrower_id,
        )

        if user:
            user.delete()
        else:
            borrower.delete()

        return Response(
            status=
                status.HTTP_204_NO_CONTENT
        )


class TrusteeViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticatedReadOnlyOrAdmin
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return TrusteeCreateSerializer

        if self.action in {
            "update",
            "partial_update",
        }:
            return TrusteeUpdateSerializer

        return TrusteeSerializer

    def get_queryset(self):
        queryset = (
            Trustee.objects
            .select_related(
                "user",
                "user__profile",
            )
            .annotate(
                borrower_total=
                    Count(
                        "borrowers",
                        distinct=True,
                    )
            )
            .all()
            .order_by(
                "community",
                "user__last_name",
                "user__first_name",
            )
        )

        role = get_role_name(
            self.request.user
        )

        if role == ROLE_ADMIN:
            return queryset

        if role == ROLE_TRUSTEE:
            trustee = getattr(
                self.request.user,
                "trustee_profile",
                None,
            )

            if not trustee:
                return queryset.none()

            return queryset.filter(
                trustee_id=
                    trustee.trustee_id
            )

        if role == ROLE_BORROWER:
            borrower = getattr(
                self.request.user,
                "borrower_profile",
                None,
            )

            if (
                not borrower
                or not borrower.trustee_id
            ):
                return queryset.none()

            return queryset.filter(
                trustee_id=
                    borrower.trustee_id
            )

        return queryset.none()

    @transaction.atomic
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        user, temporary_password = (
            create_role_user(
                role_key="trustee",
                username_seed=(
                    f"{data['first_name']}"
                    f"{data['last_name']}"
                    f"{data['community']}"
                ),
                first_name=
                    data["first_name"],
                last_name=
                    data["last_name"],
                email=
                    data.get(
                        "email",
                        "",
                    ),
                phone=
                    data.get(
                        "phone",
                        "",
                    ),
            )
        )

        trustee = Trustee.objects.create(
            user=user,
            community=data["community"],
            notes=
                data.get(
                    "notes",
                    "",
                ),
        )

        audit(
            request.user,
            "CREATE_TRUSTEE",
            "Trustee",
            trustee.trustee_id,
        )

        response_data = (
            TrusteeSerializer(
                trustee
            ).data
        )

        response_data[
            "credentials"
        ] = {
            "username":
                user.username,
            "temporary_password":
                temporary_password,
        }

        return Response(
            response_data,
            status=
                status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        partial = kwargs.pop(
            "partial",
            False,
        )

        trustee = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        user = trustee.user

        if "first_name" in data:
            user.first_name = (
                data["first_name"]
            )

        if "last_name" in data:
            user.last_name = (
                data["last_name"]
            )

        if "email" in data:
            user.email = (
                data["email"]
            )

        user.save()

        if "phone" in data:
            profile = getattr(
                user,
                "profile",
                None,
            )

            if profile:
                profile.phone = (
                    data["phone"]
                )

                profile.save(
                    update_fields=[
                        "phone",
                    ]
                )

        if "community" in data:
            trustee.community = (
                data["community"]
            )

        if "notes" in data:
            trustee.notes = (
                data["notes"]
            )

        trustee.save()

        audit(
            request.user,
            "UPDATE_TRUSTEE",
            "Trustee",
            trustee.trustee_id,
        )

        return Response(
            TrusteeSerializer(
                trustee
            ).data
        )

    @transaction.atomic
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        trustee = self.get_object()

        if trustee.borrowers.exists():
            return Response(
                {
                    "detail":
                        "The trustee cannot be "
                        "removed while borrowers "
                        "are assigned."
                },
                status=
                    status.HTTP_409_CONFLICT,
            )

        trustee_id = (
            trustee.trustee_id
        )

        user = trustee.user

        audit(
            request.user,
            "DELETE_TRUSTEE",
            "Trustee",
            trustee_id,
        )

        user.delete()

        return Response(
            status=
                status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reset-password",
        permission_classes=[
            IsAdminRole
        ],
    )
    def reset_password(
        self,
        request,
        pk=None,
    ):
        trustee = self.get_object()

        temporary_password = (
            reset_user_password(
                trustee.user
            )
        )

        audit(
            request.user,
            "RESET_TRUSTEE_PASSWORD",
            "Trustee",
            trustee.trustee_id,
        )

        return Response({
            "username":
                trustee.user.username,
            "temporary_password":
                temporary_password,
        })


class DonorViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticatedReadOnlyOrAdmin
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return DonorCreateSerializer

        if self.action in {
            "update",
            "partial_update",
        }:
            return DonorUpdateSerializer

        return DonorSerializer

    def get_queryset(self):
        queryset = (
            Donor.objects
            .select_related(
                "user",
                "user__profile",
            )
            .annotate(
                total_donated=
                    Sum(
                        "donations__amount"
                    )
            )
            .all()
            .order_by(
                "user__last_name",
                "user__first_name",
            )
        )

        role = get_role_name(
            self.request.user
        )

        if role == ROLE_ADMIN:
            return queryset

        if role == ROLE_DONOR:
            donor = getattr(
                self.request.user,
                "donor_profile",
                None,
            )

            if not donor:
                return queryset.none()

            return queryset.filter(
                donor_id=
                    donor.donor_id
            )

        return queryset.none()

    @transaction.atomic
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        user, temporary_password = (
            create_role_user(
                role_key="donor",
                username_seed=(
                    f"{data['first_name']}"
                    f"{data['last_name']}"
                    f"{data.get('phone', '')}"
                ),
                first_name=
                    data["first_name"],
                last_name=
                    data["last_name"],
                email=
                    data.get(
                        "email",
                        "",
                    ),
                phone=
                    data.get(
                        "phone",
                        "",
                    ),
            )
        )

        donor = Donor.objects.create(
            user=user,
            phone=
                data.get(
                    "phone",
                    "",
                ),
            notes=
                data.get(
                    "notes",
                    "",
                ),
        )

        audit(
            request.user,
            "CREATE_DONOR",
            "Donor",
            donor.donor_id,
        )

        response_data = (
            DonorSerializer(
                donor
            ).data
        )

        response_data[
            "credentials"
        ] = {
            "username":
                user.username,
            "temporary_password":
                temporary_password,
        }

        return Response(
            response_data,
            status=
                status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        partial = kwargs.pop(
            "partial",
            False,
        )

        donor = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        user = donor.user

        if "first_name" in data:
            user.first_name = (
                data["first_name"]
            )

        if "last_name" in data:
            user.last_name = (
                data["last_name"]
            )

        if "email" in data:
            user.email = (
                data["email"]
            )

        user.save()

        if "phone" in data:
            donor.phone = data["phone"]

            profile = getattr(
                user,
                "profile",
                None,
            )

            if profile:
                profile.phone = (
                    data["phone"]
                )

                profile.save(
                    update_fields=[
                        "phone",
                    ]
                )

        if "notes" in data:
            donor.notes = (
                data["notes"]
            )

        donor.save()

        audit(
            request.user,
            "UPDATE_DONOR",
            "Donor",
            donor.donor_id,
        )

        return Response(
            DonorSerializer(
                donor
            ).data
        )

    @transaction.atomic
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        donor = self.get_object()

        if donor.donations.exists():
            donor.user.is_active = False

            donor.user.save(
                update_fields=[
                    "is_active",
                ]
            )

            audit(
                request.user,
                "DEACTIVATE_DONOR",
                "Donor",
                donor.donor_id,
            )

            return Response({
                "detail":
                    "Donor account was deactivated "
                    "to preserve donation history."
            })

        donor_id = donor.donor_id
        user = donor.user

        audit(
            request.user,
            "DELETE_DONOR",
            "Donor",
            donor_id,
        )

        user.delete()

        return Response(
            status=
                status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reset-password",
        permission_classes=[
            IsAdminRole
        ],
    )
    def reset_password(
        self,
        request,
        pk=None,
    ):
        donor = self.get_object()

        temporary_password = (
            reset_user_password(
                donor.user
            )
        )

        audit(
            request.user,
            "RESET_DONOR_PASSWORD",
            "Donor",
            donor.donor_id,
        )

        return Response({
            "username":
                donor.user.username,
            "temporary_password":
                temporary_password,
        })


class DonationViewSet(
    viewsets.ModelViewSet
):
    serializer_class = (
        DonationSerializer
    )

    permission_classes = [
        IsAuthenticatedReadOnlyOrAdmin
    ]

    def get_queryset(self):
        queryset = (
            Donation.objects
            .select_related(
                "donor",
                "donor__user",
            )
            .all()
        )

        role = get_role_name(
            self.request.user
        )

        if role == ROLE_ADMIN:
            return queryset

        if role == ROLE_DONOR:
            donor = getattr(
                self.request.user,
                "donor_profile",
                None,
            )

            if not donor:
                return queryset.none()

            return queryset.filter(
                donor=donor
            )

        return queryset.none()

    def perform_create(
        self,
        serializer,
    ):
        donation = serializer.save()

        audit(
            self.request.user,
            "CREATE_DONATION",
            "Donation",
            donation.donation_id,
        )

    def perform_update(
        self,
        serializer,
    ):
        donation = serializer.save()

        audit(
            self.request.user,
            "UPDATE_DONATION",
            "Donation",
            donation.donation_id,
        )

    def perform_destroy(
        self,
        instance,
    ):
        donation_id = (
            instance.donation_id
        )

        audit(
            self.request.user,
            "DELETE_DONATION",
            "Donation",
            donation_id,
        )

        instance.delete()


class AdminUserViewSet(
    viewsets.ViewSet
):
    permission_classes = [
        IsAdminRole
    ]

    def get_queryset(self):
        return (
            User.objects
            .select_related(
                "profile",
                "profile__role",
            )
            .filter(
                Q(
                    is_superuser=True
                )
                |
                Q(
                    profile__role__name__iexact=
                        "Admin"
                )
            )
            .distinct()
            .order_by(
                "username"
            )
        )

    def list(self, request):
        serializer = AdminUserSerializer(
            self.get_queryset(),
            many=True,
        )

        return Response(
            serializer.data
        )

    def retrieve(
        self,
        request,
        pk=None,
    ):
        user = self.get_queryset().filter(
            pk=pk
        ).first()

        if not user:
            return Response(
                {
                    "detail":
                        "Admin not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        return Response(
            AdminUserSerializer(
                user
            ).data
        )

    @transaction.atomic
    def create(
        self,
        request,
    ):
        if not request.user.is_superuser:
            return Response(
                {
                    "detail":
                        "Only the super-admin can "
                        "create administrator accounts."
                },
                status=
                    status.HTTP_403_FORBIDDEN,
            )

        serializer = AdminCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        user, temporary_password = (
            create_role_user(
                role_key="admin",
                username_seed=(
                    f"{data['first_name']}"
                    f"{data['last_name']}"
                ),
                first_name=
                    data["first_name"],
                last_name=
                    data["last_name"],
                email=
                    data.get(
                        "email",
                        "",
                    ),
                phone=
                    data.get(
                        "phone",
                        "",
                    ),
            )
        )

        audit(
            request.user,
            "CREATE_ADMIN",
            "User",
            user.id,
        )

        response_data = (
            AdminUserSerializer(
                user
            ).data
        )

        response_data[
            "credentials"
        ] = {
            "username":
                user.username,
            "temporary_password":
                temporary_password,
        }

        return Response(
            response_data,
            status=
                status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def partial_update(
        self,
        request,
        pk=None,
    ):
        return self.update(
            request,
            pk=pk,
            partial=True,
        )

    @transaction.atomic
    def update(
        self,
        request,
        pk=None,
        partial=False,
    ):
        target = (
            self.get_queryset()
            .filter(
                pk=pk
            )
            .first()
        )

        if not target:
            return Response(
                {
                    "detail":
                        "Admin not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        if (
            target.id
            != request.user.id
            and not request.user.is_superuser
        ):
            return Response(
                {
                    "detail":
                        "Only the super-admin can "
                        "edit another administrator."
                },
                status=
                    status.HTTP_403_FORBIDDEN,
            )

        allowed_fields = {
            "first_name",
            "last_name",
            "email",
            "phone",
        }

        extra_fields = (
            set(request.data.keys())
            - allowed_fields
        )

        if extra_fields:
            return Response(
                {
                    field: [
                        "Unexpected field."
                    ]
                    for field
                    in sorted(
                        extra_fields
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST,
            )

        if "first_name" in request.data:
            target.first_name = str(
                request.data[
                    "first_name"
                ]
            ).strip()

        if "last_name" in request.data:
            target.last_name = str(
                request.data[
                    "last_name"
                ]
            ).strip()

        if "email" in request.data:
            target.email = str(
                request.data[
                    "email"
                ]
            ).strip()

        target.save()

        if "phone" in request.data:
            profile = getattr(
                target,
                "profile",
                None,
            )

            if profile:
                profile.phone = str(
                    request.data[
                        "phone"
                    ]
                ).strip()

                profile.save(
                    update_fields=[
                        "phone",
                    ]
                )

        audit(
            request.user,
            "UPDATE_ADMIN",
            "User",
            target.id,
        )

        return Response(
            AdminUserSerializer(
                target
            ).data
        )

    @transaction.atomic
    def destroy(
        self,
        request,
        pk=None,
    ):
        if not request.user.is_superuser:
            return Response(
                {
                    "detail":
                        "Only the super-admin can "
                        "deactivate administrator "
                        "accounts."
                },
                status=
                    status.HTTP_403_FORBIDDEN,
            )

        target = (
            self.get_queryset()
            .filter(
                pk=pk
            )
            .first()
        )

        if not target:
            return Response(
                {
                    "detail":
                        "Admin not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        if target.id == request.user.id:
            return Response(
                {
                    "detail":
                        "You cannot deactivate "
                        "your own account."
                },
                status=
                    status.HTTP_400_BAD_REQUEST,
            )

        if target.is_superuser:
            return Response(
                {
                    "detail":
                        "A super-admin cannot be "
                        "deactivated from this endpoint."
                },
                status=
                    status.HTTP_400_BAD_REQUEST,
            )

        target.is_active = False

        target.save(
            update_fields=[
                "is_active",
            ]
        )

        audit(
            request.user,
            "DEACTIVATE_ADMIN",
            "User",
            target.id,
        )

        return Response(
            status=
                status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reset-password",
    )
    def reset_password(
        self,
        request,
        pk=None,
    ):
        if not request.user.is_superuser:
            return Response(
                {
                    "detail":
                        "Only the super-admin can "
                        "reset another administrator's "
                        "password."
                },
                status=
                    status.HTTP_403_FORBIDDEN,
            )

        target = (
            self.get_queryset()
            .filter(
                pk=pk
            )
            .first()
        )

        if not target:
            return Response(
                {
                    "detail":
                        "Admin not found."
                },
                status=
                    status.HTTP_404_NOT_FOUND,
            )

        temporary_password = (
            reset_user_password(
                target
            )
        )

        audit(
            request.user,
            "RESET_ADMIN_PASSWORD",
            "User",
            target.id,
        )

        return Response({
            "username":
                target.username,
            "temporary_password":
                temporary_password,
        })


class DashboardLoanSummaryView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        role = get_role_name(
            request.user
        )

        if role == ROLE_DONOR:
            checks = (
                LoanChecks.objects
                .all()
            )

            standing = (
                LoanStandingOrder.objects
                .all()
            )

        else:
            checks, standing = (
                scoped_loan_querysets(
                    request.user
                )
            )

        sync_loan_querysets(
            checks,
            standing,
        )

        checks = checks.filter(
            status=
                LoanChecks.STATUS_ACTIVE
        )

        standing = standing.filter(
            status=
                LoanStandingOrder
                .STATUS_ACTIVE
        )

        active_loans_count = (
            checks.count()
            + standing.count()
        )

        checks_total = (
            checks.aggregate(
                total=Sum("amount")
            )["total"]
            or decimal_zero()
        )

        standing_total = (
            standing.aggregate(
                total=Sum("amount")
            )["total"]
            or decimal_zero()
        )

        return Response({
            "active_loans_count":
                active_loans_count,

            "total_active_loans_amount":
                checks_total
                + standing_total,
        })

class DashboardOverviewView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        role = get_role_name(
            request.user
        )

        if role == ROLE_DONOR:
            checks = (
                LoanChecks.objects.all()
            )

            standing = (
                LoanStandingOrder.objects
                .all()
            )

        else:
            checks, standing = (
                scoped_loan_querysets(
                    request.user
                )
            )

        sync_loan_querysets(
            checks,
            standing,
        )

        active_count = (
            checks.filter(
                status="ACTIVE"
            ).count()
            +
            standing.filter(
                status="ACTIVE"
            ).count()
        )

        overdue_count = (
            checks.filter(
                status="OVERDUE"
            ).count()
            +
            standing.filter(
                status="OVERDUE"
            ).count()
        )

        closed_count = (
            checks.filter(
                status="CLOSED"
            ).count()
            +
            standing.filter(
                status="CLOSED"
            ).count()
        )

        active_amount = (
            (
                checks.filter(
                    status="ACTIVE"
                ).aggregate(
                    total=Sum("amount")
                )["total"]
                or decimal_zero()
            )
            +
            (
                standing.filter(
                    status="ACTIVE"
                ).aggregate(
                    total=Sum("amount")
                )["total"]
                or decimal_zero()
            )
        )

        donation_total = (
            Donation.objects.aggregate(
                total=Sum("amount")
            )["total"]
            or decimal_zero()
        )

        response_data = {
            "loan_status": {
                "active":
                    active_count,
                "overdue":
                    overdue_count,
                "closed":
                    closed_count,
            },

            "active_loans_amount":
                active_amount,

            "total_donations_amount":
                donation_total,
        }

        if role == ROLE_ADMIN:
            response_data[
                "people"
            ] = {
                "borrowers":
                    Borrower.objects.count(),
                "trustees":
                    Trustee.objects.filter(
                        user__is_active=True
                    ).count(),
                "donors":
                    Donor.objects.filter(
                        user__is_active=True
                    ).count(),
            }

            community_data = {}

            for loan in list(
                checks.select_related(
                    "trustee"
                )
            ) + list(
                standing.select_related(
                    "trustee"
                )
            ):
                community = (
                    loan.trustee.community
                    if loan.trustee
                    else "Unassigned"
                )

                current = (
                    community_data.setdefault(
                        community,
                        {
                            "community":
                                community,
                            "loans_count":
                                0,
                            "total_amount":
                                decimal_zero(),
                        },
                    )
                )

                current[
                    "loans_count"
                ] += 1

                current[
                    "total_amount"
                ] += loan.amount

            response_data[
                "by_community"
            ] = list(
                community_data.values()
            )

        elif role == ROLE_TRUSTEE:
            trustee = getattr(
                request.user,
                "trustee_profile",
                None,
            )

            response_data[
                "community"
            ] = (
                trustee.community
                if trustee
                else ""
            )

            response_data[
                "borrowers_count"
            ] = (
                Borrower.objects.filter(
                    trustee__community=
                        trustee.community
                ).count()
                if trustee
                else 0
            )

        elif role == ROLE_BORROWER:
            borrower = getattr(
                request.user,
                "borrower_profile",
                None,
            )

            response_data[
                "borrower"
            ] = {
                "name":
                    (
                        f"{borrower.first_name or ''} "
                        f"{borrower.last_name or ''}"
                    ).strip()
                    if borrower
                    else ""
            }

        elif role == ROLE_DONOR:
            donor = getattr(
                request.user,
                "donor_profile",
                None,
            )

            own_total = decimal_zero()

            if donor:
                own_total = (
                    donor.donations.aggregate(
                        total=Sum("amount")
                    )["total"]
                    or decimal_zero()
                )

            response_data[
                "my_donations_amount"
            ] = own_total

        return Response(
            response_data
        )


class ReminderSettingsView(APIView):
    permission_classes = [
        IsAdminRole
    ]

    def get(self, request):
        settings_object, _ = (
            ReminderSettings.objects
            .get_or_create(
                singleton_id=1
            )
        )

        return Response(
            ReminderSettingsSerializer(
                settings_object
            ).data
        )

    def patch(self, request):
        settings_object, _ = (
            ReminderSettings.objects
            .get_or_create(
                singleton_id=1
            )
        )

        serializer = (
            ReminderSettingsSerializer(
                settings_object,
                data=request.data,
                partial=True,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        settings_object = (
            serializer.save()
        )

        audit(
            request.user,
            "UPDATE_REMINDER_SETTINGS",
            "ReminderSettings",
            settings_object.singleton_id,
        )

        return Response(
            ReminderSettingsSerializer(
                settings_object
            ).data
        )