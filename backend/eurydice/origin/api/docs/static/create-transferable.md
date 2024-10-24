You can send a new transferable through the network diode with this endpoint by uploading its binary content in the POST requests' body.
You can submit the file together with some metadata items, as described below.

HTTP headers starting with `Metadata-` are special when sent to this endpoint: they allow for the registration of metadata items that will be forwarded through the diode and can be retrieved on the destination side as response headers.
Among them, the header Metadata-Name is used to set the name of the file to transfer.

⚠️ **Warning:** HTTP headers only support a restricted set of characters.
To avoid running into unexpected issues, please use `base64` to transport arbitrary data.

⚠️ **Warning:** The maximum size allowed for a single file is {TRANSFERABLE_MAX_SIZE}.
If a POST request's body is greater than this limit, the server replies with a 413 HTTP code.

If you want your filenames to respect the HTTP headers format, but still want to be able to read them (and display them properly in the Eurydice's web application), please use URL encoding instead of base64 (`urllib.parse.quote`/`urllib.parse.unquote` functions in Python).
