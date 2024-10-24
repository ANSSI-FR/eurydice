from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List

from django.utils.encoding import force_str
from rest_framework.response import Response
from rest_framework.views import APIView

from eurydice.common.api.pagination.core import EurydiceSessionPaginationWithoutOpenapi


class EurydiceSessionPagination(EurydiceSessionPaginationWithoutOpenapi):
    """Custom pagination class, optimized for performances."""

    def get_paginated_response(self, data: List) -> Response:
        """Build the API response that will be forwarded to the user."""

        return Response(
            OrderedDict(
                [
                    ("offset", (self.query.queried_page - 1) * (self.page_size or 1)),
                    ("count", self.items_count),
                    ("new_items", self.new_items),
                    ("pages", self.page_identifiers),
                    ("paginated_at", self.paginated_at),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Add the custom fields to the parent's openapi description."""

        return {
            "type": "object",
            "properties": {
                "offset": {"type": "integer", "nullable": False, "minimum": 0},
                "count": {
                    "type": "integer",
                    "nullable": False,
                    "minimum": 0,
                    "example": 1,
                },
                "new_items": {"type": "boolean", "nullable": False, "example": False},
                "pages": {
                    "type": "object",
                    "nullable": False,
                    "properties": {
                        "previous": {
                            "type": "string",
                            "nullable": True,
                            "format": "byte",
                        },
                        "current": {
                            "type": "string",
                            "nullable": True,
                            "format": "byte",
                        },
                        "next": {
                            "type": "string",
                            "nullable": True,
                            "format": "byte",
                        },
                    },
                },
                "paginated_at": {
                    "type": "string",
                    "nullable": False,
                    "format": "date-time",
                },
                "results": schema,
            },
        }

    def get_schema_operation_parameters(self, _: APIView) -> List[Dict[str, Any]]:
        """Add the custom query parameters to the parent's openapi description."""

        return [
            {
                "name": self.page_size_query_param,
                "required": False,
                "in": "query",
                "description": force_str(self.page_size_query_description),
                "schema": {"type": "integer", "minimum": 1},
            },
            {
                "name": self.page_query_param,
                "required": False,
                "in": "query",
                "description": force_str(self.page_query_description),
                "schema": {"type": "string", "format": "byte"},
            },
            {
                "name": self.from_query_param,
                "required": False,
                "in": "query",
                "description": force_str(self.from_query_description),
                "schema": {"type": "string", "format": "byte"},
            },
            {
                "name": self.delta_query_param,
                "required": False,
                "in": "query",
                "description": force_str(self.delta_query_description),
                "schema": {"type": "integer"},
            },
        ]

    def get_schema_fields(self, _: APIView):  # noqa: ANN201
        """Add the custom query parameters to the parent's coreapi description."""

        raise NotImplementedError
