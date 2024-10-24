"""Custom Django Response classes."""

import logging
from typing import Dict
from typing import Optional

from django import http
from minio.error import S3Error

from eurydice.common import exceptions
from eurydice.common import minio

logger = logging.getLogger(__name__)


class ForwardedS3FileResponse(http.FileResponse):
    """
    HTTP Response that streams the content of a remote S3 object
    through the Django API to the client.

    Attributes:
        bucket_name: Name of the S3 bucket.
        object_name: Name of the object in the bucket.
        filename: Name of the file served to the client.
        extra_headers: Extra HTTP header to include in the response.
            Can override headers provided by the S3 endpoint.
        as_attachment: Whether to set the Content-Disposition header
            to attachment, which asks the browser to offer the file
            to the user as a download.
    """

    def __init__(
        self,
        *,
        bucket_name: str,
        object_name: str,
        filename: str,
        extra_headers: Optional[Dict[str, str]] = None,
        as_attachment: bool = True,
    ):
        extra_headers = extra_headers or {}

        logger.debug("Start fetching file from MinIO.")
        try:
            self._s3_response = minio.client.get_object(
                bucket_name=bucket_name, object_name=object_name
            )
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise exceptions.S3ObjectNotFoundError() from e
            raise
        logger.debug("File fetched from MinIO.")

        logger.debug("Forwarding MinIO HTTP response to user.")
        super().__init__(
            self._s3_response,
            filename=filename,
            headers={
                "Content-Length": self._s3_response.headers.get("Content-Length"),
                **extra_headers,
            },
            as_attachment=as_attachment,
            # manually override Content-Type to prevent mime sniffing
            content_type="application/octet-stream",
        )
        # tell Django to call self._s3_response.release_conn after reading data.
        # Django calls self._s3_response.close automatically.
        self._resource_closers.append(self.file_to_stream.release_conn)  # type: ignore


__all__ = ("ForwardedS3FileResponse",)
