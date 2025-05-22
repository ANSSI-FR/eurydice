from typing import Iterator

import pytest
from faker import Faker

from eurydice.destination.core import models
from eurydice.destination.storage import fs
from tests.destination.integration import factory as destination_factory


@pytest.fixture()
def ongoing_incoming_transferable(
    faker: Faker,
) -> Iterator[models.IncomingTransferable]:
    obj = destination_factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.ONGOING
    )
    try:
        fs.write_bytes(obj, faker.binary(length=1024))

        obj.save()

        yield obj
    finally:
        fs.delete(obj)
