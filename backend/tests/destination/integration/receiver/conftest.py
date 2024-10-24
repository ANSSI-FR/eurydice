import contextlib
from typing import Iterator

import pytest
from faker import Faker
from minio.error import S3Error

from eurydice.common import minio
from eurydice.destination.core import models
from tests.destination.integration import factory as destination_factory


@pytest.fixture()
def ongoing_incoming_transferable(
    faker: Faker,
) -> Iterator[models.IncomingTransferable]:
    obj = destination_factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.ONGOING
    )

    try:
        minio.client.make_bucket(bucket_name=obj.s3_bucket_name)
        obj.s3_upload_id = minio.client._create_multipart_upload(
            bucket_name=obj.s3_bucket_name, object_name=obj.s3_object_name, headers={}
        )

        obj.save()

        minio.client._upload_part(
            bucket_name=obj.s3_bucket_name,
            object_name=obj.s3_object_name,
            data=faker.binary(length=1024),
            headers={},
            upload_id=obj.s3_upload_id,
            part_number=1,
        )

        yield obj
    finally:
        with contextlib.suppress(S3Error):
            minio.client._abort_multipart_upload(
                bucket_name=obj.s3_bucket_name,
                object_name=obj.s3_object_name,
                upload_id=obj.s3_upload_id,
            )

        minio.client.remove_bucket(bucket_name=obj.s3_bucket_name)
