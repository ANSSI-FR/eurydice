This is the preferred way to authenticate.

1. Make a GET request to api/v1/user/login/ to obtain a session cookie. How to authenticate to api/v1/user/login/ depends on your reverse proxy configuration.

For example, if it's configured to use Kerberos, you need a valid Kerberos ticket, then you can use curl's `--negotiate -u :` option.

```bash
# This will output eurydice_sessionid and eurydice_csrftoken which you will need for the next step.
curl -c - -L --negotiate -u : "https://$EURYDICE_ORIGIN_HOST/api/v1/user/login/" -H "Accept: application/json"
```

2. Send eurydice_sessionid together with eurydice_csrftoken to authenticate subsequent requests. You also need to specify the Referer (sic) header.

Example :
```bash
# Upload a transferable
curl -X "POST" \
  "https://$EURYDICE_ORIGIN_HOST" \
  --cookie "eurydice_sessionid=$SESSION_ID; eurydice_csrftoken=$CSRF_TOKEN" \
  --request-target "/api/v1/transferables/" \
  -H "Referer: https://$EURYDICE_ORIGIN_HOST/" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/octet-stream" \
  -T my_file
```

For [safe requests](https://developer.mozilla.org/en-US/docs/Glossary/Safe/HTTP) (notably GET requests) you don't need the Referer or the CSRF token. Example:

```bash
# List transferables
curl \
  "https://$EURYDICE_ORIGIN_HOST" \
  --cookie "eurydice_sessionid=$SESSION_ID" \
  --request-target "/api/v1/transferables/" \
  -H "Accept: application/json"
```