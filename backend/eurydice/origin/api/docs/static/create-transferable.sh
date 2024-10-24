curl -X "POST" \
  "https://$EURYDICE_ORIGIN_HOST" \
  --request-target "/api/v1/transferables/" \
  -H "Accept: application/json" \
  -H "Authorization: Token $EURYDICE_ORIGIN_AUTHTOKEN" \
  -H "Content-Type: application/octet-stream" \
  -H "Metadata-Name: name_on_destination_side.txt" \
  -H "Metadata-Folder: /home/data/" \
  -T file_to_transfer.txt
