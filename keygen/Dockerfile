FROM ubuntu:noble AS builder

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# hadolint ignore=DL3008,DL3013
RUN apt-get update \
  && apt-get --no-install-recommends --no-install-suggests --yes --quiet install build-essential libsodium-dev \
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

COPY keygen.c /root/keygen.c

RUN gcc /root/keygen.c -o /root/keygen -lsodium

FROM ubuntu:noble AS prod

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# hadolint ignore=DL3008,DL3013
RUN apt-get update \
  && apt-get --no-install-recommends --no-install-suggests --yes --quiet install libsodium23 \
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

COPY --from=builder /root/keygen /usr/local/bin/keygen

ENTRYPOINT ["/usr/local/bin/keygen"]
