#!/usr/bin/env bash
set -e

# Railway exposes PORT for the web service
export PORT="${PORT:-8000}"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on 0.0.0.0:${PORT}"
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 120
