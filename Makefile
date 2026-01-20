SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

COMPOSE := docker compose
COMPOSE_DEV := PUID=$(shell id -u) PGID=$(shell id -g) $(COMPOSE) -f compose.yml
COMPOSE_PROD := $(COMPOSE) -f compose.prod.yml

SYSCTL_OPTIONS = net.core.rmem_max net.core.rmem_default net.core.netdev_max_backlog net.ipv4.udp_mem
SYSCTL_BACKUP_FILE = sysctl_backup.conf

# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------

.PHONY: backup-sysctl
backup-sysctl: ## export sysctl config to backup file
	@if [ ! -f $(SYSCTL_BACKUP_FILE) ]; then \
		for option in $(SYSCTL_OPTIONS); do \
			value=$$(sysctl -n $$option); \
			echo "$$option=$$value" >> $(SYSCTL_BACKUP_FILE); \
		done \
	fi;

.PHONY: restore-sysctl
restore-sysctl: ## restore sysctl config from backup file
	@while IFS= read -r line; do \
		sudo sysctl -w "$$line"; \
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
	@if ! command -v ufw >/dev/null 2>&1; then \
		echo "ufw is not installed, skipping..."; \
		exit 0; \
	fi
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

.PHONY: create-common-volumes
create-common-volumes: ## bootstrap the common volumes folders
	@if [ -f .env ]; then \
		set -a && source .env && set +a; \
	else \
		echo "no .env file found, using default values"; \
	fi
	@mkdir -p "$${FILEBEAT_LOGS_DIR:-data/filebeat-logs}"
	@mkdir -p "$${FILEBEAT_DATA_DIR:-data/filebeat-data}"

.PHONY: create-common-destination-volumes
create-common-destination-volumes: ## bootstrap the common destination volumes folders
	@if [ -f .env ]; then \
		set -a && source .env && set +a; \
	else \
		echo "no .env file found, using default values"; \
	fi
	@mkdir -p "$${PYTHON_LOGS_DIR:-data/python-logs}/"{backend-destination,receiver,dbtrimmer-destination,db-migrations-destination,file-remover-destination}

.PHONY: create-common-origin-volumes
create-common-origin-volumes: ## bootstrap the common origin volumes folders
	@if [ -f .env ]; then \
		set -a && source .env && set +a; \
	else \
		echo "no .env file found, using default values"; \
	fi
	@mkdir -p "$${PYTHON_LOGS_DIR:-data/python-logs}/"{backend-origin,sender,dbtrimmer-origin,db-migrations-origin,file-remover-origin}

# ------------------------------------------------------------------------------
# Dev
# ------------------------------------------------------------------------------

.PHONY: create-dev-volumes
create-dev-volumes: ## bootstrap the dev volumes folders
	$(MAKE) create-common-volumes
	$(MAKE) create-common-destination-volumes
	$(MAKE) create-common-origin-volumes
	@if [ -f .env ]; then \
		set -a && source .env && set +a; \
	else \
		echo "no .env file found, using default values"; \
	fi
	@mkdir -p "$${ORIGIN_DB_LOGS_DIR:-data/db-logs-origin}"
	@mkdir -p "$${ORIGIN_DB_DATA_DIR:-data/db-data-origin}"
	@mkdir -p "$${DESTINATION_DB_DATA_DIR:-data/db-data-destination}"
	@mkdir -p "$${DESTINATION_DB_LOGS_DIR:-data/db-logs-destination}"
	@mkdir -p "$${ORIGIN_TRANSFERABLE_STORAGE_DIR:-data/data-storage-origin}"
	@mkdir -p "$${DESTINATION_TRANSFERABLE_STORAGE_DIR:-data/data-storage-destination}"
	@mkdir -p "$${FILEBEAT_LOGS_DIR:-data/filebeat-logs}/origin"
	@mkdir -p "$${FILEBEAT_LOGS_DIR:-data/filebeat-logs}/destination"
	@mkdir -p "$${FILEBEAT_DATA_DIR:-data/filebeat-data}/origin"
	@mkdir -p "$${FILEBEAT_DATA_DIR:-data/filebeat-data}/destination"
	@mkdir -p "$${KEYPAIR_DIR:-data/keys}"

