#!/bin/bash
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser --username $ADMIN_USERNAME --email $ADMIN_EMAIL --password $ADMIN_PASSWORD