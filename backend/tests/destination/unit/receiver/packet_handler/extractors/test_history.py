import uuid
from typing import cast

import pytest

from eurydice.common import protocol
from eurydice.destination.receiver.packet_handler.extractors import history


class MockedHistoryEntry:
    def __init__(self):
        self.transferable_id = uuid.uuid4()


class MockedHistory:
    def __init__(self, nb_entries: int):
        self.entries = [MockedHistoryEntry() for _ in range(nb_entries)]


class Test_HistoryEntryMap:  # noqa: N801
    @pytest.mark.parametrize("nb_entries", range(3))
    def test_constructor_success(self, nb_entries: int):
        hist = cast(protocol.History, MockedHistory(nb_entries=nb_entries))
        assert history._HistoryEntryMap(hist) == {e.transferable_id: e for e in hist.entries}
