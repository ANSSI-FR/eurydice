import datetime
from unittest import mock

import freezegun
import pytest
from django import conf
from django.utils import timezone
from faker import Faker

from eurydice.common import enums
from eurydice.common.utils import signals
from eurydice.origin.api.views.outgoing_transferable import get_transferable_file_path
from eurydice.origin.cleaning.file_remover.file_remover import OriginFileRemover
from eurydice.origin.core import enums as origin_enums
from eurydice.origin.core import models
from tests.origin.integration import factory


@pytest.mark.django_db()
def test_select_transferables_to_remove_success_no_transferable():
    file_remover = OriginFileRemover()
    with pytest.raises(StopIteration):
        next(file_remover._select_transferables_to_remove())


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "submission_succeeded",
        "revocation_reason",
        "transferable_ranges_states",
        "expected_state",
        "expected_to_delete",
    ),
    [
        # Should not be removed
        # Test when Transferable has been canceled
        (
            False,
            enums.TransferableRevocationReason.USER_CANCELED,
            [],
            enums.OutgoingTransferableState.CANCELED,
            False,
        ),
        # Should be removed
        # Test when Transferable has been revoked for another reason
        (
            False,
            enums.TransferableRevocationReason.UPLOAD_SIZE_MISMATCH,
            [],
            enums.OutgoingTransferableState.ERROR,
            True,
        ),
        # Should be removed
        # Test when Transferable has been revoked for another reason
        (
            False,
            enums.TransferableRevocationReason.UPLOAD_INTERRUPTION,
            [],
            enums.OutgoingTransferableState.ERROR,
            True,
        ),
        # Should be removed
        # Test when Transferable has been revoked for another reason
        (
            False,
            enums.TransferableRevocationReason.UNEXPECTED_EXCEPTION,
            [],
            enums.OutgoingTransferableState.ERROR,
            True,
        ),
        # Should be removed
        # Test when Transferable submission in ongoing
        # but one TransferableRange has failed
        (
            False,
            None,
            [
                origin_enums.TransferableRangeTransferState.ERROR,
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
            ],
            enums.OutgoingTransferableState.ERROR,
            True,
        ),
        # Should not be
        # test when submission is finished and all TransferableRanges
        # have been transferred
        (
            True,
            None,
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
            ],
            enums.OutgoingTransferableState.SUCCESS,
            False,
        ),
        # Should be removed
        # test when the submission is ongoing but not TransferableRange
        # has yet been created
        (False, None, [], enums.OutgoingTransferableState.PENDING, True),
        # Should be removed
        # test when submission is ongoing but TransferableRanges have not
        # yet been transferred
        (
            False,
            None,
            [
                origin_enums.TransferableRangeTransferState.PENDING,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            enums.OutgoingTransferableState.PENDING,
            True,
        ),
    ],
)
def test_file_remover_delete_pending_and_error_expired(
    submission_succeeded: bool,
    revocation_reason: enums.TransferableRevocationReason,
    transferable_ranges_states: origin_enums.TransferableRangeTransferState,
    expected_state: enums.OutgoingTransferableState,
    expected_to_delete: bool,
    faker: Faker,
    settings: conf.Settings,
):
    settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)
    expired_date = timezone.now() - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER - datetime.timedelta(seconds=1)

    if submission_succeeded:
        submission_succeeded_at = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    else:
        submission_succeeded_at = None

    with freezegun.freeze_time(expired_date):
        outgoing_transferable = factory.OutgoingTransferableFactory(
            _submission_succeeded=submission_succeeded,
            _submission_succeeded_at=submission_succeeded_at,
        )

    if revocation_reason is not None:
        factory.TransferableRevocationFactory(reason=revocation_reason, outgoing_transferable=outgoing_transferable)

    for transferable_ranges_state in transferable_ranges_states:
        factory.TransferableRangeFactory(
            transfer_state=transferable_ranges_state,
            outgoing_transferable=outgoing_transferable,
        )

    queried_outgoing_transferable = models.OutgoingTransferable.objects.get(id=outgoing_transferable.id)

    assert queried_outgoing_transferable.state == expected_state

    file_remover = OriginFileRemover()
    retrieved = {t.id for t in file_remover._select_transferables_to_remove()}

    assert (len(retrieved) > 0) == expected_to_delete
    if expected_to_delete:
        assert retrieved.pop() == outgoing_transferable.id


@pytest.mark.django_db()
def test_select_transferables_to_remove_pending_and_error_transferables(settings: conf.Settings, faker: Faker):
    settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    nb_pending_transferables_to_keep = 2
    nb_pending_transferables_to_remove = 4
    nb_error_transferables_to_keep = 3
    nb_error_transferables_to_remove = 5
    expected_selected_transferable_id = set()

    unexpired_date = timezone.now() - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER + datetime.timedelta(seconds=1)
    expired_date = timezone.now() - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER - datetime.timedelta(seconds=1)

    for _ in range(nb_pending_transferables_to_keep):
        with freezegun.freeze_time(unexpired_date):
            factory.fs_stored_interrupted_upload_transferable(
                data=faker.binary(length=1024),
                make_transferable_ranges_for_state=(enums.OutgoingTransferableState.PENDING,),
            )

    for _ in range(nb_pending_transferables_to_remove):
        with (
            freezegun.freeze_time(expired_date),
            factory.fs_stored_interrupted_upload_transferable(
                data=faker.binary(length=1024),
                make_transferable_ranges_for_state=(enums.OutgoingTransferableState.PENDING,),
            ) as transferable,
        ):
            expected_selected_transferable_id.add(transferable.id)

    for _ in range(nb_error_transferables_to_keep):
        with freezegun.freeze_time(unexpired_date):
            factory.fs_stored_interrupted_upload_transferable(
                data=faker.binary(length=1024),
                make_transferable_ranges_for_state=(enums.OutgoingTransferableState.ERROR,),
            )

    for _ in range(nb_error_transferables_to_remove):
        with (
            freezegun.freeze_time(expired_date),
            factory.fs_stored_interrupted_upload_transferable(
                data=faker.binary(length=1024),
                make_transferable_ranges_for_state=(enums.OutgoingTransferableState.ERROR,),
            ) as transferable,
        ):
            expected_selected_transferable_id.add(transferable.id)

    file_remover = OriginFileRemover()
    retrieved = {t.id for t in file_remover._select_transferables_to_remove()}
    assert retrieved.difference(expected_selected_transferable_id) == set()


@pytest.mark.django_db()
@mock.patch.object(signals.BooleanCondition, "__bool__")
def test_loop_success_remove_transferable(
    boolean_cond: mock.Mock,
    settings: conf.Settings,
    interrupted_outgoing_transferable: models.OutgoingTransferable,
):
    target_file_path = get_transferable_file_path(str(interrupted_outgoing_transferable.id))

    settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    created_at = timezone.now() - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER - datetime.timedelta(seconds=1)

    interrupted_outgoing_transferable.created_at = created_at
    interrupted_outgoing_transferable.save(update_fields=["created_at"])

    assert target_file_path.exists()

    boolean_cond.side_effect = [True, True, False]
    file_remover = OriginFileRemover()
    file_remover._loop()

    interrupted_outgoing_transferable.refresh_from_db()

    assert not target_file_path.exists()

    with pytest.raises(FileNotFoundError):
        target_file_path.read_bytes()
