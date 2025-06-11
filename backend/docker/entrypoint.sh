#!/bin/sh

set -e

if [ "$DJANGO_MANAGEPY_MIGRATE" = 'on' ]; then
    while ! pg_isready -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT"; do
        echo "database is not ready"
        sleep 1
    done
    python3 manage.py migrate
fi

exec "$@"
