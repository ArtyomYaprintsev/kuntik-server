# Getting started

## Settings

1. Set up your local environment as follows:

```sh
SECRET_KEY="ze(h0$faa*43s-a+ep^r-x!pb&kuaw-=mypep(1ukp3awe_th5"
DEBUG=False

ADMIN_EMAIL="admin@email.com"
ADMIN_USERNAME="adminUsername"
ADMIN_PASSWORD="someStrongPassword"
```

2. Install requirements:

```sh
pip install -r requirements.txt
```

3. Run `migrate`, `collectstatic` and `createsuperuser` commands:

```sh
python manage.py migrate --no-input
python manage.py collectstatic --no-input

DJANGO_SUPERUSER_PASSWORD=$ADMIN_PASSWORD python manage.py createsuperuser --username $ADMIN_USERNAME --email $ADMIN_EMAIL --noinput
```

4. Run local server:

```sh
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```
