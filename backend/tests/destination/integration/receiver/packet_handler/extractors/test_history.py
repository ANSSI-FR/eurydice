import hashlib
import logging
import uuid
from pathlib import Path

import pytest
from django.conf import Settings

from eurydice.common import protocol
from eurydice.destination.core import models
from eurydice.destination.core.models.incoming_transferable import (
    IncomingTransferableState,
)
from eurydice.destination.receiver.packet_handler.extractors import history
from eurydice.destination.storage import fs
from tests.common.integration import factory as common_factory
from tests.destination.integration import factory as destination_factory


@pytest.mark.parametrize("state", set(IncomingTransferableState))
def test_transferables_states_consistency(state: IncomingTransferableState):
    assert state.is_final == (state != IncomingTransferableState.ONGOING)


@pytest.mark.django_db()
def test__list_ongoing_transferable_ids_success():
    ongoing_transferable = destination_factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.ONGOING
    )

    for state in models.IncomingTransferableState.get_final_states():
        destination_factory.IncomingTransferableFactory(state=state)

    transferable_ids = {ongoing_transferable.id}
    assert history._list_ongoing_transferable_ids(transferable_ids) == transferable_ids


@pytest.mark.django_db()
def test__list_finished_transferable_ids_success():
    final_transferables = [
        destination_factory.IncomingTransferableFactory(state=state)
        for state in models.IncomingTransferableState.get_final_states()
    ]

    destination_factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.ONGOING
    )

    transferable_ids = {t.id for t in final_transferables}
    assert history._list_finished_transferable_ids(transferable_ids) == transferable_ids


@pytest.mark.django_db()
def test__list_missed_transferable_ids_success():
    existing_transferable = destination_factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.ONGOING
    )
    missed_transferable_ids = {uuid.uuid4() for _ in range(10)}
    transferable_ids = missed_transferable_ids | {existing_transferable.id}

    assert (
        history._list_missed_transferable_ids(transferable_ids, set())
        == transferable_ids
    )


@pytest.mark.django_db()
def test__process_ongoing_transferables(
    ongoing_incoming_transferable: models.IncomingTransferable,
):
    ongoing_transferable_ids = {ongoing_incoming_transferable.id}
    history._process_ongoing_transferables(ongoing_transferable_ids)
    assert (
        models.IncomingTransferable.objects.get().state
        == models.IncomingTransferableState.ERROR
    )


@pytest.mark.django_db()
def test__process_missed_transferables():
    history_entry_map = history._HistoryEntryMap(common_factory.HistoryFactory())
    missed_transferable_ids = set(history_entry_map.keys())
    history._process_missed_transferables(missed_transferable_ids, history_entry_map)

    assert models.IncomingTransferable.objects.filter(
        id__in=missed_transferable_ids, state=models.IncomingTransferableState.ERROR
    ).count() == len(missed_transferable_ids)


