import datetime
from unittest import mock

import pytest
from django import conf
from django.utils import timezone

from eurydice.common.utils import signals
from eurydice.destination.cleaning.file_remover.file_remover import (
    DestinationFileRemover,
)
from eurydice.destination.core import models
from eurydice.destination.storage import fs
from tests.destination.integration import factory


@pytest.mark.django_db()
def test_select_transferables_to_remove_success_no_transferable():
    file_remover = DestinationFileRemover()
    with pytest.raises(StopIteration):
        next(file_remover._select_transferables_to_remove())


@pytest.mark.django_db()
def test_select_transferables_to_remove_success_single_transferable(
    settings: conf.Settings,
):
    settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    finished_at = (
        timezone.now()
        - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER
        - datetime.timedelta(seconds=1)
    )
    transferable = factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.SUCCESS,
        created_at=finished_at,
        finished_at=finished_at,
    )

    factory.IncomingTransferableFactory(state=models.IncomingTransferableState.ONGOING)

    file_remover = DestinationFileRemover()
    assert next(file_remover._select_transferables_to_remove()).id == transferable.id


@pytest.mark.django_db()
def test_select_transferables_to_remove_success_multiple_transferables(
    settings: conf.Settings,
):
    settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    nb_success_transferables = 3
    success_transferable_id = set()

    for _ in range(nb_success_transferables):
        finished_at = (
            timezone.now()
            - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER
            - datetime.timedelta(seconds=1)
        )
        transferable = factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.SUCCESS,
            created_at=finished_at,
            finished_at=finished_at,
        )
        success_transferable_id.add(transferable.id)

    # ongoing transferable should not be removed
    ongoing_transferable = factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.ONGOING
    )
    created_at = (
        timezone.now()
        - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER
        + datetime.timedelta(seconds=1)
    )
    factory.FileUploadPartFactory(
        part_number=1, incoming_transferable=ongoing_transferable, created_at=created_at
    )

    file_remover = DestinationFileRemover()
    retrieved = {t.id for t in file_remover._select_transferables_to_remove()}
    assert retrieved == success_transferable_id


@pytest.mark.django_db()
def test_select_transferables_to_remove_success_and_ongoing_transferables(
    settings: conf.Settings,
):
    settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    nb_ongoing_transferables_to_keep = 2
    nb_ongoing_transferables_to_remove = 4
    nb_success_transferables_to_keep = 3
    nb_success_transferables_to_remove = 5
    expected_selected_transferable_id = set()

    unexpired_date = (
        timezone.now()
        - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER
        + datetime.timedelta(seconds=1)
    )
    expired_date = (
        timezone.now()
        - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER
        - datetime.timedelta(seconds=1)
    )

    for _ in range(nb_ongoing_transferables_to_keep):
        transferable = factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.ONGOING,
            created_at=unexpired_date,
        )
        filepart = factory.FileUploadPartFactory(
            part_number=1,
            incoming_transferable=transferable,
        )
        filepart.created_at = unexpired_date
        filepart.save()

    for _ in range(nb_ongoing_transferables_to_remove):
        transferable = factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.ONGOING,
            created_at=expired_date,
        )
        part = factory.FileUploadPartFactory(
            part_number=1,
            incoming_transferable=transferable,
        )
        part.created_at = expired_date
        part.save()
        expected_selected_transferable_id.add(transferable.id)

    for _ in range(nb_success_transferables_to_keep):
        factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.SUCCESS,
            created_at=unexpired_date,
            finished_at=unexpired_date,
        )

    for _ in range(nb_success_transferables_to_remove):
        transferable = factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.SUCCESS,
            created_at=expired_date,
            finished_at=expired_date,
        )
        expected_selected_transferable_id.add(transferable.id)

    file_remover = DestinationFileRemover()
    retrieved = {t.id for t in file_remover._select_transferables_to_remove()}
    assert retrieved == expected_selected_transferable_id


@pytest.mark.django_db()
def test_remove_transferable_success(
    caplog: pytest.LogCaptureFixture,
    success_incoming_transferable: models.IncomingTransferable,
    settings: conf.Settings,
):
    file_remover = DestinationFileRemover()
    file_remover._remove_transferable(success_incoming_transferable)

    success_incoming_transferable.refresh_from_db()
    assert (
        success_incoming_transferable.state == models.IncomingTransferableState.EXPIRED
    )

    with pytest.raises(FileNotFoundError):
        fs.read_bytes(success_incoming_transferable)

    assert caplog.messages == [
        f"The IncomingTransferable {success_incoming_transferable.id} has been marked "
        f"as {models.IncomingTransferableState.EXPIRED.value}, "
        f"and its data removed from the storage."
    ]


@pytest.mark.django_db()
@mock.patch(
    "eurydice.destination.storage.fs.delete",
    side_effect=RuntimeError("Oh no!"),
)
def test_remove_transferable_error_ensure_atomicity(mocked_remove_object: mock.Mock):
    transferable = factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.SUCCESS
    )

    file_remover = DestinationFileRemover()
    with pytest.raises(RuntimeError, match="Oh no!"):
        file_remover._remove_transferable(transferable)

    transferable.refresh_from_db()
    assert transferable.state == models.IncomingTransferableState.SUCCESS
    mocked_remove_object.assert_called_once()


@pytest.mark.django_db()
@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch("time.sleep")
def test_loop_success_no_transferable(
    time_sleep: mock.Mock,
    boolean_cond: mock.Mock,
):
    boolean_cond.side_effect = [True, True, False]
    file_remover = DestinationFileRemover()
    file_remover._loop()
    assert time_sleep.call_count == 2


@pytest.mark.django_db()
@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch("time.sleep")
def test_loop_success_remove_transferable(
    time_sleep: mock.Mock,
    boolean_cond: mock.Mock,
    settings: conf.Settings,
    success_incoming_transferable: models.IncomingTransferable,
):
    settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    finished_at = (
        timezone.now()
        - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER
        - datetime.timedelta(seconds=1)
    )

    success_incoming_transferable.created_at = finished_at
    success_incoming_transferable.finished_at = finished_at
    success_incoming_transferable.save(update_fields=["created_at", "finished_at"])

    assert (
        success_incoming_transferable.state == models.IncomingTransferableState.SUCCESS
    )

    boolean_cond.side_effect = [True, True, False]
    file_remover = DestinationFileRemover()
    file_remover._loop()

    success_incoming_transferable.refresh_from_db()
    assert (
        success_incoming_transferable.state == models.IncomingTransferableState.EXPIRED
    )

    with pytest.raises(FileNotFoundError):
        fs.read_bytes(success_incoming_transferable)
