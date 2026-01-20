import io
from unittest import mock

import pytest
from django import conf
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from faker import Faker
from rest_framework import status, test

from eurydice.origin.api.utils.metadata_headers import NEEDED_METADATA
from eurydice.origin.api.views import outgoing_transferable
from eurydice.origin.core import models
from tests.common.decryption_constants import ENCRYPTED_PART, user_provided_metadata_encrypted
from tests.origin.integration import factory


@pytest.mark.django_db()
@pytest.mark.parametrize("nb_ranges", [1, 2])
@mock.patch(
    "eurydice.origin.api.views.outgoing_transferable._finalize_transferable",
    side_effect=RuntimeError("Something terrible happened!"),
)
def test__perform_create_transferable_ranges_error_rollback(
    mocked_finalize_transferable: mock.Mock,
    nb_ranges: int,
    faker: Faker,
    settings: conf.Settings,
):
    settings.TRANSFERABLE_RANGE_SIZE = 1
    data = faker.binary(length=settings.TRANSFERABLE_RANGE_SIZE * nb_ranges)
    transferable = factory.OutgoingTransferableFactory(
        sha1=None, bytes_received=0, size=len(data), submission_succeeded_at=None
    )

    with pytest.raises(RuntimeError, match="Something terrible happened!"):
        outgoing_transferable._perform_create_transferable_ranges(transferable=transferable, stream=io.BytesIO(data))

    transferable.refresh_from_db()
    assert transferable.bytes_received == (nb_ranges - 1) * settings.TRANSFERABLE_RANGE_SIZE
    assert transferable.sha1 is None
    assert models.TransferableRange.objects.count() == nb_ranges - 1

    mocked_finalize_transferable.assert_called_once()


@pytest.mark.django_db()
@pytest.mark.parametrize("provide_size", [False, True])
@pytest.mark.parametrize("data_size", ["TRANSFERABLE_RANGE_SIZE", 0])
def test__perform_create_transferable_ranges(
    data_size: str | int,
    provide_size: bool,
    faker: Faker,
    settings: conf.Settings,
):
    settings.TRANSFERABLE_RANGE_SIZE = 256

    if data_size == "TRANSFERABLE_RANGE_SIZE":
        data_size = settings.TRANSFERABLE_RANGE_SIZE

    data = faker.binary(data_size)
    transferable = factory.OutgoingTransferableFactory(
        sha1=None,
        bytes_received=0,
        size=len(data) if provide_size else None,
        submission_succeeded_at=None,
    )

    outgoing_transferable._perform_create_transferable_ranges(transferable=transferable, stream=io.BytesIO(data))

    transferable.refresh_from_db()
    assert transferable.bytes_received == data_size
    assert transferable.size == len(data)
    assert models.TransferableRange.objects.count() == 1


# With encryption enabled


