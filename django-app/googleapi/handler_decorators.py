from oauth2client.client import HttpAccessTokenRefreshError
from googleapi.oauth2.authorization import get_stored_credentials, refresh_stored_credentials


def handle_expired_token(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpAccessTokenRefreshError:
            # Invoke the code responsible for get a new token
            # request_new_token()
            print("The access token is expired or revoked. Refresh Invoked.")
            status = refresh_stored_credentials(1)

            # once the token is refreshed, we can retry the operation
            if status:
                return func(*args, **kwargs)

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