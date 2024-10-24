To transfer files using Eurydice, you first need to get a user account both on the origin and on the destination side.
To obtain them, contact your local friendly system administrators, they will create the required accounts and communicate to you the credentials.

Once this is done, you need to associate your user account located on the origin side with the one on the destination side. As the link between the origin and the destination networks is one way, this process must be performed manually to guarantee its success.

Proceed as follow :

- On the origin side, generate an association token :

```bash
curl -X 'GET'
'https://$EURYDICE_ORIGIN_HOST/api/v1/user/association/' \\
  -H 'accept: application/json' \\
  -H 'Authorization: Token $EURYDICE_ORIGIN_AUTHTOKEN'
```

- The response holds the association token in the form of a sequence of words, together with its expiration date:

```json
{
  "token": "infante SOIN BARBEAU agvin MARBRES AUXERRE JABOT LECHEUR rythme mascara FUN OESTRAUX ABJURANT sobriete APANAGE BEVATRON bufflant GLOSER",
  "expires_at": "2021-06-29T13:57:33Z"
}
```

- Take good note of the words of the token.

- Then, on the destination-side API, submit the association token obtained from the origin API (for instance using the cURL snippet provided for this request).

The server should reply with the 204 HTTP code, meaning that the user account on the destination side was successfully associated with the one on the origin side.
If you had already transferred files before the association, they should now appear on the destination side.
