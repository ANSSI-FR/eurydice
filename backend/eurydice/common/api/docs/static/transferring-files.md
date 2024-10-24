This section lists all transfer-related requests. In Eurydice, files that are meant to be transferred through the diode are called **Transferables**.

On the origin API, you can list, check, and create _outgoing transferables_, whereas on the destination API, you deal with _incoming transferables_.
Keep in mind, these are just files before and after their _transfer_ through the diode.

A file transfer usually goes like this:

- On the **origin-side** API :

  - you can check if you have transfers still in progress with `GET /api/v1/transferables/`;
  - you send the transferable through `POST /api/v1/transferables/`;
  - you follow the progress of your transfer with `GET /api/v1/transferables/{id}/`.

- On the **destination-side** API :

  - you list transferables recently received and check their status with `GET /api/v1/transferables/`;
  - if you already knew the ID of your transferable, you could have used `GET /api/v1/transferables/{id}/`;
  - you retrieve the transferable with `GET /api/v1/transferables/{id}/download/`;
  - you delete the transferable with `DELETE /api/v1/transferables/{id}/`.

**Deleting transferables after retrieving them is recommended**, especially if they are large (> 100MB): it saves up space for other users as well as for your future transfers.
Please note that Eurydice does not allow for long-term file storage. Transferred files are automatically deleted after a period of time.
Nonetheless, manual deletion is recommended to prevent congestion.
