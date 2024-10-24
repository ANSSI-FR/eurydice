import hashlib
from unittest import mock

import pytest

import tests.destination.integration.factory as factory
from eurydice.destination.core.models.incoming_transferable import (
    IncomingTransferableState,
)
from eurydice.destination.receiver import transferable_ingestion
from eurydice.destination.utils import rehash


@pytest.mark.django_db()
def test__get_next_part_number_parts_not_exist():
    transferable = factory.IncomingTransferableFactory()

    assert transferable_ingestion._get_next_part_number(transferable) == 1


@pytest.mark.django_db()
def test__get_next_part_number_parts_exist():
    transferable = factory.IncomingTransferableFactory()

    factory.S3UploadPartFactory(part_number=1, incoming_transferable=transferable)

    assert transferable_ingestion._get_next_part_number(transferable) == 2


@pytest.mark.django_db()
def test__update_incoming_transferable():
    data = b"hello "
    sha1 = hashlib.sha1()
    sha1.update(data)
    sha1_intermediary = rehash.sha1_to_bytes(sha1)
    mocked_transferable_range = mock.Mock()
    mocked_transferable_range.data = b"world!"

    transferable = factory.IncomingTransferableFactory(
        bytes_received=len(data),
        size=None,
        rehash_intermediary=sha1_intermediary,
        state=IncomingTransferableState.ONGOING,
    )

    new_data = b"world"
    sha1.update(new_data)
    sha1_intermediary = rehash.sha1_to_bytes(sha1)
    transferable_ingestion._update_incoming_transferable(
        transferable, transferable_ingestion.PendingIngestionData(new_data, sha1, True)
    )

    assert transferable.sha1 == sha1.digest()
    assert transferable.state == IncomingTransferableState.SUCCESS
    assert transferable.finished_at is not None
    assert transferable.bytes_received == len(data + new_data)
    assert transferable.size == len(data + new_data)
    assert transferable.rehash_intermediary == sha1_intermediary
