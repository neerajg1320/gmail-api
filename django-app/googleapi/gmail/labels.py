from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapi.error_handlers import handle_expired_token


@handle_expired_token
def show_labels(credentials):
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=credentials)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')