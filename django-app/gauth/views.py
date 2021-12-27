from oauth2client.client import flow_from_clientsecrets
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest
# from oauth2client.contrib.django_util.storage import DjangoORMStorage
from oauth2client.contrib import xsrfutil
from .models import CredentialsModel
from django.shortcuts import render
from googleapi.authorization import (get_authorization_url, exchange_code,
                                     get_credentials_using_authorization_code,
                                     get_stored_credentials, store_credentials,
                                     refresh_stored_credentials)
from googleapi.gmail.labels import show_labels
from googleapi.gmail.emails import show_emails
from googleapi.gdrive.list import list_files, list_folders

from googleapiclient.discovery import build
import json



REDIRECT_URI = 'http://127.0.0.1:8000/oauth2callback'


def home(request):
    user = request.user
    print("home() user={}".format(user))

    if not request.user.is_authenticated:
        return HttpResponseRedirect('admin')

    credentials = get_stored_credentials(user)
    if credentials is not None:
        print("home(): access_token={}".format(credentials.access_token))

    status = credentials is not None

    if credentials is not None:
        show_labels(credentials)

    return render(request, 'index.html', {'status': status})


def credentials(request):
    user = request.user
    print("home() user={}".format(user))

    if not request.user.is_authenticated:
        return HttpResponseRedirect('admin')

    credentials = get_stored_credentials(user)
    if credentials:
        # Create a dict
        raw_json_str = credentials.to_json()
        pretty_json = json.dumps(json.loads(raw_json_str), indent=4)

    result_dict = {'api': 'credentials', 'credentials': pretty_json}
    return render(request, 'api.html', result_dict)


def refresh(request):
    user = request.user
    print("home() user={}".format(user))

    if not request.user.is_authenticated:
        return HttpResponseRedirect('admin')

    status = refresh_stored_credentials(user)

    result_dict = {'api': 'refresh', 'status': status}
    return render(request, 'api.html', result_dict)


def list(request):
    user = request.user
    print("list() user={}".format(user))

    if not request.user.is_authenticated:
        return HttpResponseRedirect('admin')

    credentials = get_stored_credentials(user)
    print("home(): credentials={}".format(credentials))

    status = credentials is not None

    if credentials is not None:
        list_folders(credentials)

    return render(request, 'index.html', {'status': status})



def gmail_authenticate(request):
    user = request.user
    print("gmail_authenticate() user={}".format(user))

    email = 'neerajgupta.finance@gmail.com'
    state = 'GOOD'

    authorization_request_url = get_authorization_url(email, state, REDIRECT_URI)
    print('gmail_authenticate(): authorization_request_url={}'.format(authorization_request_url))

    return HttpResponseRedirect(authorization_request_url)


def auth_return(request):
    user = request.user
    print("auth_return() user={}".format(user))

    state = bytes(request.GET.get('state'), 'utf8')
    authorization_code = request.GET.get('code')
    print("auth_return(): state={} authorization_code={}".format(state, authorization_code))

    # Works
    credentials = exchange_code(authorization_code, REDIRECT_URI)
    store_credentials(user, credentials)
    # credentials = get_credentials_using_authorization_code(authorization_code, 'BAD', REDIRECT_URI)

    print("Redirecting after successful operation")

    return HttpResponseRedirect("/")


def gmail_authenticate_old(request):
    FLOW = flow_from_clientsecrets(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scope='https://www.googleapis.com/auth/gmail.readonly',
        redirect_uri=REDIRECT_URI,
        prompt='consent')

    storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()

    if credential is None or credential.invalid:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build('gmail', 'v1', http = http)
        print('access_token = ', credential.access_token)
        status = True

        return render(request, 'index.html', {'status': status})


def auth_return_old(request):
    get_state = bytes(request.GET.get('state'), 'utf8')
    if not xsrfutil.validate_token(settings.SECRET_KEY, get_state,
                                   request.user):
        return HttpResponseBadRequest()

    credential = FLOW.step2_exchange(request.GET.get('code'))
    storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)

    print("access_token: % s" % credential.access_token)
    return HttpResponseRedirect("/")


def home_old(request):
    status = True

    if not request.user.is_authenticated:
        return HttpResponseRedirect('admin')

    storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()

    try:
        access_token = credential.access_token
        resp, cont = Http().request("https://www.googleapis.com/auth/gmail.readonly",
                                    headers ={'Host': 'www.googleapis.com',
                                              'Authorization': access_token})
    except:
        status = False
        print('Not Found')

    return render(request, 'index.html', {'status': status})
