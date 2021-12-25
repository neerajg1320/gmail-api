from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def list_files(credentials):
    try:
        # Call the Gmail API
        service = build('drive', 'v2', credentials=credentials)

        # request a list of all the messages
        files = service.files().list().execute()

        # print("list_files(): files={}".format(files))
        print("Total Files: {}".format(len(files)))
        for file in files:
            print(file)
        return files
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
