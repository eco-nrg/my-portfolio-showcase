#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

# TODO: use gunicorn?

export DJANGO_ENV

python /code/manage.py migrate --noinput
python /code/manage.py collectstatic --noinput

daphne -b 0.0.0.0 -p 8000 mywebsite.asgi:application --verbosity=0
