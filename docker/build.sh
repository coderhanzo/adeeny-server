#!/bin/bash

set -o errexit

set -o pipefail

set -o nounset

# Apply database migrations for the 'users' app first
# echo "Apply database migrations for the users app"
# python manage.py migrate users

python manage.py makemigrations --noinput

# Apply database migrations
echo "Applying general database migrations"
python manage.py migrate --noinput

# Collect static files
python3 manage.py collectstatic --noinput

# Start Gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8000 config.wsgi:application
# python manage.py runserver 0.0.0.0:8000
