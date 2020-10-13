#!/bin/bash


django-admin startproject webpage

WORKDIR="/work/webpage/webpage/"
if [[ -n $DEBUG ]]; then
   echo "DEBUG=$DEBUG" > $WORKDIR".env"
fi

if [[ -n $ALLOWED_HOSTS ]]; then
   echo "ALLOWED_HOSTS=$ALLOWED_HOSTS" >> $WORKDIR".env"
fi

if [[ -n $TRACKER_REPO_PIPELINE_ID ]]; then
   echo "TRACKER_REPO_PIPELINE_ID=$TRACKER_REPO_PIPELINE_ID" >> $WORKDIR".env"
fi

if [[ -n $FUNCTIONAL_TESTS_PIPELINE_ID ]]; then
   echo "FUNCTIONAL_TESTS_PIPELINE_ID=$FUNCTIONAL_TESTS_PIPELINE_ID" >> $WORKDIR".env"
fi

if [[ -n $WERCKER_TOKEN ]]; then
   echo "WERCKER_TOKEN=$WERCKER_TOKEN" >> $WORKDIR.env
fi

cp /work/settings.py $WORKDIR"settings.py"
cp /work/urls.py  $WORKDIR"urls.py"
if [[ -f /mnt/mesos/sandbox/deploy/.env ]];then
  mv /mnt/mesos/sandbox/deploy/.env /tmp/.env.gz
  gzip -d /tmp/.env.gz
  base64 -d /tmp/.env > $WORKDIR".env"
fi
cd webpage || exit
cp -r /work/mng /work/webpage/
python manage.py runserver 0.0.0.0:8000