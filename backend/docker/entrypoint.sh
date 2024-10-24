#!/bin/sh

set -e

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    while ! pg_isready -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT"; do sleep 1; done
    python3 manage.py migrate
fi

exec "$@"
