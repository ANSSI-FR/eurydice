"""
Miscellaneous utilities used in the origin services of Eurydice.
"""

from .metadata_headers import extract_metadata_from_headers
from .partitioned_stream import PartitionedStream
from .partitioned_stream import StreamPartition

__all__ = (
    "PartitionedStream",
    "StreamPartition",
    "extract_metadata_from_headers",
)
