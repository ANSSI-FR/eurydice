# Project File Structure

```
eurydice
├── backend/
|   ├── docker/               # files related to building the docker image
|   ├── eurydice/             # backend's source code
|   |   ├── common/           # common code for origin and destination
|   |   ├── destination/      # destination services
|   │   └── origin/           # origin services
|   │       ├── api/          # origin API
|   │       ├── backoffice/   # Django admin interface of the origin
|   │       ├── cleaning/     # additional clean-up services (dbtrimmer, s3remover)
|   |       ├── config/       # configuration of the origin Django project
|   |       ├── core/         # code common to the "API" and "sender" services of the origin
|   │       └── sender/       # service sending data packets to lidis
|   └── tests/                # tests for the backend
|       ├── common/           # tests of the common code
|       ├── destination/      # tests of destination services
|       └── origin/           # tests of origin services
|           ├── integration/
|           └── unit/
├── docs/                     # additional misc. documentation
├── filebeat/                 # sample configuration files for filebeat container
├── frontend/
|   ├── docker/               # files related to building the docker image
|   ├── public/               # frontend's static files
|   ├── src/                  # frontend's source code
|   |   ├── common/           # common code for origin and destination frontends
|   |   |   ├── api/          # source code for making requests to the API
|   |   |   ├── components/
|   |   |   ├── layouts/
|   |   |   ├── plugins/      # VueJS plugins
|   |   |   ├── utils/        # miscellaneous common utilities
|   |   |   └── views/
|   |   ├── destination/      # destination frontend
|   │   └── origin/           # origin frontend
|   └── tests/                # tests for the frontend
├── pgadmin/                  # pgadmin container configuration
├── compose.*.yml             # sample docker compose configurations
└── README.md
```
