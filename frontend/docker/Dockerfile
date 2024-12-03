ARG EURYDICE_VERSION development

# ------------------------------------------------------------------------------
# Base
# ------------------------------------------------------------------------------

FROM node:18-bullseye AS base

ENV PATH /home/eurydice/frontend/node_modules/.bin:$PATH

# vue-cli uses the VUE_CLI_BABEL_TRANSPILE_MODULES environment variable,
# to control whether the babel-plugin-dynamic-import-node plugin is enabled.
# It only does one thing by converting all import() to require().
# This configuration can significantly increase the speed of hot updates,
# when you have a large number of pages.
# Detail:  https://github.com/vuejs/vue-cli/blob/dev/packages/@vue/babel-preset-app/index.js

ENV VUE_CLI_BABEL_TRANSPILE_MODULES true

WORKDIR /home/eurydice/frontend

# ------------------------------------------------------------------------------
# Development
# ------------------------------------------------------------------------------

FROM base AS dev

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]

CMD ["make", "dev"]

# ------------------------------------------------------------------------------
# CI
# ------------------------------------------------------------------------------

FROM base AS ci
# hadolint ignore=DL3008
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends jq \
    && rm -rf /var/lib/apt/lists/*

RUN chown node:node "$(pwd)"

USER node

COPY --chown=node:node . .

RUN make install

# ------------------------------------------------------------------------------
# Build production dependencies
# ------------------------------------------------------------------------------

FROM ci AS build-prod

ARG EURYDICE_VERSION

ENV NODE_ENV production
ENV VUE_APP_VERSION ${EURYDICE_VERSION}

RUN make build

# ------------------------------------------------------------------------------
# Production image
# ------------------------------------------------------------------------------

FROM nginx:1-alpine as prod

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
  /home/eurydice/frontend/dist /var/www/html/eurydice
