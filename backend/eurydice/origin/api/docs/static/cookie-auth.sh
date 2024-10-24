curl -c - -L --negotiate -u : \
  "https://$EURYDICE_ORIGIN_HOST/api/v1/user/login/" \
  -H "Accept: application/json"
