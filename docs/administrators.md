# 🚀 Deployment in production and administration

Instructions to deploy Eurydice manually are available below.

## 👷‍♀️ Manual deployment with docker compose

- `compose.yml` allows for launching a local development environment
  - ```bash
    docker compose up -d
    ```
- `compose.prod.yml` allows for launching the origin or destination production stack

  1.  Configure the environment variables ([more details below](#️-environment-variables))
  2.  Create the directories configured in the environment variables
  3.  Set permissions to allow read/write access to these directories for the UID configured in the environment variables

  **If you don't need elk logging:**

  4.  Configure the database by applying the migrations:
      - Origin:
        ```bash
        docker compose -f compose.prod.yml --profile origin run --rm db-migrations-origin
        ```
      - Destination (on another machine):
        ```bash
        docker compose -f compose.prod.yml --profile destination run --rm db-migrations-destination
        ```
  5.  Launch the stack:

      - Origin:
        ```bash
        docker compose -f compose.prod.yml --profile origin up -d
        ```
      - Destination (on another machine):
        ```bash
        docker compose -f compose.prod.yml --profile destination up -d
        ```

  **If you want elk logging:**

  4.  Configure the database by applying the migrations:
      - Origin:
        ```bash
        docker compose -f compose.prod.yml --profile origin-with-elk-logging run --rm db-migrations-origin-with-elk
        ```
      - Destination (on another machine):
        ```bash
        docker compose -f compose.prod.yml --profile destination-with-elk-logging run --rm db-migrations-destination-with-elk
        ```
  5.  Launch the stack:

      - Origin:
        ```bash
        docker compose -f compose.prod.yml --profile origin-with-elk-logging up -d
        ```
      - Destination (on another machine):
        ```bash
        docker compose -f compose.prod.yml --profile destination-with-elk-logging up -d
        ```
      - Note: Additional environment variables are needed: see the list below. You will need an API key:
        [more details below](#elasticsearch-api-key).

  **Optional admin user**

  6.  (optional) Create an administrator user for accessing the admin interface at `/admin` (default credentials are admin/admin)
      - Origin:
        ```bash
        docker compose -f compose.prod.yml exec backend-origin make superuser
        ```
      - Destination (on another machine):
        ```bash
        docker compose -f compose.prod.yml exec backend-destination make superuser
        ```

## ⚙️ Environment Variables

The `.env` file should be placed in the directory from which you are running `docker compose` (usually next to the `compose.yml` file).
You can also name the file as you wish [and point compose to it using the `--env-file` flag](https://docs.docker.com/compose/environment-variables/#using-the---env-file--option).

The following environment variables should be configured for the deployment (variables without a default value are mandatory):

| Variable                                    | Default value                            | Description                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EURYDICE_VERSION`                          | `latest`                                 | Tag for the Eurydice docker image ([list of tags](https://github.com/ANSSI-FR/eurydice/tags))                                                                                                                                                                                                                    |
| `LIDI_VERSION`                              | `latest`                                 | Tag for the lidis/r docker images ([list of tags](https://github.com/ANSSI-FR/lidi/tags))                                                                                                                                                                                                                        |
| `LOCAL_DOCKER_REGISTRY`                     |                                          | Docker image registry: hostname of the registry that hosts Docker images for eurydice and lidi                                                                                                                                                                                                                   |
| `REMOTE_DOCKER_REGISTRY`                    | `docker.io`                              | Docker image registry: hostname for other docker images (e.g. https://hub.docker.com/)                                                                                                                                                                                                                           |
| `PUID`                                       | `1000`                                   | Numeric identifier to the user under which the services of will run                                                                                                                                                                                                                                              |
| `PGID`                                       | `1000`                                   | Numeric identifier for the group under which the services will run                                                                                                                                                                                                                                               |
| `GUNICORN_CONFIGURATION`                    | `""`                                     | Gunicorn commandline arguments                                                                                                                                                                                                                                                                                   |
| `EURYDICE_IPV4_SUBNET`                      | `172.18.0.0/24`                          | Range of IP addresses that will be assigned to containers within the eurydice network                                                                                                                                                                                                                            |
| `BACKEND_HOSTNAMES`                         | `localhost`                              | Hostname(s) for the backend API separated by a comma: `,`                                                                                                                                                                                                                                                        |
| `CSRF_TRUSTED_ORIGINS`                      | `""`                                     | Additionnal origin(s) for CSRF validation, separated by a comma: `,`. SEE [Django documentation](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins) Must include scheme ("http://", "https://") . May be left empty.                                                                      |
| `FRONTEND_HOSTNAMES`                        | `localhost`                              | Hostname(s) for the frontend UI separated by a space: ` `                                                                                                                                                                                                                                                        |
| `KIBANA_HOSTNAME`                           | `localhost`                              | Hostname for the Kibana UI.                                                                                                                                                                                                                                                                                      |
| `LIDIR_HOST`                                | `0.0.0.0`(lidir)                         | Lidir hostname                                                                                                                                                                                                                                                                                                   |
| `LIDIR_PORT`                                | `11011`                                  | Lidir port number                                                                                                                                                                                                                                                                                                |
| `LIDI_UDP_MTU`                              | `1500`                                   | Value for lidi option `--from_udp_mtu` (see https://github.com/ANSSI-FR/lidi/blob/master/doc/parameters.rst#block-and-packet-sizes)                                                                                                                                                                              |
| `LIDI_ENCODING_BLOCK_SIZE`                  | `60000`                                  | Value for lidi option `--encoding_block_size` (see https://github.com/ANSSI-FR/lidi/blob/master/doc/parameters.rst#block-and-packet-sizes)                                                                                                                                                                       |
| `LIDI_REPAIR_BLOCK_SIZE`                    | `6000`                                   | Value for lidi option `--repair_block_size` (see https://github.com/ANSSI-FR/lidi/blob/master/doc/parameters.rst#block-and-packet-sizes)                                                                                                                                                                         |
| `LIDIS_DOCKER_HOST`                         | `0.0.0.0`(lidis), `host-gateway`(sender) | Host interface on which lidis will listen and to which the sender will connect                                                                                                                                                                                                                                   |
| `MINIO_ENABLED`                             | `true`                                   | Enables usage of minio. If minio is disabled, eurydice will store transferable data on the filesystem. See `TRANSFERABLE_STORAGE_DIR` and `MINIO_ENDPOINT`. **Disabling minio and using the filesystem is only supported on the destination side.**                                                              |
| `TRANSFERABLE_STORAGE_DIR`                  |                                          | Host path to the directory containing transferable data, if minio is disabled data                                                                                                                                                                                                                               |
| `MINIO_ENDPOINT`                            | `minio:9000`                             | Hostname and port of the s3 storage server. By default, uses the minio container embedded in the compose stack                                                                                                                                                                                                   |
| `MINIO_DATA_DIR`                            |                                          | Host path to the directory containing minio data                                                                                                                                                                                                                                                                 |
| `MINIO_CONF_DIR`                            |                                          | Host path to the directory containing the minio configuration                                                                                                                                                                                                                                                    |
| `DB_DATA_DIR`                               |                                          | Host path to the directory containing the database's data                                                                                                                                                                                                                                                        |
| `LOG_LEVEL`                                 | `INFO`                                   | Django and Eurydice Log Level                                                                                                                                                                                                                                                                                    |
| `LOG_TO_FILE`                               | `true`                                   | If true, python processes will configure their logger to log into json files. See `PYTHON_LOGS_DIR` .                                                                                                                                                                                                            |
| `PYTHON_LOGS_DIR`                           |                                          | Host path to the directory containing python logs. Each service will write into their own sub-directory, as such: `${PYTHON_LOGS_DIR}/sender-logs/log.json`                                                                                                                                                      |
| `RUST_LOG`                                  | See compose.prod.yml                     | Rust log level (i.e. Lidi log level)                                                                                                                                                                                                                                                                             |
| `DB_LOGS_DIR`                               |                                          | Host path to the directory containing the database's logs                                                                                                                                                                                                                                                        |
| `ELK_VERSION`                               | `7.17.11`                                | Version of Filebeat service. Should match the version of the targeted elastic service.                                                                                                                                                                                                                           |
| `FILEBEAT_CONFIG_PATH`                      |                                          | Host path to the filebeat config. Set this variable if you use the filebeat service (`--profile *-with-elk-logging`).                                                                                                                                                                                            |
| `FILEBEAT_LOGS_DIR`                         |                                          | Host path to the directory [containing logs created by filebeat](https://www.elastic.co/guide/en/beats/filebeat/8.0/directory-layout.html) . Set this variable if you use the filebeat service (`--profile *-with-elk-logging`).                                                                                 |
| `FILEBEAT_DATA_DIR`                         |                                          | Host path to the directory [containing filebeat's persistent data files](https://www.elastic.co/guide/en/beats/filebeat/8.0/directory-layout.html) . Set this variable if you use the filebeat service (`--profile *-with-elk-logging`).                                                                         |
| `ELASTICSEARCH_API_KEY`                     | `""`                                     | API key used by filebeat to publish logs to elasticsearch. Set this variable if you use the filebeat service (`--profile *-with-elk-logging`).                                                                                                                                                                   |
| `ELASTICSEARCH_HOSTS`                       |                                          | Elasticsearch URL. Set this variable if you use the filebeat service (`--profile *-with-elk-logging`). Should start with https.                                                                                                                                                                                  |
| `ELASTICSEARCH_CERT_PATH`                   | `/etc/ssl/certs/ca-certificates.crt`     | Absolute path to certificate that should be used to connect to elastic search. Set this variable if you use the filebeat service (`--profile *-with-elk-logging`).                                                                                                                                               |
| `MINIO_SECRET_KEY`                          |                                          | Secret key for Minio's S3 API                                                                                                                                                                                                                                                                                    |
| `MINIO_EXPIRATION_DAYS`                     | `8`                                      | Expiration delay for Minio objects, in days, after which they will automatically be deleted on the origin side. Default is 8. (On the destination side, this expiration delay is automatically computed to be `S3REMOVER_EXPIRE_TRANSFERABLES_AFTER` + 1 day, rounded down a day.)                               |
| `EURYDICE_TRANSFERABLE_MAX_SIZE`            | `54975581388800`                         | File upload size limit on the origin side. Should be less than your storage capacity. Default is 50TiB, the [maximum size that Minio can handle](https://min.io/docs/minio/linux/operations/checklists/thresholds.html#minio-server-limits).                                                                     |
| `DJANGO_SECRET_KEY`                         |                                          | [Django secret key](https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key) django                                                                                                                                                                                                                       |
| `DB_PASSWORD`                               |                                          | PostgreSQL database password d'Eurydice                                                                                                                                                                                                                                                                          |
| `USER_ASSOCIATION_TOKEN_SECRET_KEY`         |                                          | Secret key for generating association tokens (must be the same for the origin and destination APIs)                                                                                                                                                                                                              |
| `S3REMOVER_RUN_EVERY`                       | `1min`                                   | Run frequency for the S3Remover (service which removes minio objects and sets Transferable to `EXPIRED` on the destination side)                                                                                                                                                                                 |
| `S3REMOVER_EXPIRE_TRANSFERABLES_AFTER`      | `7days`                                  | Duration before which files received on the destination side are marked as `EXPIRED`.                                                                                                                                                                                                                            |
| `S3REMOVER_POLL_EVERY`                      | `200ms`                                  | Maximum acceptable duration between the S3Remover receiving a `SIGINT` signal and the process' termination                                                                                                                                                                                                       |
| `DBTRIMMER_RUN_EVERY`                       | `6h`                                     | Launch frequency for the DBTrimmer (service which removes old transferables from the database)                                                                                                                                                                                                                   |
| `DBTRIMMER_TRIM_TRANSFERABLES_AFTER`        | `7days`                                  | Availability duration for a transferable's metadata once it has been sent, received, or if either have failed (after this duration, a transferable will 404 if request)                                                                                                                                          |
| `DBTRIMMER_POLL_EVERY`                      | `200ms`                                  | Maximum acceptable duration between the DBTrimmer receiving a `SIGINT` signal and the process' termination                                                                                                                                                                                                       |
| `SENDER_RANGE_FILLER_CLASS`                 | `UserRotatingTransferableRangeFiller`    | Changes the Sender's Transferable fetch strategy. Available choices are `UserRotatingTransferableRangeFiller` (default, attempts to fairly distribute bandwidth for Transferables among Users) or `FIFOTransferableRangeFiller` (faster implementation that ignores User priority; good for single-user usages). |
| `REMOTE_USER_HEADER_AUTHENTICATION_ENABLED` | `False`                                  | Enable authentication through the HTTP header set by `HTTP_X_REMOTE_USER` [**⚠️ beware of associated security implications**](#️-security-risks-associated-with-http-header-authentication)                                                                                                                      |
| `REMOTE_USER_HEADER`                        | `HTTP_X_REMOTE_USER`                     | Select the remote user authentication method, note the `HTTP_` prefix for HTTP header based authentication                                                                                                                                                                                                       |
| `THROTTLE_RATE`                             | `30/second`                              | File upload rate limiting                                                                                                                                                                                                                                                                                        |
| `RECEIVER_BUFFER_MAX_ITEMS`                 | `4`                                      | Maximum amount of incoming transferables awaiting processing that the receiver can hold before dropping incoming data. Should roughly match (`MEM_LIMIT_RECEIVER` / 2 \* `TRANSFERABLE_RANGE_SIZE`)                                                                                                              |
| `CPUS_BACKEND`                              | See compose.prod.yml                     | CPU docker limit for each backend service                                                                                                                                                                                                                                                                        |
| `CPUS_DATABASE`                             | See compose.prod.yml                     | CPU docker limit for database service                                                                                                                                                                                                                                                                            |
| `CPUS_<CONTAINER_NAME>`                     | See compose.prod.yml                     | CPU docker limit                                                                                                                                                                                                                                                                                                 |
| `MEM_LIMIT_BACKEND`                         | See compose.prod.yml                     | Memory docker limit for each backend service                                                                                                                                                                                                                                                                     |
| `MEM_LIMIT_DATABASE`                        | See compose.prod.yml                     | Memory docker limit for database service                                                                                                                                                                                                                                                                         |
| `MEM_LIMIT_<CONTAINER_NAME>`                | See compose.prod.yml                     | Memory docker limit                                                                                                                                                                                                                                                                                              |
| `SHM_SIZE_DATABASE`                         | See compose.prod.yml                     | Shared memory docker limit for the database container                                                                                                                                                                                                                                                            |
| `EURYDICE_CONTACT`                          | See compose.prod.yml                     | Contact information, useful to report bugs for example. It is displayed in the API documentation.                                                                                                                                                                                                                |
| `EURYDICE_CONTACT_FR`                       | See compose.prod.yml                     | Contact information in French. It is displayed in the frontend.                                                                                                                                                                                                                                                  |
| `UI_BADGE_CONTENT`                          | See compose.prod.yml                     | Configurable banner to be displayed on the front page in the frontend.                                                                                                                                                                                                                                           |
| `UI_BADGE_COLOR`                            | See compose.prod.yml                     | Color for the configurable frontpage banner. List of available colors: https://vuetifyjs.com/en/styles/colors/#material-colors                                                                                                                                                                                   |
| `METRICS_SLIDING_WINDOW`                    | See compose.prod.yml                     | Duration used to compute metrics for /metrics endpoints.                                                                                                                                                                                                                                                         |
| `USER_ASSOCIATION_TOKEN_EXPIRES_AFTER`      | See compose.prod.yml                     | Expiration delay of user association token.                                                                                                                                                                                                                                                                      |
| `TRANSFERABLE_HISTORY_DURATION`             |                                          | Duration of the history.                                                                                                                                                                                                                                                                                         |
| `TRANSFERABLE_HISTORY_SEND_EVERY`           |                                          | Frequency of the history.                                                                                                                                                                                                                                                                                        |
| `HTTP_SERVICES_BIND_HOST`                   | 127.0.0.1                                | TCP bind address for docker services.                                                                                                                                                                                                                                                                            |

**Warning: make sure that `DBTRIMMER_TRIM_TRANSFERABLES_AFTER` is greater than `TRANSFERABLE_HISTORY_DURATION`.**
If `DBTRIMMER_TRIM_TRANSFERABLES_AFTER` is less than `TRANSFERABLE_HISTORY_DURATION`, the DBTrimmer on the destination side will remove transferables that the history from the origin will recreate.
This will lead to previously deleted transferables being marked as `ERROR` on the destination side.

### History management

In some cases, the origin-side database may end up holding millions of Transferable entries. Combined with a long history duration, this may lead to the sender generating enormous quantities of data, just to send the history.

If that happens, you may want to consider using a much smaller history duration, while keeping the same `DBTRIMMER_TRIM_TRANSFERABLES_AFTER`. This will allow you to manually ask the sender to send a complete history only when needed, with the following command:

```bash
docker compose -f compose.prod.yml exec sender python manage.py send_history --duration 7days
```

## 👤 UID, GID and bind mounts

The `PUID` and `PGID` variables must have read/write permissions on the directories defined in the other variables.

### Storing data

If `MINIO_ENABLED` is false, Eurydice will attempt to use the filesystem as storage, instead of a remote s3 storage server. `TRANSFERABLE_STORAGE_DIR` should be set to the path to a directory.

### Logging

If `LOG_TO_FILE` is true, Eurydice will write additional logs at `${PYTHON_LOGS_DIR}/<service>-logs/log.json`. This is useful when using a `-with-elk-logging` profile, so that filebeat may read, process and share applicative logs to a remote elk server.

## 🖥️ Reverse Proxy

Eurydice needs to be setup behind a reverse proxy to work securely and optimally.
Setting up a reverse proxy will also enable authentication at the reverse proxy level rather than relying on the application's authentication mechanism.

The application's services are exposed on `localhost` by the `compose.prod.yml`.
It is advised to route them like so:

- Web UI at `http://localhost:8888`
  - Should handle requests who don't match the rules for the services below
- API at `http://localhost:8080`
  - Should handle requests whose path is prefixed by `/api` `/admin` `/static`
- Minio at `http://localhost:9000`
  - Should handle requests whose path is prefixed by `/minio` (the `/minio` prefix should be removed by the reverse proxy)
- pgadmin at `http://localhost:5050`
  - Should handle requests whose path is prefixed by `/pgadmin` (the `/pgadmin` prefix should be removed by the reverse proxy)
  - The reverse proxy should only allow authenticated users on this endpoint as all pgadmin authentication is disabled

The reverse proxy should also serve all endpoints over TLS.
It should also set the `X-Forwarded-Proto`, `X-Forwarded-For` and `X-Forwarded-Host` headers to forward information from the original request to the services.

### ⚠️ Security risks associated with HTTP header authentication

**Warning: [django normalizes HTTP headers](https://django.readthedocs.io/en/stable/releases/1.6.10.html#wsgi-header-spoofing-via-underscore-dash-conflation). So it is important to make sure that a user cannot forge an authentication HTTP header that would be considered safe by the reverse proxy, but would in fact be normalized by Django into a valid authentication header**

This risk can be mitigated by configuring which header is used for authenticating the header with the `REMOTE_USER_HEADER` variable.
This environment variable could for example be set to a purely alphanumeric value (not affected by normalization) which could not easily be guessed by the user.
In such a scenario, one would still need to make sure that the reverse proxy correctly prevents users from submitting their own authentication header.

### 🛣️ Basic authentication

**Warning: Basic HTTP authentication passes your credentials over the network as clear text. As such, it is NOT the recommended method of authentication. If you need to run Eurydice using basic auth, at least use HTTPS.**

In case you are unable to setup a reverse proxy and remote user authentication, Eurydice may support [Basic HTTP Authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).

Basic HTTP Authentication is enabled when the `REMOTE_USER_HEADER_AUTHENTICATION_ENABLED` variable is set to `false`.

### Elasticsearch API key

To send applicative logs into an ELK you need an API key for a user with following role restrictions:

```
{
  "filebeat_writer": {
    "cluster": ["monitor", "read_ilm", "read_pipeline"],
    "index": [
      {
        "names": ["eurydice-*"],
        "privileges": ["view_index_metadata", "create_doc", "auto_configure"]
      }
    ]
  }
}
```
