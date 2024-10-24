This method of authentication is intended for non human users (scripts, software etc...) only.

Auth tokens are typically given to service accounts, and created by administrators. If you need to access the API using an auth token, ask an administrator.

You'll have to prefix your token in the HTTP header with the keyword `Token` like so: `Authorization: Token dcd98b7102dd2f0e8b11d0f600bfb0c093`

Example:

```bash
# Delete transferable with id TRANSFERABLE_ID
curl -X "DELETE" \
  "https://$EURYDICE_DESTINATION_HOST/api/v1/transferables/$TRANSFERABLE_ID/" \
  -H "Accept: application/json" \
  -H "Authorization: Token $EURYDICE_ORIGIN_AUTHTOKEN"
```
