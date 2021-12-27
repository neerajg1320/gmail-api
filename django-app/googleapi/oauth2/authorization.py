# https://developers.google.com/gmail/api/auth/web-server


import logging
import os
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from apiclient.discovery import build
import httplib2
from google.oauth2.credentials import Credentials
from oauth2client.client import OAuth2Credentials, TokenRevokeError


# Path to client_secrets.json which should contain a JSON document such as:
#   {
#     "web": {
#       "client_id": "[[YOUR_CLIENT_ID]]",
#       "client_secret": "[[YOUR_CLIENT_SECRET]]",
#       "redirect_uris": [],
#       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#       "token_uri": "https://accounts.google.com/o/oauth2/token"
#     }
#   }
CLIENTSECRETS_LOCATION = 'client_secret.json'

GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    # Add other requested scopes.
]

GDRIVE_SCOPES = [

    'https://www.googleapis.com/auth/drive.metadata.readonly'
]


CREDENTIALS_LOCATION = 'credentials.json'
CREDENTIALS_REFRESH_LOCATION = 'credentials_refresh.json'


class GetCredentialsException(Exception):
    """Error raised when an error occurred while retrieving credentials.

    Attributes:
      authorization_url: Authorization URL to redirect the user to in order to
                         request offline access.
    """

    def __init__(self, authorization_url):
        """Construct a GetCredentialsException."""
        self.authorization_url = authorization_url


class NoCredentialsException(GetCredentialsException):
    """Error raised when credentials file is not found."""

class CodeExchangeException(GetCredentialsException):
    """Error raised when a code exchange has failed."""


class NoRefreshTokenException(GetCredentialsException):
    """Error raised when no refresh token has been found."""


class NoUserIdException(Exception):
    """Error raised when no user ID could be retrieved."""


def refresh_stored_credentials(user_id, debug=False):
    """Retrieved stored credentials for the provided user ID.

    Args:
      user_id: User's ID.
    Returns:
      Stored oauth2client.client.OAuth2Credentials if found, None otherwise.
    Raises:
      NotImplemented: This function has not been implemented.
    """
    # TODO: Implement this function to work with your database.
    #       To instantiate an OAuth2Credentials instance from a Json
    #       representation, use the oauth2client.client.Credentials.new_from_json
    #       class method.
    if debug:
        print("refresh_stored_credentials(): user_id={}".format(user_id))

    status = False
    credentials = get_stored_credentials(user_id, refresh_token_needed=True)
    h = httplib2.Http()
    # h = credentials.authorize(h)
    if debug:
        print("refresh_stored_credentials(): type(credentials)={} h={}".format(type(credentials), h))
    try:
        credentials.refresh(h)
        status = True
        store_credentials(user_id, credentials)
    except TokenRevokeError as e:
        print("Error revoke: {}".format(e))

    return status


def revoke_stored_credentials(user_id):
    """Retrieved stored credentials for the provided user ID.

    Args:
      user_id: User's ID.
    Returns:
      Stored oauth2client.client.OAuth2Credentials if found, None otherwise.
    Raises:
      NotImplemented: This function has not been implemented.
    """
    # TODO: Implement this function to work with your database.
    #       To instantiate an OAuth2Credentials instance from a Json
    #       representation, use the oauth2client.client.Credentials.new_from_json
    #       class method.

    status = False
    credentials = get_stored_credentials(user_id)
    h = httplib2.Http()
    # h = credentials.authorize(h)
    print("refresh_stored_credentials(): type(credentials)={} h={}".format(type(credentials), h))
    try:
        credentials.refresh(h)
        status = True
        # store_credentials(user_id, credentials)
    except TokenRevokeError as e:
        print("Error revoke: {}".format(e))

    return status


def get_credentials_path(user_id, refresh_token_present=False, create_path = False, debug=False):
    from django.conf import settings

    if refresh_token_present:
        file_name = CREDENTIALS_REFRESH_LOCATION
    else:
        file_name = CREDENTIALS_LOCATION
    storage_path = os.path.join(settings.BASE_DIR, "storage", "user_{}".format(user_id), file_name)
    storage_folder = os.path.dirname(storage_path)

    if create_path:
        if not os.path.exists(storage_folder):
            os.makedirs(storage_folder)

    if debug:
        print("get_credentials_path(): storage_path={}".format(storage_path))

    return storage_path


def get_stored_credentials(user_id, refresh_token_needed=False):
    """Retrieved stored credentials for the provided user ID.

    Args:
      user_id: User's ID.
    Returns:
      Stored oauth2client.client.OAuth2Credentials if found, None otherwise.
    Raises:
      NotImplemented: This function has not been implemented.
    """
    # TODO: Implement this function to work with your database.
    #       To instantiate an OAuth2Credentials instance from a Json
    #       representation, use the oauth2client.client.Credentials.new_from_json
    #       class method.

    credentials = None
    credentials_file_path = get_credentials_path(user_id, refresh_token_present=refresh_token_needed)
    if os.path.exists(credentials_file_path):
        with open(credentials_file_path, "r") as f:
            credentials = OAuth2Credentials.from_json(f.read())
    else:
        raise NoCredentialsException('Credentials file not found')

    return credentials


