curl -c - -L --negotiate -u : \
  "https://$EURYDICE_DESTINATION_HOST/api/v1/user/login/" \
  -H "Accept: application/json"
