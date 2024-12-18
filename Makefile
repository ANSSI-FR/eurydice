SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
COMPOSE := PUID=$(shell id -u) PGID=$(shell id -g) docker compose
COMPOSE_DEV := $(COMPOSE) -f compose.yml
COMPOSE_PROD := $(COMPOSE) -f compose.prod.yml

SYSCTL_OPTIONS = net.core.rmem_max net.core.rmem_default net.core.netdev_max_backlog net.ipv4.udp_mem
SYSCTL_BACKUP_FILE = sysctl_backup.conf
### config

.PHONY: backup-sysctl
backup-sysctl: ## export sysctl config to backup file
	@for option in $(SYSCTL_OPTIONS); do \
		value=$$(sysctl -n $$option); \
		echo "$$option = $$value" >> $(SYSCTL_BACKUP_FILE); \
	done

.PHONY: restore-sysctl
restore-sysctl: ## restore sysctl config from backup file
	@while IFS= read -r line; do \
		sysctl -w "$$line"; \
	done < $(SYSCTL_BACKUP_FILE)

.PHONY: config-sysctl
config-sysctl: ## sysctl config of LIDI
	# https://github.com/ANSSI-FR/lidi/blob/master/doc/tweaking.rst
	$(MAKE) backup-sysctl
	sudo sysctl -w net.core.rmem_max=67108864 \
		-w net.core.rmem_default=67108864 \
		-w net.core.netdev_max_backlog=10000 \
		-w net.ipv4.udp_mem="12148128 16197504 24296256"

.PHONY: config-ufw
config-ufw: ## open sender and receiver firewall ports
	sudo ufw allow 5000/tcp
	sudo ufw allow 6000/udp

.PHONY: reset-ufw
reset-ufw: ## reset sender and receiver firewall ports
	@for PORT_PROTO in "5000/tcp" "6000/udp"; do \
		while sudo ufw status numbered | grep -q "$${PORT_PROTO}"; do \
			RULE_NUMBER=$$(sudo ufw status numbered | grep "$${PORT_PROTO}" | awk -F'[][]' '{print $$2}' | head -n 1); \
			if [ -n "$${RULE_NUMBER}" ]; then \
				sudo ufw --force delete $${RULE_NUMBER}; \
			fi; \
		done; \
	done

### dev

.PHONY: dev-config
dev-config:
	$(MAKE) config-sysctl config-ufw

.PHONY: dev-up
dev-up:
	$(MAKE) dev-config
	$(COMPOSE_DEV) up -d

.PHONY: dev-up-elk
dev-up-elk:
	$(COMPOSE_DEV) -f compose.kibana.yml up -d

.PHONY: dev-down
dev-down:
	$(COMPOSE_DEV) down --volumes --remove-orphans

.PHONY: dev-reset
dev-reset:
	$(MAKE) dev-down
	$(MAKE) dev-up

### prod

.PHONY: prod-config
prod-config:
	mkdir -p data/minio-data
	mkdir -p data/minio-conf
	mkdir -p data/db-data
	mkdir -p data/db-logs
	mkdir -p data/filebeat-logs
	mkdir -p data/filebeat-data
	mkdir -p data/python-logs/backend-origin
	mkdir -p data/python-logs/backend-destination
	mkdir -p data/python-logs/receiver
	mkdir -p data/python-logs/dbtrimmer-origin
	mkdir -p data/python-logs/dbtrimmer-destination
	mkdir -p data/python-logs/db-migrations-origin
	mkdir -p data/python-logs/db-migrations-destination

.PHONY: prod-up-origin
prod-up-origin:
	$(COMPOSE_PROD) --profile origin --env-file .env.prod run --rm db-migrations-origin
	$(COMPOSE_PROD) --profile origin --env-file .env.prod up -d

.PHONY: prod-stop-origin
prod-stop-origin:
	$(COMPOSE_PROD) --profile origin --env-file .env.prod stop

.PHONY: prod-up-destination
prod-up-destination:
	$(COMPOSE_PROD) --profile destination --env-file .env.prod run --rm db-migrations-destination
	$(COMPOSE_PROD) --profile destination --env-file .env.prod up -d

.PHONY: prod-stop-destination
prod-stop-destination:
	$(COMPOSE_PROD) --profile destination --env-file .env.prod stop

### Static Analysis

.PHONY: hadolint
hadolint:	## Lint the Dockerfiles.
	docker run --rm -i hadolint/hadolint:2.8.0-alpine < backend/docker/Dockerfile
	docker run --rm -i hadolint/hadolint:2.8.0-alpine < frontend/docker/Dockerfile
	docker run --rm -i hadolint/hadolint:2.8.0-alpine < pgadmin/Dockerfile

### help

.PHONY: help
help: ## Show this help
    @echo "Usage:"
    @grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
