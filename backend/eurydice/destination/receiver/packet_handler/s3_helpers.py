from typing import Any
from typing import List

from minio.datatypes import Part

import eurydice.destination.core.models as models
from eurydice.common import minio


def initiate_multipart_upload(
    incoming_transferable: models.IncomingTransferable,
) -> str:
    """
    Given a Transferable create an associated multipart upload

    Args:
        incoming_transferable: the IncomingTransferable for which to initiate upload

    Returns:
        The new multipart upload's ID
    """
    return minio.client._create_multipart_upload(
        bucket_name=incoming_transferable.s3_bucket_name,
        object_name=str(incoming_transferable.id),
        headers={},
    )


def clean_etag(etag: str) -> str:
    """Cleans the given etag string by removing unwanted characters.

    ETags are defined according to the S3 specification:
    https://docs.aws.amazon.com/AmazonS3/latest/API/RESTCommonResponseHeaders.html

    Args:
        etag: the etag string to clean

    Returns:
        The cleaned ETag.
    """
    return "".join(char for char in etag if char.isalnum() or char == "-")


def _build_multipart_upload_dict(
    transferable: models.IncomingTransferable,
) -> List[Any]:
    """
    Given a Transferable, build the Parts dictionary required for completing the
     multipart upload.

    Args:
        transferable: IncomingTransferable for which to build multipart upload dict

    Returns:
        A dictionary containing the list of all parts making up the Transferable's
        multipart upload.
    """

    parts: List = []

    for part in models.S3UploadPart.objects.filter(
        incoming_transferable=transferable
    ).order_by("part_number"):
        parts.append(Part(part.part_number, part.etag.hex()))

    return parts


def complete_multipart_upload(transferable: models.IncomingTransferable) -> None:
    """
    Given a Transferable, mark its associated S3 multipart upload as complete.

    Args:
        transferable: IncomingTransferable to complete upload.
    """
    minio.client._complete_multipart_upload(
        bucket_name=transferable.s3_bucket_name,
        object_name=transferable.s3_object_name,
        upload_id=transferable.s3_upload_id,
        parts=_build_multipart_upload_dict(transferable),
    )


def abort_multipart_upload(transferable: models.IncomingTransferable) -> None:
    """
    Given a Transferable, abort its associated S3 multipart upload, if any.

    Args:
        transferable: IncomingTransferable to abord upload.
    """
    if transferable.s3_upload_id:
        minio.client._abort_multipart_upload(
            bucket_name=transferable.s3_bucket_name,
            object_name=transferable.s3_object_name,
            upload_id=transferable.s3_upload_id,
        )


__all__ = ("initiate_multipart_upload", "clean_etag", "complete_multipart_upload")
