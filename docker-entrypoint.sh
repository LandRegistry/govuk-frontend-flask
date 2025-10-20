#!/bin/sh
set -e

echo "Running DB migrations..."
flask db upgrade

# Dynamic worker count (default: 2×CPU + 1)
: "${WORKERS:=$(( $(nproc) * 2 + 1 ))}"
: "${BIND_ADDR:=0.0.0.0:5000}"
: "${ACCESS_LOG:=-}"

echo "Starting Gunicorn on $BIND_ADDR with $WORKERS workers..."
exec gunicorn --bind "$BIND_ADDR" -w "$WORKERS" --access-logfile "$ACCESS_LOG" govuk-frontend-flask:app
