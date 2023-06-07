#!/bin/bash

python manage.py collectstatic --noinput &&  cp -r /opt/admin_init/. /opt/admin/ && uwsgi --strict --ini uwsgi/uwsgi.ini
