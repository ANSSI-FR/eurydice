# ⚙️ Environment Variables

## Docker images configuration

| Variable                 | Default value                                 | Description                                                                                                                       |
| ------------------------ | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `LOCAL_DOCKER_REGISTRY`  | `docker.io` | Docker image registry hostname local                                                                                              |
| `REMOTE_DOCKER_REGISTRY` | `docker.io`                                   | Docker image registry hostname for images from the [docker hub](https://hub.docker.com/)                                          |
| `EURYDICE_VERSION`       | `latest`                                      | Tag for the Eurydice docker image ([list of tags](https://github.com/ANSSI-FR/eurydice/tags)) |
| `LIDI_VERSION`           | `latest`                                      | Tag for the lidis/r docker images ([list of tags](https://github.com/ANSSI-FR/lidi/tags))     |
| `ELK_VERSION`            | `7.17.11`                                     | Version of Filebeat service. Should match the version of the targeted elastic service.                                            |

## User configuration

| Variable | Default value | Description                                                         |
| -------- | ------------- | ------------------------------------------------------------------- |
| `PUID`   | `1000`        | Numeric identifier to the user under which the services of will run |
| `PGID`   | `1000`        | Numeric identifier for the group under which the services will run  |

## Backend configuration

| Variable                               | Default value    | Description                                                                                                                                                                                                                                 |
| -------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GUNICORN_CONFIGURATION`               | `""`             | Gunicorn commandline arguments                                                                                                                                                                                                              |
| `CSRF_TRUSTED_ORIGINS`                 | `""`             | Additionnal origin(s) for CSRF validation, separated by a comma: `,`. SEE [Django documentation](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins) Must include scheme ("http://", "https://") . May be left empty. |
| `EURYDICE_TRANSFERABLE_MAX_SIZE`       | `54975581388800` | File upload size limit on the origin side. Should be less than your storage capacity. Default is 50TiB.                                                                                                                                     |
| `DJANGO_SECRET_KEY`                    |                  | [Django secret key](https://docs.djangoproject.com/fr/5.2/ref/settings/#secret-key) django                                                                                                                                                  |
| `USER_ASSOCIATION_TOKEN_SECRET_KEY`    |                  | Secret key for generating association tokens (must be the same for the origin and destination APIs)                                                                                                                                         |
| `USER_ASSOCIATION_TOKEN_EXPIRES_AFTER` | `30min`          | Expiration delay of user association token.                                                                                                                                                                                                 |
| `METRICS_SLIDING_WINDOW`               | `60min`          | Duration used to compute metrics for /metrics endpoints.                                                                                                                                                                                    |

## Authentication configuration

| Variable                                    | Default value        | Description                                                                                                                                                                                                                                                                       |
| ------------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `REMOTE_USER_HEADER_AUTHENTICATION_ENABLED` | `False`              | Enable authentication through the HTTP header set by `REMOTE_USER_HEADER`. Warning: Django is subject to [WSGI header spoofing via underscore/dash conflation](https://django.readthedocs.io/en/stable/releases/1.6.10.html#wsgi-header-spoofing-via-underscore-dash-conflation). |
| `REMOTE_USER_HEADER`                        | `HTTP_X_REMOTE_USER` | Select the remote user authentication method, note the `HTTP_` prefix for HTTP header based authentication                                                                                                                                                                        |

## Database configuration

| Variable            | Default value | Description                                           |
| ------------------- | ------------- | ----------------------------------------------------- |
| `DB_NAME`           | `eurydice`    | PostgreSQL database name                              |
| `DB_USER`           | `eurydice`    | PostgreSQL database user                              |
| `DB_PASSWORD`       |               | PostgreSQL database password                          |
| `SHM_SIZE_DATABASE` | `1g`          | Shared memory docker limit for the database container |

## Hostnames configuration

| Variable             | Default value | Description                                                   |
| -------------------- | ------------- | ------------------------------------------------------------- |
| `FRONTEND_HOSTNAMES` | `localhost`   | Hostname(s) for the frontend UI separated by a **space**: ` ` |
| `BACKEND_HOSTNAMES`  | `localhost`   | Hostname(s) for the backend API separated by a **comma**: `,` |

## Server configuration

| Variable                  | Default value | Description                           |
| ------------------------- | ------------- | ------------------------------------- |
| `HTTP_SERVICES_BIND_HOST` | `127.0.0.1`   | TCP bind address for docker services. |

## Lidi configuration

| Variable                    | Default value | Description                                                                                                                                |
| --------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `LIDIR_PORT`                | `11011`       | Lidir port number                                                                                                                          |
| `LIDIS_PORT`                | `33010`       | Lidis port number                                                                                                                          |
| `LIDIR_NB_DECODING_THREADS` | `2`           | Value for lidi option `--nb_decoding_threads` (see <https://anssi-fr.github.io/lidi/parameters.html#multithreading>)                       |
| `LIDI_UDP_MTU`              | `1500`        | Value for lidi option `--from_udp_mtu` (see https://github.com/ANSSI-FR/lidi/blob/master/doc/parameters.rst#block-and-packet-sizes)        |
| `LIDI_ENCODING_BLOCK_SIZE`  | `60000`       | Value for lidi option `--encoding_block_size` (see https://github.com/ANSSI-FR/lidi/blob/master/doc/parameters.rst#block-and-packet-sizes) |
| `LIDI_REPAIR_BLOCK_SIZE`    | `6000`        | Value for lidi option `--repair_block_size` (see https://github.com/ANSSI-FR/lidi/blob/master/doc/parameters.rst#block-and-packet-sizes)   |
| `LIDIS_NB_ENCODING_THREADS` | `2`           | Value for lidi option `--nb_encoding_threads` (see <https://anssi-fr.github.io/lidi/parameters.html#multithreading>)                       |
| `LIDI_BANDWIDTH_LIMIT`      | `1000`        | Value fir lidi option `--bandwidth_limit` (not yet documented) limit bandwith for the lidis/r. This Parameter affects performance and reliability and avoid lost blocks for 10Go/s )      |

## Network configuration

| Variable               | Default value   | Description                                                                           |
| ---------------------- | --------------- | ------------------------------------------------------------------------------------- |
| `EURYDICE_IPV4_SUBNET` | `172.18.0.0/24` | Range of IP addresses that will be assigned to containers within the eurydice network |

## Backend logging configuration

| Variable      | Default value        | Description                                                                                          |
| ------------- | -------------------- | ---------------------------------------------------------------------------------------------------- |
| `LOG_TO_FILE` | `true`               | If true, python processes will configure their logger to log into json files. See `PYTHON_LOGS_DIR`. |
| `LOG_LEVEL`   | `INFO`               | Django and Eurydice Log Level                                                                        |
| `RUST_LOG`    | See compose.prod.yml | Rust log level (i.e. Lidi log level)                                                                 |

## File remover configuration

| Variable                                  | Default value | Description                                                                                                                 |
| ----------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `FILE_REMOVER_RUN_EVERY`                  | `1min`        | Run frequency for the File Remover (service which removes files and sets Transferable to `EXPIRED` on the destination side) |
| `FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER` | `7days`       | Duration before which files received on the destination side are marked as `EXPIRED`.                                       |
| `FILE_REMOVER_POLL_EVERY`                 | `200ms`       | Maximum acceptable duration between the File Remover receiving a `SIGINT` signal and the process' termination               |

## DB trimmer configuration

| Variable                             | Default value | Description                                                                                                                                                             |
| ------------------------------------ | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DBTRIMMER_RUN_EVERY`                | `6h`          | Launch frequency for the DBTrimmer (service which removes old transferables from the database)                                                                          |
| `DBTRIMMER_TRIM_TRANSFERABLES_AFTER` | `7days`       | Availability duration for a transferable's metadata once it has been sent, received, or if either have failed (after this duration, a transferable will 404 if request) |
| `DBTRIMMER_POLL_EVERY`               | `200ms`       | Maximum acceptable duration between the DBTrimmer receiving a `SIGINT` signal and the process' termination                                                              |

## Filebeat configuration

| Variable                  | Default value                                       | Description                                                                                                                                                            |
| ------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `FILEBEAT_CONFIG_PATH`    |                                                     | Host path to the filebeat config. Set this variable if you use the filebeat service (`--profile *-with-elk-logging`).                                                  |
| `ELASTICSEARCH_API_KEY`   | `""`                                                | API key used by filebeat to publish logs to elasticsearch. Set this variable if you use the filebeat service (`--profile *-with-elk-logging`).                         |
| `ELASTICSEARCH_HOSTS`     |                                                     | Elasticsearch URL. Set this variable if you use the filebeat service (`--profile *-with-elk-logging`). Should start with https.                                        |
| `ELASTICSEARCH_CERT_PATH` | `/etc/ssl/certs/ca-certificates.crt` | Absolute path to SSL certificate that should be used to connect to elastic search. Set this variable if you use the filebeat service (`--profile *-with-elk-logging`). |

## Sender configuration

| Variable                    | Default value                         | Description                                                                                                                                                                                                                                                                                                      |
| --------------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SENDER_RANGE_FILLER_CLASS` | `UserRotatingTransferableRangeFiller` | Changes the Sender's Transferable fetch strategy. Available choices are `UserRotatingTransferableRangeFiller` (default, attempts to fairly distribute bandwidth for Transferables among Users) or `FIFOTransferableRangeFiller` (faster implementation that ignores User priority; good for single-user usages). |

## Receiver configuration

| Variable                    | Default value | Description                                                                                                                                                                                               |
| --------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RECEIVER_BUFFER_MAX_ITEMS` | `4`           | Maximum amount of incoming transferables range awaiting processing that the receiver can hold before dropping incoming data. Should roughly match (`MEM_LIMIT_RECEIVER` / 2 \* `TRANSFERABLE_RANGE_SIZE`) |

## CPU and memory configuration

| Variable                     | Default value        | Description                                  |
| ---------------------------- | -------------------- | -------------------------------------------- |
| `CPUS_BACKEND`               | See compose.prod.yml | CPU docker limit for each backend service    |
| `CPUS_DATABASE`              | See compose.prod.yml | CPU docker limit for database service        |
| `CPUS_<CONTAINER_NAME>`      | See compose.prod.yml | CPU docker limit                             |
| `MEM_LIMIT_BACKEND`          | See compose.prod.yml | Memory docker limit for each backend service |
| `MEM_LIMIT_DATABASE`         | See compose.prod.yml | Memory docker limit for database service     |
| `MEM_LIMIT_<CONTAINER_NAME>` | See compose.prod.yml | Memory docker limit                          |

## Folder configuration

| Variable                   | Default value | Description                                                                                                                                                                                                                              |
| -------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `TRANSFERABLE_STORAGE_DIR` |               | Host path to the directory containing transferable data                                                                                                                                                                                  |
| `DB_DATA_DIR`              |               | Host path to the directory containing the database's data                                                                                                                                                                                |
| `DB_LOGS_DIR`              |               | Host path to the directory containing the database's logs                                                                                                                                                                                |
| `PYTHON_LOGS_DIR`          |               | Host path to the directory containing python logs. Each service will write into their own sub-directory, as such: `${PYTHON_LOGS_DIR:?}/sender-logs/log.json`                                                                            |
| `FILEBEAT_LOGS_DIR`        |               | Host path to the directory [containing logs created by filebeat](https://www.elastic.co/guide/en/beats/filebeat/8.0/directory-layout.html) . Set this variable if you use the filebeat service (`--profile *-with-elk-logging`).         |
| `FILEBEAT_DATA_DIR`        |               | Host path to the directory [containing filebeat's persistent data files](https://www.elastic.co/guide/en/beats/filebeat/8.0/directory-layout.html) . Set this variable if you use the filebeat service (`--profile *-with-elk-logging`). |

## Transferable history

| Variable                          | Default value | Description               |
| --------------------------------- | ------------- | ------------------------- |
| `TRANSFERABLE_HISTORY_DURATION`   | `15min`       | Duration of the history.  |
| `TRANSFERABLE_HISTORY_SEND_EVERY` | `15min`       | Frequency of the history. |

## Other

| Variable              | Default value                 | Description                                                                                                                                                                                             |
| --------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EURYDICE_CONTACT`    | `by mail`                     | Contact information, useful to report bugs for example. It is displayed in the API documentation.                                                                                                       |
| `EURYDICE_CONTACT_FR` | `par mail`                    | Contact information in French. It is displayed in the frontend.                                                                                                                                         |
| `UI_BADGE_CONTENT`    | `Environment1 → Environment2` | Configurable badge content to be displayed on the front page in the frontend.                                                                                                                           |
| `UI_BADGE_COLOR`      | `#01426a`                     | Color for the configurable frontpage badge. See the [list of available colors](https://www.w3schools.com/colors/colors_hex.asp). Please prefer using dark colors as the badge text color will be white. |

## ⚠️ Warning ⚠️

Make sure that `DBTRIMMER_TRIM_TRANSFERABLES_AFTER` is greater than `TRANSFERABLE_HISTORY_DURATION`.
If `DBTRIMMER_TRIM_TRANSFERABLES_AFTER` is less than `TRANSFERABLE_HISTORY_DURATION`, the DBTrimmer on the destination side will remove transferables that the history from the origin will recreate.
This will lead to previously deleted transferables being marked as `ERROR` on the destination side.
