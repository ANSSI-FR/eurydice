# ------------------------------------------------------------------------------
# Static Analysis
# ------------------------------------------------------------------------------

.PHONY: hadolint
hadolint:	## Lint the Dockerfiles.
	docker run --rm -i hadolint/hadolint:2.8.0-alpine < backend/docker/Dockerfile
	docker run --rm -i hadolint/hadolint:2.8.0-alpine < frontend/docker/Dockerfile
	docker run --rm -i hadolint/hadolint:2.8.0-alpine < pgadmin/Dockerfile
