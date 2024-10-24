from pathlib import Path

from django.conf import settings

from eurydice.destination.core import models


def file_path(incoming_transferable: models.IncomingTransferable) -> Path:
    """
    Returns the expected file path for a given transferable.
    """
    return (
        Path(settings.TRANSFERABLE_STORAGE_DIR)
        / incoming_transferable.s3_bucket_name
        / incoming_transferable.s3_object_name
    )


def delete(incoming_transferable: models.IncomingTransferable) -> None:
    """
    Deletes data from the filesystem for a given transferable.
    """
    path = file_path(incoming_transferable)
    path.unlink(missing_ok=True)
