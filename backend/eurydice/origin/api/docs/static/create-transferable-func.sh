function send_file {
  function encodebasename {
    python3 \
    -c "import sys, urllib.parse; \
      print(urllib.parse.quote(sys.argv[1]))" \
    "$(basename "$1")"
  }
  curl -X "POST" \
    "https://$EURYDICE_ORIGIN_HOST" \
    --request-target "/api/v1/transferables/" \
    -H "Accept: application/json" \
    -H "Authorization: Token $EURYDICE_ORIGIN_AUTHTOKEN" \
    -H "Content-Type: application/octet-stream" \
    -H "Metadata-Name: $(encodebasename "$1")" \
    -T "$1"
} && echo "Usage: send_file FILE"
