ARG REGISTRY="docker.io/"
ARG DEBIAN_RELEASE="bullseye"
ARG PYTHON_VERSION="3.12"

FROM ${REGISTRY}python:${PYTHON_VERSION}-${DEBIAN_RELEASE} AS devcontainer

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG RUN_PACKAGES="make"
ARG DEV_PACKAGES="shellcheck"

# hadolint ignore=DL3008,DL3013,DL3003
RUN apt-get update \
  && apt-get --no-install-recommends --no-install-suggests --yes --quiet install ${RUN_PACKAGES} ${DEV_PACKAGES} \
  && wget -q -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64 \
  && chmod +x /usr/local/bin/hadolint \
  && mkdir /var/log/app \
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
  /usr/share/man/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY .devcontainer/abc.sh /tmp/abc.sh
# hadolint ignore=SC1091
RUN source /tmp/abc.sh && rm -f /tmp/abc.sh
COPY .devcontainer/matchown.sh /usr/local/bin/matchown
RUN chmod +x /usr/local/bin/matchown
COPY .devcontainer/matchown_volumes.sh /usr/local/bin/matchown_volumes
RUN chmod +x /usr/local/bin/matchown_volumes

COPY .devcontainer/nodejs.sh /tmp/nodejs.sh
# hadolint ignore=SC1091
RUN source /tmp/nodejs.sh && rm -f /tmp/nodejs.sh

COPY .devcontainer/devcontainer.sh /tmp/devcontainer.sh
# hadolint ignore=SC1091
RUN source /tmp/devcontainer.sh && rm -f /tmp/devcontainer.sh

COPY .devcontainer/entrypoint.sh /entrypoint
RUN chmod +x /entrypoint

WORKDIR /home/abc/workdir

ENTRYPOINT ["/entrypoint"]
CMD ["sleep", "infinity"]

# backend-origin
EXPOSE 8000
# frontend-origin
EXPOSE 8080
# backend-destination
EXPOSE 8001
# frontend-destination
EXPOSE 8081
# receiver
EXPOSE 7000
