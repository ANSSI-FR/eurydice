from pathlib import Path
from uuid import UUID

import pytest
from django.conf import Settings

from eurydice.origin.storage import fs
from tests.origin.integration import factory


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("storage_dir", "transferable_range_id", "expected_path"),
    [
        (
            "storage_dir",
            UUID("a8fcc4dd-4448-42f0-b678-a99ae8a8189a"),
            Path("storage_dir/a8fcc4dd-4448-42f0-b678-a99ae8a8189a"),
        ),
        (
            "1",
            UUID("fc7a8f27-cdca-486d-b55d-7a9d1e1b2fe7"),
            Path("1/fc7a8f27-cdca-486d-b55d-7a9d1e1b2fe7"),
        ),
        (
            "/",
            UUID("c49190cd-16dc-4027-953d-d5c1a92f8560"),
            Path("/c49190cd-16dc-4027-953d-d5c1a92f8560"),
        ),
    ],
)
def test_fs_file_path(
    settings: Settings,
    storage_dir: str,
    transferable_range_id: str,
    expected_path: Path,
):
    settings.TRANSFERABLE_STORAGE_DIR = storage_dir

    obj = factory.TransferableRangeFactory(id=transferable_range_id)
    assert expected_path == fs.file_path(obj)
    fs.delete(obj)


@pytest.mark.django_db()
def test_fs_delete():

    obj = factory.TransferableRangeFactory(
        id=UUID("a8fcc4dd-4448-42f0-b678-a99ae8a8189a")
    )

    file_path = fs.file_path(obj)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()

    fs.delete(obj)

    assert not file_path.exists()


@pytest.mark.django_db()
def test_fs_write_bytes():
    obj = factory.TransferableRangeFactory(
        id=UUID("a8fcc4dd-4448-42f0-b678-a99ae8a8189a")
    )

    fs.write_bytes(obj, b"test data")

    assert fs.file_path(obj).exists()
    assert fs.file_path(obj).read_text() == "test data"
    fs.delete(obj)


@pytest.mark.django_db()
def test_fs_append_bytes():
    obj = factory.TransferableRangeFactory(
        id=UUID("a8fcc4dd-4448-42f0-b678-a99ae8a8189b")
    )

    fs.append_bytes(obj, b"test")
    fs.append_bytes(obj, b" data")

    assert fs.file_path(obj).exists()
    assert fs.file_path(obj).read_text() == "test data"
    fs.delete(obj)


@pytest.mark.django_db()
def test_fs_read_bytes():

    obj = factory.TransferableRangeFactory(
        id=UUID("a8fcc4dd-4448-42f0-b678-a99ae8a8189a")
    )

    file_path = fs.file_path(obj)
    file_path.write_bytes(b"test data")

    assert fs.read_bytes(obj) == b"test data"
    fs.delete(obj)
