from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
import json
import requests
from django.contrib import messages
import environ
import os

# Create your views here.


environ.Env.read_env()
env = environ.Env(
    DEBUG=(bool, False),
    DEBUG_TOOLBAR=(bool, False),
    WERCKER_TOKEN=str,
    TOKEN=str,
    ACTIONS_URL=str,
    REPO_ACTIONS_URL = str,
    ALLOWED_HOSTS=list,
    TRACKER_REPO_PIPELINE_ID=str,
    FUNCTIONAL_TESTS_PIPELINE_ID=str,
    FUNCTIONAL_TESTS_BRANCH_NAME=str,
    WERCKER_URL=str,
    WERCKER_FUNCTIONAL_URL=str,
)
WERCKER_TOKEN = env('WERCKER_TOKEN')
GIT_TOKEN = env('TOKEN')
TRACKER_REPO_PIPELINE_ID = env('TRACKER_REPO_PIPELINE_ID')
FUNCTIONAL_TESTS_PIPELINE_ID = env('FUNCTIONAL_TESTS_PIPELINE_ID')
FUNCTIONAL_TESTS_BRANCH_NAME = env('FUNCTIONAL_TESTS_BRANCH_NAME')
X_WERCKER_URL = env('WERCKER_URL')
X_WERCKER_FUNCTIONAL_URL = env('WERCKER_FUNCTIONAL_URL')
ACTIONS_URL = env('ACTIONS_URL')
REPO_ACTIONS_URL = env('REPO_ACTIONS_URL')

def index(request):
    return render(request, 'base.html' )

def deploy(request):

    if request.method == 'POST':
        FROM_BRANCH=request.POST.get('FromBranch')
        TO_BRANCH=request.POST.get('ToBranch')
        RUN_TESTS = request.POST.get('run_tests')
        X_FORCE_CLONE = request.POST.get('force_clone')
        X_FORCE_DEPLOY = request.POST.get('force_deploy')
        x_message = "Preparing deployment of %s on %s " % (FROM_BRANCH,TO_BRANCH)
        data = {}
        data['pipelineId'] = TRACKER_REPO_PIPELINE_ID
        data['branch'] = "start-deploy"
        data['message'] = x_message
        data['envVars'] = [{ "key": "TO_BRANCH", "value": TO_BRANCH}, { "key": "RUN_TESTS", "value": RUN_TESTS}, { "key": "SOURCE_BRANCH", "value": FROM_BRANCH}, { "key": "FORCE_CLONE", "value": X_FORCE_CLONE}, { "key": "FORCE_DEPLOY", "value": X_FORCE_DEPLOY} ]

        data1 = json.dumps(data)
        x_headers = {'Content-Type': 'application/json'}
        x_headers['Authorization'] = "Bearer %s" % (WERCKER_TOKEN)
        wercker_url = 'https://app.wercker.com/api/v3/runs/'
        r = requests.post(wercker_url, data=data1, headers=x_headers)
        messages.add_message(request, messages.INFO, "The deployment has been started")
        x_message= 'Please check the progress <a href="%s"> wercker </a>' % (X_WERCKER_URL)
        messages.success(request,  x_message, extra_tags='safe')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'deploy.html')
    

def create_branch(request):

    if request.method == 'POST':
        FROM_BRANCH=request.POST.get('FromBranch')
        NEW_BRANCH=request.POST.get('ToBranch')
        CI_CD=request.POST.get('ci_cd')
        x_message = "Create branch %s from branch %s" % (NEW_BRANCH, FROM_BRANCH)
        data = {}
        if CI_CD == "wercker":
            data['pipelineId'] = TRACKER_REPO_PIPELINE_ID
            data['branch'] = "create-branch"
            data['message'] = x_message
            data['envVars'] = [{ "key": "NEW_BRANCH", "value": NEW_BRANCH}, { "key": "SOURCE_BRANCH", "value": FROM_BRANCH}, { "key": "FORCE_CLONE", "value": "yes"} ]
            data1 = json.dumps(data)

            x_headers = {'Content-Type': 'application/json'}
            x_headers['Authorization'] = "Bearer %s" % (WERCKER_TOKEN)
            wercker_url = 'https://app.wercker.com/api/v3/runs/'
            r = requests.post(wercker_url, data=data1, headers=x_headers)
            x_message = 'Please check the progress <a href="%s"> wercker </a>' % (X_WERCKER_URL)
            messages.add_message(request, messages.INFO, "Creating the new branch has been started")
            messages.success(request,  x_message, extra_tags='safe')
        else:
            data['event_type'] = "create-branch"
            data['client_payload'] = { "NEW_BRANCH": NEW_BRANCH, "SOURCE_BRANCH": FROM_BRANCH, "FORCE_CLONE":"yes"}
            data1 = json.dumps(data)

            x_headers = {'Accept': 'application/vnd.github.everest-preview+json'}
            x_headers['Authorization'] = "token %s" % (GIT_TOKEN)
            r = requests.post(ACTIONS_URL, data=data1, headers=x_headers)
            messages.add_message(request, messages.INFO, "Creating the new branch has been started")
            x_message = 'Please check the progress <a href="%s"> actions </a>' % (REPO_ACTIONS_URL)
            messages.success(request,  x_message, extra_tags='safe')

        return HttpResponseRedirect('/')
    else:
        return render(request, 'create_branch.html')
    
def functional_tests(request):

    if request.method == 'POST':
        VERSION=request.POST.get('Version')
        ENVIRONMENT=request.POST.get('Environment')
        SUITE=request.POST.get('Suite')
        x_message = "Test build  %s on environment %s, suite %s" % (VERSION, ENVIRONMENT, SUITE)
        data = {}
        data['pipelineId'] = FUNCTIONAL_TESTS_PIPELINE_ID
        data['branch'] = FUNCTIONAL_TESTS_BRANCH_NAME
        data['message'] = x_message
        data['envVars'] = [{ "key": "BUILD_VERSION", "value": VERSION}, { "key": "ENVIRONMENT", "value": ENVIRONMENT }, { "key": "SUITE", "value": SUITE } ]

        data1 = json.dumps(data)
        x_headers = {'Content-Type': 'application/json'}
        x_headers['Authorization'] = "Bearer %s" % (WERCKER_TOKEN)
        wercker_url = 'https://app.wercker.com/api/v3/runs/'
        r = requests.post(wercker_url, data=data1, headers=x_headers)
        messages.add_message(request, messages.INFO, "Functional tests has been started")
        x_message = 'Please check the progress <a href="%s"> wercker </a>' % (X_WERCKER_FUNCTIONAL_URL)
        messages.success(request,  x_message, extra_tags='safe')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'functional_tests.html')
    

