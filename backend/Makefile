SHELL := bash
.ONESHELL:
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

SRC_DIR := eurydice
PACKAGES := common origin destination
TESTS_DIR := tests
CODE_DIRS := $(SRC_DIR) $(TESTS_DIR)
DUMMY_MINIO_ENV_VARIABLES := MINIO_ENDPOINT="" MINIO_ACCESS_KEY="" MINIO_SECRET_KEY="" TRANSFERABLE_STORAGE_DIR="/tmp/"
DUMMY_DB_ENV_VARIABLES := DB_NAME="" DB_USER="" DB_PASSWORD="" DB_HOST="" DB_PORT=""
DUMMY_LIDIS_ENV_VARIABLES := LIDIS_HOST="127.0.0.1" LIDIS_PORT="1"

# ------------------------------------------------------------------------------
# Dependency management
# ------------------------------------------------------------------------------

.PHONY: install
install: ## Install dependencies on production environment.
	PIPENV_VENV_IN_PROJECT=true pipenv install --deploy --ignore-pipfile

.PHONY: install-dev
install-dev: ## Install development dependencies.
	PIPENV_VENV_IN_PROJECT=true pipenv install --dev --deploy

.PHONY: install-dev-docker
install-dev-docker: ## Install development dependencies.
	pipenv install --dev --deploy --system

# ------------------------------------------------------------------------------
# Application management
# ------------------------------------------------------------------------------

.PHONY: run-dev
run-dev: ## Run the eurydice development server.
	python manage.py runserver 0.0.0.0:8080

.PHONY: run-origin-api
run-origin-api: ## Run the eurydice origin API production server.
	gunicorn -c eurydice/common/config/gunicorn.conf.py $$GUNICORN_CONFIGURATION eurydice.origin.config.wsgi

.PHONY: run-destination-api
run-destination-api: ## Run the eurydice destination API production server.
	gunicorn -c eurydice/common/config/gunicorn.conf.py $$GUNICORN_CONFIGURATION eurydice.destination.config.wsgi

.PHONY: run-sender
run-sender: ## Run the eurydice sender.
	python -m eurydice.origin.sender

.PHONY: run-receiver
run-receiver: ## Run the eurydice receiver.
	python -m eurydice.destination.receiver

.PHONY: run-destination-s3remover
run-destination-s3remover: ## Run the eurydice destination s3remover cleaning tool.
	python -m eurydice.destination.cleaning.s3remover

.PHONY: run-destination-dbtrimmer
run-destination-dbtrimmer: ## Run the eurydice destination dbtrimmer cleaning tool.
	python -m eurydice.destination.cleaning.dbtrimmer

.PHONY: run-origin-dbtrimmer
run-origin-dbtrimmer: ## Run the eurydice origin dbtrimmer cleaning tool.
	python -m eurydice.origin.cleaning.dbtrimmer

.PHONY: superuser
superuser: ## Create Django super user.
	DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_PASSWORD=admin DJANGO_SUPERUSER_EMAIL=admin@example.com python manage.py createsuperuser --noinput

.PHONY: user
user: ## Create Django user with an associated token.
	echo "import django; from rest_framework.authtoken.models import Token; user = django.contrib.auth.get_user_model().objects.create_user('user', 'user@example.com', 'user'); print(Token.objects.create(user=user))" | python manage.py shell

.PHONY: migrations
migrations: ## Create new migrations based on the changes made to the models.
	python manage.py makemigrations

.PHONY: migrations-check
migrations-check: ## Check that models are not changed without the appropriate migrations.
	USER_ASSOCIATION_TOKEN_SECRET_KEY="" DJANGO_ENV=TEST EURYDICE_API=origin python manage.py makemigrations --check
	USER_ASSOCIATION_TOKEN_SECRET_KEY="" DJANGO_ENV=TEST EURYDICE_API=destination python manage.py makemigrations --check

.PHONY: migrate
migrate: ## Apply migrations.
	python manage.py migrate

