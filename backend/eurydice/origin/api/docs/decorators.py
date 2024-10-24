from datetime import datetime

import humanfriendly
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_spectacular import types
from drf_spectacular import utils as spectacular_utils
from rest_framework import exceptions as drf_exceptions
from rest_framework import status

from eurydice.common.api import serializers as common_serializers
from eurydice.common.api.docs import custom_spectacular
from eurydice.common.api.docs import utils as docs
from eurydice.origin.api import exceptions
from eurydice.origin.api import serializers

outgoing_transferable_example = {
    "id": "00002800-0000-1000-8000-00805f9b34fb",
    "created_at": "1969-12-28T14:15:22Z",
    "name": "name_on_destination_side.txt",
    "sha1": "31320896aedc8d3d1aaaee156be885ba0774da73",
    "size": 97,
    "user_provided_meta": {
        "Metadata-Folder": "/home/data/",
        "Metadata-Name": "name_on_destination_side.txt",
    },
    "submission_succeeded": True,
    "submission_succeeded_at": "1969-12-28T14:15:23Z",
    "state": "ONGOING",
    "progress": 43,
    "bytes_transferred": 42,
    "transfer_finished_at": "1969-12-28T14:16:42Z",
    "transfer_speed": 17891337,
    "transfer_estimated_finish_date": "1969-12-28T14:16:42Z",
}

