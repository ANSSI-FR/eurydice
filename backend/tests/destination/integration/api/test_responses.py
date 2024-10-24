import io
from typing import Dict
from typing import Optional
from unittest import mock

import faker
import pytest
from urllib3._collections import HTTPHeaderDict
from urllib3.response import HTTPResponse

from eurydice.destination.api import responses


class TestForwardedS3FileResponse:
    @pytest.mark.parametrize("input_filename", [None, "file.ext", "file", ""])
    @pytest.mark.parametrize(
        "extra_headers", [{}, {"Foo": "Bar"}, {"Foo": "Bar", "Baz": "Xyz"}]
    )
    @pytest.mark.parametrize(
        "data", [b"", b"Lorem ipsum dolor sit amet, consectetur adipiscing elit."]
    )
    @mock.patch("eurydice.common.minio.client")
    def test_create_and_read_success(
        self,
        minio_client: mock.Mock,
        data: bytes,
        extra_headers: Dict[str, str],
        input_filename: Optional[str],
        faker: faker.Faker,
    ) -> None:
        mock_http_response = mock.Mock(name="httplib.HTTPResponse")
        headers = HTTPHeaderDict()
        headers.add("Content-Length", f"{len(data)}")
        s3_response = HTTPResponse(
            body=io.BytesIO(data),
            status=200,
            preload_content=False,
            headers=headers,
            original_response=mock_http_response,
        )
        minio_client.get_object.return_value = s3_response

        filename = input_filename or faker.file_name()
        res = responses.ForwardedS3FileResponse(
            bucket_name="foo",
            object_name="bar",
            filename=filename,
            extra_headers=extra_headers,
        )

        expected_content_disposition = (
            "attachment" if not filename else f'attachment; filename="{filename}"'
        )

        assert res.headers == {
            "Content-Length": f"{len(data)}",
            "Content-Type": "application/octet-stream",
            "Content-Disposition": expected_content_disposition,
            **extra_headers,
        }

        assert res.getvalue() == data

        with mock.patch("django.http.response.signals"):
            res.close()
