import hashlib
import math
from itertools import product
from typing import Any
from unittest import mock

import dateutil.parser
import pytest
from django import conf
from django.db.models.query import Prefetch
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from freezegun import freeze_time
from rest_framework import status
from rest_framework import test
from rest_framework.authtoken.models import Token

from eurydice.common import enums
from eurydice.common import minio
from eurydice.origin.api.views import OutgoingTransferableViewSet
from eurydice.origin.core import enums as origin_enums
from eurydice.origin.core import models
from tests.origin.integration import factory as models_factory


@pytest.fixture()
def _s3_bucket(faker: Faker, settings: conf.Settings) -> Any:
    bucket_name = f"test-{faker.pystr().lower()}"
    settings.MINIO_BUCKET_NAME = bucket_name

    minio.client.make_bucket(bucket_name=bucket_name)

    yield

    for s3_obj in minio.client.list_objects(bucket_name=bucket_name):
        minio.client.remove_object(
            bucket_name=bucket_name, object_name=s3_obj.object_name
        )

    minio.client.remove_bucket(bucket_name=bucket_name)


def _api_client_session_auth(api_client: test.APIClient, user: models.User) -> None:
    api_client.force_login(user)


def _api_client_token_auth(api_client: test.APIClient, user: models.User) -> None:
    token = Token.objects.create(user=user)

    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")


