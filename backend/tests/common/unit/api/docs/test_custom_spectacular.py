from unittest import mock

from drf_spectacular import utils

from eurydice.common.api.docs import custom_spectacular


@mock.patch.object(utils, "extend_schema")
@mock.patch.object(custom_spectacular, "_code_samples", new_callable=dict)
def test_extend_schema(code_samples: dict, mocked_extend_schema: mock.Mock):
    redoc_code_samples = [
        {
            "lang": "Python",
            "label": "Python 3",
            "source": "import this",
        }
    ]

    custom_spectacular.extend_schema(
        operation_id="test_op_id",
        summary="heyy",
        code_samples=redoc_code_samples,
    )

    mocked_extend_schema.assert_called_once_with(
        operation_id="test_op_id",
        summary="heyy",
    )

    assert code_samples["test_op_id"] == redoc_code_samples


@mock.patch.object(utils, "extend_schema")
@mock.patch.object(custom_spectacular, "_code_samples", new_callable=dict)
def test_extend_schema_no_samples(code_samples: dict, mocked_extend_schema: mock.Mock):
    custom_spectacular.extend_schema(
        operation_id="test_op_id",
        summary="heyy",
    )

    mocked_extend_schema.assert_called_once_with(
        operation_id="test_op_id",
        summary="heyy",
    )

    assert "test_op_id" not in code_samples


@mock.patch.object(utils, "extend_schema")
@mock.patch.object(custom_spectacular, "_code_samples", new_callable=dict)
def test_postprocessing_hook(*_):
    redoc_code_samples = [
        {
            "lang": "Python",
            "label": "Python 3",
            "source": "import this",
        }
    ]

    custom_spectacular.extend_schema(
        operation_id="test_op_id",
        code_samples=redoc_code_samples,
    )

    openapi_json = {
        "paths": {
            "/transferables": {
                "post": {
                    "operationId": "test_other_op_id",
                    "summary": "Bye",
                },
                "get": {
                    "operationId": "test_op_id",
                    "summary": "Coucou",
                },
            }
        }
    }

    openapi_json = custom_spectacular.postprocessing_hook(
        result=openapi_json, generator=None, request=None, public=None
    )

    schema = openapi_json["paths"]["/transferables"]["get"]

    assert schema["summary"] == "Coucou"
    assert schema["x-codeSamples"] == redoc_code_samples

    other_schema = openapi_json["paths"]["/transferables"]["post"]

    assert other_schema["summary"] == "Bye"
    assert "x-codeSamples" not in other_schema
