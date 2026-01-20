from eurydice.common.enums import OutgoingTransferableState
from eurydice.origin.core.models import OutgoingTransferable
from tests.common.integration.endpoints import pagination
from tests.origin.integration import factory


def make_transferables(count: int, state: OutgoingTransferableState | None = None, **kwargs):
    factory.OutgoingTransferableFactory.create_batch(count, make_transferable_ranges_for_state=state, **kwargs)


class TestPagination(pagination.PaginationTestsSuperclass):
    user_profile_factory = factory.UserProfileFactory
    transferable_class = OutgoingTransferable
    success_state = OutgoingTransferableState.SUCCESS
    error_state = OutgoingTransferableState.ERROR
    make_transferables = make_transferables


class TestPaginationInTransaction(pagination.PaginationTestsInTransactionSuperclass):
    user_profile_factory = factory.UserProfileFactory
    transferable_class = OutgoingTransferable
    success_state = OutgoingTransferableState.SUCCESS
    error_state = OutgoingTransferableState.ERROR
    make_transferables = make_transferables
