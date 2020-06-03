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
    ALLOWED_HOSTS=list,
    TRACKER_REPO_PIPELINE_ID=str,
    FUNCTIONAL_TESTS_PIPELINE_ID=str,
    FUNCTIONAL_TESTS_BRANCH_NAME=str,
)
WERCKER_TOKEN = env('WERCKER_TOKEN')
TRACKER_REPO_PIPELINE_ID = env('TRACKER_REPO_PIPELINE_ID')
FUNCTIONAL_TESTS_PIPELINE_ID = env('FUNCTIONAL_TESTS_PIPELINE_ID')
FUNCTIONAL_TESTS_BRANCH_NAME = env('FUNCTIONAL_TESTS_BRANCH_NAME')

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
        data['envVars'] = [{ "key": "TO_BRANCH", "value": TO_BRANCH}, { "key": "RUN_TESTS", "value": RUN_TESTS}, { "key": "SOURCE_BRANCH", "value": FROM_BRANCH}, { "key": "FORCE_CLONE", "value": X_FORCE_CLONE}, , { "key": "FORCE_DEPLOY", "value": X_FORCE_DEPLOY} ]

        data1 = json.dumps(data)
        x_headers = {'Content-Type': 'application/json'}
        x_headers['Authorization'] = "Bearer %s" % (WERCKER_TOKEN)
        wercker_url = 'https://app.wercker.com/api/v3/runs/'
        r = requests.post(wercker_url, data=data1, headers=x_headers)
        messages.add_message(request, messages.INFO, "The deployment has been started")
        messages.success(request,  'Please check the progress <a href="https://app.wercker.com/Essentra/tracker-repo/runs"> wercker </a>', extra_tags='safe')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'deploy.html')
    

def create_branch(request):

    if request.method == 'POST':
        FROM_BRANCH=request.POST.get('FromBranch')
        NEW_BRANCH=request.POST.get('ToBranch')
        x_message = "Create branch %s from branch %s" % (NEW_BRANCH, FROM_BRANCH)
        data = {}
        data['pipelineId'] = TRACKER_REPO_PIPELINE_ID
        data['branch'] = "create-branch"
        data['message'] = x_message
        data['envVars'] = [{ "key": "NEW_BRANCH", "value": NEW_BRANCH}, { "key": "SOURCE_BRANCH", "value": FROM_BRANCH}, { "key": "FORCE_CLONE", "value": "yes"} ]

        data1 = json.dumps(data)
        x_headers = {'Content-Type': 'application/json'}
        x_headers['Authorization'] = "Bearer %s" % (WERCKER_TOKEN)
        wercker_url = 'https://app.wercker.com/api/v3/runs/'
        r = requests.post(wercker_url, data=data1, headers=x_headers)
        messages.add_message(request, messages.INFO, "Creating the new branch has been started")
        messages.success(request,  'Please check the progress <a href="https://app.wercker.com/Essentra/tracker-repo/runs"> wercker </a>', extra_tags='safe')
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
        messages.success(request,  'Please check the progress <a href="https://app.wercker.com/Essentra/functional-tests/runs"> wercker </a>', extra_tags='safe')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'functional_tests.html')
    

