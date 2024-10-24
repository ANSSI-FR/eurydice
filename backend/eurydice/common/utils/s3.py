"""Utility functions to deal with S3 resources."""

import logging

from django.conf import settings
from minio.commonconfig import ENABLED
from minio.commonconfig import Filter
from minio.error import S3Error
from minio.lifecycleconfig import Expiration
from minio.lifecycleconfig import LifecycleConfig
from minio.lifecycleconfig import Rule

from eurydice.common import minio

logger = logging.getLogger(__name__)


def create_bucket_if_does_not_exist() -> None:
    """Check if configured bucket exists, create it if it does not."""
    try:
        minio.client.make_bucket(bucket_name=settings.MINIO_BUCKET_NAME)
        config = LifecycleConfig(
            [
                Rule(
                    ENABLED,
                    rule_filter=Filter(prefix=""),
                    rule_id="expiration-rule",
                    expiration=Expiration(days=settings.MINIO_EXPIRATION_DAYS),
                )
            ]
        )
        minio.client.set_bucket_lifecycle(settings.MINIO_BUCKET_NAME, config)
    except S3Error as error:
        if error.code != "BucketAlreadyOwnedByYou":
            raise error
    else:
        logger.info(
            f"Bucket '{settings.MINIO_BUCKET_NAME}' did " f"not exist and was created"
        )


__all__ = ("create_bucket_if_does_not_exist",)
