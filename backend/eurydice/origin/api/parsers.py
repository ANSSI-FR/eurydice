from rest_framework import parsers


class OctetStreamParser(parsers.BaseParser):
    """
    DRF parser class for handling raw octet-stream file uploads
    """

    media_type = "application/octet-stream"

    def parse(
        self,
        stream,
        media_type=None,
        parser_context=None,  # noqa: ANN001
    ):  # noqa: ANN201
        """
        NOTE: This is not actually used by the OutgoingTransferable creation view
              because it accesses the HTTP body stream directly not through request.data
              so we don't return anything
        """
        pass  # pragma: no cover
