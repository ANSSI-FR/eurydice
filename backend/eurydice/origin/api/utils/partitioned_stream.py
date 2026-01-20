"""
StreamPartition Object along with the PartitionedStream iterable to generate them.
"""

import io
from typing import Callable


class StreamPartition:
    """
    A partition of `partition_size` from the given `parent_stream`.

    Args:
        read: The Stream's read Callable
        partition_size: The size in bytes of the StreamPartition
        initial_buffer: bytes already read from the stream.

    Attributes:
        bytes_read: The number of bytes read.

    """

    def __init__(
        self,
        read: Callable[[int], bytes],
        partition_size: int,
        initial_buffer: bytes,
    ):
        self._initial_buffer = initial_buffer
        self._read = read
        self._partition_size = partition_size
        self._partition_eof = False
        self.bytes_read = 0

    def read(self, chunk_size: int = -1) -> bytes:
        """Read `chunk_size` bytes from the parent stream.

        Args:
            chunk_size: Number of bytes to read. Defaults to None.

        Returns:
            Bytes read from the parent stream.

        """
        if self._partition_eof:
            return b""

        # default to _partition_size if no chunk_size
        if chunk_size < 0:
            chunk_size = self._partition_size

        # smaller chunk to prevent exceeding sub_stream_size
        if self.bytes_read + chunk_size >= self._partition_size:
            chunk_size = self._partition_size - self.bytes_read
            self._partition_eof = True

        if self._initial_buffer and chunk_size != 0:
            chunk = self._initial_buffer + self._read(chunk_size - len(self._initial_buffer))
            self._initial_buffer = b""
        else:
            chunk = self._read(chunk_size)

        self.bytes_read += len(chunk)

        return chunk


class PartitionedStream:
    """
    `StreamPartition` Iterable which separates the given stream
    into multiple `StreamPartition` of size `partition_size`,
    calling `on_read` passing it the bytes read from the stream.

    Args:
        stream: The stream to read bytes from.
        partition_size: The size for each StreamPartition.
        on_read: Called with bytes read as argument for each read. Defaults to None.
    """

    def __init__(
        self,
        stream: io.BufferedIOBase,
        partition_size: int,
        on_read: Callable | None = None,
    ):
        self._stream = stream
        self._partition_size = partition_size
        self._on_read = on_read

    def read(self, chunk_size: int) -> bytes:
        """Read `chunk_size` bytes from the stream,
        calls the optional callback with the read bytes as argument

        Args:
            chunk_size: Number of bytes to read from stream

        Returns:
            Bytes read from the stream
        """
        chunk = self._stream.read(chunk_size)

        if self._on_read is not None:
            self._on_read(chunk)

        return chunk

    def __iter__(self):
        while byte := self.read(1):
            yield StreamPartition(self.read, self._partition_size, byte)
