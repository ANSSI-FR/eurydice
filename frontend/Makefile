SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# ------------------------------------------------------------------------------
# Dependency management
# ------------------------------------------------------------------------------

.PHONY: install
install:		## Install dependencies for production environment.
	NODE_ENV=production npm install --loglevel verbose

.PHONY: install-dev
install-dev:	## Install development dependencies.
	npm install --loglevel verbose --save-dev

# ------------------------------------------------------------------------------
# Application management
# ------------------------------------------------------------------------------

.PHONY: run-watch
run-watch: install-dev	## Run development server.
	npm run dev

.PHONY: run-preview
run-preview:	## Run preview server.
	VITE_API_URL=http://eurydice.test $(MAKE) build
	npm run preview

.PHONY: build
build: build-origin build-destination	## Build app for origin and destination.

.PHONY: build-origin
build-origin: install-dev ## Build app for origin.
	VITE_EURYDICE_GUICHET=origin npm run build-only

.PHONY: build-destination
build-destination: install-dev ## Build app for destination.
	VITE_EURYDICE_GUICHET=destination npm run build-only


# ------------------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------------------

.PHONY: tests
tests:	## Launch unit test on app.
	npm run test:unit

# ------------------------------------------------------------------------------
# Static Analysis
# ------------------------------------------------------------------------------

.PHONY: format-check
format-check:	## Format code check.
	npm run format-check

.PHONY: format-fix
format-fix:	## Format code and imports.
	npm run format-fix

.PHONY: format
format:	format-fix ## Format code and imports.

.PHONY: lint-check
lint-check:	## Check lint code.
	npm run type-check
	npm run lint-check

.PHONY: lint-fix
lint-fix:	## Lint code and fix.
	npm run type-check
	npm run lint-fix

.PHONY: lint
lint:	lint-fix ## Lint code and fix.

.PHONY: audit
audit:	## Checks production dependencies for vulnerabilities.
	npm audit

.PHONY: checks
checks:
	$(MAKE) lint-check format-check && echo All checks succeeded!

# ------------------------------------------------------------------------------
# Clean
# ------------------------------------------------------------------------------
.PHONY: clean
clean: ## Clean useless folders
	rm -rf node_modules

# ------------------------------------------------------------------------------
# Docker image build by stage
# ------------------------------------------------------------------------------

.PHONY: build-docker-base
build-docker-base: ## Build docker image for stage base
	docker build -t eurydice/frontend:base --target base -f docker/Dockerfile .

.PHONY:build-docker-dev
build-docker-dev: ## Build docker image for stage dev
	docker build -t eurydice/frontend:dev --target dev -f docker/Dockerfile .

.PHONY:build-docker-ci
build-docker-ci: ## Build docker image for stage ci
	docker build -t eurydice/frontend:ci --target ci -f docker/Dockerfile .

.PHONY:build-docker-build
build-docker-build: ## Build docker image for stage build-prod
	docker build -t eurydice/frontend:build-prod --target build-prod -f docker/Dockerfile .

.PHONY:build-docker-prod
build-docker-prod: ## Build docker image for stage prod
	docker build -t eurydice/frontend:prod --target prod -f docker/Dockerfile .

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------

.PHONY: help
help:		## Show this help.
	@echo "Usage:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
