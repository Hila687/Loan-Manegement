from pathlib import Path

from django.conf import settings
from rest_framework.exceptions import ValidationError


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


def validation_error(
    field_name: str,
    message: str,
):
    raise ValidationError(
        {
            field_name: [
                message
            ]
        }
    )


def validate_signed_form(
    file,
    field_name: str = "form_file",
):
    if file is None:
        validation_error(
            field_name,
            "A signed form is required.",
        )

    if file.size <= 0:
        validation_error(
            field_name,
            "The uploaded file is empty.",
        )

    if (
        file.size
        > settings.SIGNED_FORM_MAX_BYTES
    ):
        validation_error(
            field_name,
            "The uploaded file is too large.",
        )

    extension = Path(
        file.name
    ).suffix.lower()

    if (
        extension
        not in ALLOWED_EXTENSIONS
    ):
        validation_error(
            field_name,
            "Only PDF, JPG and PNG files are allowed.",
        )

    content_type = (
        getattr(
            file,
            "content_type",
            "",
        )
        or ""
    ).lower()

    if (
        content_type
        and content_type
        not in ALLOWED_CONTENT_TYPES
    ):
        validation_error(
            field_name,
            "Invalid file content type.",
        )

    original_position = (
        file.tell()
    )

    header = file.read(16)

    file.seek(
        original_position
    )

    valid_signature = False

    if extension == ".pdf":
        valid_signature = (
            header.startswith(
                b"%PDF"
            )
        )

    elif extension in {
        ".jpg",
        ".jpeg",
    }:
        valid_signature = (
            header.startswith(
                b"\xff\xd8\xff"
            )
        )

    elif extension == ".png":
        valid_signature = (
            header.startswith(
                b"\x89PNG\r\n\x1a\n"
            )
        )

    if not valid_signature:
        validation_error(
            field_name,
            "The file content does not match its extension.",
        )

    return file
