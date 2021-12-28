from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup


def get_emails(credentials, debug=False):
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=credentials)

        # request a list of all the messages
        result = service.users().messages().list(maxResults=10, userId='me').execute()

        # We can also pass maxResults to get any number of emails. Like this:
        # result = service.users().messages().list(maxResults=200, userId='me').execute()
        messages = result.get('messages')
        print("Got {} messages".format(len(messages)))

        emails = []
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = txt['payload']
            headers = payload['headers']

            email = {}
            for d in headers:
                if d['name'] == 'Subject':
                    email['subjet'] = d['value']
                if d['name'] == 'From':
                    email['sender'] = d['value']

            parts = payload.get('parts', None)
            if parts is not None:
                part0 = parts[0]
                if 'body' in part0 and 'data' in part0['body']:
                    data = part0['body']['data']
                    data = data.replace("-","+").replace("_","/")
                    decoded_data = base64.b64decode(data)

                    # Now, the data obtained is in lxml. So, we will parse
                    # it with BeautifulSoup library
                    soup = BeautifulSoup(decoded_data , "lxml")
                    # email['body'] = soup.body()
                else:
                    print("part0['body']['data'] not found in payload for emails={}".format(email))
            else:
                print("parts not found in payload for emails={}".format(email))

            emails.append(email)

        return emails

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
