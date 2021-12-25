from oauth2client.client import flow_from_clientsecrets
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from oauth2client.contrib.django_util.storage import DjangoORMStorage
from oauth2client.contrib import xsrfutil
from .models import CredentialsModel
from django.shortcuts import render
from gmail.authorization import get_authorization_url, exchange_code
from gmail.labels import show_labels
from gmail.emails import show_emails


REDIRECT_URI = 'http://127.0.0.1:8000/oauth2callback'


def home(request):
    status = False

    if not request.user.is_authenticated:
        return HttpResponseRedirect('admin')

    return render(request, 'index.html', {'status': status})


def gmail_authenticate(request):
    email = 'neerajgupta.finance@gmail.com'
    state = 'GOOD'

    authorization_request_url = get_authorization_url(email, state, REDIRECT_URI)
    print('gmail_authenticate(): authorization_request_url={}'.format(authorization_request_url))

    return HttpResponseRedirect(authorization_request_url)


def auth_return(request):
    state = bytes(request.GET.get('state'), 'utf8')
    authorization_code = request.GET.get('code')
    print("auth_return(): state={} authorization_code={}".format(state, authorization_code))

    # credential = FLOW.step2_exchange(authorization_code)
    credential = exchange_code(authorization_code, REDIRECT_URI)

    # show_labels(credential)

    show_emails(credential)

    print("access_token: % s" % credential.access_token)
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
