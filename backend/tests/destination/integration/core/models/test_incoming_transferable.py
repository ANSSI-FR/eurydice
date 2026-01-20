import datetime
from typing import Callable

import factory as factory_boy
import freezegun
import pytest
from django import conf
from django.utils import timezone

from eurydice.destination.core import models
from tests.destination.integration import factory


@pytest.mark.parametrize("has_file_upload_parts", [True, False])
@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize(
    ("update_state_func", "target_state"),
    [
        (
            models.IncomingTransferable.mark_as_expired,
            models.IncomingTransferableState.EXPIRED,
        ),
        (
            models.IncomingTransferable.mark_as_removed,
            models.IncomingTransferableState.REMOVED,
        ),
    ],
)
@pytest.mark.django_db()
def test_mark_as(
    update_state_func: Callable[[models.IncomingTransferable, bool], None],
    target_state: models.IncomingTransferableState,
    save: bool,
    has_file_upload_parts: bool,
):
    transferable = factory.IncomingTransferableFactory(state=models.IncomingTransferableState.SUCCESS)
    if has_file_upload_parts:
        factory.FileUploadPartFactory.create_batch(
            3,
            part_number=factory_boy.Iterator([1, 2, 3]),
            incoming_transferable=transferable,
        )

    update_state_func(transferable, save)

    if save:
        transferable.refresh_from_db()

    assert transferable.state == target_state

    assert not models.FileUploadPart.objects.filter(incoming_transferable=transferable).only("id").exists()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "size",
        "bytes_received",
        "expected_progress",
    ),
    [
        (None, 0, None),
        (None, 1024, None),
        (1024, 1024, 100),
        (1024, 0, 0),
        (1024, 512, 50),
        (0, 0, 100),
    ],
)
def test_incoming_transferable_progress(
    size: int | None,
    bytes_received: int,
    expected_progress: int,
):
    if bytes_received == size:
        state = models.IncomingTransferableState.SUCCESS
    else:
        state = models.IncomingTransferableState.ONGOING

    incoming_transferable = factory.IncomingTransferableFactory(size=size, bytes_received=bytes_received, state=state)

    queried_incoming_transferable = models.IncomingTransferable.objects.get(id=incoming_transferable.id)

    assert queried_incoming_transferable.progress == expected_progress


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("finished_at", "state", "file_remover_retention", "expected_expires_at"),
    [
        (
            datetime.datetime(year=1983, month=6, day=21, tzinfo=timezone.get_current_timezone()),
            models.IncomingTransferableState.SUCCESS,
            datetime.timedelta(days=1),
            datetime.datetime(year=1983, month=6, day=22, tzinfo=timezone.get_current_timezone()),
        ),
        (
            None,
            models.IncomingTransferableState.ONGOING,
            datetime.timedelta(days=1),
            None,
        ),
        (
            timezone.now(),
            models.IncomingTransferableState.ERROR,
            datetime.timedelta(days=1),
            None,
        ),
        (
            timezone.now(),
            models.IncomingTransferableState.REVOKED,
            datetime.timedelta(days=1),
            None,
        ),
        (
            timezone.now(),
            models.IncomingTransferableState.EXPIRED,
            datetime.timedelta(days=1),
            None,
        ),
    ],
)
def test_incoming_transferable_expires_at(
    finished_at: datetime.datetime | None,
    state: models.IncomingTransferableState,
    file_remover_retention: datetime.timedelta,
    expected_expires_at: datetime.datetime | None,
    settings: conf.Settings,
):
    settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = file_remover_retention

    with freezegun.freeze_time(datetime.datetime(year=1982, month=6, day=21, tzinfo=timezone.get_current_timezone())):
        incoming_transferable = factory.IncomingTransferableFactory(
            state=state,
            finished_at=finished_at,
        )

    queried_incoming_transferable = models.IncomingTransferable.objects.get(id=incoming_transferable.id)

    assert queried_incoming_transferable.expires_at == expected_expires_at
