Download the file corresponding to an incoming transferable.

The file is returned in the response body.
Its integrity is automatically checked so that it is theoretically impossible to retrieve a corrupted transferable.

During the initial transfer to Eurydice's origin API (`POST /api/v1/transferables/`), if HTTP headers starting with `Metadata-` were provided, they will be restored and returned by this endpoint in the response's HTTP headers.
