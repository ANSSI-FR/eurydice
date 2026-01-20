from typing import Iterator

import pytest
from faker import Faker

from eurydice.origin.core import models
from tests.origin.integration import factory as origin_factory


@pytest.fixture()
def interrupted_outgoing_transferable(
    faker: Faker,
) -> Iterator[models.OutgoingTransferable]:
    with origin_factory.fs_stored_interrupted_upload_transferable(
        data=faker.binary(length=1024),
    ) as obj:
        yield obj
