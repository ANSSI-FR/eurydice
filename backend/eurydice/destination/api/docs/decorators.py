from datetime import datetime

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_spectacular import types
from drf_spectacular import utils as spectacular_utils
from rest_framework import status

from eurydice.common.api import serializers as common_serializers
from eurydice.common.api.docs import custom_spectacular
from eurydice.common.api.docs import utils as docs
from eurydice.destination.api import exceptions
from eurydice.destination.api import serializers

incoming_transferable_example = {
    "id": "00002800-0000-1000-8000-00805f9b34fb",
    "created_at": "1969-12-28T14:15:22Z",
    "name": "name_on_destination_side.txt",
    "sha1": "31320896aedc8d3d1aaaee156be885ba0774da73",
    "size": 97,
    "user_provided_meta": {
        "Metadata-Folder": "/home/data/",
        "Metadata-Name": "name_on_destination_side.txt",
    },
    "state": "ONGOING",
    "progress": 43,
    "finished_at": "1969-12-28T14:16:42Z",
    "expires_at": "1970-01-04T14:16:42Z",
    "bytes_received": 42,
}

incoming_transferable = spectacular_utils.extend_schema_view(
    list=custom_spectacular.extend_schema(
        operation_id="list-transferables",
        summary=_("List incoming transferables"),
        description=_((settings.DOCS_PATH / "list-transferables.md").read_text()),
        parameters=[
            spectacular_utils.OpenApiParameter(
                name="created_after",
                description="Minimum creation date within the result set.",
                type=datetime,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
            spectacular_utils.OpenApiParameter(
                name="created_before",
                description="Maximum creation date within the result set.",
                type=datetime,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
            spectacular_utils.OpenApiParameter(
                name="finished_after",
                description=(
                    "Minimum finish date within the result set. The finish date "
                    "is when the transferable first became ready to download."
                ),
                type=datetime,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
            spectacular_utils.OpenApiParameter(
                name="finished_before",
                description=(
                    "Maximum finish date within the result set. The finish date "
                    "is when the transferable first became ready to download."
                ),
                type=datetime,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
            spectacular_utils.OpenApiParameter(
                name="name",
                description=(
                    "The name (or a part of the name, for instance '.txt') to "
                    "filter on."
                ),
                type=str,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
            spectacular_utils.OpenApiParameter(
                name="sha1",
                description="The SHA1 to filter on, hexadecimal format.",
                type=str,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
        ],
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                response=serializers.IncomingTransferableSerializer(many=True),
                description=_("The list of transferables was successfully created."),
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
        },
        examples=[
            spectacular_utils.OpenApiExample(
                name="Transfer state",
                value={
                    "offset": 0,
                    "count": 1,
                    "new_items": False,
                    "pages": {
                        "previous": "ksRFmM6Mkw_DzwF=",
                        "current": "ksRFmM6Mkw_Dzw1=",
                        "next": "ksRFmM6Mkw_DzwQ=",
                    },
                    "paginated_at": "2021-02-01 14:10:01+00:00",
                    "results": [incoming_transferable_example],
                },
            )
        ],
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (settings.DOCS_PATH / "list-transferables.sh").read_text(),
            }
        ],
        tags=[_("Transferring files")],
    ),
    retrieve=custom_spectacular.extend_schema(
        operation_id="check-transferable",
        summary=_("Check a transfer's state"),
        description=_((settings.DOCS_PATH / "check-transferable.md").read_text()),
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                response=serializers.IncomingTransferableSerializer,
                description=_(
                    "Information about the transferable was successfully retrieved."
                ),
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
            status.HTTP_404_NOT_FOUND: docs.NotFoundResponse,
        },
        examples=[
            spectacular_utils.OpenApiExample(
                name="Transferable", value=incoming_transferable_example
            )
        ],
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (settings.DOCS_PATH / "check-transferable.sh").read_text(),
            }
        ],
        tags=[_("Transferring files")],
    ),
    destroy=custom_spectacular.extend_schema(
        operation_id="delete-transferable",
        summary=_("Delete a transferable"),
        description=_((settings.DOCS_PATH / "delete-transferable.md").read_text()),
        responses={
            status.HTTP_204_NO_CONTENT: spectacular_utils.OpenApiResponse(
                description=_(
                    "The transferable was removed from Eurydice destination storage."
                    "There is no response body."
                ),
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
            status.HTTP_404_NOT_FOUND: docs.NotFoundResponse,
            status.HTTP_409_CONFLICT: docs.create_open_api_response(
                exceptions.UnsuccessfulTransferableError
            ),
        },
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (settings.DOCS_PATH / "delete-transferable.sh").read_text(),
            }
        ],
        tags=[_("Transferring files")],
    ),
    delete=custom_spectacular.extend_schema(
        operation_id="delete-all-transferable",
        summary=_("Delete all transferables"),
        description=_((settings.DOCS_PATH / "delete-all-transferables.md").read_text()),
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                description=_("No transferable data remains on the storage"),
                response=types.OpenApiTypes.STR,
                examples=[
                    spectacular_utils.OpenApiExample(
                        _("No file to remove"),
                        value={
                            "response": "Aucun fichier n'a été supprimé",
                        },
                    ),
                    spectacular_utils.OpenApiExample(
                        _("1 file to remove"),
                        value={
                            "response": "1 fichier a été supprimé",
                        },
                    ),
                    spectacular_utils.OpenApiExample(
                        _("Multiple files to remove"),
                        value={
                            "response": "2 fichiers ont été supprimés",
                        },
                    ),
                ],
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
            status.HTTP_404_NOT_FOUND: docs.NotFoundResponse,
            status.HTTP_409_CONFLICT: docs.create_open_api_response(
                exceptions.UnsuccessfulTransferableError
            ),
        },
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (
                    settings.DOCS_PATH / "delete-all-transferables.sh"
                ).read_text(),
            }
        ],
        tags=[_("Transferring files")],
    ),
    download=custom_spectacular.extend_schema(
        operation_id="download-transferable",
        summary=_("Retrieve a transferable"),
        description=_((settings.DOCS_PATH / "download-transferable.md").read_text()),
        responses={
            (
                status.HTTP_200_OK,
                "application/octet-stream",
            ): spectacular_utils.OpenApiResponse(
                response=types.OpenApiTypes.BINARY,
                description=_(
                    "The transferable was successfully retrieved and is returned in "
                    "the response body."
                ),
            ),
            (
                status.HTTP_401_UNAUTHORIZED,
                "application/json",
            ): docs.NotAuthenticatedResponse,
            (
                status.HTTP_403_FORBIDDEN,
                "application/json",
            ): docs.create_open_api_response(exceptions.TransferableErroredError),
            (
                status.HTTP_404_NOT_FOUND,
                "application/json",
            ): docs.NotFoundResponse,
            (
                status.HTTP_409_CONFLICT,
                "application/json",
            ): docs.create_open_api_response(exceptions.TransferableOngoingError),
            (
                status.HTTP_410_GONE,
                "application/json",
            ): docs.create_open_api_response(exceptions.TransferableExpiredError),
            # Converting the status code to a string with an extra whitespace is a hack
            # to be able to have multiple responses for one status code
            (
                f"{status.HTTP_410_GONE} ",
                "application/json",
            ): docs.create_open_api_response(exceptions.TransferableRevokedError),
        },
        parameters=[
            # Hide the format query parameter, user should not be able to use it
            spectacular_utils.OpenApiParameter(
                name="format",
                location=spectacular_utils.OpenApiParameter.QUERY,
                exclude=True,
            ),
            spectacular_utils.OpenApiParameter(
                name="Content-Length",
                description="The size of the body, in bytes.",
                type=str,
                location=spectacular_utils.OpenApiParameter.HEADER,
                response=[status.HTTP_200_OK],
            ),
            spectacular_utils.OpenApiParameter(
                name="Digest",
                description="A SHA-1 digest of the requested file.",
                type=str,
                location=spectacular_utils.OpenApiParameter.HEADER,
                response=[status.HTTP_200_OK],
            ),
            spectacular_utils.OpenApiParameter(
                name=f"{settings.METADATA_HEADER_PREFIX}*",
                description=(
                    "Optional file metadata provided as HTTP headers "
                    "when submitting the file."
                ),
                type=str,
                location=spectacular_utils.OpenApiParameter.HEADER,
                response=[status.HTTP_200_OK],
            ),
        ],
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (settings.DOCS_PATH / "download-transferable.sh").read_text(),
            }
        ],
        tags=[_("Transferring files")],
    ),
)

