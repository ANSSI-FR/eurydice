ARG DEBIAN_RELEASE="bullseye"
ARG NODE_VERSION="22"
ARG REGISTRY="docker.io"

ARG EURYDICE_VERSION development

# ------------------------------------------------------------------------------
# Base
# ------------------------------------------------------------------------------

FROM ${REGISTRY}/node:${NODE_VERSION}-${DEBIAN_RELEASE} AS base

# used for source command
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /home/eurydice/frontend
ENV PATH=/home/eurydice/frontend/node_modules/.bin:$PATH

RUN chown node:node "$(pwd)"

USER node

# ------------------------------------------------------------------------------
# Development
# ------------------------------------------------------------------------------
FROM base AS dev

EXPOSE 8080

COPY --chown=node:node . .

CMD ["make", "run-watch"]

# ------------------------------------------------------------------------------
# CI
# ------------------------------------------------------------------------------
FROM base AS ci

COPY --chown=node:node . .

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

COPY --chown=nginx:nginx docker/nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx docker/default.conf.template /etc/nginx/templates/default.conf.template

# switch to NGINX user
USER nginx

EXPOSE 8080

# copy the dist folder built during the build stage
COPY --from=build-prod --chown=nginx:nginx \
  /home/eurydice/frontend/dist /var/www/html/app
