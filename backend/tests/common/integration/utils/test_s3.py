import logging
from unittest import mock

import pytest
from django import conf
from minio.error import S3Error

from eurydice.common import minio
from eurydice.common.utils import s3 as s3_utils


def test_create_bucket_if_does_not_exist_success_create(
    settings: conf.Settings, caplog: pytest.LogCaptureFixture
):
    caplog.set_level(logging.INFO)

    bucket = "non-existing-bucket-x7859"
    settings.MINIO_BUCKET_NAME = bucket

    s3_utils.create_bucket_if_does_not_exist()
    minio.client.remove_bucket(bucket_name=bucket)

    assert caplog.messages == [f"Bucket '{bucket}' did not exist and was created"]


def test_create_bucket_if_does_not_exist_success_bucket_already_own(
    settings: conf.Settings, caplog: pytest.LogCaptureFixture
):
    caplog.set_level(logging.INFO)

    bucket = "non-existing-bucket-x5195"
    settings.MINIO_BUCKET_NAME = bucket

    try:
        minio.client.make_bucket(bucket_name=bucket)

        s3_utils.create_bucket_if_does_not_exist()
    finally:
        minio.client.remove_bucket(bucket_name=bucket)

    assert not caplog.messages


@mock.patch("eurydice.common.utils.s3.minio")
def test_create_bucket_raise_client_error(
    minio: mock.Mock, caplog: pytest.LogCaptureFixture
):
    response = {"Error": {"Code": "SomethingBadHappened"}}
    minio.client.make_bucket.side_effect = S3Error(
        code="SomethingBadHappened",
        message="Oups",
        resource="Resource",
        request_id=42,
        host_id=123,
        response=response,
    )

    with pytest.raises(S3Error) as exc:
        s3_utils.create_bucket_if_does_not_exist()

        assert exc.code == response["Error"]["Code"]

    assert not caplog.messages
    minio.client.make_bucket.assert_called_once()


class SomeException(RuntimeError):
    pass


@mock.patch("eurydice.common.utils.s3.minio")
def test_create_bucket_raise_error(minio: mock.Mock, caplog: pytest.LogCaptureFixture):
    minio.client.make_bucket.side_effect = SomeException

    with pytest.raises(SomeException):
        s3_utils.create_bucket_if_does_not_exist()

    assert not caplog.messages
    minio.client.make_bucket.assert_called_once()
