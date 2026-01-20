import contextlib
import datetime
from typing import Any, ContextManager

import django.utils.timezone
import factory
from django.conf import settings
from django.db import models
from django.db.models import signals

from eurydice.common import enums
from eurydice.origin.api.views.outgoing_transferable import get_transferable_file_path
from eurydice.origin.core import enums as origin_enums
from eurydice.origin.core import models as origin_models
from eurydice.origin.core import signals as eurydice_signals
from eurydice.origin.storage import fs
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
        signals.post_save.disconnect(receiver=eurydice_signals.create_user_profile, sender=origin_models.User)
        try:
            instance = super()._create(*args, **kwargs)
        finally:
            signals.post_save.connect(eurydice_signals.create_user_profile, sender=origin_models.User)
        return instance


class UserProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    priority = factory.Faker("pyint", min_value=0, max_value=POSITIVE_SMALL_INTEGER_FIELD_MAX_VALUE)

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
    def sha1(self) -> bytes | None:
        if self.submission_succeeded_at:
            return self._sha1

        return None

    @factory.lazy_attribute
    def bytes_received(self) -> int:
        if self.submission_succeeded_at:
            return self.size

        return factory.Faker("pyint", min_value=0, max_value=self.size).evaluate(None, None, {"locale": None})

    @factory.lazy_attribute
    def submission_succeeded_at(self) -> datetime.datetime | None:
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
    byte_offset = factory.Faker("pyint", min_value=0, max_value=settings.TRANSFERABLE_MAX_SIZE)
    size = factory.Faker("pyint", min_value=0, max_value=settings.TRANSFERABLE_RANGE_SIZE)
    transfer_state = factory.Faker("random_element", elements=origin_enums.TransferableRangeTransferState)
    finished_at = factory.Faker("future_datetime", tzinfo=django.utils.timezone.get_current_timezone())

    @classmethod
    def _create(cls, model_class: models.Model, *args, **kwargs) -> Any:
        if kwargs["transfer_state"] == origin_enums.TransferableRangeTransferState.PENDING:
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


class TransferableRevocationFactory(factory.django.DjangoModelFactory):
    outgoing_transferable = factory.SubFactory(OutgoingTransferableFactory)

    reason = factory.Faker("random_element", elements=enums.TransferableRevocationReason)

    transfer_state = factory.Faker("random_element", elements=origin_enums.TransferableRevocationTransferState)

    class Meta:
        model = origin_models.TransferableRevocation


@contextlib.contextmanager
def fs_stored_interrupted_upload_transferable(
    data: bytes, **kwargs
) -> ContextManager[origin_models.OutgoingTransferable]:
    obj = OutgoingTransferableFactory(**kwargs)
    target_file_path = get_transferable_file_path(str(obj.id))
    target_file_path.write_bytes(data)

    yield obj


@contextlib.contextmanager
def stored_transferable_range(data: bytes, **kwargs) -> ContextManager[origin_models.TransferableRange]:
    obj = TransferableRangeFactory(**kwargs)

    try:
        fs.write_bytes(obj, data)
        yield obj
    finally:
        fs.delete(obj)


@contextlib.contextmanager
def stored_transferable_ranges(
    data: bytes, count: int, **kwargs
) -> ContextManager[list[origin_models.TransferableRange]]:
    transferable_ranges = [TransferableRangeFactory(**kwargs) for _ in range(count)]
    try:
        for transferable_range in transferable_ranges:
            fs.write_bytes(transferable_range, data)
        yield transferable_ranges
    finally:
        for transferable_range in transferable_ranges:
            fs.delete(transferable_range)


__all__ = (
    "UserFactory",
    "UserFactoryWithSignal",
    "OutgoingTransferableFactory",
    "TransferableRangeFactory",
    "TransferableRevocationFactory",
    "stored_transferable_range",
    "stored_transferable_ranges",
    "fs_stored_interrupted_upload_transferable",
)
