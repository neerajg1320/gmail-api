from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def list_files(credentials):
    try:
        # Call the Gmail API
        service = build('drive', 'v3', credentials=credentials)

        # request a list of all the messages

        response = service.files().list().execute()
        files = response.get('files')

        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = service.files().list().execute()
            files.extend(response.get('files'))
            nextPageToken = response.get('nextPageToken')

        if files is not None:
            print("list_files(): files={}".format(len(files)))
            # print("Total Files: {}".format(len(response.items)))
            for file in files:
                print(file)
        return files
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

# https://developers.google.com/drive/api/v3/search-files#python
def list_folders(credentials):
    try:
        # Call the Gmail API
        service = build('drive', 'v3', credentials=credentials)

        # request a list of all the messages

        response = service.files().list(
            q="mimeType='application/vnd.google-apps.folder'",
            fields='nextPageToken, files(id, name)'
        ).execute()
        files = response.get('files')

        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = service.files().list().execute()
            files.extend(response.get('files'))
            nextPageToken = response.get('nextPageToken')

        if files is not None:
            print("list_files(): files={}".format(len(files)))
            # print("Total Files: {}".format(len(response.items)))
            for file in files:
                print(file)
        return files
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
