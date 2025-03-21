import base64
import contextlib
import io
from typing import Dict

import dateutil.parser
import pytest
from django.urls import reverse
from faker import Faker
from minio.error import S3Error
from rest_framework import status
from rest_framework import test

from eurydice.common import minio
from eurydice.destination.core import models
from tests.destination.integration import factory


@contextlib.contextmanager
def s3_stored_incoming_transferable():
    obj = factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.SUCCESS
    )
    data = b"Lorem ipsum dolor sit amet"

    try:
        minio.client.make_bucket(bucket_name=obj.s3_bucket_name)
        minio.client.put_object(
            bucket_name=obj.s3_bucket_name,
            object_name=obj.s3_object_name,
            data=io.BytesIO(data),
            length=len(data),
        )

        yield obj
    finally:
        minio.client.remove_object(
            bucket_name=obj.s3_bucket_name, object_name=obj.s3_object_name
        )
        minio.client.remove_bucket(bucket_name=obj.s3_bucket_name)


@pytest.mark.django_db()
class TestIncomingTransferable:
    def test_list_incoming_transferables(self, api_client: test.APIClient) -> None:
        obj = factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.ONGOING
        )

        api_client.force_login(user=obj.user_profile.user)
        url = reverse("transferable-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1

        data = response.data["results"][0]
        assert data["name"] == obj.name
        assert bytes.fromhex(data["sha1"]) == obj.sha1
        assert data["size"] == obj.size
        assert data["user_provided_meta"] == obj.user_provided_meta
        assert data["state"] == obj.state.value
        assert data["progress"] == 0
        assert data["expires_at"] is None
        assert data["bytes_received"] == obj.bytes_received

        if data["finished_at"] is None:
            assert obj.finished_at is None
        else:
            assert dateutil.parser.parse(data["finished_at"]) == obj.finished_at

    def test_list_incoming_transferables_error_not_authenticated(
        self, api_client: test.APIClient
    ):
        url = reverse("transferable-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"

    def test_retrieve_incoming_transferable(self, api_client: test.APIClient) -> None:
        obj = factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.ONGOING
        )

        api_client.force_login(user=obj.user_profile.user)
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        data = response.data
        assert data["name"] == obj.name
        assert bytes.fromhex(data["sha1"]) == obj.sha1
        assert data["size"] == obj.size
        assert data["user_provided_meta"] == obj.user_provided_meta
        assert data["state"] == obj.state.value
        assert data["progress"] == 0
        assert data["expires_at"] is None
        assert data["bytes_received"] == obj.bytes_received

        if data["finished_at"] is None:
            assert obj.finished_at is None
        else:
            assert dateutil.parser.parse(data["finished_at"]) == obj.finished_at

    def test_retrieve_incoming_transferable_error_not_authenticated(
        self, api_client: test.APIClient
    ):
        obj = factory.IncomingTransferableFactory()
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"

    def test_retrieve_outgoing_transferable_error_not_owner(
        self, api_client: test.APIClient
    ):
        obj = factory.IncomingTransferableFactory()
        another_user = factory.UserProfileFactory().user

        api_client.force_login(user=another_user)
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"].code == "not_found"

    def test_retrieve_incoming_transferable_error_not_associated(
        self, api_client: test.APIClient
    ):
        obj = factory.IncomingTransferableFactory()
        another_user = factory.UserFactory()

        api_client.force_login(user=another_user)
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"].code == "permission_denied"

    def test_retrieve_incoming_transferable_error_no_transferable(
        self,
        api_client: test.APIClient,
        faker: Faker,
    ):
        user = factory.UserProfileFactory().user

        api_client.force_login(user=user)
        url = reverse("transferable-detail", kwargs={"pk": faker.uuid4()})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"].code == "not_found"

    def test_destroy_incoming_transferable_error_not_authenticated(
        self, api_client: test.APIClient
    ) -> None:
        obj = factory.IncomingTransferableFactory()
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"

    def test_destroy_incoming_transferable_error_not_owner(
        self, api_client: test.APIClient
    ) -> None:
        obj = factory.IncomingTransferableFactory()
        another_user = factory.UserProfileFactory().user

        api_client.force_login(user=another_user)
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"].code == "not_found"

    def test_destroy_incoming_transferable_error_not_associated(
        self, api_client: test.APIClient
    ) -> None:
        obj = factory.IncomingTransferableFactory()
        another_user = factory.UserFactory()

        api_client.force_login(user=another_user)
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"].code == "permission_denied"

    def test_destroy_incoming_transferable_error_no_transferable(
        self,
        api_client: test.APIClient,
        faker: Faker,
    ):
        user = factory.UserProfileFactory().user

        api_client.force_login(user=user)
        url = reverse("transferable-detail", kwargs={"pk": faker.uuid4()})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"].code == "not_found"

    @pytest.mark.parametrize("is_multipart", [True, False])
    def test_destroy_incoming_transferable_success(
        self, is_multipart: bool, api_client: test.APIClient
    ) -> None:
        with s3_stored_incoming_transferable() as obj:
            if is_multipart:
                for i in range(1, 3):
                    factory.S3UploadPartFactory(
                        part_number=i, incoming_transferable=obj
                    )

            api_client.force_login(user=obj.user_profile.user)
            url = reverse("transferable-detail", kwargs={"pk": obj.id})
            response = api_client.delete(url)

            assert response.status_code == status.HTTP_204_NO_CONTENT

            with pytest.raises(S3Error) as error:
                minio.client.get_object(
                    bucket_name=obj.s3_bucket_name, object_name=obj.s3_object_name
                )

            assert error.value.code == "NoSuchKey"

            obj.refresh_from_db()
            assert obj.state == models.IncomingTransferableState.REMOVED

    @pytest.mark.parametrize(
        "incoming_transferable_state",
        [
            models.IncomingTransferableState.ONGOING,
            models.IncomingTransferableState.EXPIRED,
            models.IncomingTransferableState.ERROR,
            models.IncomingTransferableState.REMOVED,
        ],
    )
    def test_destroy_incoming_transferable_ongoing_error(
        self,
        incoming_transferable_state: models.IncomingTransferableState,
        api_client: test.APIClient,
    ) -> None:
        obj = factory.IncomingTransferableFactory(state=incoming_transferable_state)
        api_client.force_login(user=obj.user_profile.user)
        url = reverse("transferable-detail", kwargs={"pk": obj.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data["detail"].code == "UnsuccessfulTransferableError"

    def test_download_incoming_transferable_error_not_authenticated(
        self, api_client: test.APIClient
    ) -> None:
        obj = factory.IncomingTransferableFactory()
        url = reverse("transferable-download", kwargs={"pk": obj.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.headers["Content-Type"] == "application/json"
        assert response.data["detail"].code == "not_authenticated"

    def test_download_incoming_transferable_error_not_owner(
        self, api_client: test.APIClient
    ) -> None:
        obj = factory.IncomingTransferableFactory()
        another_user = factory.UserProfileFactory().user

        api_client.force_login(user=another_user)
        url = reverse("transferable-download", kwargs={"pk": obj.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.headers["Content-Type"] == "application/json"
        assert response.data["detail"].code == "not_found"

    def test_download_incoming_transferable_error_not_associated(
        self, api_client: test.APIClient
    ) -> None:
        obj = factory.IncomingTransferableFactory()
        another_user = factory.UserFactory()

        api_client.force_login(user=another_user)
        url = reverse("transferable-download", kwargs={"pk": obj.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.headers["Content-Type"] == "application/json"
        assert response.data["detail"].code == "permission_denied"

    def test_download_incoming_transferable_error_no_transferable(
        self,
        api_client: test.APIClient,
        faker: Faker,
    ):
        user = factory.UserProfileFactory().user

        api_client.force_login(user=user)
        url = reverse("transferable-download", kwargs={"pk": faker.uuid4()})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.headers["Content-Type"] == "application/json"
        assert response.data["detail"].code == "not_found"

    @pytest.mark.parametrize(
        (
            "incoming_transferable_state",
            "expected_http_status_code",
            "expected_error_detail_code",
        ),
        [
            (
                models.IncomingTransferableState.ERROR,
                status.HTTP_403_FORBIDDEN,
                "TransferableErroredError",
            ),
            (
                models.IncomingTransferableState.ONGOING,
                status.HTTP_409_CONFLICT,
                "TransferableOngoingError",
            ),
            (
                models.IncomingTransferableState.EXPIRED,
                status.HTTP_410_GONE,
                "TransferableExpiredError",
            ),
            (
                models.IncomingTransferableState.REVOKED,
                status.HTTP_410_GONE,
                "TransferableRevokedError",
            ),
            (
                models.IncomingTransferableState.REMOVED,
                status.HTTP_410_GONE,
                "TransferableRemovedError",
            ),
        ],
    )
    def test_download_incoming_transferable_error_due_to_transferable_state(
        self,
        incoming_transferable_state: models.IncomingTransferableState,
        expected_http_status_code: int,
        expected_error_detail_code: str,
        api_client: test.APIClient,
    ) -> None:
        obj = factory.IncomingTransferableFactory(state=incoming_transferable_state)

        api_client.force_login(user=obj.user_profile.user)

        url = reverse("transferable-download", kwargs={"pk": obj.id})
        response = api_client.get(url)

        assert response.status_code == expected_http_status_code
        assert response.data["detail"].code == expected_error_detail_code

    def test_download_incoming_transferable_s3_object_not_found(
        self,
        api_client: test.APIClient,
    ) -> None:
        with factory.s3_stored_incoming_transferable(
            data=b"",
            state=models.IncomingTransferableState.SUCCESS,
        ) as transferable:
            minio.client.remove_object(
                bucket_name=transferable.s3_bucket_name,
                object_name=transferable.s3_object_name,
            )

            api_client.force_login(user=transferable.user_profile.user)
            url = reverse("transferable-download", kwargs={"pk": transferable.id})

            response = api_client.get(url)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

            transferable.refresh_from_db()
            assert transferable.state == models.IncomingTransferableState.ERROR

    @pytest.mark.parametrize(
        "http_headers",
        [
            {},
            {"HTTP_ACCEPT": "application/octet-stream"},
            {"HTTP_ACCEPT": "application/*"},
            # ignoring the Accept header is valid in this case, see:
            # https://datatracker.ietf.org/doc/html/rfc7231#section-5.3.2
            {"HTTP_ACCEPT": "application/json"},
        ],
    )
    @pytest.mark.parametrize(
        ("data", "filename"),
        [
            (b"", "file.ext"),
            (b"Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "file.ext"),
            (b"hello", ""),
        ],
    )
    def test_download_incoming_transferable_success(
        self,
        data: bytes,
        filename: str,
        http_headers: Dict[str, str],
        api_client: test.APIClient,
        faker: Faker,
    ) -> None:
        data = faker.binary(1024)

        with factory.s3_stored_incoming_transferable(
            data=data,
            size=len(data),
            name=filename,
            user_provided_meta={"Metadata-Foo": "Bar", "Metadata-Baz": "Xyz"},
            state=models.IncomingTransferableState.SUCCESS,
        ) as obj:
            api_client.force_login(user=obj.user_profile.user)
            url = reverse("transferable-download", kwargs={"pk": obj.id})
            response = api_client.get(url, **http_headers)

            if not filename:
                filename = str(obj.id)

            assert response.status_code == status.HTTP_200_OK
            assert (
                response.headers.items()
                >= {
                    "Content-Length": f"{len(data)}",
                    "Content-Type": "application/octet-stream",
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Digest": "SHA=" + base64.b64encode(obj.sha1).decode("utf-8"),
                }.items()
            )
            assert response.getvalue() == data

    @pytest.mark.parametrize(
        ("nb_files", "expected_message"),
        [
            (0, "Aucun fichier à supprimer"),
            (1, "1 fichier a été supprimé"),
            (2, "2 fichiers ont été supprimés"),
        ],
    )
    def test_delete_all_incoming_transferables_success(
        self,
        api_client: test.APIClient,
        nb_files: int,
        expected_message: str,
    ) -> None:
        user_profile = factory.UserProfileFactory()
        for _ in range(nb_files):
            obj = factory.IncomingTransferableFactory(
                user_profile=user_profile,
                state=models.IncomingTransferableState.SUCCESS,
            )
            data = b"Lorem ipsum dolor sit amet"

            minio.client.make_bucket(bucket_name=obj.s3_bucket_name)
            minio.client.put_object(
                bucket_name=obj.s3_bucket_name,
                object_name=obj.s3_object_name,
                data=io.BytesIO(data),
                length=len(data),
            )

        api_client.force_login(user=user_profile.user)
        url = reverse("transferable-destroy-all")
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_message
        # Use again to see if the message changes
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == "Aucun fichier à supprimer"