.PHONY: dev-config
dev-config: ## run dev configuration recipes
	$(MAKE) config-sysctl
	$(MAKE) config-ufw
	$(MAKE) create-dev-volumes
	$(MAKE) generate-keys
	$(MAKE) generate-apache-dev-config
	mv ./eurydice* "$${KEYPAIR_DIR:-data/keys}"

.PHONY: dev-up
dev-up: ## start the dev stack
	$(MAKE) dev-config
	$(COMPOSE_DEV) build --pull
	$(COMPOSE_DEV) watch

.PHONY: dev-up-elk
dev-up-elk: ## start the dev stack with ELK
	$(MAKE) dev-config
	$(COMPOSE_DEV) build --pull
	$(COMPOSE_DEV) -f compose.kibana.yml watch

.PHONY: dev-stop
dev-stop: ## stop the dev stack
	$(COMPOSE_DEV) down --remove-orphans

.PHONY: dev-stop-elk
dev-stop-elk: ## stop the dev stack with ELK
	$(COMPOSE_DEV) -f compose.kibana.yml down --remove-orphans

.PHONY: dev-clean
dev-clean: ## stop and clean the dev stack
	$(COMPOSE_DEV) -f compose.kibana.yml down --volumes --remove-orphans
	rm -rf data/

.PHONY: dev-reset
dev-reset: ## stop, clean then restart the dev stack
	$(MAKE) dev-clean
	$(MAKE) dev-up

.PHONY: install-dev
install-dev: ## install local environments & dependencies
	$(MAKE) -C backend install-dev
	$(MAKE) -C frontend install-dev

.PHONY: generate-apache-dev-config
generate-apache-dev-config:
	@set -a
	source apache2/configs/.env
	AppSide=origin envsubst < apache2/configs/dev-local-oidc.conf.tmpl > apache2/configs/dev-local-origin.conf
	AppSide=destination envsubst < apache2/configs/dev-local-oidc.conf.tmpl > apache2/configs/dev-local-destination.conf

# ------------------------------------------------------------------------------
# Production Volumes
# ------------------------------------------------------------------------------

.PHONY: create-common-prod-volumes
create-common-prod-volumes: ## bootstrap the common production volumes folders
	$(MAKE) create-common-volumes
	@if [ -f .env ]; then \
		set -a && source .env && set +a; \
	else \
		echo "no .env file found, using default values"; \
	fi
	@mkdir -p "$${HOST_TRANSFERABLE_STORAGE_DIR:-data/storage-data}"
	@mkdir -p "$${DB_DATA_DIR:-data/db-data}"
	@mkdir -p "$${DB_LOGS_DIR:-data/db-logs}"

.PHONY: create-prod-destination-volumes
create-prod-destination-volumes: ## bootstrap the production destination volumes folders
	$(MAKE) create-common-prod-volumes
	$(MAKE) create-common-destination-volumes

.PHONY: create-prod-origin-volumes
create-prod-origin-volumes: ## bootstrap the common production volumes folders
	$(MAKE) create-common-prod-volumes
	$(MAKE) create-common-origin-volumes

.PHONY: generate-apache-prod-config
generate-apache-prod-config:
	@set -a
	source deployment/prod/.env
	envsubst < deployment/prod/config-ssl.conf.tmpl > deployment/prod/config-ssl.conf

# ------------------------------------------------------------------------------
# Production Origin
# ------------------------------------------------------------------------------

.PHONY: prod-up-origin
prod-up-origin: ## start the production origin stack
	$(MAKE) create-prod-origin-volumes
	$(COMPOSE_PROD) --profile origin run --rm db-migrations-origin
	$(COMPOSE_PROD) --profile origin up -d

