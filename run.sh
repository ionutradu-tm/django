#!/bin/bash


REPLICA_TEMPLATE="
    <tr>
      <td>__DEPLOYMENT_NAME__:</td>
      <td><input type=\"text\" name=\"__DEPLOYMENT_NAME__\" value=\"__DEPLOYMENT_REPLICA__\" size=\"2\"></td>
    </tr>
"

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
sed -i -r "s/__wagons__/${WAGONS}/g" /work/mng/templates/train.html
sed -i -r "s/__repos__/${REPOS}/g" /work/mng/templates/train.html
sed -i -r "s/__Custom_locale__/${CUSTOM_LOCALE}/g" /work/mng/templates/functional_tests.html
sed -i -r "s/__BPR_sites__/${BPR_SITES}/g" /work/mng/templates/functional_tests.html
sed -i -r "s/__Locale_en__/${LOCALE_EN}/g" /work/mng/templates/functional_tests.html
sed -i -r "s/__Locale_non_en__/${LOCALE_NON_EN}/g" /work/mng/templates/functional_tests.html
sed -i -r "s/__Locale_all__/${LOCALE_ALL}/g" /work/mng/templates/functional_tests.html

#generate start/stop replicas
REPLICA_HTML=""
while IFS='=' read -r name value ; do
   if [[ $name == *'_DEPLOYMENT' ]]; then
      prefix=${name%%_*} # delete longest match from back (everything after first _)
      deployment_name="${prefix}_DEPLOYMENT"
      deployment_replica="${prefix}_REPLICA"
      replica_html=${REPLICA_TEMPLATE//__DEPLOYMENT_NAME__/${!deployment_name}}
      replica_html=${replica_html/__DEPLOYMENT_REPLICA__/${!deployment_replica}}
      REPLICA_HTML+=$replica_html$'\n'

   fi
done < <(env | sort -n) 
IFS= read -d '' -r < <(sed -e ':a' -e '$!{N;ba' -e '}' -e 's/[&/\]/\\&/g; s/\n/\\&/g' <<<"$REPLICA_HTML") || true
REPLICA_HTML_REPLACED=${REPLY%$'\n'}
sed -i -r "s/#__REPLICA_HTML_PLACEHOLDER__/${REPLICA_HTML_REPLACED}/g" /work/mng/templates/replica.html
sed -i -r "s/__TITLE__/${TITLE_REPLICA}/g" /work/mng/templates/replica.html




cd webpage || exit
cp -r /work/mng /work/webpage/
python manage.py runserver 0.0.0.0:8000