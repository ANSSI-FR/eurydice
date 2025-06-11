# 🐳 Docker images

The compiled docker image are available on DockerHub.
The following images are available:

- `anssi/eurydice_backend`
  - docker image for most of the backend services (API, sender, database trimmer)
- `anssi/eurydice_frontend`
  - docker image for the server responsible for serving the frontend

The following tags are available for the aforementioned docker images:

- `development` docker image built for the latest commit on the `development` branch
- `master` docker image built for the latest commit on the `master` branch
- `latest` docker image built for the latest tagged release
- `X.Y.Z` docker image built for a specific tagged release
