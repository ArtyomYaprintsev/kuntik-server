#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --no-input

DJANGO_SUPERUSER_PASSWORD=$ADMIN_PASSWORD python manage.py createsuperuser --username $ADMIN_USERNAME --email $ADMIN_EMAIL --noinput

gunicorn config.wsgi:application --bind 0.0.0.0:8000
