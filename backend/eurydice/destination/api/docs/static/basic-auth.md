Eurydice accepts the [Basic authentication scheme](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).

Simply pass your credentials as a base64 encoded username/password pair through the [`Authorization`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization) header.

With curl, you may use the `-u` flag:

```bash
curl -u $EURYDICE_USERNAME:$EURYDICE_PASSWORD "https://$EURYDICE_DESTINATION_HOST/api/v1/transferables/"
```

[Unsafe requests](https://developer.mozilla.org/en-US/docs/Glossary/Safe/HTTP) also require you to specify the Referer (sic) header.

Example :

```bash
# Delete transferable with id TRANSFERABLE_ID
curl -X "DELETE" \
  "https://$EURYDICE_DESTINATION_HOST/api/v1/transferables/$TRANSFERABLE_ID/" \
  -u $EURYDICE_USERNAME:$EURYDICE_PASSWORD \
  -H "Referer: https://$EURYDICE_DESTINATION_HOST/"
```

For [safe requests](https://developer.mozilla.org/en-US/docs/Glossary/Safe/HTTP) (notably GET requests) you don't need the Referer . Example:

```bash
# List transferables
curl \
  "https://$EURYDICE_DESTINATION_HOST" \
  -u $EURYDICE_USERNAME:$EURYDICE_PASSWORD \
  --request-target "/api/v1/transferables/" \
  -H "Accept: application/json"
```