@pytest.mark.django_db()
class TestOngoingHistoryExtractor:
    def test_extract_empty_history_success(self, caplog: pytest.LogCaptureFixture):
        caplog.set_level(logging.INFO)
        packet = protocol.OnTheWirePacket(history=protocol.History(entries=[]))
        history.OngoingHistoryExtractor().extract(packet)
        assert not models.IncomingTransferable.objects.exists()
        assert "History processed." in caplog.text

    def test_extract_history_success_nothing_to_process(self):
        nb_transferables = 3

        incoming_transferables = (
            destination_factory.IncomingTransferableFactory.create_batch(
                size=nb_transferables, state=models.IncomingTransferableState.SUCCESS
            )
        )
        packet = protocol.OnTheWirePacket(
            history=protocol.History(
                entries=[
                    protocol.HistoryEntry(
                        transferable_id=t.id,
                        user_profile_id=uuid.uuid4(),
                        state=models.IncomingTransferableState.SUCCESS,
                        name="archive.zip",
                        sha1=hashlib.sha1(b"archive.zip").hexdigest(),
                    )
                    for t in incoming_transferables
                ]
            )
        )
        history.OngoingHistoryExtractor().extract(packet)

        assert models.IncomingTransferable.objects.count() == nb_transferables
        assert (
            models.IncomingTransferable.objects.filter(
                state=models.IncomingTransferableState.SUCCESS
            ).count()
            == nb_transferables
        )

    def test_extract_history_success_process_ongoing(
        self, ongoing_incoming_transferable: models.IncomingTransferable
    ):
        assert (
            ongoing_incoming_transferable.state
            == models.IncomingTransferableState.ONGOING
        )
        packet = protocol.OnTheWirePacket(
            history=protocol.History(
                entries=[
                    protocol.HistoryEntry(
                        transferable_id=ongoing_incoming_transferable.id,
                        user_profile_id=ongoing_incoming_transferable.user_profile.id,
                        state=models.IncomingTransferableState.SUCCESS,
                        name="archive.zip",
                        sha1=hashlib.sha1(b"archive.zip").hexdigest(),
                    )
                ]
            )
        )
        history.OngoingHistoryExtractor().extract(packet)
        ongoing_incoming_transferable.refresh_from_db()
        assert (
            ongoing_incoming_transferable.state
            == models.IncomingTransferableState.ERROR
        )

    def test_extract_history_success_process_ongoing_with_filesystem_storage(
        self,
        settings: Settings,
        tmp_path: Path,
    ):
        settings.TRANSFERABLE_STORAGE_DIR = tmp_path
        ongoing_incoming_transferable = destination_factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.ONGOING
        )
        fs.file_path(ongoing_incoming_transferable).parent.mkdir(
            parents=True, exist_ok=True
        )
        fs.file_path(ongoing_incoming_transferable).touch()

        assert (
            ongoing_incoming_transferable.state
            == models.IncomingTransferableState.ONGOING
        )
        assert fs.file_path(ongoing_incoming_transferable).exists()

        packet = protocol.OnTheWirePacket(
            history=protocol.History(
                entries=[
                    protocol.HistoryEntry(
                        transferable_id=ongoing_incoming_transferable.id,
                        user_profile_id=ongoing_incoming_transferable.user_profile.id,
                        state=models.IncomingTransferableState.SUCCESS,
                        name="archive.zip",
                        sha1=hashlib.sha1(b"archive.zip").hexdigest(),
                    )
                ]
            )
        )
        history.OngoingHistoryExtractor().extract(packet)
        ongoing_incoming_transferable.refresh_from_db()
        assert (
            ongoing_incoming_transferable.state
            == models.IncomingTransferableState.ERROR
        )
        assert not fs.file_path(ongoing_incoming_transferable).exists()

    def test_extract_history_success_process_missed(self):
        assert not models.IncomingTransferable.objects.exists()

        packet = protocol.OnTheWirePacket(
            history=protocol.History(
                entries=[
                    protocol.HistoryEntry(
                        transferable_id=uuid.uuid4(),
                        user_profile_id=uuid.uuid4(),
                        state=models.IncomingTransferableState.SUCCESS,
                        name="archive.zip",
                        sha1=hashlib.sha1(b"archive.zip").hexdigest(),
                        user_provided_meta={"Metadata-Foo": "Bar"},
                    )
                ]
            )
        )
        history.OngoingHistoryExtractor().extract(packet)

        assert models.IncomingTransferable.objects.count() == 1
        incoming_transferable = models.IncomingTransferable.objects.get()
        assert incoming_transferable.id == packet.history.entries[0].transferable_id
        assert incoming_transferable.name == packet.history.entries[0].name
        assert bytes(incoming_transferable.sha1) == packet.history.entries[0].sha1
        assert (
            incoming_transferable.user_profile.associated_user_profile_id
            == packet.history.entries[0].user_profile_id
        )
        assert incoming_transferable.state == models.IncomingTransferableState.ERROR
        assert incoming_transferable.user_provided_meta == {"Metadata-Foo": "Bar"}

    def test_extract_history_success_no_history(self):
        packet = protocol.OnTheWirePacket()
        history.OngoingHistoryExtractor().extract(packet)

    def test_extract_history_process_cleaned_entry(self):
        """
        Tests that an IncomingTransferable does not go to status ERROR if its status
        is set to EXPIRED by the file remover
        """
        incoming_transferable = destination_factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.SUCCESS
        )

        # simulate file remover
        incoming_transferable.state = IncomingTransferableState.EXPIRED
        incoming_transferable.save()

        packet = protocol.OnTheWirePacket(
            history=protocol.History(
                entries=[
                    protocol.HistoryEntry(
                        transferable_id=incoming_transferable.id,
                        user_profile_id=uuid.uuid4(),
                        state=models.IncomingTransferableState.SUCCESS,
                        name="archive.zip",
                        sha1=hashlib.sha1(b"archive.zip").hexdigest(),
                    )
                ]
            )
        )
        history.OngoingHistoryExtractor().extract(packet)

        # history didn't make the transferable go bad
        assert models.IncomingTransferable.objects.count() == 1
        assert (
            models.IncomingTransferable.objects.filter(
                state=models.IncomingTransferableState.EXPIRED
            ).count()
            == 1
        )
