#!/bin/bash


WORKDRI="/work/webpage/webpage/"
if [[ -n $DEBUG ]]; then
   echo "DEBUG=$DEBUG" > $WORKDIR.env
fi

if [[ -n $ALLOWED_HOSTS ]]; then
   echo "ALLOWED_HOSTS=$ALLOWED_HOSTS" >> $WORKDIR.env
fi


django-admin startproject webpage
cp /work/settings.py $WORKDIRsettings.py
cd webpage
pythons manage.py startapp mng
python manage.py runserver 0.0.0.0:8000