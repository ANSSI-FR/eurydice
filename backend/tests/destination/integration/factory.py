import contextlib
import datetime
import hashlib
import io
from typing import ContextManager
from typing import Optional

import django.contrib.auth
import django.utils.timezone
import factory
import faker.utils.decorators
from django.conf import settings

from eurydice.common import minio
from eurydice.common.models import fields
from eurydice.destination.core import models as destination_models
from eurydice.destination.core.models import s3_upload_part
from eurydice.destination.utils import rehash
from tests import utils


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"{utils.fake.user_name()}_{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.Faker("password")
    is_superuser = False

    class Meta:
        model = django.contrib.auth.get_user_model()
        django_get_or_create = ("username",)


class UserProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    associated_user_profile_id = factory.Faker("uuid4")

    class Meta:
        model = destination_models.UserProfile


class IncomingTransferableFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("file_name")
    sha1 = factory.Faker("sha1", raw_output=True)
    size = factory.Faker("pyint", min_value=0, max_value=settings.TRANSFERABLE_MAX_SIZE)

    _s3_bucket_name = factory.Faker(
        "pystr",
        min_chars=fields.S3BucketNameField.MIN_LENGTH,
        max_chars=fields.S3BucketNameField.MAX_LENGTH,
    )
    _s3_object_name = factory.Faker(
        "pystr",
        min_chars=fields.S3ObjectNameField.MIN_LENGTH,
        max_chars=fields.S3ObjectNameField.MAX_LENGTH,
    )
    _s3_upload_id = factory.Faker(
        "pystr",
        min_chars=destination_models.incoming_transferable.S3_UPLOAD_ID_LENGTH,
        max_chars=destination_models.incoming_transferable.S3_UPLOAD_ID_LENGTH,
    )
    _random_bytes = factory.Faker("binary", length=20)
    _finished_at = factory.Faker(
        "future_datetime", tzinfo=django.utils.timezone.get_current_timezone()
    )

    @factory.lazy_attribute
    def bytes_received(self) -> int:
        if self.state == destination_models.IncomingTransferableState.SUCCESS:
            return self.size

        return factory.Faker("pyint", min_value=0, max_value=self.size - 1).evaluate(
            None, None, {"locale": None}
        )

    @factory.lazy_attribute
    @faker.utils.decorators.slugify
    def s3_bucket_name(self) -> str:
        return self._s3_bucket_name

    @factory.lazy_attribute
    @faker.utils.decorators.slugify
    def s3_object_name(self) -> str:
        return self._s3_object_name

    @factory.lazy_attribute
    def s3_upload_id(self) -> str:
        return self._s3_upload_id

    @factory.lazy_attribute
    def rehash_intermediary(self) -> bytes:
        return rehash.sha1_to_bytes(hashlib.sha1(self._random_bytes))  # nosec: B303

    user_profile = factory.SubFactory(UserProfileFactory)

    user_provided_meta = {"Metadata-Foo": "Bar"}

    state = factory.Faker(
        "random_element", elements=destination_models.IncomingTransferableState
    )

    @factory.lazy_attribute
    def finished_at(self) -> Optional[datetime.datetime]:
        if self.state == destination_models.IncomingTransferableState.ONGOING:
            return None

        return self._finished_at

    class Meta:
        model = destination_models.IncomingTransferable
        exclude = (
            "_s3_bucket_name",
            "_s3_object_name",
            "_s3_upload_id",
            "_random_bytes",
            "_finished_at",
        )


class S3UploadPartFactory(factory.django.DjangoModelFactory):
    etag = factory.Faker("binary", length=s3_upload_part._S3_PART_ETAG_LENGTH)
    part_number = factory.Sequence(lambda n: n + 1)
    incoming_transferable = factory.SubFactory(IncomingTransferableFactory)

    class Meta:
        model = destination_models.S3UploadPart


@contextlib.contextmanager
def s3_stored_incoming_transferable(
    data: bytes, **kwargs
) -> ContextManager[destination_models.IncomingTransferable]:
    obj = IncomingTransferableFactory(**kwargs)

    try:
        minio.client.make_bucket(bucket_name=obj.s3_bucket_name)
        minio.client.put_object(
            bucket_name=obj.s3_bucket_name,
            object_name=obj.s3_object_name,
            data=io.BytesIO(data),
            length=len(
                data,
            ),
        )

        yield obj
    finally:
        minio.client.remove_object(
            bucket_name=obj.s3_bucket_name, object_name=obj.s3_object_name
        )

        minio.client.remove_bucket(bucket_name=obj.s3_bucket_name)


__all__ = (
    "UserFactory",
    "UserProfileFactory",
    "IncomingTransferableFactory",
    "S3UploadPartFactory",
    "s3_stored_incoming_transferable",
)