.PHONY: prod-stop-origin
prod-stop-origin: ## stop the production origin stack
	$(COMPOSE_PROD) --profile origin stop

# ------------------------------------------------------------------------------
# Production Origin with ELK
# ------------------------------------------------------------------------------

.PHONY: prod-up-origin-elk
prod-up-origin-elk: ## start the production origin stack
	$(MAKE) create-prod-origin-volumes
	$(COMPOSE_PROD) --profile origin-with-elk-logging run --rm db-migrations-origin
	$(COMPOSE_PROD) --profile origin-with-elk-logging up -d

.PHONY: prod-stop-origin-elk
prod-stop-origin-elk: ## stop the production origin stack
	$(COMPOSE_PROD) --profile origin-with-elk-logging stop

# ------------------------------------------------------------------------------
# Production Destination
# ------------------------------------------------------------------------------

.PHONY: prod-up-destination
prod-up-destination: ## start the production destination stack
	$(MAKE) create-prod-destination-volumes
	$(COMPOSE_PROD) --profile destination run --rm db-migrations-destination
	$(COMPOSE_PROD) --profile destination up -d

.PHONY: prod-stop-destination
prod-stop-destination: ## stop the production destination stack
	$(COMPOSE_PROD) --profile destination stop

# ------------------------------------------------------------------------------
# Production Origin with ELK
# ------------------------------------------------------------------------------

.PHONY: prod-up-destination-elk
prod-up-destination-elk: ## start the production destination stack
	$(MAKE) create-prod-destination-volumes
	$(COMPOSE_PROD) --profile destination-with-elk-logging run --rm db-migrations-destination
	$(COMPOSE_PROD) --profile destination-with-elk-logging up -d

.PHONY: prod-stop-destination-elk
prod-stop-destination-elk: ## stop the production destination stack
	$(COMPOSE_PROD) --profile destination-with-elk-logging stop

# ------------------------------------------------------------------------------
# Static Analysis
# ------------------------------------------------------------------------------

.PHONY: hadolint
hadolint:	## Lint the Dockerfiles.
	docker run --rm -i hadolint/hadolint:2.8.0-alpine < backend/docker/Dockerfile
	docker run --rm -i hadolint/hadolint:2.8.0-alpine < frontend/docker/Dockerfile
	docker run --rm -i hadolint/hadolint:2.8.0-alpine < pgadmin/Dockerfile

# ------------------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------------------

.PHONY: tests
tests:
	$(MAKE) -C backend tests
	$(MAKE) -C frontend tests

.PHONY: compose-check
compose-check:
	docker compose -f compose.yml --env-file .env.dev.example config --quiet
	docker compose -f compose.yml -f compose.kibana.yml --env-file .env.dev.example config --quiet
	DB_PASSWORD=xxx docker compose -f compose.prod.yml --env-file .env.prod.example config --quiet

# ------------------------------------------------------------------------------
# Checks and Format
# ------------------------------------------------------------------------------

.PHONY: checks
checks:
	$(MAKE) -C backend checks
	$(MAKE) -C frontend checks
	$(MAKE) compose-check

.PHONY: format
format:
	$(MAKE) -C backend format
	$(MAKE) -C frontend format

# ------------------------------------------------------------------------------
# Miscellaneous
# ------------------------------------------------------------------------------

.PHONY: clean
clean: ## clean environments & dependencies
	$(MAKE) -C backend clean
	$(MAKE) -C frontend clean

.PHONY: install-git-hooks
install-git-hooks:
	git config --local core.hooksPath .githooks

.PHONY: generate-keys
generate-keys: ## generate a pair of keys (pub/priv) in the current folder (eurydice + eurydice.pub) to encrypt the files
	docker build -t eurydice/keygen:latest ./keygen
	docker run --rm -u $${PUID:-$(shell id -u)}:$${PGID:-$(shell id -g)} -v "$(shell pwd):/keys" eurydice/keygen:latest

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------

.PHONY: help
help: ## Show this help
	@echo "Usage:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