outgoing_transferable = spectacular_utils.extend_schema_view(
    list=custom_spectacular.extend_schema(
        operation_id="list-transferables",
        summary=_("List outgoing transferables"),
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
            spectacular_utils.OpenApiParameter(
                name="submission_succeeded_after",
                description="Minimum submission success date within the result set.",
                type=datetime,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
            spectacular_utils.OpenApiParameter(
                name="submission_succeeded_before",
                description="Maximum submission success date within the result set.",
                type=datetime,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
            spectacular_utils.OpenApiParameter(
                name="transfer_finished_after",
                description="Minimum transfer finish date within the result set.",
                type=datetime,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
            spectacular_utils.OpenApiParameter(
                name="transfer_finished_before",
                description="Maximum transfer finish date within the result set.",
                type=datetime,
                location=spectacular_utils.OpenApiParameter.QUERY,
            ),
        ],
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                response=serializers.OutgoingTransferableSerializer(many=True),
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
                    "results": [outgoing_transferable_example],
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
                response=serializers.OutgoingTransferableSerializer,
                description=_(
                    "Information about the transferable was successfully retrieved."
                ),
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
            status.HTTP_404_NOT_FOUND: docs.NotFoundResponse,
        },
        examples=[
            spectacular_utils.OpenApiExample(
                name="Transfer state", value=outgoing_transferable_example
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
    create=custom_spectacular.extend_schema(
        operation_id="create-transferable",
        summary=_("Initiate a transfer"),
        description=_(
            (settings.DOCS_PATH / "create-transferable.md")
            .read_text()
            .format(
                TRANSFERABLE_MAX_SIZE=humanfriendly.format_size(
                    settings.TRANSFERABLE_MAX_SIZE,
                    binary=True,
                )
            )
        ),
        request={"application/octet-stream": types.OpenApiTypes.BINARY},
        parameters=[
            spectacular_utils.OpenApiParameter(
                name=f"{settings.METADATA_HEADER_PREFIX}Name",
                type=str,
                location=spectacular_utils.OpenApiParameter.HEADER,
                required=False,
                description=_("Optional file name."),
            ),
            spectacular_utils.OpenApiParameter(
                name=f"{settings.METADATA_HEADER_PREFIX}*",
                type=str,
                location=spectacular_utils.OpenApiParameter.HEADER,
                required=False,
                description=_(
                    "Optional additional file metadata. Any header prefixed with "
                    f"`{settings.METADATA_HEADER_PREFIX}` will be restored on the "
                    f"destination."
                ),
            ),
        ],
        responses={
            status.HTTP_201_CREATED: spectacular_utils.OpenApiResponse(
                description=_(
                    "This response is returned with the uploaded Transferable's "
                    "metadata when it has successfully been created."
                ),
                response=serializers.OutgoingTransferableSerializer,
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
            status.HTTP_400_BAD_REQUEST: docs.create_open_api_response(
                exceptions.MissingContentTypeError
            ),
            # workaround to be able to have multiple responses for one status code
            f"{status.HTTP_400_BAD_REQUEST} ": docs.create_open_api_response(
                exceptions.InconsistentContentLengthError
            ),
            # workaround to be able to have multiple responses for one status code
            f"{status.HTTP_400_BAD_REQUEST}  ": docs.create_open_api_response(
                exceptions.InvalidContentLengthError
            ),
            f"{status.HTTP_400_BAD_REQUEST} ": docs.create_open_api_response(
                exceptions.TransferableNotSuccessfullySubmittedError
            ),
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: docs.create_open_api_response(
                exceptions.RequestEntityTooLargeError
            ),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: docs.create_open_api_response(
                drf_exceptions.UnsupportedMediaType
            ),
        },
        examples=[
            spectacular_utils.OpenApiExample(
                name="Transfer state", value=outgoing_transferable_example
            )
        ],
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (settings.DOCS_PATH / "create-transferable.sh").read_text(),
            },
            {
                "lang": "bash",
                "label": "Bash Function",
                "source": (
                    settings.DOCS_PATH / "create-transferable-func.sh"
                ).read_text(),
            },
        ],
        tags=[_("Transferring files")],
    ),
    destroy=custom_spectacular.extend_schema(
        operation_id="revoke-transferable",
        summary=_("Cancel a transfer"),
        description=_((settings.DOCS_PATH / "revoke-transferable.md").read_text()),
        responses={
            status.HTTP_204_NO_CONTENT: spectacular_utils.OpenApiResponse(
                description=_("The transferable was successfully revoked."),
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
            status.HTTP_404_NOT_FOUND: docs.NotFoundResponse,
        },
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (settings.DOCS_PATH / "revoke-transferable.sh").read_text(),
            }
        ],
        tags=[_("Transferring files")],
    ),
)

user_association = spectacular_utils.extend_schema_view(
    get=custom_spectacular.extend_schema(
        operation_id="associate-users",
        summary=_("Link two user accounts"),
        description=_((settings.DOCS_PATH / "link-user-accounts.md").read_text()),
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                description=_("An association token has successfully been created."),
                response=common_serializers.AssociationTokenSerializer,
                examples=[
                    spectacular_utils.OpenApiExample(
                        _("Generate association token"),
                        description=_(
                            "The response body will respect this format (the "
                            "expiration date is provided for information purposes only)"
                        ),
                        value={
                            "token": (
                                "BIENAYME aggraver juteuse deferer AZOIQUE inavouee "
                                "COUQUE mixte chaton PERIPATE exaucant fourgue pastis "
                                "ayuthia FONDIS prostre HALLE TAVAUX"
                            ),
                            "expires_at": "2021-07-02T09:59:57Z",
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
                            "pending_transferables": 8,
                            "ongoing_transferables": 3,
                            "recent_successes": 14,
                            "recent_errors": 0,
                            "last_packet_sent_at": "2023-09-12T16:03:57.217694+02:00",
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

sender_status = spectacular_utils.extend_schema_view(
    get=custom_spectacular.extend_schema(
        operation_id="get-status",
        summary=_("Get sender status"),
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                response=serializers.StatusSerializer,
                examples=[
                    spectacular_utils.OpenApiExample(
                        _("Get sender status"),
                        value={
                            "maintenance": False,
                            "last_packet_sent_at": "2023-07-24T12:39:23.320950Z",
                        },
                    ),
                ],
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
        },
        tags=[_("Administration")],
    )
)

__all__ = (
    "sender_status",
    "metrics",
    "outgoing_transferable",
    "user_association",
)
