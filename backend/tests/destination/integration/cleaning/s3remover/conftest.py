from typing import Iterator

import pytest
from faker import Faker

from eurydice.destination.core import models
from tests.destination.integration import factory as destination_factory


@pytest.fixture()
def success_incoming_transferable(
    faker: Faker,
) -> Iterator[models.IncomingTransferable]:
    with destination_factory.s3_stored_incoming_transferable(
        data=faker.binary(length=1024), state=models.IncomingTransferableState.SUCCESS
    ) as obj:
        yield obj
