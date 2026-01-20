import hashlib
from unittest import mock

import pytest
from django.conf import Settings

import tests.destination.integration.factory as factory
from eurydice.destination.core.models.incoming_transferable import (
    IncomingTransferableState,
)
from eurydice.destination.receiver import transferable_ingestion_fs
from eurydice.destination.utils import rehash


@pytest.mark.django_db()
def test__abort_ingestion(
    settings: Settings,
):
    transferable = factory.IncomingTransferableFactory(state=IncomingTransferableState.ONGOING)

    transferable_ingestion_fs.abort_ingestion(transferable)

    assert transferable.state == IncomingTransferableState.ERROR


@pytest.mark.django_db()
def test__update_incoming_transferable(
    settings: Settings,
):
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

    transferable_ingestion_fs.ingest(
        transferable,
        transferable_ingestion_fs.PendingIngestionData(new_data, sha1, False),
    )

    assert transferable.state == IncomingTransferableState.ONGOING
    assert transferable.finished_at is None
    assert transferable.bytes_received == len(data + new_data)
    assert transferable.rehash_intermediary == sha1_intermediary
    assert transferable_ingestion_fs._storage_exists(transferable)

    new_data2 = b"!"
    sha1.update(new_data2)
    sha1_intermediary = rehash.sha1_to_bytes(sha1)

    transferable_ingestion_fs.ingest(
        transferable,
        transferable_ingestion_fs.PendingIngestionData(new_data2, sha1, True),
    )

    assert transferable.sha1 == sha1.digest()
    assert transferable.state == IncomingTransferableState.SUCCESS
    assert transferable.finished_at is not None
    assert transferable.bytes_received == len(data + new_data + new_data2)
    assert transferable.size == len(data + new_data + new_data2)
    assert transferable.rehash_intermediary == sha1_intermediary
    assert transferable_ingestion_fs._storage_exists(transferable)
