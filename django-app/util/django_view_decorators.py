from django.http import HttpResponseRedirect, HttpResponse
import json
from googleapi.oauth2.authorization import get_stored_credentials
from django.shortcuts import render


def redirect_to_admin_for_unauthenticated(func):
    def wrapper(*args, **kwargs):
        if len(args) < 1:
            raise RuntimeError("Expecting request parameter at position 0")

        request = args[0]
        if not request.user.is_authenticated:
            return HttpResponseRedirect('admin')

        return func(*args, **kwargs)

    return wrapper


def authenticated_api(func):
    def wrapper(request):
        user = request.user

        creds = get_stored_credentials(user.id)
        # print("{}(): credentials={}".format(func.__name__, creds))

        result_dict = {'api': func.__name__}
        if creds is not None:
            kwargs = {'credentials' : creds}
            response = func(request, **kwargs)
            result_dict ['status'] = 'Authenticated'
            try:
                result_dict ['response'] = json.dumps(response, indent=4)
            except TypeError as e:
                print("Serialization error: {}".format(e))
        else:
            result_dict ['status'] = 'Unauthenticated'

        return render(request, 'api.html', result_dict)

    return wrapper
