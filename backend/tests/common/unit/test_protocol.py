import hashlib
from unittest import mock

import humanfriendly as hf
import pydantic
import pytest
from faker import Faker

from eurydice.common import enums, protocol


class TestHistoryEntry:
    FINAL_STATES = enums.OutgoingTransferableState.get_final_states()
    TRANSITORY_STATES = set(enums.OutgoingTransferableState) - FINAL_STATES

    @pytest.mark.parametrize("state", FINAL_STATES)
    def test_validation_success(self, state: enums.OutgoingTransferableState, faker: Faker):
        protocol.HistoryEntry(
            transferable_id=faker.uuid4(),
            user_profile_id=faker.uuid4(),
            state=state,
            name="archive.zip",
            sha1=hashlib.sha1(b"archive.zip").hexdigest(),
        )

    @pytest.mark.parametrize("state", TRANSITORY_STATES)
    def test_validation_failure(self, state: enums.OutgoingTransferableState, faker: Faker):
        with pytest.raises(pydantic.ValidationError):
            protocol.HistoryEntry(
                transferable_id=faker.uuid4(),
                user_profile_id=faker.uuid4(),
                state=state,
                name="archive.zip",
                sha1=hashlib.sha1(b"archive.zip").hexdigest(),
            )


def test__pack_default_success_uuid(faker: Faker):
    obj = faker.uuid4(cast_to=None)
    assert protocol._pack_default(obj) == str(obj)


class TestOnTheWirePacket:
    @pytest.mark.parametrize("nb_transferable_revocations", list(range(5)))
    @pytest.mark.parametrize("nb_transferable_ranges", list(range(5)))
    @pytest.mark.parametrize("has_history", [False, True])
    def test_encode_decode_success(
        self,
        has_history: bool,
        nb_transferable_ranges: int,
        nb_transferable_revocations: int,
        faker: Faker,
    ):
        packet_to_send = protocol.OnTheWirePacket()

        if has_history:
            packet_to_send.history = protocol.History(
                entries=[
                    protocol.HistoryEntry(
                        transferable_id=faker.uuid4(),
                        user_profile_id=faker.uuid4(),
                        state=enums.OutgoingTransferableState.SUCCESS,
                        name="archive.zip",
                        sha1=hashlib.sha1(b"archive.zip").hexdigest(),
                    ),
                    protocol.HistoryEntry(
                        transferable_id=faker.uuid4(),
                        user_profile_id=faker.uuid4(),
                        state=enums.OutgoingTransferableState.ERROR,
                        name="archive.zip",
                        sha1=hashlib.sha1(b"archive.zip").hexdigest(),
                    ),
                ]
            )

        if nb_transferable_ranges > 0:
            transferable = protocol.Transferable(
                id=faker.uuid4(),
                name=faker.file_name(),
                user_profile_id=faker.uuid4(),
                user_provided_meta={"Meta-Foo": "bar", "Meta-Baz": "xyz"},
            )

            for idx in range(nb_transferable_ranges):
                data = faker.binary(length=1024)

                transferable_range_is_last = idx + 1 == nb_transferable_ranges
                if transferable_range_is_last:
                    transferable.sha1 = faker.sha1(raw_output=True)
                    transferable.size = faker.pyint(min_value=0, max_value=500) * hf.parse_size("1MB")

                packet_to_send.transferable_ranges.append(
                    protocol.TransferableRange(
                        transferable=transferable,
                        byte_offset=idx * len(data),
                        data=data,
                        is_last=transferable_range_is_last,
                    )
                )

        for _ in range(nb_transferable_revocations):
            packet_to_send.transferable_revocations.append(
                protocol.TransferableRevocation(
                    transferable_id=faker.uuid4(cast_to=None),
                    user_profile_id=faker.uuid4(cast_to=None),
                    reason=enums.TransferableRevocationReason.USER_CANCELED,
                    transferable_name="archive.zip",
                    transferable_sha1=hashlib.sha1(b"archive.zip").hexdigest(),
                )
            )

        serialized = packet_to_send.to_bytes()
        received_packet = protocol.OnTheWirePacket.from_bytes(serialized)

        assert received_packet == packet_to_send

    @mock.patch.object(pydantic.BaseModel, "dict")
    def test_to_bytes_error_raises_SerializationError(  # noqa: N802
        self, mocked_dict_func: mock.Mock
    ):
        mocked_dict_func.return_value = {"non_supported_object": object()}
        packet = protocol.OnTheWirePacket()

        with pytest.raises(protocol.SerializationError):
            packet.to_bytes()

    def test_from_bytes_error_raises_DeserializationError(self):  # noqa: N802
        with pytest.raises(protocol.DeserializationError):
            protocol.OnTheWirePacket.from_bytes(b"hello, world")


@pytest.mark.parametrize(
    ("packet", "expected_emptiness"),
    [
        # empty packet is empty
        (protocol.OnTheWirePacket(), True),
        # packet with empty history is not empty
        (protocol.OnTheWirePacket(history=protocol.History(entries=[])), False),
        # packet with at least one history entry is not empty
        (
            protocol.OnTheWirePacket(history=protocol.History(entries=[mock.Mock(spec=protocol.HistoryEntry)])),
            False,
        ),
        # packet with at least one transferable range is not empty
        (
            protocol.OnTheWirePacket(transferable_ranges=[mock.Mock(spec=protocol.TransferableRange)]),
            False,
        ),
        # packet with at least one transferable revocation is not empty
        (
            protocol.OnTheWirePacket(transferable_revocations=[mock.Mock(spec=protocol.TransferableRevocation)]),
            False,
        ),
    ],
)
def test_on_the_wire_packet_is_empty(
    packet: protocol.OnTheWirePacket,
    expected_emptiness: bool,
):
    assert packet.is_empty() is expected_emptiness
