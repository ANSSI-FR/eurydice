import datetime
from unittest import mock

import pytest
from django import conf
from django.utils import timezone
from minio.error import S3Error

from eurydice.common import minio
from eurydice.common.utils import signals
from eurydice.destination.cleaning.s3remover.s3remover import DestinationS3Remover
from eurydice.destination.core import models
from tests.destination.integration import factory


@pytest.mark.django_db()
def test_select_transferables_to_remove_success_no_transferable():
    s3remover = DestinationS3Remover()
    with pytest.raises(StopIteration):
        next(s3remover._select_transferables_to_remove())


@pytest.mark.django_db()
def test_select_transferables_to_remove_success_single_transferable(
    settings: conf.Settings,
):
    settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    finished_at = (
        timezone.now()
        - settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER
        - datetime.timedelta(seconds=1)
    )
    transferable = factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.SUCCESS,
        created_at=finished_at,
        finished_at=finished_at,
    )

    factory.IncomingTransferableFactory(state=models.IncomingTransferableState.ONGOING)

    s3remover = DestinationS3Remover()
    assert next(s3remover._select_transferables_to_remove()).id == transferable.id


@pytest.mark.django_db()
def test_select_transferables_to_remove_success_multiple_transferables(
    settings: conf.Settings,
):
    settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    nb_success_transferables = 3
    success_transferable_id = set()

    for _ in range(nb_success_transferables):
        finished_at = (
            timezone.now()
            - settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER
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
        - settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER
        + datetime.timedelta(seconds=1)
    )
    factory.S3UploadPartFactory(
        part_number=1, incoming_transferable=ongoing_transferable, created_at=created_at
    )

    s3remover = DestinationS3Remover()
    retrieved = {t.id for t in s3remover._select_transferables_to_remove()}
    assert retrieved == success_transferable_id


@pytest.mark.django_db()
def test_select_transferables_to_remove_success_and_ongoing_transferables(
    settings: conf.Settings,
):
    settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    nb_ongoing_transferables_to_keep = 2
    nb_ongoing_transferables_to_remove = 4
    nb_success_transferables_to_keep = 3
    nb_success_transferables_to_remove = 5
    expected_selected_transferable_id = set()

    unexpired_date = (
        timezone.now()
        - settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER
        + datetime.timedelta(seconds=1)
    )
    expired_date = (
        timezone.now()
        - settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER
        - datetime.timedelta(seconds=1)
    )

    for _ in range(nb_ongoing_transferables_to_keep):
        transferable = factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.ONGOING,
            created_at=unexpired_date,
        )
        s3part = factory.S3UploadPartFactory(
            part_number=1,
            incoming_transferable=transferable,
        )
        s3part.created_at = unexpired_date
        s3part.save()

    for _ in range(nb_ongoing_transferables_to_remove):
        transferable = factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.ONGOING,
            created_at=expired_date,
        )
        s3part = factory.S3UploadPartFactory(
            part_number=1,
            incoming_transferable=transferable,
        )
        s3part.created_at = expired_date
        s3part.save()
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

    s3remover = DestinationS3Remover()
    retrieved = {t.id for t in s3remover._select_transferables_to_remove()}
    assert retrieved == expected_selected_transferable_id


@pytest.mark.django_db()
def test_remove_transferable_success(
    caplog: pytest.LogCaptureFixture,
    success_incoming_transferable: models.IncomingTransferable,
):
    s3remover = DestinationS3Remover()
    s3remover._remove_transferable(success_incoming_transferable)

    success_incoming_transferable.refresh_from_db()
    assert (
        success_incoming_transferable.state == models.IncomingTransferableState.EXPIRED
    )

    with pytest.raises(S3Error) as exc:
        minio.client.get_object(
            bucket_name=success_incoming_transferable.s3_bucket_name,
            object_name=success_incoming_transferable.s3_object_name,
        )

    assert exc.value.code == "NoSuchKey"
    assert caplog.messages == [
        f"The IncomingTransferable {success_incoming_transferable.id} has been marked "
        f"as {models.IncomingTransferableState.EXPIRED.value}, "
        f"and its data removed from the storage."
    ]


@pytest.mark.django_db()
@mock.patch(
    "eurydice.common.minio.client.remove_object",
    side_effect=RuntimeError("Oh no!"),
)
def test_remove_transferable_error_ensure_atomicity(mocked_remove_object: mock.Mock):
    transferable = factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.SUCCESS
    )

    s3remover = DestinationS3Remover()
    with pytest.raises(RuntimeError, match="Oh no!"):
        s3remover._remove_transferable(transferable)

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
    s3remover = DestinationS3Remover()
    s3remover._loop()
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
    settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    finished_at = (
        timezone.now()
        - settings.S3REMOVER_EXPIRE_TRANSFERABLES_AFTER
        - datetime.timedelta(seconds=1)
    )

    success_incoming_transferable.created_at = finished_at
    success_incoming_transferable.finished_at = finished_at
    success_incoming_transferable.save(update_fields=["created_at", "finished_at"])

    assert (
        success_incoming_transferable.state == models.IncomingTransferableState.SUCCESS
    )

    boolean_cond.side_effect = [True, True, False]
    s3remover = DestinationS3Remover()
    s3remover._loop()

    success_incoming_transferable.refresh_from_db()
    assert (
        success_incoming_transferable.state == models.IncomingTransferableState.EXPIRED
    )

    with pytest.raises(S3Error) as exc:
        minio.client.get_object(
            bucket_name=success_incoming_transferable.s3_bucket_name,
            object_name=success_incoming_transferable.s3_object_name,
        )

    assert exc.value.code == "NoSuchKey"
