# 👩‍💻 Development

## 🏁 Usage

### 🚀 Run the development environment

Run the config task.

```bash
make dev-config
```

Start the development stack

```bash
# Development stack with basic console logging
make dev-up

# Development stack with advanced ElasticSearch logging using filebeat (accessible at `kibana.localhost`)
make dev-up-elk
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

### 🚏 Stop the development environment

```bash
make dev-down
```

### Start the production stack locally

Copy `env.example` to `env.prod` and update variables according to your needs. Then run `make prod-up-origin` or `make prod-up-destination` depending on your case.

## ✨ Frontend

The developer documentation for the frontend of eurydice is available here: [`frontend/README.md`](../frontend/README.md)

## 🖥️ Backend

The developer documentation for the backend of eurydice is available here: [`backend/README.md`](../backend/README.md)
