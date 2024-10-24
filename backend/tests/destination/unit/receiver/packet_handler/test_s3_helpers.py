import pytest
from faker import Faker

from eurydice.common import minio
from eurydice.destination.receiver.packet_handler import s3_helpers
from tests.destination.integration import factory


@pytest.fixture()
def s3_bucket(faker: Faker):
    bucket_name = faker.slug()
    minio.client.make_bucket(bucket_name=bucket_name)
    yield bucket_name
    minio.client.remove_bucket(bucket_name=bucket_name)


@pytest.mark.django_db()
def test__initiate_multipart_upload(s3_bucket: str):
    incoming_transferable = factory.IncomingTransferableFactory(
        s3_bucket_name=s3_bucket
    )
    upload_id = s3_helpers.initiate_multipart_upload(incoming_transferable)
    list_parts_result = minio.client._list_parts(
        bucket_name=s3_bucket,
        object_name=str(incoming_transferable.id),
        upload_id=upload_id,
    )
    assert list_parts_result.object_name == str(incoming_transferable.id)
    assert list_parts_result.bucket_name == s3_bucket
