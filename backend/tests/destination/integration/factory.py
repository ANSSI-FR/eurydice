import contextlib
import datetime
import hashlib
from typing import ContextManager

import django.contrib.auth
import django.utils.timezone
import factory
from django.conf import settings

from eurydice.destination.core import models as destination_models
from eurydice.destination.storage import fs
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

    _random_bytes = factory.Faker("binary", length=20)
    _finished_at = factory.Faker("future_datetime", tzinfo=django.utils.timezone.get_current_timezone())

    @factory.lazy_attribute
    def bytes_received(self) -> int:
        if self.state == destination_models.IncomingTransferableState.SUCCESS:
            return self.size

        return factory.Faker("pyint", min_value=0, max_value=self.size - 1).evaluate(None, None, {"locale": None})

    @factory.lazy_attribute
    def rehash_intermediary(self) -> bytes:
        return rehash.sha1_to_bytes(hashlib.sha1(self._random_bytes))  # nosec: B303

    user_profile = factory.SubFactory(UserProfileFactory)

    user_provided_meta = {"Metadata-Foo": "Bar"}

    state = factory.Faker("random_element", elements=destination_models.IncomingTransferableState)

    @factory.lazy_attribute
    def finished_at(self) -> datetime.datetime | None:
        if self.state == destination_models.IncomingTransferableState.ONGOING:
            return None

        return self._finished_at

    class Meta:
        model = destination_models.IncomingTransferable
        exclude = (
            "_random_bytes",
            "_finished_at",
        )


class FileUploadPartFactory(factory.django.DjangoModelFactory):
    part_number = factory.Sequence(lambda n: n + 1)
    incoming_transferable = factory.SubFactory(IncomingTransferableFactory)

    class Meta:
        model = destination_models.FileUploadPart


@contextlib.contextmanager
def fs_stored_incoming_transferable(data: bytes, **kwargs) -> ContextManager[destination_models.IncomingTransferable]:
    obj = IncomingTransferableFactory(**kwargs)

    try:
        fs.write_bytes(obj, data)

        yield obj
    finally:
        fs.delete(obj)


__all__ = (
    "UserFactory",
    "UserProfileFactory",
    "IncomingTransferableFactory",
    "FileUploadPartFactory",
    "fs_stored_incoming_transferable",
)
