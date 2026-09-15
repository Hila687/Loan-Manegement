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


def validate_signed_form(file):
    if file is None:
        raise ValidationError({
            "form_file": [
                "A signed form is required."
            ]
        })

    if file.size <= 0:
        raise ValidationError({
            "form_file": [
                "The uploaded file is empty."
            ]
        })

    if file.size > settings.SIGNED_FORM_MAX_BYTES:
        raise ValidationError({
            "form_file": [
                "The uploaded file is too large."
            ]
        })

    extension = Path(file.name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError({
            "form_file": [
                "Only PDF, JPG and PNG files are allowed."
            ]
        })

    content_type = (
        getattr(file, "content_type", "")
        or ""
    ).lower()

    if (
        content_type
        and content_type not in ALLOWED_CONTENT_TYPES
    ):
        raise ValidationError({
            "form_file": [
                "Invalid file content type."
            ]
        })

    original_position = file.tell()

    header = file.read(16)

    file.seek(original_position)

    valid_signature = False

    if extension == ".pdf":
        valid_signature = header.startswith(b"%PDF")

    elif extension in {
        ".jpg",
        ".jpeg",
    }:
        valid_signature = header.startswith(
            b"\xff\xd8\xff"
        )

    elif extension == ".png":
        valid_signature = header.startswith(
            b"\x89PNG\r\n\x1a\n"
        )

    if not valid_signature:
        raise ValidationError({
            "form_file": [
                "The file content does not match its extension."
            ]
        })

    return file