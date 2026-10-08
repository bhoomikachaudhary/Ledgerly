import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.core.constants import RECEIPT_ALLOWED_CONTENT_TYPES, RECEIPT_MAX_SIZE_BYTES

settings = get_settings()

_EXTENSION_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}


def _validate(file: UploadFile, size: int) -> None:
    if file.content_type not in RECEIPT_ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported file type: {file.content_type}. Allowed: "
            f"{', '.join(sorted(RECEIPT_ALLOWED_CONTENT_TYPES))}",
        )
    if size > RECEIPT_MAX_SIZE_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File too large: max {RECEIPT_MAX_SIZE_BYTES // (1024 * 1024)}MB",
        )


def save_receipt(file: UploadFile, user_id: uuid.UUID, expense_id: uuid.UUID) -> str:
    """
    Validate and persist a receipt file, returning its storage key.

    Dev implementation writes to local disk under settings.upload_dir. In prod this
    function's body is the only thing that needs to change (swap in an S3/R2 client) —
    callers only ever see the returned key, never a filesystem path.
    """
    contents = file.file.read()
    _validate(file, len(contents))

    extension = _EXTENSION_BY_CONTENT_TYPE[file.content_type]
    key = f"receipts/{user_id}/{expense_id}{extension}"

    destination = Path(settings.upload_dir) / key
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(contents)

    return key
