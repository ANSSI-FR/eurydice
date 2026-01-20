from rest_framework import negotiation


class IgnoreClientContentNegotiation(negotiation.BaseContentNegotiation):
    """DRF content negotiation configuration to ignore content negotiation ;)"""

    def select_renderer(
        self,
        request,
        renderers,
        format_suffix=None,  # noqa: ANN001
    ):  # noqa: ANN201
        """
        Select the first renderer in the `.renderer_classes` list.
        """
        return (renderers[0], renderers[0].media_type)
