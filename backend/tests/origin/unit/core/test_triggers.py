import datetime

import factory as factory_boy
import freezegun
import pytest
from django.db import transaction
from django.db.utils import InternalError
from django.utils import timezone
from faker import Faker

from eurydice.common import enums as common_enums
from eurydice.origin.core import enums, models
from tests.origin.integration import factory


@pytest.mark.django_db()
def test_range_auto_fields_standard_usage():
    transferable = factory.OutgoingTransferableFactory()
    noise_transferable = factory.OutgoingTransferableFactory()

    assert transferable.auto_revocations_count == 0
    assert transferable.auto_user_revocations_count == 0
    assert transferable.auto_ranges_count == 0
    assert transferable.auto_pending_ranges_count == 0
    assert transferable.auto_transferred_ranges_count == 0
    assert transferable.auto_canceled_ranges_count == 0
    assert transferable.auto_error_ranges_count == 0
    assert transferable.auto_last_range_finished_at is None
    assert transferable.auto_bytes_transferred == 0

    bytes_transferred = 0

    for current_transferable in (transferable, noise_transferable):
        for num_ranges, state in enumerate(enums.TransferableRangeTransferState):
            for _ in range(num_ranges + 1):
                transferable_range = factory.TransferableRangeFactory(
                    transfer_state=state,
                    outgoing_transferable=current_transferable,
                )

                if current_transferable == transferable:
                    last_range_finished_at = transferable_range.finished_at
                    if transferable_range.transfer_state == enums.TransferableRangeTransferState.TRANSFERRED:
                        bytes_transferred += transferable_range.size

    transferable.refresh_from_db()

    assert transferable.auto_revocations_count == 0
    assert transferable.auto_user_revocations_count == 0
    assert transferable.auto_ranges_count == 10
    assert transferable.auto_pending_ranges_count == 1
    assert transferable.auto_transferred_ranges_count == 2
    assert transferable.auto_canceled_ranges_count == 3
    assert transferable.auto_error_ranges_count == 4
    assert transferable.auto_last_range_finished_at == last_range_finished_at
    assert transferable.auto_bytes_transferred == bytes_transferred


@pytest.mark.django_db()
def test_revocation_auto_fields_standard_usage():
    (
        transferable,
        user_transferable,
        noise_transferable,
    ) = factory.OutgoingTransferableFactory.create_batch(3)

    assert transferable.auto_revocations_count == 0
    assert transferable.auto_user_revocations_count == 0

    factory.TransferableRangeFactory(
        transfer_state=enums.TransferableRangeTransferState.CANCELED,
        outgoing_transferable=user_transferable,
    )

    factory.TransferableRevocationFactory.create_batch(
        3,
        reason=factory_boy.Iterator(
            (
                common_enums.TransferableRevocationReason.UPLOAD_SIZE_MISMATCH,
                common_enums.TransferableRevocationReason.USER_CANCELED,
                common_enums.TransferableRevocationReason.USER_CANCELED,
            )
        ),
        outgoing_transferable=factory_boy.Iterator((transferable, user_transferable, noise_transferable)),
    )

    transferable.refresh_from_db()
    user_transferable.refresh_from_db()
    noise_transferable.refresh_from_db()

    assert transferable.auto_revocations_count == 1
    assert transferable.auto_user_revocations_count == 0
    assert transferable.auto_ranges_count == 0
    assert transferable.auto_pending_ranges_count == 0
    assert transferable.auto_transferred_ranges_count == 0
    assert transferable.auto_canceled_ranges_count == 0
    assert transferable.auto_error_ranges_count == 0
    assert transferable.auto_last_range_finished_at is None
    assert transferable.auto_bytes_transferred == 0

    assert user_transferable.auto_revocations_count == 1
    assert user_transferable.auto_user_revocations_count == 1


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "field",
    [
        "auto_revocations_count",
        "auto_user_revocations_count",
        "auto_ranges_count",
        "auto_pending_ranges_count",
        "auto_transferred_ranges_count",
        "auto_canceled_ranges_count",
        "auto_error_ranges_count",
        "auto_last_range_finished_at",
        "auto_bytes_transferred",
        "auto_state_updated_at",
    ],
)
def test_auto_fields_protection(field: str):
    transferable = factory.OutgoingTransferableFactory()

    # the atomic transaction is necessary, otherwise `django_db` thinks the
    # test failed (because the test transaction is broken)
    with pytest.raises(InternalError), transaction.atomic():
        transferable.save(update_fields=[field])


