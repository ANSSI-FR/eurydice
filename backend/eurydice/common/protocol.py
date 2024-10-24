"""This modules defines serializable objects used to communicate between the origin
and destination sides.
"""

import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import msgpack
import pydantic

from eurydice.common import enums


class Transferable(pydantic.BaseModel):
    """A Transferable sent as part of an OnTheWirePacket.

    Attributes:
        id: a UUID identifying the Transferable on the origin and destination side.
        name: the name of the file corresponding to the Transferable.
        user_profile_id: the UUID of the user profile owning the Transferable on the
            origin side.
        user_provided_meta: the metadata provided by the user on file submission.
        sha1: the SHA-1 digest of the file corresponding to the Transferable.
            This attribute can be None as the digest of the Transferable is only
            provided if the TransferableRange that refers to the object is the last.
        size: the size in bytes of the file corresponding to the Transferable.
            This attribute can be None as the size of the Transferable is only
            provided if the TransferableRange that refers to the object is the last.

    """

    id: uuid.UUID  # noqa: VNE003
    name: str
    user_profile_id: uuid.UUID
    user_provided_meta: Dict[str, str]
    sha1: Optional[bytes]
    size: Optional[int]


class TransferableRange(pydantic.BaseModel):
    """A TransferableRange sent as part of an OnTheWirePacket.

    Attributes:
        transferable: the Transferable corresponding to the TransferableRange.
        is_last: boolean indicating if it is the last range for this Transferable.
        byte_offset: the start position of this range in the related Transferable.
        data: the data payload of the TransferableRange i.e. a chunk of the file
            of the related Transferable.

    """

    transferable: Transferable
    is_last: bool
    byte_offset: int
    data: bytes


class TransferableRevocation(pydantic.BaseModel):
    """A TransferableRevocation sent as part of an OnTheWirePacket.

    Attributes:
        transferable_id: a UUID identifying the revoked Transferable.
            The identifier is the same on the origin and destination side.
        user_profile_id: the UUID of the user profile owning the concerned Transferable
            on the origin side.
        reason: why the transferable has been revoked.
        transferable_name: the filename of the transferable in the revocation.
        transferable_sha1: the SHA-1 of the transferable in the revocation.

    """

    transferable_id: uuid.UUID
    user_profile_id: uuid.UUID
    reason: enums.TransferableRevocationReason
    transferable_name: str
    transferable_sha1: Optional[bytes]


class HistoryEntry(pydantic.BaseModel):
    """A history entry logging a processed Transferable on the origin side.

    Attributes:
        transferable_id: a UUID identifying the concerned Transferable.
            The identifier is the same on the origin and destination side.
        user_profile_id: the UUID of the user profile owning the concerned Transferable
            on the origin side. Used to notify the user on the destination side if none
            of the concerned TransferableRanges was received.
        state: the state of the OutgoingTransferable after processing.
        name: the filename of the OutgoingTransferable.
        sha1: the SHA-1 of the OutgoingTransferable.
        user_provided_meta: metadata provided by the user.

    """

    transferable_id: uuid.UUID
    user_profile_id: uuid.UUID
    state: enums.OutgoingTransferableState
    name: str
    sha1: Optional[bytes]
    user_provided_meta: Optional[Dict[str, str]]

    @pydantic.validator("state")
    def _check_state_is_final(
        cls, state: enums.OutgoingTransferableState  # noqa: N805
    ) -> enums.OutgoingTransferableState:
        if not state.is_final:
            raise ValueError(
                f"State must be final i.e. must be one of {state.get_final_states()}"
            )

        return state


class History(pydantic.BaseModel):
    """A History of processed Transferables sent as part of an OnTheWirePacket.

    Attributes:
        entries: HistoryEntries that make up the History.

    """

    entries: List[HistoryEntry]


class SerializationError(RuntimeError):
    """Signal an error encountered while serializing an OnTheWirePacket to bytes."""


class DeserializationError(RuntimeError):
    """Signal an error encountered while deserializing an OnTheWirePacket from bytes."""


def _pack_default(obj: Any) -> Any:
    """Default converts UUID to str when packing with MessagePack."""
    if isinstance(obj, uuid.UUID):
        obj = str(obj)
    return obj


class OnTheWirePacket(pydantic.BaseModel):
    """A packet of data and metadata sent over the network.

    Attributes:
        transferable_ranges: a list of the TransferableRanges in the packet.
        transferable_revocations: a list of the TransferableRevocations in the packet.
        history: an optional History of processed Transferables.

    """

    transferable_ranges: List[TransferableRange] = []
    transferable_revocations: List[TransferableRevocation] = []
    history: Optional[History]

    def to_bytes(self) -> bytes:
        """Serialize the OnTheWirePacket object to bytes.

        Returns:
            The bytes of the serialized OnTheWirePacket.

        Raises:
            SerializationError: if the serialization fails.

        """
        try:
            return msgpack.packb(self.dict(), default=_pack_default)
        except Exception as exc:
            raise SerializationError from exc

    @classmethod
    def from_bytes(cls, data: bytes) -> "OnTheWirePacket":
        """Deserialize an OnTheWirePacket object from bytes.

        Args:
            data: bytes corresponding to a serialized OnTheWirePacket.

        Returns:
            The OnTheWirePacket object resulting from the deserialization.

        Raises:
            DeserializationError: if the deserialization fails.

        """
        try:
            unpacked = msgpack.unpackb(data)
            return cls.parse_obj(unpacked)
        except Exception as exc:
            raise DeserializationError from exc

    def is_empty(self) -> bool:
        """Check if packet is empty.

        Returns:
            True if the packet has no TransferableRanges, TransferableRevocations
            and OngoingHistory.

        """
        return (
            len(self.transferable_ranges) == len(self.transferable_revocations) == 0
        ) and self.history is None

    def __str__(self) -> str:
        self.history: Optional[History] = self.history  # pytype
        return (
            "OnTheWirePacket<"
            f"transferable ranges: {len(self.transferable_ranges)}, "
            f"revocations: {len(self.transferable_revocations)}, "
            f"history entries: {len(self.history.entries) if self.history else 0 }"
            ">"
        )


__all__ = (
    "Transferable",
    "TransferableRange",
    "TransferableRevocation",
    "HistoryEntry",
    "History",
    "SerializationError",
    "DeserializationError",
    "OnTheWirePacket",
)
