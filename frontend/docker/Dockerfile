ARG DEBIAN_RELEASE="bookworm"
ARG NODE_VERSION="24"
ARG REGISTRY="docker.io"

ARG EURYDICE_VERSION development

# ------------------------------------------------------------------------------
# Base
# ------------------------------------------------------------------------------
FROM ${REGISTRY}/node:${NODE_VERSION}-${DEBIAN_RELEASE} AS base

# used for source command
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# root user is switched in entrypoint
# hadolint ignore=DL3002
USER root

RUN groupadd --system --gid 1029 abc \
  && useradd --uid 1029 --gid abc --no-log-init --create-home --shell /bin/bash abc \
  && mkdir -p /home/abc/workdir \
  && chown abc:abc /home/abc/workdir

ENV PATH=/home/abc/workdir/node_modules/.bin:$PATH

USER abc
WORKDIR /home/abc/workdir
COPY --chown=abc:abc . .

EXPOSE 8080

# ------------------------------------------------------------------------------
# Development
# ------------------------------------------------------------------------------
FROM base AS dev

CMD ["make", "run-watch"]

# ------------------------------------------------------------------------------
# CI
# ------------------------------------------------------------------------------
FROM base AS ci

RUN make install-dev

# ------------------------------------------------------------------------------
# Build production dependencies
# ------------------------------------------------------------------------------
FROM ci AS build-prod

ARG EURYDICE_VERSION
RUN make build

# ------------------------------------------------------------------------------
# Production image
# ------------------------------------------------------------------------------
FROM nginx:1-alpine AS prod

## rewrite nginx user UID and GID to 1000:1000
RUN sed -i 's/nginx:x:101:101:nginx/nginx:x:1000:1000:nginx/g' /etc/passwd \
  && chown -R nginx:nginx /etc/nginx
# no mirror for alpine in CI, can't update packages
# RUN apk update && apk upgrade
COPY --chown=nginx:nginx docker/nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx docker/default.conf.template /etc/nginx/templates/default.conf.template

# switch to NGINX user
USER nginx

EXPOSE 8080

# copy the dist folder built during the build stage
COPY --from=build-prod --chown=nginx:nginx \
  /home/abc/workdir/dist /var/www/html/app
