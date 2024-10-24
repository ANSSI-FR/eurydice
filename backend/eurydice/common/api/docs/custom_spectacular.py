from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from drf_spectacular import utils

_RedocCodeSample = Dict[str, str]
_code_samples: Dict[str, List[_RedocCodeSample]] = {}


def extend_schema(
    operation_id: str,
    code_samples: Optional[List[_RedocCodeSample]] = None,
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
