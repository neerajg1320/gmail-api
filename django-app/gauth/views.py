from oauth2client.client import flow_from_clientsecrets
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest
# from oauth2client.contrib.django_util.storage import DjangoORMStorage
from oauth2client.contrib import xsrfutil
from .models import CredentialsModel
from django.shortcuts import render
from googleapi.oauth2.authorization import (get_authorization_url, exchange_code,
                                     get_credentials_using_authorization_code,
                                     get_stored_credentials, store_credentials,
                                     refresh_stored_credentials)
from googleapi.gmail.labels import get_labels
from googleapi.gmail.emails import show_emails
from googleapi.gdrive.list import list_files, list_folders

from googleapiclient.discovery import build
import json
from googleapi.django_googleapi_decorators import (handle_expired_token, force_refresh_token,
                                                   refresh_token_on_expiry_deletion)
from util.django_view_decorators import redirect_to_admin_for_unauthenticated, authenticated_api


REDIRECT_URI = 'http://127.0.0.1:8000/oauth2callback'


# @handle_expired_token
# @force_refresh_token
@refresh_token_on_expiry_deletion
@redirect_to_admin_for_unauthenticated
def home(request):
    user = request.user
    credentials = get_stored_credentials(user.id)
    if credentials is not None:
        print("home(): access_token={}".format(credentials.access_token))

    status = credentials is not None

    return render(request, 'index.html', {'status': status, 'user': request.user})


@refresh_token_on_expiry_deletion
@redirect_to_admin_for_unauthenticated
@authenticated_api
def labels(request, credentials=None):
    return get_labels(credentials)


@refresh_token_on_expiry_deletion
@redirect_to_admin_for_unauthenticated
@authenticated_api
def credentials(request, credentials=None):
    return json.loads(credentials.to_json())


# Function to force refresh the access token
@refresh_token_on_expiry_deletion
@redirect_to_admin_for_unauthenticated
@authenticated_api
def refresh(request, credentials=None):
    status = refresh_stored_credentials(request.user.id)
    return {'api': 'refresh', 'status': status}


@refresh_token_on_expiry_deletion
@redirect_to_admin_for_unauthenticated
@authenticated_api
def list(request, credentials=None):
    return list_folders(credentials)


# The following definition has been kept for reference.
# The list() function looked like following before we made it an api using decorator
@refresh_token_on_expiry_deletion
@redirect_to_admin_for_unauthenticated
def list_without_decorator(request):
    user = request.user
    credentials = get_stored_credentials(user.id)
    print("home(): credentials={}".format(credentials))

    status = credentials is not None

    result_dict = {'api': 'list'}

    if credentials is not None:
        files = list_folders(credentials)
        result_dict ['response'] = json.dumps(files, indent=4)

    return render(request, 'api.html', result_dict)


def gmail_authenticate(request):
    user = request.user
    uri = request.GET.get('uri')
    print("gmail_authenticate() user={} method={} uri={}".format(user, request.method, uri))

    # email = 'neerajgupta.finance@gmail.com'
    email = None
    state = uri

    authorization_request_url = get_authorization_url(email, state, REDIRECT_URI)
    print('gmail_authenticate(): authorization_request_url={}'.format(authorization_request_url))

    return HttpResponseRedirect(authorization_request_url)


def auth_return(request):
    user = request.user
    print("auth_return() user={}".format(user))

    # state = bytes(request.GET.get('state'), 'utf8')
    state = request.GET.get('state')
    authorization_code = request.GET.get('code')
    print("auth_return(): state={} authorization_code={}".format(state, authorization_code))

    user_id = request.user.id
    uri = state

    # Works
    credentials = exchange_code(user_id, authorization_code, REDIRECT_URI)
    store_credentials(user_id, credentials)

    # credentials = get_credentials_using_authorization_code(authorization_code, 'BAD', REDIRECT_URI)

    print("Redirecting after successful operation")
    if uri is None:
        uri = "/"

    return HttpResponseRedirect(uri)


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
