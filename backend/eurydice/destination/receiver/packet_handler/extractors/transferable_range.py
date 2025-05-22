import hashlib
import logging
from typing import Tuple

import humanfriendly as hf

import eurydice.common.protocol as protocol
import eurydice.destination.core.models as models
import eurydice.destination.receiver.packet_handler.extractors.base as base_extractor
import eurydice.destination.receiver.transferable_ingestion_fs as transferable_ingestion_fs  # noqa: E501
import eurydice.destination.utils.rehash as rehash

logger = logging.getLogger(__name__)


class TransferableRangeExtractionError(RuntimeError):
    """
    Base Exception for errors while extracting a TransferableRange from an
    OnTheWirePacket.
    """


class MissedTransferableRangeError(TransferableRangeExtractionError):
    """The received TransferableRange's byte offset is not the expected one."""


class FinalDigestMismatchError(TransferableRangeExtractionError):
    """
    The received successful IncomingTransferable's final digest
    does not match the one received in the OnTheWirePacket.
    """


class FinalSizeMismatchError(TransferableRangeExtractionError):
    """
    The received successful IncomingTransferable's final size
    does not match the one received in the OnTheWirePacket.
    """


class TransferableAlreadyInFinalState(TransferableRangeExtractionError):
    """
    Received a TransferableRange for an IncomingTransferable that is already
    in a final state.
    """


def _get_or_create_transferable(
    transferable_range: protocol.TransferableRange,
) -> models.IncomingTransferable:
    """
    Given a TransferableRange found in an OnTheWirePacket, get or create the associated
    IncomingTransferable. Only the transferable ID is used if the IncomingTransferable
    already existed (other fields are ignored).

    If the TransferableRange references an unknown user profile, it is also created.

    Args:
        transferable_range: the TransferableRange (its data may be used for creations).

    Returns:
        The IncomingTransferable ORM instance corresponding to the given range.

    """
    user_profile, _ = models.UserProfile.objects.get_or_create(
        associated_user_profile_id=transferable_range.transferable.user_profile_id
    )

    transferable, _ = models.IncomingTransferable.objects.get_or_create(
        id=transferable_range.transferable.id,
        defaults={
            "id": transferable_range.transferable.id,
            "user_profile": user_profile,
            "name": transferable_range.transferable.name,
            "bytes_received": 0,
            "size": transferable_range.transferable.size,
            "sha1": None,
            "user_provided_meta": transferable_range.transferable.user_provided_meta,
        },
    )

    return transferable


def _assert_no_transferable_ranges_were_missed(
    transferable_range: protocol.TransferableRange,
    transferable: models.IncomingTransferable,
) -> None:
    """
    Given a TransferableRange and the number of bytes received so far
    for the associated IncomingTransferable, check if a TransferableRange
    was missed.

    Args:
        transferable_range: the supposed next TransferableRange.
        transferable: the associated IncomingTransferable.

    Raises:
        MissedTransferableRangeError when a TransferableRange was missed.

    """
    expected_byte_offset = transferable.bytes_received
    if expected_byte_offset != transferable_range.byte_offset:
        raise MissedTransferableRangeError(
            f"Expected byte offset {transferable.bytes_received} but got "
            f"TransferableRange with byte offset {transferable_range.byte_offset} for "
            f"Transferable {transferable_range.transferable.id}"
        )


def _assert_transferable_is_ready(transferable: models.IncomingTransferable) -> None:
    """
    Given an IncomingTransferable, make sure it is ready to ingest new data, i.e. it
    is still in the ONGOING state.

    Args:
        transferable: an IncomingTransferable whose state should be ONGOING.

    Raises:
        TransferableAlreadyInFinalState when the Transferable could not receive new
        data.

    """
    if transferable.state != models.IncomingTransferableState.ONGOING:
        raise TransferableAlreadyInFinalState(
            f"Received TransferableRange for Transferable {transferable.id} which"
            f" is not currently in an ONGOING state: {transferable.state}."
        )


def _assert_transferable_size_is_consistent(
    transferable_range: protocol.TransferableRange,
    transferable: models.IncomingTransferable,
) -> None:
    """Given a received TransferableRange and its associated IncomingTransferable,
    raise an exception and log an error if the number of bytes received is unexpected.

    NOTE: this function is supposed to be called on the last TransferableRange.

    Args:
        transferable_range: the received TransferableRange.
        transferable: the associated IncomingTransferable.

    Raises:
        FinalSizeMismatchError: when the number of bytes received for the Transferable
                                is unexpected.

    """
    bytes_received = transferable.bytes_received + len(transferable_range.data)
    bytes_expected = transferable_range.transferable.size

    if bytes_received != bytes_expected:
        raise FinalSizeMismatchError(
            f"Received {hf.format_size(bytes_received)}, "
            f"expected {hf.format_size(bytes_expected)} "
            f"for Transferable {transferable_range.transferable.id}"
        )

    if transferable.size is not None and transferable.size != bytes_expected:
        logger.warning(
            f"IncomingTransferable {transferable.id} was initially announced with "
            f"size {transferable.size}o but final size is {bytes_received}o."
        )


