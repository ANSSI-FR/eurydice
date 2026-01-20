import factory
from django.conf import settings

from eurydice.common import enums, protocol


class TransferableFactory(factory.Factory):
    id = factory.Faker("uuid4", cast_to=None)
    name = factory.Faker("file_name")
    user_profile_id = factory.Faker("uuid4", cast_to=None)
    user_provided_meta = {"Meta-Foo": "bar", "Meta-Baz": "xyz"}
    sha1 = factory.Faker("sha1", raw_output=True)
    size = factory.Faker("pyint", min_value=0, max_value=settings.TRANSFERABLE_MAX_SIZE)

    class Meta:
        model = protocol.Transferable


class TransferableRangeFactory(factory.Factory):
    is_last = factory.Faker("pybool")
    data = factory.Faker("binary", length=1024)
    transferable = factory.SubFactory(TransferableFactory)
    id = factory.LazyAttribute(lambda self: self.transferable.id)

    _byte_offset = factory.Faker("pyint", max_value=settings.TRANSFERABLE_MAX_SIZE)

    @factory.lazy_attribute
    def byte_offset(self) -> int:
        return max(0, self._byte_offset - len(self.data))

    class Meta:
        model = protocol.TransferableRange
        exclude = ("_byte_offset",)


class TransferableRevocationFactory(factory.Factory):
    transferable_id = factory.Faker("uuid4", cast_to=None)
    user_profile_id = factory.Faker("uuid4", cast_to=None)
    reason = factory.Faker("random_element", elements=enums.TransferableRevocationReason)
    transferable_name = factory.Faker("file_name")
    transferable_sha1 = factory.Faker("sha1", raw_output=True)

    class Meta:
        model = protocol.TransferableRevocation


class HistoryEntryFactory(factory.Factory):
    transferable_id = factory.Faker("uuid4", cast_to=None)
    user_profile_id = factory.Faker("uuid4", cast_to=None)
    state = factory.Faker(
        "random_element",
        elements=enums.OutgoingTransferableState.get_final_states(),
    )
    name = factory.Faker("file_name")
    sha1 = factory.Faker("sha1", raw_output=True)

    class Meta:
        model = protocol.HistoryEntry


class HistoryFactory(factory.Factory):
    entries = factory.List([factory.SubFactory(HistoryEntryFactory) for _ in range(3)])

    class Meta:
        model = protocol.History


class OnTheWirePacketFactory(factory.Factory):
    transferable_ranges = factory.List([factory.SubFactory(TransferableRangeFactory) for _ in range(3)])
    transferable_revocations = factory.List([factory.SubFactory(TransferableRevocationFactory) for _ in range(3)])
    history = factory.Maybe("_has_history", factory.SubFactory(HistoryFactory), None)

    class Meta:
        model = protocol.OnTheWirePacket
        exclude = ("_has_history",)


__all__ = (
    "TransferableFactory",
    "TransferableRangeFactory",
    "TransferableRevocationFactory",
    "HistoryEntryFactory",
    "HistoryFactory",
    "OnTheWirePacketFactory",
)
