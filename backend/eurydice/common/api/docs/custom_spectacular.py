from typing import Any

from drf_spectacular import utils

_RedocCodeSample = dict[str, str]
_code_samples: dict[str, list[_RedocCodeSample]] = {}


def extend_schema(
    operation_id: str,
    code_samples: list[_RedocCodeSample] | None = None,
    **kwargs,
) -> Any:
    """Wrapper of drf_spectacular's extend schema that supports Redoc code samples."""

    if code_samples:
        _code_samples[operation_id] = code_samples

    return utils.extend_schema(operation_id=operation_id, **kwargs)


def postprocessing_hook(result: dict, **_) -> dict:
    """Hook that adds code samples to endpoints documentation in the OpenApi document"""

    for openapi_path in result["paths"].values():
        for openapi_operation in openapi_path.values():
            if json := _code_samples.get(openapi_operation["operationId"]):
                openapi_operation["x-codeSamples"] = json

    return result
