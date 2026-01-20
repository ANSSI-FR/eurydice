FROM dpage/pgadmin4:9.8 as base

ENV PGADMIN_DISABLE_POSTFIX="1" \
  PGADMIN_CONFIG_SHOW_GRAVATAR_IMAGE="False" \
  PGADMIN_LISTEN_ADDRESS="0.0.0.0"

FROM base as dev

COPY --chown=pgadmin:root dev/* /pgadmin4/

RUN chmod 600 /pgadmin4/.pgpass

# PassFile in servers.json is relative to the user's home directory (/ in this case)
# https://stackoverflow.com/a/67267786
ENV HOME=/

FROM base as prod

COPY --chown=pgadmin:root prod/postgres-reg.ini /etc/postgres-reg.ini

RUN chmod 644 /etc/postgres-reg.ini

