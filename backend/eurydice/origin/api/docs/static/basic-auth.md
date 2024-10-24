Eurydice accepts the [Basic authentication scheme](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).

Simply pass your credentials as a base64 encoded username/password pair through the [`Authorization`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization) header, the way basic auth works.

With curl, you may use the `-u` flag:

```bash
curl -u $EURYDICE_USERNAME:$EURYDICE_PASSWORD "https://$EURYDICE_ORIGIN_HOST/api/v1/transferables/"
```

[Unsafe requests](https://developer.mozilla.org/en-US/docs/Glossary/Safe/HTTP) also require you to specify the Referer (sic) header.

Example :
```bash
# Upload a transferable
curl -X "POST" \
  "https://$EURYDICE_ORIGIN_HOST" \
  -u $EURYDICE_USERNAME:$EURYDICE_PASSWORD \
  --request-target "/api/v1/transferables/" \
  -H "Referer: https://$EURYDICE_ORIGIN_HOST/" \
  -H "Accept: application/json" \
  -H "Content-Type: application/octet-stream" \
  -T my_file
```

For [safe requests](https://developer.mozilla.org/en-US/docs/Glossary/Safe/HTTP) (notably GET requests) you don't need the Referer. Example:

```bash
# List transferables
curl \
  "https://$EURYDICE_ORIGIN_HOST" \
  -u $EURYDICE_USERNAME:$EURYDICE_PASSWORD \
  --request-target "/api/v1/transferables/" \
  -H "Accept: application/json"
```