class TestOutgoingTransferableInTransaction(test.APITransactionTestCase):
    def test_destroy_outgoing_transferable_error_not_authorized(
        self,
    ):
        obj = models_factory.OutgoingTransferableFactory()
        another_user = models_factory.UserFactory()

        self.client.force_login(user=another_user)
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"].code == "not_found"

    def test_retrieve_outgoing_transferable_error_not_authorized(
        self,
    ):
        obj = models_factory.OutgoingTransferableFactory()
        another_user = models_factory.UserFactory()

        self.client.force_login(user=another_user)
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"].code == "not_found"

    def test_create_outgoing_transferable_empty_upload_wrong_content_length(
        self,
    ):
        user_profile = models_factory.UserProfileFactory()
        self.client.force_login(user=user_profile.user)

        url = reverse("transferable-list")
        response = self.client.post(
            url,
            data=b"",
            content_type="application/octet-stream",
            HTTP_CONTENT_LENGTH="42",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_outgoing_transferable_invalid_content_length_header(
        self,
    ):
        user_profile = models_factory.UserProfileFactory()
        self.client.force_login(user=user_profile.user)

        url = reverse("transferable-list")
        response = self.client.post(
            url,
            data=b"0" * 1024,
            content_type="application/octet-stream",
            HTTP_CONTENT_LENGTH="invalid-content-length-value",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data["detail"]) == "Invalid value for Content-Length header"

    # NOTE: We test both authentication methods because,
    #       for some reason, DRF's parsers are ignored
    #       on the OutgoingTransferable view when using
    #       DRF's TokenAuthentication.
    def test_create_outgoing_transferable_unsupported_content_type_api_client(self):
        authentication_methods = [_api_client_token_auth, _api_client_session_auth]
        content_types = [
            "application/x-www-form-urlencoded",
            'multipart/form-data;boundary="boundary"',
        ]
        for authentication_method, content_type in product(
            authentication_methods, content_types
        ):
            with self.subTest():
                user_profile = models_factory.UserProfileFactory()

                url = reverse("transferable-list")

                authentication_method(self.client, user_profile.user)

                response = self.client.post(
                    url, content_type=content_type, data={"file": "Hello, world"}
                )

                assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
                assert response.data["detail"].code == "unsupported_media_type"

    def test_filter_sha1_should_raise(self):
        user_profile = models_factory.UserProfileFactory()
        self.client.force_login(user=user_profile.user)

        url = reverse("transferable-list")

        response = self.client.get(
            url, {"sha1": hashlib.sha1(b"invalid").hexdigest()[:5]}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "field sha1 malformed."}


@pytest.mark.django_db()
class TestOutgoingTransferable:
    def test_list_outgoing_transferables(self, api_client: test.APIClient):
        created_obj = models_factory.OutgoingTransferableFactory()

        obj = models.OutgoingTransferable.objects.get(id=created_obj.id)

        url = reverse("transferable-list")
        api_client.force_login(user=obj.user_profile.user)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1

        data = response.data["results"][0]
        assert data["name"] == obj.name
        if obj.sha1 is not None:
            assert bytes.fromhex(data["sha1"]) == bytes(obj.sha1)
        else:
            assert data["sha1"] is None
        assert data["size"] == obj.size
        assert data["progress"] == 0
        assert data["user_provided_meta"] == obj.user_provided_meta
        assert data["state"] == obj.state

        if obj.submission_succeeded_at is not None:
            assert (
                dateutil.parser.parse(data["submission_succeeded_at"])
                == obj.submission_succeeded_at
            )

    def test_retrieve_outgoing_transferable(self, api_client: test.APIClient):
        created_obj = models_factory.OutgoingTransferableFactory(
            submission_succeeded_at=timezone.now()
        )

        obj = models.OutgoingTransferable.objects.get(id=created_obj.id)

        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        api_client.force_login(user=obj.user_profile.user)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data["name"] == obj.name
        assert bytes.fromhex(data["sha1"]) == bytes(obj.sha1)
        assert data["size"] == obj.size
        assert data["progress"] == 0
        assert data["user_provided_meta"] == obj.user_provided_meta
        assert data["state"] == obj.state
        if obj.submission_succeeded_at is not None:
            assert (
                dateutil.parser.parse(data["submission_succeeded_at"])
                == obj.submission_succeeded_at
            )

    def test_retrieve_outgoing_transferable_error_not_authenticated(
        self, api_client: test.APIClient
    ):
        obj = models_factory.OutgoingTransferableFactory()
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"

    def test_list_outgoing_transferable_error_not_authenticated(
        self, api_client: test.APIClient
    ):
        url = reverse("transferable-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"

    def test_list_outgoing_transferable_only_own_transferables_visible(
        self, api_client: test.APIClient
    ):
        models_factory.OutgoingTransferableFactory()
        another_user = models_factory.UserFactory()

        api_client.force_login(user=another_user)
        url = reverse("transferable-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    @pytest.mark.usefixtures("_s3_bucket")
    @pytest.mark.parametrize(
        ("transferable_size", "transferable_range_size"),
        [
            # test when the len(transferable) == transferable_range_size
            (10, 10),
            # test when the len(transferable) > transferable_range_size
            (10, 5),
            # test when len(transferable) < transferable_range_size
            (5, 10),
            # test when len(transferable) > transferable_range_size
            # and non proportional transferable_range_size
            (10, 3),
            (0, 1),
        ],
    )
    def test_create_outgoing_transferable(
        self,
        transferable_size: int,
        transferable_range_size: int,
        api_client: test.APIClient,
        settings: conf.Settings,
        faker: Faker,
    ):
        """Upload a file to the origin API.
        Assert DB entries are correctly created.
        Assert the S3 objects contain the correct file.

        Args:
            transferable_size (int): size of the random bytes to upload
            transferable_range_size (int): overridden django settings eurydice parameter
        """
        user_profile = models_factory.UserProfileFactory()

        file_path = faker.file_path()

        random_bytes = faker.binary(length=transferable_size)

        url = reverse("transferable-list")

        api_client.force_login(user=user_profile.user)

        settings.TRANSFERABLE_RANGE_SIZE = transferable_range_size

        now = timezone.now()
        with freeze_time(now):
            # post file
            response = api_client.post(
                url,
                data=random_bytes,
                content_type="application/octet-stream",
                HTTP_METADATA_PATH=file_path,
            )

            data = response.data

            assert dateutil.parser.parse(data["created_at"]) == now

        assert bytes.fromhex(data["sha1"]) == hashlib.sha1(random_bytes).digest()
        assert data["size"] == len(random_bytes)
        assert dateutil.parser.parse(data["submission_succeeded_at"]) == now
        assert data["state"] == enums.OutgoingTransferableState.PENDING.value
        assert data["user_provided_meta"] == {"Metadata-Path": file_path}
        assert data["progress"] == 0
        assert data["bytes_transferred"] == 0
        assert data["finished_at"] is None
        assert data["speed"] is None
        assert data["estimated_finish_date"] is None

        outgoing_transferable = models.OutgoingTransferable.objects.prefetch_related(
            Prefetch(
                "transferable_ranges",
                queryset=models.TransferableRange.objects.order_by("byte_offset"),
            )
        ).get(id=data["id"])

        if transferable_size == 0:
            expected_transferable_range_count = 1
        else:
            expected_transferable_range_count = math.ceil(
                transferable_size / transferable_range_size
            )

        assert (
            len(outgoing_transferable.transferable_ranges.all())
            == expected_transferable_range_count
        )

        # Verify uploaded transferable_ranges
        final_transferable_digest = hashlib.sha1()
        for transferable_range in outgoing_transferable.transferable_ranges.all():
            response = None
            try:
                response = minio.client.get_object(
                    bucket_name=transferable_range.s3_bucket_name,
                    object_name=transferable_range.s3_object_name,
                )
                final_transferable_digest.update(response.read())
            finally:
                if response:
                    response.close()
                    response.release_conn()

    def test_create_outgoing_transferable_unauthorized(
        self, faker: Faker, api_client: test.APIClient
    ):
        """
        Assert only authenticated users can create Transferables
        """
        random_bytes = faker.binary(length=5)

        url = reverse("transferable-list")

        # post file
        response = api_client.post(
            url,
            data=random_bytes,
            content_type="application/octet-stream",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db(transaction=True)
    def test_create_outgoing_transferable_too_large(
        self,
        api_client: test.APIClient,
        settings: conf.Settings,
        faker: Faker,
    ):
        """
        Assert HTTP 413 is raised when trying to create a Transferable that is too large
        """

        user_profile = models_factory.UserProfileFactory()

        api_client.force_login(user=user_profile.user)

        url = reverse("transferable-list")

        # post file with a "Content-Length: 2" header
        settings.TRANSFERABLE_MAX_SIZE = 1
        response = api_client.post(
            url, content_type="application/octet-stream", HTTP_CONTENT_LENGTH="2"
        )

        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert response.data["detail"].code == "RequestEntityTooLargeError"

        # post file with a "Transfer-Encoding: chunked" header
        settings.TRANSFERABLE_RANGE_SIZE = 1
        response = api_client.post(
            url,
            content_type="application/octet-stream",
            data=faker.binary(length=2),
            HTTP_TRANSFER_ENCODING="chunked",
        )

        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert response.data["detail"].code == "RequestEntityTooLargeError"

    @mock.patch(
        "eurydice.origin.api.views.outgoing_transferable._create_transferable_ranges"
    )
    def test_create_outgoing_transferable_unexpected_exception(
        self,
        mocked_create_transferable_ranges: mock.Mock,
    ):
        assert not models.OutgoingTransferable.objects.exists()
        assert not models.TransferableRevocation.objects.exists()

        mocked_create_transferable_ranges.side_effect = RuntimeError(
            "Something bad happened!"
        )

        user_profile = models_factory.UserProfileFactory()

        api_client = test.APIClient(raise_request_exception=False)
        api_client.force_login(user=user_profile.user)
        url = reverse("transferable-list")

        response = api_client.post(
            url,
            data=b"0" * 1024,
            content_type="application/octet-stream",
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        outgoing_transferable = models.OutgoingTransferable.objects.get()
        assert outgoing_transferable.state == enums.OutgoingTransferableState.ERROR
        assert models.TransferableRevocation.objects.filter(
            reason=enums.TransferableRevocationReason.UNEXPECTED_EXCEPTION,
            outgoing_transferable=outgoing_transferable.id,
        ).exists()

    def test_create_outgoing_transferable_empty_content_length_header(
        self,
        api_client: test.APIClient,
    ):
        assert not models.OutgoingTransferable.objects.exists()

        user_profile = models_factory.UserProfileFactory()
        api_client.force_login(user=user_profile.user)

        url = reverse("transferable-list")
        response = api_client.post(
            url,
            data=b"0" * 1024,
            content_type="application/octet-stream",
            HTTP_CONTENT_LENGTH="",
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_outgoing_transferable_missing_content_type(self):
        url = reverse("transferable-list")
        user_profile = models_factory.UserProfileFactory()

        request_factory = RequestFactory()

        token = Token.objects.create(user=user_profile.user)

        request = request_factory.post(
            url, data={}, HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        request.META.pop("CONTENT_TYPE", None)

        view = OutgoingTransferableViewSet.as_view({"post": "create"})

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"].code == "MissingContentTypeError"

    def test_destroy_outgoing_transferable_success(self, api_client: test.APIClient):
        obj = models_factory.OutgoingTransferableFactory(
            _submission_succeeded=True, _submission_succeeded_at=timezone.now()
        )
        models_factory.TransferableRangeFactory(
            outgoing_transferable=obj,
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
        )
        obj = models.OutgoingTransferable.objects.get(id=obj.id)

        assert obj.state == enums.OutgoingTransferableState.PENDING

        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        api_client.force_login(user=obj.user_profile.user)
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        obj = models.OutgoingTransferable.objects.get(id=obj.id)
        assert obj.state == enums.OutgoingTransferableState.CANCELED

    def test_destroy_outgoing_transferable_error_not_authenticated(
        self, api_client: test.APIClient
    ):
        obj = models_factory.OutgoingTransferableFactory()
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"

    def test_destroy_outgoing_transferable_error_not_successfully_submitted(
        self, api_client: test.APIClient
    ):
        obj = models_factory.OutgoingTransferableFactory(submission_succeeded_at=None)

        assert not obj.submission_succeeded

        api_client.force_login(user=obj.user_profile.user)
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        revocations = models.TransferableRevocation.objects.filter(
            outgoing_transferable=obj
        )

        assert revocations.count() == 1
        assert (
            revocations.get().reason == enums.TransferableRevocationReason.USER_CANCELED
        )


@pytest.mark.parametrize("transferable_range_size", [1, 2])
@pytest.mark.parametrize(
    (
        "content_length",
        "transferable_size",
        "expected_status_code",
        "expected_revocation_count",
        "expected_error_detail",
    ),
    [
        # Test when content length == transferable size == 0
        (0, 0, status.HTTP_201_CREATED, 0, None),
        # Test when content length is 0
        (0, 2, status.HTTP_400_BAD_REQUEST, 1, "InconsistentContentLengthError"),
        # Test when content length < transferable size
        (1, 2, status.HTTP_400_BAD_REQUEST, 1, "InconsistentContentLengthError"),
        # Test when content length > transferable size
        (3, 2, status.HTTP_400_BAD_REQUEST, 1, "InconsistentContentLengthError"),
        # Test when content length == transferable size
        (2, 2, status.HTTP_201_CREATED, 0, None),
        # Test when content length is not given
        (None, 2, status.HTTP_201_CREATED, 0, None),
        # Test when content length given is just an empty string
        # (it is sometimes added like that by gunicorn)
        ("", 2, status.HTTP_201_CREATED, 0, None),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_create_outgoing_transferable_content_length(
    content_length: int,
    transferable_size: int,
    expected_status_code: int,
    transferable_range_size: int,
    expected_revocation_count: int,
    expected_error_detail: str,
    settings: conf.Settings,
    faker: Faker,
):
    """
    Assert HTTP 400 is raised when trying to create a Transferable
    with an incorrect Content-Length header
    """
    settings.TRANSFERABLE_RANGE_SIZE = transferable_range_size

    random_bytes = faker.binary(length=transferable_size)

    user_profile = models_factory.UserProfileFactory()

    client = test.APIClient()

    client.force_login(user_profile.user)

    url = reverse("transferable-list")

    request_kwargs = {
        "content_type": "application/octet-stream",
        "data": random_bytes,
    }

    if content_length is not None:
        request_kwargs["HTTP_CONTENT_LENGTH"] = content_length

    response = client.post(url, **request_kwargs)

    assert response.status_code == expected_status_code

    revocations = models.TransferableRevocation.objects.filter(
        outgoing_transferable__user_profile=user_profile
    )

    assert len(revocations) == expected_revocation_count

    if response.status_code != status.HTTP_201_CREATED:
        assert response.data["detail"].code == expected_error_detail
