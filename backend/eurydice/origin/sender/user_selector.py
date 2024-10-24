from typing import List
from typing import Optional
from uuid import UUID

import eurydice.origin.core.models as models
from eurydice.origin.core import enums


class WeightedRoundRobinUserSelector:
    """
    A User selector that implements a Weighted Round Robin algorithm to select the
    next user with PENDING TransferableRange(s) to send.
    """

    def __init__(self) -> None:
        self._round_counter: int = 0
        self._current_user: Optional[models.User] = None
        self._pending_users_in_round: List[UUID] = []

    def start_round(self) -> None:
        """
        Start a Weighted Round Robin Round.

        This will fetch the UUIDs of all users that have at least one pending
        TransferableRange when the round starts, and put them in the internal
        pending users list.
        """

        self._pending_users_in_round = sorted(
            models.TransferableRange.objects.values_list(  # type: ignore
                "outgoing_transferable__user_profile__user_id",
                flat=True,
            )
            .filter(transfer_state=enums.TransferableRangeTransferState.PENDING)
            .distinct("outgoing_transferable__user_profile_id")
        )

    def get_next_user(self) -> Optional[models.User]:
        """
        Retrieve the next user using a Weighted Round Robin algorithm.

        It is important to note that a user can only be selected once per round,
        (i.e. once per OnTheWirePacket), even with a high priority.

        Indeed, when the algorithm selects a user, all of this user's pending
        TransferableRanges will be retrieved and put in the OnTheWirePacket. If
        after this the OnTheWirePacket is still not full, it is not suitable
        to select the same user again (actually it could even cause a denial of
        service with accurately timed zero-length files).

        Returns:
            The user selected by the weighted round robin algorithm.
        """

        if not self._pending_users_in_round:
            self._reset_current_user()
        elif self._current_user is None:
            self._select_arbitrary_pending_user()
        elif (
            self._round_counter < self._current_user.user_profile.priority
            and self._current_user.id in self._pending_users_in_round
        ):
            self._reselect_current_user()
        else:
            self._select_next_pending_user()

        self._round_counter += 1
        return self._current_user

    def _reset_current_user(self) -> None:
        """Set the current user to None."""

        # counting None rounds serves no purpose but makes the code clearer
        self._round_counter = 0
        self._current_user = None

    def _select_arbitrary_pending_user(self) -> None:
        """Selects the user with pending TransferableRanges with the lowest UUID."""

        self._round_counter = 0
        self._current_user = models.User.objects.select_related("user_profile").get(
            id=self._pending_users_in_round.pop(0)
        )

    def _reselect_current_user(self) -> None:
        """Increase current user's rounds count and remove them from current round."""

        current_user_id: UUID = self._current_user.id  # type: ignore
        self._pending_users_in_round.remove(current_user_id)

    def _select_next_pending_user(self) -> None:
        """Select the user that comes after the current one."""

        self._round_counter = 0
        self._current_user = models.User.objects.select_related("user_profile").get(
            id=self._select_next_pending_user_id()
        )

        self._pending_users_in_round.remove(self._current_user.id)

    def _select_next_pending_user_id(self) -> UUID:
        """Select the user ID that comes right after the current one, sorted by ID."""

        return next(
            filter(
                (lambda user_id: user_id > self._current_user.id),  # type: ignore
                self._pending_users_in_round,
            ),
            self._pending_users_in_round[0],
        )


__all__ = ("WeightedRoundRobinUserSelector",)
