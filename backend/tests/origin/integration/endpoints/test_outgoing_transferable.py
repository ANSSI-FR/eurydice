import io
from typing import Union
from unittest import mock

import pytest
from django import conf
from faker import Faker

from eurydice.origin.api.views import outgoing_transferable
from eurydice.origin.core import models
from tests.origin.integration import factory


@pytest.mark.django_db()
@pytest.mark.parametrize("nb_ranges", [1, 2])
@mock.patch(
    "eurydice.origin.api.views.outgoing_transferable._finalize_transferable",
    side_effect=RuntimeError("Something terrible happened!"),
)
def test__perform_create_transferable_ranges_error_rollback(
    mocked_finalize_transferable: mock.Mock,
    nb_ranges: int,
    faker: Faker,
    settings: conf.Settings,
):
    settings.TRANSFERABLE_RANGE_SIZE = 1
    data = faker.binary(length=settings.TRANSFERABLE_RANGE_SIZE * nb_ranges)
    transferable = factory.OutgoingTransferableFactory(
        sha1=None, bytes_received=0, size=len(data), submission_succeeded_at=None
    )

    with pytest.raises(RuntimeError, match="Something terrible happened!"):
        outgoing_transferable._perform_create_transferable_ranges(
            transferable=transferable, stream=io.BytesIO(data)
        )

    transferable.refresh_from_db()
    assert (
        transferable.bytes_received
        == (nb_ranges - 1) * settings.TRANSFERABLE_RANGE_SIZE
    )
    assert transferable.sha1 is None
    assert models.TransferableRange.objects.count() == nb_ranges - 1

    mocked_finalize_transferable.assert_called_once()


@pytest.mark.django_db()
@pytest.mark.parametrize("provide_size", [False, True])
@pytest.mark.parametrize("data_size", ["TRANSFERABLE_RANGE_SIZE", 0])
def test__perform_create_transferable_ranges(
    data_size: Union[str, int],
    provide_size: bool,
    faker: Faker,
    settings: conf.Settings,
):
    settings.TRANSFERABLE_RANGE_SIZE = 256

    if data_size == "TRANSFERABLE_RANGE_SIZE":
        data_size = settings.TRANSFERABLE_RANGE_SIZE

    data = faker.binary(data_size)
    transferable = factory.OutgoingTransferableFactory(
        sha1=None,
        bytes_received=0,
        size=len(data) if provide_size else None,
        submission_succeeded_at=None,
    )

    outgoing_transferable._perform_create_transferable_ranges(
        transferable=transferable, stream=io.BytesIO(data)
    )

    transferable.refresh_from_db()
    assert transferable.bytes_received == data_size
    assert transferable.size == len(data)
    assert models.TransferableRange.objects.count() == 1
