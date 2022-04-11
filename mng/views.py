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
    ACTIONS_URL_FUNCTIONAL_TESTS=str,
    REPO_ACTIONS_URL = str,
    REPO_ACTIONS_URL_FUNCTIONAL_TESTS=str,
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
ACTIONS_URL_FT = env('ACTIONS_URL_FUNCTIONAL_TESTS')
REPO_ACTIONS_URL = env('REPO_ACTIONS_URL')
REPO_ACTIONS_URL_FT = env('REPO_ACTIONS_URL_FUNCTIONAL_TESTS')

def index(request):
    return render(request, 'base.html' )

def deploy(request):

    if request.method == 'POST':
        FROM_BRANCH=request.POST.get('FromBranch')
        TO_BRANCH=request.POST.get('ToBranch')
        RUN_TESTS = request.POST.get('run_tests')
        X_FORCE_CLONE = 'yes'
        X_FORCE_DEPLOY = request.POST.get('force_deploy')
        CI_CD = request.POST.get('ci_cd')
        x_message = "Preparing deployment of %s on %s " % (FROM_BRANCH,TO_BRANCH)
        data = {}
        if CI_CD == "wercker":
            data['pipelineId'] = TRACKER_REPO_PIPELINE_ID
            data['branch'] = "start-deploy"
            data['message'] = x_message
            data['envVars'] = [{ "key": "TO_BRANCH", "value": TO_BRANCH}, { "key": "RUN_TESTS", "value": RUN_TESTS}, { "key": "SOURCE_BRANCH", "value": FROM_BRANCH}, { "key": "FORCE_CLONE", "value": X_FORCE_CLONE}, { "key": "FORCE_DEPLOY", "value": X_FORCE_DEPLOY} ]

            data1 = json.dumps(data)
            x_headers = {'Content-Type': 'application/json', 'Authorization': "Bearer %s" % (WERCKER_TOKEN)}
            wercker_url = 'https://app.wercker.com/api/v3/runs/'
            r = requests.post(wercker_url, data=data1, headers=x_headers)
            messages.add_message(request, messages.INFO, "The deployment has been started")
            x_message= 'Please check the progress <a href="%s"> wercker </a> ' % (X_WERCKER_URL)
            messages.success(request,  x_message, extra_tags='safe')

        else:
            x_event_type = "Deployment preparation --- %s into %s" % (FROM_BRANCH,TO_BRANCH)
            data['event_type'] = x_event_type
            if FROM_BRANCH == 'empty' or TO_BRANCH == 'empty':
                return render(request, 'deploy.html')
            else: 
                data['client_payload'] = { "TO_BRANCH": TO_BRANCH, "SOURCE_BRANCH": FROM_BRANCH, "FORCE_CLONE": X_FORCE_CLONE, "RUN_TESTS": RUN_TESTS, "FORCE_DEPLOY": X_FORCE_DEPLOY}
                data1 = json.dumps(data)

                x_headers = {'Accept': 'application/vnd.github.everest-preview+json',
                            'Authorization': "token %s" % (GIT_TOKEN)}
                r = requests.post(ACTIONS_URL, data=data1, headers=x_headers)
                messages.add_message(request, messages.INFO, "Creating the new branch has been started")
                x_message = 'Please check the progress <a href="%s"> actions </a> ' % (REPO_ACTIONS_URL)
                messages.success(request,  x_message, extra_tags='safe')
            return HttpResponseRedirect('/')  
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

            x_headers = {'Content-Type': 'application/json', 'Authorization': "Bearer %s" % (WERCKER_TOKEN)}
            wercker_url = 'https://app.wercker.com/api/v3/runs/'
            r = requests.post(wercker_url, data=data1, headers=x_headers)
            x_message = 'Please check the progress <a href="%s"> wercker </a>' % (X_WERCKER_URL)
            messages.add_message(request, messages.INFO, "Creating the new branch has been started")
            messages.success(request,  x_message, extra_tags='safe')
        else:
            data['event_type'] = "create-branch"
            data['client_payload'] = { "NEW_BRANCH": NEW_BRANCH, "SOURCE_BRANCH": FROM_BRANCH, "FORCE_CLONE":"yes"}
            data1 = json.dumps(data)

            x_headers = {'Accept': 'application/vnd.github.everest-preview+json',
                         'Authorization': "token %s" % (GIT_TOKEN)}
            r = requests.post(ACTIONS_URL, data=data1, headers=x_headers)
            messages.add_message(request, messages.INFO, "Creating the new branch has been started")
            x_message = 'Please check the progress <a href="%s"> actions </a>' % (REPO_ACTIONS_URL)
            messages.success(request,  x_message, extra_tags='safe')

        return HttpResponseRedirect('/')
    else:
        return render(request, 'create_branch.html')


def train(request):

    if request.method == 'POST':
        WAGONS = request.POST.get('wagons')
        REPOS = request.POST.get('repos')
        data = {'event_type': "train", 'client_payload': {"WAGONS": WAGONS, "REPOS": REPOS}}
        data1 = json.dumps(data)

        x_headers = {'Accept': 'application/vnd.github.everest-preview+json', 'Authorization': "token %s" % (GIT_TOKEN)}
        r = requests.post(ACTIONS_URL, data=data1, headers=x_headers)
        messages.add_message(request, messages.INFO, "Thomas leaves the Vicarstown Station")
        x_message = 'Please check the progress <a href="%s"> actions </a>' % (REPO_ACTIONS_URL)
        messages.success(request,  x_message, extra_tags='safe')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'train.html')

