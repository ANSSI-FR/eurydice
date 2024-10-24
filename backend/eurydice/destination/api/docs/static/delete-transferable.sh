# Replace {id} with your transferable's ID, without the braces
curl -X "DELETE" \
  "https://$EURYDICE_DESTINATION_HOST/api/v1/transferables/{id}/" \
  -H "Authorization: Token $EURYDICE_DESTINATION_AUTHTOKEN"
