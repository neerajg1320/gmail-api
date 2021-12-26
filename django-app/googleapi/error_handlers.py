from oauth2client.client import HttpAccessTokenRefreshError


def handle_expired_token(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpAccessTokenRefreshError:
            # Invoke the code responsible for get a new token
            # request_new_token()
            print("The access token is expired or revoked")
            # once the token is refreshed, we can retry the operation
            # return func(*args, **kwargs)
            return
        
    return wrapper