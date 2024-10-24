curl "https://$EURYDICE_DESTINATION_HOST/api/v1/user/me/" \
  -H "Accept: application/json" \
  -H "Authorization: Token $EURYDICE_DESTINATION_AUTHTOKEN"
