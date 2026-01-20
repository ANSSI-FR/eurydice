from eurydice.destination.core.models import IncomingTransferable, IncomingTransferableState
from tests.common.integration.endpoints import pagination
from tests.destination.integration import factory


def make_transferables(count: int, **kwargs):
    factory.IncomingTransferableFactory.create_batch(count, **kwargs)


class TestPagination(pagination.PaginationTestsSuperclass):
    user_profile_factory = factory.UserProfileFactory
    transferable_class = IncomingTransferable
    success_state = IncomingTransferableState.SUCCESS
    error_state = IncomingTransferableState.ERROR
    make_transferables = make_transferables


class TestPaginationInTransaction(pagination.PaginationTestsInTransactionSuperclass):
    user_profile_factory = factory.UserProfileFactory
    transferable_class = IncomingTransferable
    success_state = IncomingTransferableState.SUCCESS
    error_state = IncomingTransferableState.ERROR
    make_transferables = make_transferables
