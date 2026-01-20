ARG EURYDICE_VERSION development

ARG DEBIAN_RELEASE="bullseye"
ARG PYTHON_BUILD_VERSION="3.12"
# packages required to build project dependencies
ARG BUILD_DEBIAN_PACKAGES="libpq-dev build-essential"
# packages required to run the project
ARG RUN_DEBIAN_PACKAGES="make postgresql-client"

# ------------------------------------------------------------------------------
# Base
# ------------------------------------------------------------------------------
FROM python:$PYTHON_BUILD_VERSION-$DEBIAN_RELEASE AS base

ARG BUILD_DEBIAN_PACKAGES
ARG RUN_DEBIAN_PACKAGES
ARG DEBIAN_RELEASE

ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV PATH="/home/eurydice/backend/.venv/bin:$PATH"
# default backend gunicorn port
ENV PORT=8080

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get --no-install-recommends --no-install-suggests --yes --quiet install $BUILD_DEBIAN_PACKAGES $RUN_DEBIAN_PACKAGES \
  && pip install --no-cache-dir --upgrade pip==25.0 \
  && apt-get upgrade --yes \
  && apt-get clean \
  && chmod +x /usr/local/bin/uv /usr/local/bin/uvx \
  && apt-get --yes --quiet autoremove --purge \
  && rm -rf \
  /var/lib/apt/lists/* \
  /tmp/* \
  /var/tmp/* \
  /usr/share/doc/* \
  /usr/share/groff/* \
  /usr/share/info/* \
  /usr/share/linda/* \
  /usr/share/lintian/* \
  /usr/share/locale/* \
  /usr/share/man/*

RUN mkdir /var/log/app

WORKDIR /home/eurydice/backend

# ------------------------------------------------------------------------------
# Development
# ------------------------------------------------------------------------------

FROM base AS dev

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/healthcheck.py /healthcheck.py
RUN chmod +x /entrypoint.sh /healthcheck.py
ENTRYPOINT ["/entrypoint.sh"]

COPY pyproject.toml uv.lock Makefile ./
RUN make install-dev

COPY . .

# ------------------------------------------------------------------------------
# Compile production dependencies Stage
# ------------------------------------------------------------------------------

FROM base AS compile-prod

COPY pyproject.toml uv.lock Makefile ./
RUN make install-prod

# ------------------------------------------------------------------------------
# Production Image
# ------------------------------------------------------------------------------

FROM python:$PYTHON_BUILD_VERSION-slim-$DEBIAN_RELEASE AS prod

ARG RUN_DEBIAN_PACKAGES

ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get --no-install-recommends --no-install-suggests --yes --quiet install $RUN_DEBIAN_PACKAGES \
  && apt-get upgrade --yes \
  && apt-get clean \
  && apt-get --yes --quiet autoremove --purge \
  && rm -rf \
  /var/lib/apt/lists/* \
  /tmp/* \
  /var/tmp/* \
  /usr/share/doc/* \
  /usr/share/groff/* \
  /usr/share/info/* \
  /usr/share/linda/* \
  /usr/share/lintian/* \
  /usr/share/locale/* \
  /usr/share/man/* \
  && adduser --disabled-password --gecos "" --home /home/eurydice/backend eurydice

RUN mkdir /var/log/app /home/eurydice/data \
  && chown -R eurydice:eurydice /var/log/app /home/eurydice/data

WORKDIR /home/eurydice/backend

COPY --chown=eurydice:eurydice Makefile .
COPY --chown=eurydice:eurydice eurydice eurydice
COPY --chown=eurydice:eurydice --from=compile-prod /home/eurydice/backend/.venv /home/eurydice/backend/.venv
COPY --chown=eurydice:eurydice manage.py .
COPY --chown=eurydice:eurydice docker/entrypoint.sh /entrypoint.sh
COPY --chown=eurydice:eurydice docker/healthcheck.py /healthcheck.py
COPY --chown=eurydice:eurydice pyproject.toml .

# hadolint ignore=DL3044
ENV PATH="/home/eurydice/backend/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
# default backend gunicorn port
ENV PORT=8080

RUN chmod +x manage.py /entrypoint.sh /healthcheck.py \
  && rm -rf ./*/tests \
  && make collectstatic

ENTRYPOINT ["/entrypoint.sh"]
EXPOSE 8080

USER eurydice

ARG EURYDICE_VERSION
ENV EURYDICE_VERSION=$EURYDICE_VERSION
