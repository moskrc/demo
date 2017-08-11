#!/bin/bash

set -e
if [ "$DATABASE_URL" != "" ]; then
    until psql $DATABASE_URL -c '\l'; do
      >&2 echo "Postgres is unavailable - sleeping"
      sleep 3
    done

    >&2 echo "Postgres is up - continuing"
fi

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    python manage.py migrate --noinput
fi

if [ "x$DJANGO_MANAGEPY_COLLECTSTATIC" = 'xon' ]; then
    python manage.py collectstatic --noinput
fi

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting server"

exec "$@"

gunicorn project.wsgi:application -w 1 -b :8000 --reload --log-file project.log