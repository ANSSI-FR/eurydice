from minio.error import S3Error

from eurydice.common import minio
from eurydice.destination.core import models


def multipart_upload_exists(incoming_transferable: models.IncomingTransferable) -> bool:
    try:
        minio.client._list_parts(
            bucket_name=incoming_transferable.s3_bucket_name,
            object_name=incoming_transferable.s3_object_name,
            upload_id=incoming_transferable.s3_upload_id,
        )
    except S3Error as e:
        if e.code == "NoSuchUpload":
            return False
        raise

    return True


__all__ = ("multipart_upload_exists",)