user_association = spectacular_utils.extend_schema_view(
    post=custom_spectacular.extend_schema(
        operation_id="associate-users",
        summary=_("Link two user accounts"),
        description=_((settings.DOCS_PATH / "link-user-accounts.md").read_text()),
        request=common_serializers.AssociationTokenSerializer,
        examples=[
            spectacular_utils.OpenApiExample(
                _("Submit association token"),
                description=_("The body of the request should respect this format:"),
                value={
                    "token": (
                        "BIENAYME aggraver juteuse deferer AZOIQUE inavouee COUQUE "
                        "mixte chaton PERIPATE exaucant fourgue pastis ayuthia "
                        "FONDIS prostre HALLE TAVAUX"
                    )
                },
            ),
        ],
        responses={
            status.HTTP_204_NO_CONTENT: spectacular_utils.OpenApiResponse(
                description=_("The users have been successfully associated."),
            ),
            status.HTTP_400_BAD_REQUEST: docs.ValidationErrorResponse,
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
            status.HTTP_409_CONFLICT: docs.create_open_api_response(
                exceptions.AlreadyAssociatedError
            ),
        },
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (settings.DOCS_PATH / "link-user-accounts.sh").read_text(),
            }
        ],
        tags=[_("Account management")],
    )
)

metrics = spectacular_utils.extend_schema_view(
    get=custom_spectacular.extend_schema(
        operation_id="check-rolling-metrics",
        summary=_("Access rolling metrics"),
        description=_((settings.DOCS_PATH / "check-rolling-metrics.md").read_text()),
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                description=_("Rolling metrics have successfully been created."),
                response=serializers.RollingMetricsSerializer,
                examples=[
                    spectacular_utils.OpenApiExample(
                        _("Read metrics"),
                        value={
                            "ongoing_transferables": 3,
                            "recent_successes": 14,
                            "recent_errors": 0,
                            "last_packet_received_at": (
                                "2023-09-12T16:03:57.217694+02:00"
                            ),
                        },
                    ),
                ],
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
        },
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (settings.DOCS_PATH / "check-rolling-metrics.sh").read_text(),
            }
        ],
        tags=[_("Administration")],
    )
)

receiver_status = spectacular_utils.extend_schema_view(
    get=custom_spectacular.extend_schema(
        operation_id="get-status",
        summary=_("Get receiver status"),
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                response=serializers.StatusSerializer,
                examples=[
                    spectacular_utils.OpenApiExample(
                        _("Get receiver status"),
                        value={
                            "last_packet_received_at": "2023-07-24T12:39:23.320950Z",
                        },
                    ),
                ],
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
        },
        tags=[_("Administration")],
    )
)


__all__ = ("incoming_transferable", "metrics", "user_association")
