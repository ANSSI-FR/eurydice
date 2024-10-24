# Replace {id} with your transferable's ID, without the braces
curl "https://$EURYDICE_DESTINATION_HOST/api/v1/transferables/{id}/" \
  -H "Accept: application/json" \
  -H "Authorization: Token $EURYDICE_DESTINATION_AUTHTOKEN"
