import contextlib
import datetime
import io
from typing import Any
from typing import ContextManager
from typing import List
from typing import Optional

import django.contrib.auth.models
import django.utils.timezone
import factory
import faker.utils.decorators
from django.conf import settings
from django.db import models
from django.db.models import signals

from eurydice.common import enums
from eurydice.common import minio
from eurydice.common.models import fields
from eurydice.origin.core import enums as origin_enums
from eurydice.origin.core import models as origin_models
from eurydice.origin.core import signals as eurydice_signals
from tests import utils

POSITIVE_SMALL_INTEGER_FIELD_MAX_VALUE: int = 32767


class UserFactoryWithSignal(factory.django.DjangoModelFactory):
    """UserFactory with a signal for creating an associated UserProfile"""

    username = factory.Sequence(lambda n: f"{utils.fake.user_name()}_{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.Faker("password")
    is_superuser = False

    class Meta:
        model = django.contrib.auth.get_user_model()
        django_get_or_create = ("username",)


class UserFactory(UserFactoryWithSignal):
    """UserFactory without a signal for creating an associated UserProfile"""

    @classmethod
    def _create(cls, *args, **kwargs) -> django.contrib.auth.get_user_model():
        """Overridden _create method to disable the create_user_profile signal"""
        signals.post_save.disconnect(
            receiver=eurydice_signals.create_user_profile, sender=origin_models.User
        )
        try:
            instance = super()._create(*args, **kwargs)
        finally:
            signals.post_save.connect(
                eurydice_signals.create_user_profile, sender=origin_models.User
            )
        return instance


class UserProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    priority = factory.Faker(
        "pyint", min_value=0, max_value=POSITIVE_SMALL_INTEGER_FIELD_MAX_VALUE
    )

    class Meta:
        model = origin_models.UserProfile


class OutgoingTransferableFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("file_name")
    size = factory.Faker("pyint", min_value=0, max_value=settings.TRANSFERABLE_MAX_SIZE)
    user_profile = factory.SubFactory(UserProfileFactory)
    user_provided_meta = {"Metadata-Foo": "Bar"}

    _sha1 = factory.Faker("sha1", raw_output=True)
    _submission_succeeded = factory.Faker("pybool")
    _submission_succeeded_at = factory.Faker(
        "date_time_this_decade", tzinfo=django.utils.timezone.get_current_timezone()
    )

    @factory.lazy_attribute
    def sha1(self) -> Optional[bytes]:
        if self.submission_succeeded_at:
            return self._sha1

        return None

    @factory.lazy_attribute
    def bytes_received(self) -> int:
        if self.submission_succeeded_at:
            return self.size

        return factory.Faker("pyint", min_value=0, max_value=self.size).evaluate(
            None, None, {"locale": None}
        )

    @factory.lazy_attribute
    def submission_succeeded_at(self) -> Optional[datetime.datetime]:
        if self._submission_succeeded:
            return self._submission_succeeded_at

        return None

    @factory.post_generation
    def make_transferable_ranges_for_state(
        self,
        create: bool,
        state: origin_enums.TransferableRangeTransferState,
        **kwargs,
    ):
        if not create:
            return

        if state == enums.OutgoingTransferableState.ONGOING:
            TransferableRangeFactory(
                transfer_state=origin_enums.TransferableRangeTransferState.TRANSFERRED,
                outgoing_transferable=self,
                **kwargs,
            )
            TransferableRangeFactory(
                transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
                outgoing_transferable=self,
                **kwargs,
            )
        elif state == enums.OutgoingTransferableState.CANCELED:
            TransferableRevocationFactory(
                reason=enums.TransferableRevocationReason.USER_CANCELED,
                outgoing_transferable=self,
                **kwargs,
            )
        elif state == enums.OutgoingTransferableState.ERROR:
            TransferableRevocationFactory(
                reason=enums.TransferableRevocationReason.UNEXPECTED_EXCEPTION,
                outgoing_transferable=self,
                **kwargs,
            )
        elif state == enums.OutgoingTransferableState.SUCCESS:
            TransferableRangeFactory(
                transfer_state=origin_enums.TransferableRangeTransferState.TRANSFERRED,
                outgoing_transferable=self,
                **kwargs,
            )

    class Meta:
        model = origin_models.OutgoingTransferable
        exclude = ("_sha1", "_submission_succeeded", "_submission_succeeded_at")


class TransferableRangeFactory(factory.django.DjangoModelFactory):
    byte_offset = factory.Faker(
        "pyint", min_value=0, max_value=settings.TRANSFERABLE_MAX_SIZE
    )
    size = factory.Faker(
        "pyint", min_value=0, max_value=settings.TRANSFERABLE_RANGE_SIZE
    )
    transfer_state = factory.Faker(
        "random_element", elements=origin_enums.TransferableRangeTransferState
    )
    finished_at = factory.Faker(
        "future_datetime", tzinfo=django.utils.timezone.get_current_timezone()
    )

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

    @factory.lazy_attribute
    @faker.utils.decorators.slugify
    def s3_bucket_name(self) -> str:
        return self._s3_bucket_name

    @factory.lazy_attribute
    @faker.utils.decorators.slugify
    def s3_object_name(self) -> str:
        return self._s3_object_name

    @classmethod
    def _create(cls, model_class: models.Model, *args, **kwargs) -> Any:
        if (
            kwargs["transfer_state"]
            == origin_enums.TransferableRangeTransferState.PENDING
        ):
            kwargs["finished_at"] = None
            return super()._create(model_class, *args, **kwargs)

        target_transfer_state = kwargs["transfer_state"]
        kwargs["transfer_state"] = origin_enums.TransferableRangeTransferState.PENDING
        target_finished_at = kwargs["finished_at"]
        kwargs["finished_at"] = None

        obj = super()._create(model_class, *args, **kwargs)
        obj.transfer_state = target_transfer_state
        obj.finished_at = target_finished_at
        obj.save()

        return obj

    outgoing_transferable = factory.SubFactory(OutgoingTransferableFactory)

    class Meta:
        model = origin_models.TransferableRange
        exclude = (
            "_s3_bucket_name",
            "_s3_object_name",
        )


class TransferableRevocationFactory(factory.django.DjangoModelFactory):
    outgoing_transferable = factory.SubFactory(OutgoingTransferableFactory)

    reason = factory.Faker(
        "random_element", elements=enums.TransferableRevocationReason
    )

    transfer_state = factory.Faker(
        "random_element", elements=origin_enums.TransferableRevocationTransferState
    )

    class Meta:
        model = origin_models.TransferableRevocation


@contextlib.contextmanager
def s3_stored_transferable_range(
    data: bytes, **kwargs
) -> ContextManager[origin_models.TransferableRange]:
    obj = TransferableRangeFactory(**kwargs)

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


@contextlib.contextmanager
def s3_stored_transferable_ranges(
    data: bytes, count: int, s3_bucket_name: str, **kwargs
) -> ContextManager[List[origin_models.TransferableRange]]:
    kwargs["s3_bucket_name"] = s3_bucket_name

    transferable_ranges = [TransferableRangeFactory(**kwargs) for _ in range(count)]

    try:
        minio.client.make_bucket(bucket_name=s3_bucket_name)
        for transferable_range in transferable_ranges:
            minio.client.put_object(
                bucket_name=s3_bucket_name,
                object_name=transferable_range.s3_object_name,
                data=io.BytesIO(data),
                length=len(data),
            )

        yield transferable_ranges
    finally:
        for transferable_range in transferable_ranges:
            minio.client.remove_object(
                bucket_name=s3_bucket_name,
                object_name=transferable_range.s3_object_name,
            )
        minio.client.remove_bucket(bucket_name=s3_bucket_name)


__all__ = (
    "UserFactory",
    "UserFactoryWithSignal",
    "OutgoingTransferableFactory",
    "TransferableRangeFactory",
    "TransferableRevocationFactory",
    "s3_stored_transferable_range",
    "s3_stored_transferable_ranges",
)
