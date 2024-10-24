from pathlib import Path

import pytest
from django.conf import Settings

import eurydice.destination.storage.fs as fs
from tests.destination.integration import factory


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("storage_dir", "bucket_name", "object_name", "expected_path"),
    [
        (
            "storage_dir",
            "bucket_name",
            "object_name",
            Path("storage_dir/bucket_name/object_name"),
        ),
        ("1", "2", "3", Path("1/2/3")),
        ("/", "2", "3", Path("/2/3")),
    ],
)
def test_fs_file_path(
    settings: Settings,
    storage_dir: str,
    bucket_name: str,
    object_name: str,
    expected_path: Path,
):
    settings.TRANSFERABLE_STORAGE_DIR = storage_dir

    obj = factory.IncomingTransferableFactory(
        s3_bucket_name=bucket_name,
        s3_object_name=object_name,
    )
    assert expected_path == fs.file_path(obj)


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("bucket_name", "object_name"),
    [
        (
            "bucket_name",
            "object_name",
        ),
        ("2", "3"),
    ],
)
def test_fs_delete(
    settings: Settings,
    tmp_path: Path,
    bucket_name: str,
    object_name: str,
):
    settings.TRANSFERABLE_STORAGE_DIR = tmp_path

    obj = factory.IncomingTransferableFactory(
        s3_bucket_name=bucket_name,
        s3_object_name=object_name,
    )

    file_path = fs.file_path(obj)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()

    fs.delete(obj)

    assert not file_path.exists()
