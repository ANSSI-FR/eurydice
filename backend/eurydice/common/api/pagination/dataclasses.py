from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode
from datetime import datetime
from typing import NamedTuple
from typing import Optional

from django.utils import timezone
from msgpack import packb
from msgpack import unpackb

MICROSECONDS = 1_000_000


def pack_datetime(date: Optional[datetime]) -> Optional[int]:
    """Convert a datetime string to a more memory-efficient integer."""
    return int(date.timestamp() * MICROSECONDS) if date else None


def unpack_datetime(packed_date: Optional[int]) -> Optional[datetime]:
    """Convert a memory-efficient integer to a datetime string."""
    if packed_date is None:
        return None

    return timezone.make_aware(datetime.fromtimestamp(packed_date / MICROSECONDS))


class Link(NamedTuple):
    """
    A Link points to a page in the database.

    There are mainly three types of links:

        - OFFSET/LIMIT links:
            - `position`: None
            - `reverse`: False
            - `offset`: the amount of items to skip to reach the beginning of the page

        - Forward links:
            - `position`: a reference to the item that is just before the current page
            - `reverse`: False
            - `offset`: 0

        - Reverse links:
            - `position`: a reference to the item that is just after the current page
            - `reverse`: True
            - `offset`: 0

    There are edge cases where `position` is not None and `offset` is not null, but
    they are mostly handled in the parent class.
    """

    offset: int
    reverse: bool = False
    position: Optional[datetime] = None

    def with_offset(self, offset: int) -> "Link":
        """Create a new Link with an offset."""

        return Link(self.offset + offset, self.reverse, self.position)

    def packb(self) -> bytes:
        """Serialize the link to bytes."""

        topack = list(self)
        topack[2] = pack_datetime(self.position)

        return packb(topack)

    @classmethod
    def unpackb(cls, packed: bytes) -> "Link":
        """Deserialize a link from bytes."""

        unpacked = unpackb(packed, use_list=True)
        unpacked[2] = unpack_datetime(unpacked[2])

        return cls(*unpacked)


class Session(NamedTuple):
    """
    A Session contains information that can be forwarded from a request to another.

    When information is transmitted through a session accross requests:

        - the performances are those of cursor-based pagination,
        - and iteration over pages is consistent.

    The session token contains :
        - links that will allow fast database reads,
        - the page number accessed within the session,
        - the amount of items in the database when the session started,
        - the ID of the most recent item in the database (the "beacon"),
        - and a fingerprint of side query parameters which are not supposed to change
          within a session (e.g. page size and filters),
        - the moment when this session was created, for informative purposes.

    These pieces of information are necessary both for performances and to enable
    advanced features like pseudo-stateful navigation and new items detection.
    """

    previous_link: Optional[Link]
    current_link: Link
    next_link: Optional[Link]
    page_number: int
    items_count: int
    first_item: Optional[datetime]
    last_item: Optional[datetime]
    query_params_hash: bytes
    paginated_at: datetime

    def packb(self) -> bytes:
        """Serialize the session to bytes."""

        topack = list(self)
        topack[0] = Link(*self.previous_link).packb() if self.previous_link else None
        topack[1] = Link(*self.current_link).packb()
        topack[2] = Link(*self.next_link).packb() if self.next_link else None
        topack[5] = pack_datetime(self.first_item)
        topack[6] = pack_datetime(self.last_item)
        topack[8] = pack_datetime(self.paginated_at)

        return packb(topack)

    @classmethod
    def unpackb(cls, packed: bytes) -> "Session":
        """Deserialize a session from bytes."""

        unpacked = unpackb(packed, use_list=True)
        unpacked[0] = Link.unpackb(unpacked[0]) if unpacked[0] else None
        unpacked[1] = Link.unpackb(unpacked[1])
        unpacked[2] = Link.unpackb(unpacked[2]) if unpacked[2] else None
        unpacked[5] = unpack_datetime(unpacked[5])
        unpacked[6] = unpack_datetime(unpacked[6])
        unpacked[8] = unpack_datetime(unpacked[8])

        return cls(*unpacked)


class PageIdentifier(NamedTuple):
    """
    A PageIdentifier contains a session and an offset.

    The offset represents the identified page relative to the session's
    current page number.
    """

    session: Session
    offset: int

    def pack(self) -> str:
        """Serialize the page identifier in a URL-safe base 64 string."""

        return urlsafe_b64encode(packb((self.session.packb(), self.offset))).decode(
            "ascii"
        )

    @classmethod
    def unpack(cls, packed: str) -> "PageIdentifier":
        """Deserialize a page identifier from its URL-safe base 64 format."""

        unpacked = unpackb(urlsafe_b64decode(packed.encode("ascii")), use_list=True)
        unpacked[0] = Session.unpackb(unpacked[0])

        return cls(*unpacked)


class Query(NamedTuple):
    """
    A Query object contains structured metadata about information in query parameters.

    Such an object is built at every API request, and takes into account the following
    query parameters:

        - `page`;
        - `delta`;
        - `from`;
        - `session`.
    """

    queried_page: int
    session: Optional[Session]
