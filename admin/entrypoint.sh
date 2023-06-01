#!/bin/bash

python manage.py collectstatic --noinput &&  uwsgi --strict --ini uwsgi.ini
