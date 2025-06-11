# Project File Structure

```bash
├── backend                     # backend's source code
│   ├── docker                  # files related to building the docker image
│   ├── eurydice
│   │   ├── common              # common code for origin and destination
│   │   ├── destination         # destination services
│   │   │   ├── api             # destination api
│   │   │   ├── backoffice      # django admin
│   │   │   ├── cleaning        # additional clean-up services (dbtrimmer, file_remover)
│   │   │   ├── config          # destination django configuration
│   │   │   ├── core            # code common to the "API" and "receiver" services of the destination
│   │   │   ├── receiver        # service receiving data packets from lidir
│   │   │   ├── storage
│   │   │   └── utils
│   │   ├── origin              # origin services
│   │   │   ├── api             # origin api
│   │   │   ├── backoffice      # django admin
│   │   │   ├── cleaning        # additional clean-up services (dbtrimmer, file_remover)
│   │   │   ├── config          # origin django configuration
│   │   │   ├── core            # code common to the "API" and "sender" services of the origin
│   │   │   ├── sender          # service sending data packets to lidis
│   │   │   └── storage
│   │   └── templates
│   │       └── admin
│   └── tests                   # test folder
├── docs                        # documentation
├── filebeat                    # filebeat configuration
├── frontend                    # frontend's code source
│   ├── docker                  # docker configuration
│   ├── public                  # public assets (favicon, etc...)
│   └── src
│       ├── assets
│       │   ├── i18n            # translation files
│       │   └── img             # images files
│       ├── common              # common code for origin and destination 
│       │   ├── api
│       │   ├── components
│       │   ├── layouts
│       │   ├── models
│       │   ├── plugins
│       │   ├── router
│       │   ├── services
│       │   ├── store
│       │   ├── utils
│       │   └── views
│       ├── destination         # destination frontend
│       │   ├── components
│       │   ├── router
│       │   ├── services
│       │   └── views
│       ├── origin              # origin frontend
│       │   ├── components
│       │   ├── models
│       │   ├── router
│       │   ├── services
│       │   └── views
│       └── tests               # tests for the frontend
├── pgadmin                     # pgadmin container configuration
├── compose.*.yml               # sample docker compose configurations
└── README.md
```