def replica(request):
    payload = {}
    if request.method == 'POST':
        for name, value in request.POST.items():
            if name != "csrfmiddlewaretoken":
                payload[name] = value
        data = {'event_type': "replica", 'client_payload': payload}
        data1 = json.dumps(data)

        x_headers = {'Accept': 'application/vnd.github.everest-preview+json', 'Authorization': "token %s" % (GIT_TOKEN)}
        r = requests.post(ACTIONS_URL, data=data1, headers=x_headers)
        messages.add_message(request, messages.INFO, "Update deployments replica")
        x_message = 'Please check the progress <a href="%s"> actions </a>' % (REPO_ACTIONS_URL)
        messages.success(request,  x_message, extra_tags='safe')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'replica.html')

def debug(request):
    payload = {}
    if request.method == 'POST':
        for name, value in request.POST.items():
            if name != "csrfmiddlewaretoken":
                payload[name] = value
        data = {'event_type': "debug", 'client_payload': payload}
        data1 = json.dumps(data)

        x_headers = {'Accept': 'application/vnd.github.everest-preview+json', 'Authorization': "token %s" % (GIT_TOKEN)}
        r = requests.post(ACTIONS_URL, data=data1, headers=x_headers)
        messages.add_message(request, messages.INFO, "Update deployments debug")
        x_message = 'Please check the progress <a href="%s"> actions </a>' % (REPO_ACTIONS_URL)
        messages.success(request,  x_message, extra_tags='safe')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'debug.html')


def vm_power(request):

    if request.method == 'POST':
        POWER=request.POST.get('power')
        data = {'event_type': "vm Zalenium",
                'client_payload': {"POWER": POWER, "resource_group": "Functional-tests", "vm_name": "zalenium"}}
        data1 = json.dumps(data)

        x_headers = {'Accept': 'application/vnd.github.everest-preview+json', 'Authorization': "token %s" % (GIT_TOKEN)}
        r = requests.post(ACTIONS_URL, data=data1, headers=x_headers)
        if POWER == "on":
            messages.add_message(request, messages.INFO, "Starting Zalenium VM")
        else:
            messages.add_message(request, messages.INFO, "Stopping Zalenium VM")
        x_message = 'Please check the progress <a href="%s"> actions </a>' % (REPO_ACTIONS_URL)
        messages.success(request,  x_message, extra_tags='safe')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'azure-vm.html')

def functional_tests(request):

    if request.method == 'POST':
        VERSION=request.POST.get('Version')
        ENVIRONMENT=request.POST.get('Environment')
        SUITE=request.POST.get('Suite')
        CUSTOM_LOCALE = request.POST.get('Custom_locale')
        BPR_SITES = request.POST.get('BPR_sites')
        LOCALE_EN = request.POST.get('Locale_en')
        LOCALE_NON_EN = request.POST.get('Locale_non_en')
        LOCALE_ALL = request.POST.get('Locale_all')
        CLUSTER = request.POST.get('Cluster')
        HUB = request.POST.get('Hub')
        DOCKER_TAG = request.POST.get('Docker tag')
        if CLUSTER == "dcos":
            x_message = "Test build %s on environment %s, suite %s, on %s cluster" % (VERSION, ENVIRONMENT, SUITE, CLUSTER)
            data = {'event_type': "functional-tests",
                    'client_payload': {"version_tag": VERSION, "ENVIRONMENT": ENVIRONMENT, "SUITE": SUITE, "CUSTOM_LOCALE": CUSTOM_LOCALE, "BPR_SITES": BPR_SITES,
                                       "LOCALE_EN": LOCALE_EN, "LOCALE_NON_EN": LOCALE_NON_EN, "LOCALE_ALL": LOCALE_ALL,
                                       "resource_group": "Functional-tests", "vm_name": "zalenium"}}
            data1 = json.dumps(data)

            x_headers = {'Accept': 'application/vnd.github.everest-preview+json', 'Authorization': "token %s" % (GIT_TOKEN)}
            r = requests.post(ACTIONS_URL_FT, data=data1, headers=x_headers)
            messages.add_message(request, messages.INFO, "Starting functional-tests")
            x_message = 'Please check the progress <a href="%s"> actions </a>' % (REPO_ACTIONS_URL_FT)
            messages.success(request,  x_message, extra_tags='safe')
            return HttpResponseRedirect('/')
        else:
            x_message = "Test build %s on environment %s, suite %s, on %s cluster" % (VERSION, ENVIRONMENT, SUITE, CLUSTER)
            data = {'event_type': "functional-tests-aks",
                    'client_payload': {"version_tag": VERSION, "ENVIRONMENT": ENVIRONMENT, "SUITE": SUITE, "CUSTOM_LOCALE": CUSTOM_LOCALE, "BPR_SITES": BPR_SITES,
                                       "LOCALE_EN": LOCALE_EN, "LOCALE_NON_EN": LOCALE_NON_EN, "LOCALE_ALL": LOCALE_ALL, "HUB": HUB, "DOCKER_TAG": DOCKER_TAG}}
            data1 = json.dumps(data)

            x_headers = {'Accept': 'application/vnd.github.everest-preview+json', 'Authorization': "token %s" % (GIT_TOKEN)}
            r = requests.post(ACTIONS_URL, data=data1, headers=x_headers)
            messages.add_message(request, messages.INFO, "Starting aks functional-tests")
            x_message = 'Please check the progress <a href="%s"> actions </a>' % (REPO_ACTIONS_URL)
            messages.success(request,  x_message, extra_tags='safe')
            return HttpResponseRedirect('/')
    else:
        return render(request, 'functional_tests.html')