@pytest.mark.django_db()
def test_ranges_forbidden_inserts(faker: Faker):
    transferable = factory.OutgoingTransferableFactory()

    # the atomic transaction is necessary, otherwise `django_db` thinks the
    # test failed (because the test transaction is broken)
    with pytest.raises(InternalError), transaction.atomic():
        models.TransferableRange.objects.create(
            byte_offset=0,
            size=218,
            transfer_state=enums.TransferableRangeTransferState.TRANSFERRED,
            finished_at=faker.future_datetime(tzinfo=timezone.get_current_timezone()),
            outgoing_transferable=transferable,
        )


@pytest.mark.django_db()
def test_ranges_forbidden_updates():
    transferable_range = factory.TransferableRangeFactory(transfer_state=enums.TransferableRangeTransferState.PENDING)

    transferable = factory.OutgoingTransferableFactory()

    # the atomic transaction is necessary, otherwise `django_db` thinks the
    # test failed (because the test transaction is broken)
    with pytest.raises(InternalError), transaction.atomic():
        transferable_range.mark_as_transferred(save=False)
        transferable_range.outgoing_transferable = transferable
        transferable_range.save()

    with pytest.raises(InternalError), transaction.atomic():
        transferable_range.size = 5
        transferable_range.save()

    transferable_range.mark_as_transferred()

    with pytest.raises(InternalError), transaction.atomic():
        transferable_range.mark_as_canceled()


@pytest.mark.django_db()
def test_revocations_forbidden_updates():
    transferable_revocation = factory.TransferableRevocationFactory(
        reason=common_enums.TransferableRevocationReason.UNEXPECTED_EXCEPTION,
        transfer_state=enums.TransferableRevocationTransferState.PENDING,
    )

    # the atomic transaction is necessary, otherwise `django_db` thinks the
    # test failed (because the test transaction is broken)
    with pytest.raises(InternalError), transaction.atomic():
        transferable_revocation.reason = common_enums.TransferableRevocationReason.USER_CANCELED
        transferable_revocation.save()

    transferable_revocation.transfer_state = enums.TransferableRevocationTransferState.TRANSFERRED
    transferable_revocation.save(update_fields=["transfer_state"])


@pytest.mark.django_db()
def test_state_update_through_ranges():
    transferable = factory.OutgoingTransferableFactory()

    current_time = transferable.auto_state_updated_at
    assert current_time is not None

    for state in enums.TransferableRangeTransferState:
        current_time = current_time + datetime.timedelta(minutes=1)
        with freezegun.freeze_time(current_time):
            factory.TransferableRangeFactory(
                transfer_state=state,
                outgoing_transferable=transferable,
                finished_at=(None if state == enums.TransferableRangeTransferState.PENDING else current_time),
            )

        transferable.refresh_from_db()
        assert transferable.auto_state_updated_at == current_time


@pytest.mark.django_db()
@pytest.mark.parametrize("reason", common_enums.TransferableRevocationReason)
def test_state_update_through_revocation(
    reason: common_enums.TransferableRevocationReason,
):
    transferable = factory.OutgoingTransferableFactory()

    current_time = transferable.auto_state_updated_at
    assert current_time is not None

    current_time = current_time + datetime.timedelta(minutes=1)
    with freezegun.freeze_time(current_time):
        factory.TransferableRevocationFactory(
            reason=reason,
            outgoing_transferable=transferable,
        )

    transferable.refresh_from_db()
    assert transferable.auto_state_updated_at == current_time
