from pathlib import Path

from django.conf import settings

from eurydice.destination.core.models import IncomingTransferable


def file_path(transferable: IncomingTransferable) -> Path:
    """
    Returns the expected file path for a given transferable.
    """
    return Path(settings.TRANSFERABLE_STORAGE_DIR) / str(transferable.id)


def delete(transferable: IncomingTransferable) -> None:
    """
    Deletes data from the filesystem for a given transferable range.
    """
    path = file_path(transferable)
    path.unlink(missing_ok=True)


def write_bytes(transferable: IncomingTransferable, data: bytes) -> None:
    """
    Writes data to the filesystem for a given transferable range.
    """
    path = file_path(transferable)
    path.write_bytes(data)


def append_bytes(transferable: IncomingTransferable, data: bytes) -> None:
    """
    Writes data to the filesystem for a given transferable range by adding to its file.
    """
    path = file_path(transferable)
    with open(path, "ab+") as file:
        file.write(data)


def read_bytes(transferable: IncomingTransferable) -> bytes:
    """
    Reads data from the filesystem for a given transferable range.
    """
    path = file_path(transferable)
    return path.read_bytes()
