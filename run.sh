#!/bin/bash


if [[ -n $DEBUG ]]; then
   echo "DEBUG=$DEBUG" > .env
fi

if [[ -n $ALLOWED_HOSTS ]]; then
   echo "ALLOWED_HOSTS=$ALLOWED_HOSTS" >> .env
fi


django-admin startproject webpage
cp /work/settings.py /work/webpage/webpage/settings.py
cd webpage
pythons manage.py startapp mng
python manage.py runserver 0.0.0.0:8000