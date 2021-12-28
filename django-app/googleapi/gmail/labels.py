from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_labels(credentials, debug=False):
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=credentials)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if debug:
            if not labels:
                print('No labels found.')
                return
            print('Labels:')
            for label in labels:
                print(label['name'])

        return labels

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
