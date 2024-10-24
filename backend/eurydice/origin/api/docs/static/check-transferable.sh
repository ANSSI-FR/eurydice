# Replace {id} with your transferable's ID, without the braces
curl "https://$EURYDICE_ORIGIN_HOST/api/v1/transferables/{id}/" \
  -H "Accept: application/json" \
  -H "Authorization: Token $EURYDICE_ORIGIN_AUTHTOKEN"