@pytest.mark.django_db(transaction=True)
def test_encrypted_multiplart_upload_should_succeeed(
    api_client: test.APIClient,
):
    user_profile = factory.UserProfileFactory()
    api_client.force_authenticate(user_profile.user)
    request = {
        "user": {"username": "test"},
        "data": {},
    }

    # Init
    url = reverse("transferable-init-multipart-upload")
    transferables = models.OutgoingTransferable.objects.get_queryset()
    assert len(transferables) == 0

    response = api_client.post(
        url,
        request,
        headers={"Metadata-Encrypted": "true", "Metadata-Name": "testname"},
    )

    transferable_id = response.data["id"]
    assert response.status_code == status.HTTP_200_OK, response.status_code

    transferables = models.OutgoingTransferable.objects.get_queryset()
    assert len(transferables) == 1
    assert transferables[0].name == "testname"

    # Upload part
    url = reverse(
        "transferable-upload-file-part",
        kwargs={"pk": transferable_id},
    )
    file_data = SimpleUploadedFile(
        "part1.bin",
        ENCRYPTED_PART,
        content_type="application/octet-stream",
    )

    response = api_client.post(
        url,
        {"file_part": file_data},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK, response.status_code

    # Finalize upload
    url = reverse("transferable-finalize-multipart-upload", kwargs={"pk": transferable_id})

    response = api_client.get(
        url,
        request,
        headers=user_provided_metadata_encrypted,
    )

    assert response.status_code == status.HTTP_201_CREATED, response.status_code

    transferables = models.OutgoingTransferable.objects.get_queryset()
    assert len(transferables) == 1
    transferable: models.OutgoingTransferable = transferables[0]
    assert transferable.name == "testname"


@pytest.mark.django_db(transaction=True)
def test_upload_single_part_no_data_should_fail(
    faker: Faker,
    api_client: test.APIClient,
):
    user_profile = factory.UserProfileFactory()
    api_client.force_authenticate(user_profile.user)

    request = {
        "user": {"username": "test"},
        "data": {},
    }

    # Init
    url = reverse("transferable-init-multipart-upload")
    transferables = models.OutgoingTransferable.objects.get_queryset()
    assert len(transferables) == 0

    response = api_client.post(
        url,
        request,
        headers={"Metadata-Encrypted": "true", "Metadata-Name": "testname"},
    )

    transferable_id = response.data["id"]

    url = reverse(
        "transferable-upload-file-part",
        kwargs={"pk": transferable_id},
    )

    response = api_client.post(
        url,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.status_code
    transferable = models.OutgoingTransferable.objects.get_queryset()[0]
    assert transferable.bytes_received == 0
    assert transferable.size is None
    assert not transferable.submission_succeeded


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "removed_metadata",
    NEEDED_METADATA,
)
def test_finalize_upload_missing_metadata_should_fail(
    removed_metadata: str,
    api_client: test.APIClient,
):
    user_profile = factory.UserProfileFactory()
    api_client.force_authenticate(user_profile.user)

    request = {
        "user": {"username": "test"},
        "data": {},
    }

    metadata = user_provided_metadata_encrypted.copy()
    metadata.pop(removed_metadata)

    # Init
    url = reverse("transferable-init-multipart-upload")
    transferables = models.OutgoingTransferable.objects.get_queryset()
    assert len(transferables) == 0

    response = api_client.post(
        url,
        request,
        headers={"Metadata-Encrypted": "true", "Metadata-Name": "testname"},
    )

    transferable_id = response.data["id"]
    # Upload part
    url = reverse(
        "transferable-upload-file-part",
        kwargs={"pk": transferable_id},
    )
    file_data = SimpleUploadedFile(
        "part1.bin",
        ENCRYPTED_PART,
        content_type="application/octet-stream",
    )

    response = api_client.post(
        url,
        {"file_part": file_data},
        format="multipart",
    )

    # Finalize
    url = reverse("transferable-finalize-multipart-upload", kwargs={"pk": transferable_id})

    response = api_client.get(
        url,
        request,
        headers=metadata,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.status_code


@pytest.mark.django_db(transaction=True)
def test_upload_encrypted_size_mismatch_error(
    faker: Faker,
    api_client: test.APIClient,
):
    user_profile = factory.UserProfileFactory()
    api_client.force_authenticate(user_profile.user)

    request = {
        "user": {"username": "test"},
        "data": {},
    }

    # Init
    url = reverse("transferable-init-multipart-upload")

    response = api_client.post(
        url,
        request,
        headers={"Metadata-Encrypted": "true", "Metadata-Name": "testname"},
    )

    transferable_id = response.data["id"]
    # Upload part
    url = reverse(
        "transferable-upload-file-part",
        kwargs={"pk": transferable_id},
    )
    file_data = SimpleUploadedFile(
        "part1.bin",
        ENCRYPTED_PART,
        content_type="application/octet-stream",
    )

    response = api_client.post(
        url,
        {"file_part": file_data},
        format="multipart",
    )

    # Finalize
    url = reverse("transferable-finalize-multipart-upload", kwargs={"pk": transferable_id})
    transferables = models.OutgoingTransferable.objects.get_queryset()
    assert len(transferables) == 1
    metadata = user_provided_metadata_encrypted.copy()
    metadata["Metadata-Encrypted-Size"] = "1000"
    response = api_client.get(url, request, headers=metadata)

    json_data = response.json()

    assert response.status_code == 400
    assert json_data["detail"] == (
        "Content-Length header does not match"
        f" the size of the request's body. Read {len(ENCRYPTED_PART)} bytes,"
        f" expected {metadata['Metadata-Encrypted-Size']}."
    )
    transferable = models.OutgoingTransferable.objects.get(id=transferable_id)

    assert transferable.size == int(metadata["Metadata-Encrypted-Size"])
    assert not transferable.submission_succeeded
