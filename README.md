<div align="center">
  <img width="128" height="128" src="frontend/public/lyre.png" alt="Eurydice icon">
</div>

<div align="center"><h1>Eurydice</h1></div>

<div align="center">
Eurydice (<b>E</b>metteur <b>U</b>nidirectionnel <b>R</b>edondant de <b>Y</b>ottabit pour le <b>D</b>ialogue <b>I</b>ntergiciel avec <b>C</b>orrection d'<b>E</b>rreur) provides an interface to transfer files through a physical diode using the [Lidi](https://github.com/ANSSI-FR/lidi/) utility.
</div>

## 📁 Project structure

See [ARCHITECTURE.md](ARCHITECTURE.md).

## 📦 Versioning

This project adheres to the [Semantic Versioning specification](https://semver.org/).
Versions are represented as [git tags](https://github.com/ANSSI-FR/eurydice/tags).
You can view the release history with the accompanying changelog [here](https://github.com/ANSSI-FR/eurydice/releases).

## 🔨 Prerequisites

- [`docker>=19.03.0`](https://docs.docker.com/engine/install/)
  - support for the compose specification [was added in `19.03.0`](https://docs.docker.com/compose/compose-file/compose-versioning/#compatibility-matrix)

## 🐳 Docker images

The compiled docker image are publicly available on the docker hub.

Dockerfiles are provided for each component.

The following images are available:

- `anssi/eurydice-backend`
  - docker image for the backend service (API, sender, database trimmer)
- `anssi/eurydice-frontend`
  - docker image for the server responsible for serving the frontend

The following tags are available for the aforementioned docker images:

- `0.x.x` docker image built for a specific tagged release

## 🚧 Development

See [docs/developers.md](docs/developers.md).

## 🚀 Deployment in production & administration

See [docs/administrators.md](docs/administrators.md).

## ▶️ Usage

### 👩‍💻 HTTP API

See documentation directories:

- [Common API documentation](backend/eurydice/common/api/docs/static/).
- [Origin API documentation and code snippets](backend/eurydice/origin/api/docs/static/).
- [Destination API documentation and code snippets](backend/eurydice/destination/api/docs/static/).

## 🙏 Credits

- Logo by [Freepik](https://www.freepik.com)
