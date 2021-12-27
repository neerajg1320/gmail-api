from oauth2client.client import HttpAccessTokenRefreshError
from googleapi.authorization import refresh_stored_credentials


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