def store_credentials(user_id, credentials, debug=False):
    """Store OAuth 2.0 credentials in the application's database.

    This function stores the provided OAuth 2.0 credentials using the user ID as
    key.

    Args:
      user_id: User's ID.
      credentials: OAuth 2.0 credentials to store.
    Raises:
      NotImplemented: This function has not been implemented.
    """
    # TODO: Implement this function to work with your database.
    #       To retrieve a Json representation of the credentials instance, call the
    #       credentials.to_json() method.

    if debug:
        print("store_credentials(): refresh_token={}".format(credentials.refresh_token))

    if credentials.refresh_token is not None:
        credentials_file_path = get_credentials_path(user_id, refresh_token_present=True, create_path=True)
        print("Storing the credentials for user_id={} at {}".format(user_id, credentials_file_path))
        with open(credentials_file_path, "w") as f:
            f.write(credentials.to_json())

    credentials_file_path = get_credentials_path(user_id, create_path=True)
    credentials.refresh_token = None
    if debug:
        print("store_credentials(): Storing the credentials for user_id={} at {}".format(user_id, credentials_file_path))

    with open(credentials_file_path, "w") as f:
        f.write(credentials.to_json())


def exchange_code(user_id, authorization_code, redirect_uri):
    """Exchange an authorization code for OAuth 2.0 credentials.

    Args:
      authorization_code: Authorization code to exchange for OAuth 2.0
                          credentials.
    Returns:
      oauth2client.client.OAuth2Credentials instance.
    Raises:
      CodeExchangeException: an error occurred.
    """
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(GMAIL_SCOPES + GDRIVE_SCOPES))
    flow.redirect_uri = redirect_uri
    try:
        credentials = flow.step2_exchange(authorization_code)
        return credentials
    except FlowExchangeError as error:
        logging.error('An error occurred: %s', error)
        raise CodeExchangeException(None)


def get_user_info(credentials):
    """Send a request to the UserInfo API to retrieve the user's information.

    Args:
      credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                   request.
    Returns:
      User information as a dict.
    """
    user_info_service = build(
        serviceName='oauth2', version='v2',
        http=credentials.authorize(httplib2.Http()))
    user_info = None
    try:
        user_info = user_info_service.userinfo().get().execute()
    except errors.HttpError as e:
        logging.error('An error occurred: %s', e)
    if user_info and user_info.get('id'):
        return user_info
    else:
        raise NoUserIdException()


def get_authorization_url(email_address, state, redirect_url):
    """Retrieve the authorization URL.

    Args:
      email_address: User's e-mail address.
      state: State for the authorization URL.
    Returns:
      Authorization URL to redirect the user to.
    """
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION,
                                   ' '.join(GMAIL_SCOPES + GDRIVE_SCOPES),
                                   redirect_uri=redirect_url
                                   )
    flow.params['access_type'] = 'offline'
    # The force value causes problems if we have Gmail and GDrive present
    # flow.params['approval_prompt'] = 'force'
    if email_address is not None:
        flow.params['user_id'] = email_address
    flow.params['state'] = state
    flow.params['user_id'] = 2
    return flow.step1_get_authorize_url()


def get_credentials_using_authorization_code(authorization_code, state, redirect_uri):
    """Retrieve credentials using the provided authorization code.

    This function exchanges the authorization code for an access token and queries
    the UserInfo API to retrieve the user's e-mail address.
    If a refresh token has been retrieved along with an access token, it is stored
    in the application database using the user's e-mail address as key.
    If no refresh token has been retrieved, the function checks in the application
    database for one and returns it if found or raises a NoRefreshTokenException
    with the authorization URL to redirect the user to.

    Args:
      authorization_code: Authorization code to use to retrieve an access token.
      state: State to set to the authorization URL in case of error.
    Returns:
      oauth2client.client.OAuth2Credentials instance containing an access and
      refresh token.
    Raises:
      CodeExchangeError: Could not exchange the authorization code.
      NoRefreshTokenException: No refresh token could be retrieved from the
                               available sources.
    """
    email_address = ''
    try:
        credentials = exchange_code(authorization_code, redirect_uri)
        print("credentials:\n {} access_token={}\n refresh_token={}".format(
            type(credentials), credentials.access_token, credentials.refresh_token)
        )

        user_info = get_user_info(credentials)
        email_address = user_info.get('email')
        user_id = user_info.get('id')
        if credentials.refresh_token is not None:
            store_credentials(user_id, credentials)
            return credentials
        else:
            credentials = get_stored_credentials(user_id)
            if credentials and credentials.refresh_token is not None:
                return credentials
    except CodeExchangeException as error:
        logging.error('An error occurred during code exchange.')
        # Drive apps should try to retrieve the user and credentials for the current
        # session.
        # If none is available, redirect the user to the authorization URL.
        error.authorization_url = get_authorization_url(email_address, state)
        raise error
    except NoUserIdException:
        logging.error('No user ID could be retrieved.')

    # No refresh token has been retrieved.
    authorization_url = get_authorization_url(email_address, state, redirect_uri)
    raise NoRefreshTokenException(authorization_url)

