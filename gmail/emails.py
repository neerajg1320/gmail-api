from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup


def show_emails(credentials):
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=credentials)

        # request a list of all the messages
        result = service.users().messages().list(userId='me').execute()

        # We can also pass maxResults to get any number of emails. Like this:
        # result = service.users().messages().list(maxResults=200, userId='me').execute()
        messages = result.get('messages')
        print("Got {} messages".format(len(messages)))

        for msg in messages[0:2]:
            # print(msg)
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            # print(txt)
            payload = txt['payload']
            headers = payload['headers']

            sender = None
            subject = None
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']

            if sender is not None and subject is not None:
                if "axisdirect" in sender:
                    print("sender:{} subject:{}".format(sender, subject))

            parts = payload.get('parts')[0]
            data = parts['body']['data']
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data)

            # Now, the data obtained is in lxml. So, we will parse
            # it with BeautifulSoup library
            soup = BeautifulSoup(decoded_data , "lxml")
            body = soup.body()

            # Printing the subject, sender's email and message
            print("Subject: ", subject)
            print("From: ", sender)
            print("Message: ", body)
            print('\n')


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')