.PHONY: collectstatic
collectstatic: ## Collect static files.
	USER_ASSOCIATION_TOKEN_SECRET_KEY="" MINIO_ENABLED=false \
	$(DUMMY_MINIO_ENV_VARIABLES) $(DUMMY_DB_ENV_VARIABLES) $(DUMMY_LIDIS_ENV_VARIABLES) \
	python manage.py collectstatic --no-input --clear --ignore rest_framework

# ------------------------------------------------------------------------------
# Static Analysis & Tests
# ------------------------------------------------------------------------------

# Overwrite files in place to ensure file flags and mode are unchanged when isort is run
# inside a Docker container.
.PHONY: isort
isort: ## Format imports.
	isort --overwrite-in-place $(CODE_DIRS)

.PHONY: black
black: ## Format code.
	black $(CODE_DIRS)

.PHONY: format
format: ## Format code and imports.
	$(MAKE) isort black

.PHONY: black-check
black-check: ## Check that the code is properly formatted.
	black --check $(CODE_DIRS)

.PHONY: isort-check
isort-check: ## Check that the imports are properly sorted.
	isort --check-only $(CODE_DIRS)

.PHONY: flake8
flake8: ## Check PEP8, PyFlakes and circular complexity of the code.
	flakeheaven lint $(CODE_DIRS)

.PHONY: mypy
mypy: ## Run MyPy static type check across the code.
	export EURYDICE_MYPY_ERROR=0;\
	for dir in $(PACKAGES); do \
		DS=eurydice.$$dir.config.settings.base \
		USER_ASSOCIATION_TOKEN_SECRET_KEY="" \
		DJANGO_ENV=TEST \
		MINIO_ENABLED=false \
		$(DUMMY_MINIO_ENV_VARIABLES) \
		$(DUMMY_DB_ENV_VARIABLES) \
		$(DUMMY_LIDIS_ENV_VARIABLES) \
		mypy --check eurydice/$$dir \
		|| EURYDICE_MYPY_ERROR=1; \
	done;\
	if [ "$$EURYDICE_MYPY_ERROR" = '1' ] ; then exit 1; fi

.PHONY: pytype
pytype: ## Run Pytype static type check across the code.
	pytype $(CODE_DIRS) --jobs $$(nproc)

.PHONY: bandit
bandit: ## Run a security oriented static analysis of the code.
	bandit -r --ini setup.cfg

.PHONY: safety
safety:	## Check installed dependencies for known security vulnerabilities.
	safety \
	--disable-telemetry \
	check \
	--full-report

.PHONY: checks
checks: ## Runs all the static analysis tools (Flake8, MyPy, Bandit and Safety) at once.
	$(MAKE) flake8 mypy pytype bandit black-check isort-check safety

.PHONY: tests
tests: ## Run tests, iterate over test modules to configure DJANGO_SETTINGS_MODULE, to fail correctly, this should be one command.
	coverage erase
	export EURYDICE_TESTS_ERROR=0;\
	for dir in $(PACKAGES); do \
		USER_ASSOCIATION_TOKEN_SECRET_KEY="" \
		DJANGO_ENV=TEST pytest $(TESTS_DIR)/$$dir \
		--ds=eurydice.$$dir.config.settings.test \
		--cov-append \
		--cov-report= \
		--cov=$(SRC_DIR) \
		--junitxml=.report/$$dir-junit.xml \
		|| EURYDICE_TESTS_ERROR=1 ;\
	done; \
	coverage xml; \
	coverage report -m; \
	if [ "$$EURYDICE_TESTS_ERROR" = '1' ] ; then exit 1; fi

# ------------------------------------------------------------------------------
# Misc
# ------------------------------------------------------------------------------

.PHONY: clean
clean: ## clean environments & dependencies
	rm -rf .venv
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	rm -f coverage coverage.xml
	rm -rf .report

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------

.PHONY: help
help: ## Show this help.
	@echo "Usage:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