def _assert_transferable_sha1_is_consistent(
    transferable_range: protocol.TransferableRange,
    computed_sha1: "hashlib._Hash",
) -> None:
    """Given a received TransferableRange and the sha1 computed on the bytes received,
    raise an exception and log an error if the computed and expected digest diverge.

    NOTE: this function is supposed to be called on the last TransferableRange.

    Args:
        transferable_range: the received TransferableRange.
        computed_sha1: the computed SHA1 from all previous ranges for this Transferable.

    Raises:
        FinalDigestMismatchError: when the two digests don't match

    """

    if computed_sha1.digest() != transferable_range.transferable.sha1:
        # in final TransferableRange the sha1 attribute should always be present
        expected_sha1_hex = transferable_range.transferable.sha1.hex()  # type: ignore
        computed_sha1_hex = computed_sha1.hexdigest()

        raise FinalDigestMismatchError(
            f"Computed digest for Transferable {transferable_range.transferable.id} "
            f"was {computed_sha1_hex} expected {expected_sha1_hex}"
        )


def _extract_data(
    transferable_range: protocol.TransferableRange,
    transferable: models.IncomingTransferable,
) -> Tuple[bytes, "hashlib._Hash"]:
    """
    Given a TransferableRange and its associated Transferable database entry, returns
    the TransferableRange's data and an updated version of its SHA1 hash.

    Raises:
        RangeSizeMismatchError when TransferableRange's data is not the right length.

    Args:
        transferable_range: the TransferableRange to get data from.
        transferable: the database entry used to retrieve the current SHA1.

    """
    sha1 = rehash.sha1_from_bytes(bytes(transferable.rehash_intermediary))
    sha1.update(transferable_range.data)

    return transferable_range.data, sha1


def _prepare_ingestion(
    source: protocol.TransferableRange,
    destination: models.IncomingTransferable,
) -> transferable_ingestion_fs.PendingIngestionData:
    """
    Given a TransferableRange (the source), make sure it is valid and ready to be
    incorporated to the associated IncomingTransferable (the destination).

    Args:
        source: the TransferableRange to read information from.
        destination: the push new data to.

    """
    _assert_transferable_is_ready(destination)
    _assert_no_transferable_ranges_were_missed(source, destination)

    data, computed_sha1 = _extract_data(source, destination)

    if source.is_last:
        _assert_transferable_size_is_consistent(source, destination)
        _assert_transferable_sha1_is_consistent(source, computed_sha1)

    return transferable_ingestion_fs.PendingIngestionData(
        data=data,
        sha1=computed_sha1,
        eof=source.is_last,
    )


def _extract_transferable_range(transferable_range: protocol.TransferableRange) -> None:
    """Extract a single transferable range.

    Args:
        transferable_range: the transferable range to process.

    """
    logger.info(f"Extracting data for {transferable_range.transferable.id}")

    transferable = _get_or_create_transferable(transferable_range)

    if transferable.state == models.IncomingTransferableState.ERROR:
        logger.info(
            f"IncomingTransferable {transferable.id} has state "
            f"{models.IncomingTransferableState.ERROR.value}. "  # pytype: disable=attribute-error  # noqa: E501
            "Ignoring the associated transferable range received."
        )
        return

    try:
        to_ingest = _prepare_ingestion(
            source=transferable_range,
            destination=transferable,
        )

        transferable_ingestion_fs.ingest(transferable, to_ingest)

        logger.info(
            f"Successfully extracted and ingested TransferableRange for "
            f"{transferable_range.transferable.id}"
        )

        if transferable.state == models.IncomingTransferableState.SUCCESS:
            logger.info(f"IncomingTransferable {transferable.id} fully received")

    except Exception:
        transferable_ingestion_fs.abort_ingestion(transferable)
        logger.exception(
            f"Encountered an error when trying to extract and ingest "
            f"transferable range for transferable {transferable.id}"
            f"from an OnTheWirePacket."
        )


class TransferableRangeExtractor(base_extractor.OnTheWirePacketExtractor):
    """
    Object to extract TransferableRanges from a given OnTheWirePacket.
    """

    def extract(self, packet: protocol.OnTheWirePacket) -> None:
        """Given an OnTheWirePacket, extract all its TransferableRanges.

        Args:
            packet: packet to extract TransferableRanges from.

        """
        for transferable_range in packet.transferable_ranges:
            _extract_transferable_range(transferable_range)


__all__ = ("TransferableRangeExtractor",)
