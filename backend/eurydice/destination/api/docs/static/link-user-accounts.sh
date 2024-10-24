curl -X "POST" \
  "https://$EURYDICE_DESTINATION_HOST/api/v1/user/association/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $EURYDICE_DESTINATION_AUTHTOKEN" \
  -d '{ "token": "case SENSITIVE association TOKEN here" }'
