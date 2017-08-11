#!/bin/bash

set -e
if [ "$DATABASE_URL" != "" ]; then
    until psql $DATABASE_URL -c '\l'; do
      >&2 echo "Postgres is unavailable - sleeping"
      sleep 3
    done

    >&2 echo "Postgres is up - continuing"
fi

echo "Starting celery/scheduler"

exec "$@"

celery worker -A project -l debug -c 2 -B