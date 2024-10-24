from uuid import UUID

import factory
import pytest

import eurydice.origin.core.models as models
import eurydice.origin.sender.user_selector as user_selector
import tests.origin.integration.factory as origin_factory
from eurydice.origin.core import enums


@pytest.mark.django_db()
def test_weighted_round_robin_user_selector_defaults_to_user_with_pending_transferable_ranges():  # noqa: E501
    pending_transferable_range = origin_factory.TransferableRangeFactory(
        transfer_state=enums.TransferableRangeTransferState.PENDING
    )

    origin_factory.TransferableRangeFactory(
        transfer_state=enums.TransferableRangeTransferState.TRANSFERRED
    )

    selector = user_selector.WeightedRoundRobinUserSelector()
    selector.start_round()

    assert (
        selector.get_next_user()
        == pending_transferable_range.outgoing_transferable.user_profile.user
    )


@pytest.mark.django_db()
def test_weighted_round_robin_user_selector_defaults_to_first_user_with_pending_transferable_ranges():  # noqa: E501
    origin_factory.TransferableRangeFactory.create_batch(
        size=2, transfer_state=enums.TransferableRangeTransferState.PENDING
    )

    users = models.User.objects.all().order_by("id")

    # delete first user's OutgoingTransferables
    models.TransferableRange.objects.filter(
        outgoing_transferable__user_profile__user__id=users[0].id
    ).delete()

    selector = user_selector.WeightedRoundRobinUserSelector()
    selector.start_round()

    assert selector.get_next_user() == users[1]


@pytest.mark.django_db()
def test_weighted_round_robin_user_selector_defaults_to_none():
    """
    Assert WRR user selector returns None if no transferable ranges are pending
    """

    for transfer_state in enums.TransferableRangeTransferState:
        if transfer_state is not enums.TransferableRangeTransferState.PENDING:
            origin_factory.TransferableRangeFactory(transfer_state=transfer_state)

    selector = user_selector.WeightedRoundRobinUserSelector()
    selector.start_round()

    assert selector.get_next_user() is None


@pytest.mark.django_db()
def test_weighted_round_robin_user_selector_round_count_behavior():
    # create two users
    user_profiles = origin_factory.UserProfileFactory.create_batch(
        2,
        priority=factory.Iterator((2, 1)),
        user__id=factory.Iterator(
            [
                UUID("00005dcf-5135-4b12-900d-d3bc7ab745fb"),
                UUID("ffff9af2-6a6c-414e-ba54-516268b3b113"),
            ]
        ),
    )

    # create pending ranges
    origin_factory.TransferableRangeFactory.create_batch(
        2,
        outgoing_transferable__user_profile=factory.Iterator(user_profiles),
        transfer_state=enums.TransferableRangeTransferState.PENDING,
    )

    selector = user_selector.WeightedRoundRobinUserSelector()
    assert selector._round_counter == 0

    selector.start_round()

    assert selector.get_next_user() == user_profiles[0].user
    assert selector._round_counter == 1

    selector.start_round()
    assert selector.get_next_user() == user_profiles[0].user
    assert selector._round_counter == 2

    selector.start_round()
    assert selector.get_next_user() == user_profiles[1].user
    assert selector._round_counter == 1

    selector.start_round()
    assert selector.get_next_user() == user_profiles[0].user
    assert selector._round_counter == 1

    assert selector.get_next_user() == user_profiles[1].user
    assert selector._round_counter == 1

    assert selector.get_next_user() is None


@pytest.mark.django_db()
def test_weighted_round_robin_user_selector_returns_user_with_smallest_uuid():  # noqa: E501
    origin_factory.TransferableRangeFactory.create_batch(
        size=10, transfer_state=enums.TransferableRangeTransferState.PENDING
    )

    users = models.User.objects.all().order_by("id")

    # delete first user's OutgoingTransferables
    models.TransferableRange.objects.filter(
        outgoing_transferable__user_profile__user__id=users[0].id
    ).delete()

    selector = user_selector.WeightedRoundRobinUserSelector()
    selector.start_round()

    # simulate the fact that users[0] should be selected again if they had
    # PENDING ranges
    selector._current_user = users[0]
    selector._round_counter = 0

    # make sure it's not the case and that lowest UUID is selected
    assert selector.get_next_user() == users[1]


@pytest.mark.django_db()
def test_weighted_round_robin_user_selector_returns_none():
    """
    Assert WRR user selector returns None if no transferable ranges are pending
    and the sole user is currently selected
    """

    current_user_profile = origin_factory.UserProfileFactory(priority=1)

    for transfer_state in enums.TransferableRangeTransferState:
        if transfer_state is not enums.TransferableRangeTransferState.PENDING:
            origin_factory.TransferableRangeFactory(
                outgoing_transferable__user_profile=current_user_profile,
                transfer_state=transfer_state,
            )

    selector = user_selector.WeightedRoundRobinUserSelector()
    selector.start_round()

    selector._current_user = current_user_profile.user
    selector._round_counter = 0

    assert selector.get_next_user() is None
