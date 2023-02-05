#!/bin/bash

# Uncomment the following line to wipe the database on every container start
#echo "Deleting database..."
#python manage.py flush --no-input

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating superuser..."
python manage.py createsuperuser --noinput

echo "Starting server..."
python manage.py runserver 0.0.0.0:9000
