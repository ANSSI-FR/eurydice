# 👩‍💻 Development

## 🏁 Usage

### 🚀 Run the development environment

Start the container used for development in detached mode.

```bash
# Development stack with basic console logging
docker compose up -d

# Development stack with advanced ElasticSearch logging using filebeat (accessible at `kibana.localhost`)
docker compose -f compose.yml -f compose.kibana.yml up -d
```

_Note: it is [recommended](https://github.com/moby/moby/issues/40379) to use the environment variable `DOCKER_BUILDKIT=1`_

The following URLs are available in the development environment:

- http://origin.localhost: the origin user interface.
- http://origin.localhost/api/docs/: the origin API documentation.
- http://origin.localhost/api/v1/: the origin API.
- http://origin.localhost/admin/: the origin administration interface.
- http://destination.localhost: the destination user interface.
- http://destination.localhost/api/docs/: the destination API documentation.
- http://destination.localhost/api/v1/: the destination API.
- http://destination.localhost/admin/: the destination administration interface.
- http://minio.localhost/: the Minio to store the origin and destination files.
- http://pgadmin.localhost/: database management tool.
- http://traefik.localhost/: the traefik dashboard

### Start the production stack locally

You may use the example environment variables defined in `.env.example`.
Create needed directories on you host:

```bash
mkdir /tmp/eurydice
mkdir /tmp/eurydice/minio-data
mkdir /tmp/eurydice/minio-conf
mkdir /tmp/eurydice/db-data
mkdir /tmp/eurydice/db-logs
mkdir /tmp/eurydice/filebeat-logs
mkdir /tmp/eurydice/filebeat-data
sudo chown -R 1000:1000 /tmp/eurydice/
```

Then, run database migrations:

```bash
docker compose -f compose.prod.yml --profile origin --env-file .env.example run --rm db-migrations-origin
```

or

```bash
docker compose -f compose.prod.yml --profile destination --env-file .env.example run --rm db-migrations-destination
```

Finally, you can start the stack:

```bash
docker compose -f compose.prod.yml --env-file .env.example --profile origin up -d
```

or

```bash
docker compose -f compose.prod.yml --env-file .env.example --profile destination up -d
```

## ✨ Frontend

The developer documentation for the frontend of eurydice is available here: [`frontend/README.md`](../frontend/README.md)

## 🖥️ Backend

The developer documentation for the backend of eurydice is available here: [`backend/README.md`](../backend/README.md)
