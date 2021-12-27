from oauth2client.client import HttpAccessTokenRefreshError
from googleapi.oauth2.authorization import (get_stored_credentials, refresh_stored_credentials,
                                            NoCredentialsException, NoRefreshCredentialsException)
from django.shortcuts import render



def refresh_token_on_expiry_deletion(func):
    def wrapper(*args, **kwargs):
        if len(args) < 1:
            raise RuntimeError("Expecting request parameter at position 0")

        request = args[0]
        uri = request.get_full_path()
        print("refresh_token_on_expiry_deletion(): uri={}".format(uri))

        try:
            return func(*args, **kwargs)
        except (HttpAccessTokenRefreshError, NoCredentialsException) as e:

            print("user {}: {}. Refresh Invoked.".format(request.user, e))

            try:
                status = refresh_stored_credentials(request.user.id)
            except NoRefreshCredentialsException as e:
                status = False
                print(e)
                return render(request, 'index.html', {'status': status, 'user': request.user, 'uri': uri})

            # once the token is refreshed, we can retry the operation
            if status:
                return func(*args, **kwargs)

    return wrapper


def handle_expired_token(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpAccessTokenRefreshError:
            # Invoke the code responsible for get a new token
            # request_new_token()
            request = args[0]
            print("The access token is expired or revoked for user {}.".format(request.user))
            return render(request, 'index.html', {'status': False, 'user': request.user})

    return wrapper


def force_refresh_token(func):
    def wrapper(*args, **kwargs):

        print("Force Refresh Invoked.")
        if len(args) < 1:
            raise RuntimeError("Expecting request parameter at position 0")

        request = args[0]
        try:
            status = refresh_stored_credentials(request.user.id)
        except Exception as e:
            print("force_refresh_token():", e)

        return func(*args, **kwargs)

    return wrapper
