#!/usr/bin/env bash
set -e

# Ensure pip is recent
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run DB migrations and collect static files
# Ensure we run from the Django project directory where manage.py lives
cd breathe_esg
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Gunicorn (bind to Render-provided $PORT)
exec gunicorn breathe_esg.wsgi:application --bind 0.0.0.0:$PORT --workers 3
