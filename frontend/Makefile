.PHONY: install
install:	## Install dependencies.
	npm ci

.PHONY: build-origin
build-origin:	## Build origin for production environment
	npm run build:origin

.PHONY: build-destination
build-destination:	## Build destination for production environment
	npm run build:destination

.PHONY: build
build:	## Build for production environment
	$(MAKE) build-origin build-destination

.PHONY: dev
dev:	## Run development server.
	npm run dev

.PHONY: prod-origin
prod-origin:	## Serve origin production bundle. WARNING: do not use this in production, this is only intended for testing the production bundle
	npm run prod:origin

.PHONY: prod-destination
prod-destination:	## Serve destination production bundle. WARNING: do not use this in production, this is only intended for testing the production bundle
	npm run prod:destination

.PHONY: lint
lint:	## Runs a static analysis of the code.
	npm run lint
	npm run lint:css

.PHONY: lint-fix
lint-fix: ## Runs a static analysis of the code and fix linting errors.
	npm run lint:fix
	npm run lint:css:fix

.PHONY: audit
audit:	## Checks production dependencies for vulnerabilities.
	bash npm_audit_ignore.sh

.PHONY: format
format:	## Format CSS, SCSS, YAML, JSON and Markdown files.
	npm run format

.PHONY: tests
tests:	## Runs unit tests.
	npm run tests

.PHONY: help
help:	## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
