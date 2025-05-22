from pathlib import Path

from django.conf import settings

from eurydice.origin.core.models import TransferableRange


def file_path(transferable_range: TransferableRange) -> Path:
    """
    Returns the expected file path for a given transferable.
    """
    return Path(settings.TRANSFERABLE_STORAGE_DIR) / str(transferable_range.id)


def delete(transferable_range: TransferableRange) -> None:
    """
    Deletes data from the filesystem for a given transferable range.
    """
    path = file_path(transferable_range)
    path.unlink(missing_ok=True)


def write_bytes(transferable_range: TransferableRange, data: bytes) -> None:
    """
    Writes data to the filesystem for a given transferable range.
    """
    path = file_path(transferable_range)
    path.write_bytes(data)


def append_bytes(transferable_range: TransferableRange, data: bytes) -> None:
    """
    Writes data to the filesystem for a given transferable range by adding to its file.
    """
    path = file_path(transferable_range)
    with open(path, "ab+") as file:
        file.write(data)


def read_bytes(transferable_range: TransferableRange) -> bytes:
    """
    Reads data from the filesystem for a given transferable range.
    """
    path = file_path(transferable_range)
    return path.read_bytes()
