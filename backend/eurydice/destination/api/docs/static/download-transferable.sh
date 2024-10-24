# Replace {id} with your transferable's ID, without the braces
curl "https://$EURYDICE_DESTINATION_HOST/api/v1/transferables/{id}/download/" \
  -H "Accept: application/octet-stream" \
  -H "Authorization: Token $EURYDICE_DESTINATION_AUTHTOKEN" \
  -o transferred_file.txt
