from django.utils import timezone

from eurydice.common import protocol
from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.destination.core import models
from eurydice.destination.receiver.packet_handler.extractors import base


def _create_revoked_transferable(revocation: protocol.TransferableRevocation) -> None:
    """Create an IncomingTransferable object with the state REVOKED in the database.

    If a UserProfile corresponding to the `user_profile_id` in the revocation does not
    exist, it will be created.
    """
    user_profile, _ = models.UserProfile.objects.get_or_create(associated_user_profile_id=revocation.user_profile_id)

    now = timezone.now()
    models.IncomingTransferable.objects.create(
        id=revocation.transferable_id,
        name=revocation.transferable_name,
        sha1=revocation.transferable_sha1,
        bytes_received=0,
        size=None,
        user_profile=user_profile,
        user_provided_meta={},
        created_at=now,
        finished_at=now,
        state=models.IncomingTransferableState.REVOKED,
    )


def _revoke_transferable(transferable: models.IncomingTransferable) -> None:
    """Mark a transferable as REVOKED in the database and remove its data from the
    storage.
    """
    transferable.mark_as_revoked()


def _process_revocation(revocation: protocol.TransferableRevocation) -> None:
    """Attempt to mark an IncomingTransferable as REVOKED and to remove its data.

    Args:
        revocation: the TransferableRevocation to process.

    """
    try:
        transferable = models.IncomingTransferable.objects.get(id=revocation.transferable_id)
    except models.IncomingTransferable.DoesNotExist:
        _create_revoked_transferable(revocation)
    else:
        if transferable.state != models.IncomingTransferableState.ONGOING:
            logger.error(
                {
                    LOG_KEY: "transferable_cannot_be_revoked",
                    "transferable_id": str(transferable.id),
                    "transferable_state": transferable.state,
                    "message": f"Only {models.IncomingTransferableState.ONGOING.value} transferables can be revoked.",
                }
            )

            return

        _revoke_transferable(transferable)

    logger.info({LOG_KEY: "transferable_revoked", "transferable_id": str(revocation.transferable_id)})


class TransferableRevocationExtractor(base.OnTheWirePacketExtractor):
    """Process the transferable revocations in an OnTheWirePacket."""

    def extract(self, packet: protocol.OnTheWirePacket) -> None:
        """Sequentially process the transferable revocations in an OnTheWirePacket,
        and log encountered errors.

        Args:
            packet: the OnTheWirePacket to extract the revocations from.

        """

        for revocation in packet.transferable_revocations:
            try:
                _process_revocation(revocation)
            except Exception as error:
                logger.exception(
                    {
                        LOG_KEY: "failed_to_revoke",
                        "transferable_id": str(revocation.transferable_id),
                        "error": str(error),
                    }
                )


__all__ = ("TransferableRevocationExtractor",)
