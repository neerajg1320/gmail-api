from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup
import os


def getEmails(credentials, maxResults=10, headers_all=True, attachment_folder=None, debug=True):
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=credentials)

        # request a list of all the messages
        result = service.users().messages().list(maxResults=maxResults, userId='me').execute()

        # We can also pass maxResults to get any number of emails. Like this:
        # result = service.users().messages().list(maxResults=200, userId='me').execute()
        messages = result.get('messages')
        if debug:
            print("Got {} messages".format(len(messages)))

        read_headers = ['Content-Type', 'Subject', 'From']
        emails = []
        count = 0
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            txt_payload = txt['payload']

            payload_headers = txt_payload['headers']
            payload_body = txt_payload['body']
            payload_parts = txt_payload.get('parts', None)
            payload_mime_type = txt_payload['mimeType']

            # Process headers
            headers = {}
            body_text = ''
            for d in payload_headers:
                if headers_all or d['name'] in read_headers:
                        headers[d['name']] = d['value']

            print('\nSubject={}'.format(headers['Subject']))
            print('mimeType={}'.format(payload_mime_type))

            if debug:
                print("  txt.keys()={}".format(list(txt.keys())))
                print("  payload.keys()={}".format(list(txt_payload.keys())))
                print("  headers.keys()={}".format(list(map(lambda ent: ent['name'], payload_headers))))

            # Process body
            if 'multipart' in payload_mime_type:
                if payload_parts is not None:
                    for part in payload_parts:
                        part_keys = list(part.keys())
                        print("    partId={} filename='{}' part.keys()={}".format(
                            part['partId'], part['filename'], part_keys
                        ))
                        if 'body' in part_keys:
                            part_body = part['body']
                            part_body_keys = list(part_body.keys())
                            print('    part_body_keys={}'.format(part_body_keys))
                            print("        part['body']['size']={}  part['filename']={}".format(
                                part_body['size'], part_body.get('filename', None)
                            ))

                            part_headers = part['headers']
                            p_headers = {}
                            for d in part_headers:
                                p_headers[d['name']] = d['value']
                            print("        part['headers'].keys={}  part['headers'].values={}".format(
                                p_headers.keys(), p_headers.values()
                            ))

                            if 'data' in part_body:
                                data = part_body['data']

                                # Now, the data obtained is in lxml. So, we will parse
                                # it with BeautifulSoup library
                                if 'html' in payload_mime_type:
                                    # Why is this here?
                                    data = data.replace("-","+").replace("_","/")
                                    decoded_data = base64.b64decode(data)
                                    soup = BeautifulSoup(decoded_data , "lxml")
                                    body_text = soup.body()
                                else:
                                    # Copied code
                                    #data = payload_body['data']
                                    data = data.replace("-","+").replace("_","/")
                                    bytes = base64.b64decode(data)
                                    body_text += bytes.decode('utf-8')

                            # Process attachments
                            # if part_body.get('attachmentId', None):
                            if part['filename'] or part_body.get('attachmentId', None):
                                if part['filename']:
                                    file_name = part['filename']
                                else:
                                    part_content_type = p_headers['Content-Type']
                                    extn = part_content_type.split("/")[1]
                                    file_name = "email{}_part{}.{}".format(count, part['partId'], extn)

                                if 'data' in part['body']:
                                    print("        len(part['body']['data'])={}".format(len(part['body']['data'])))
                                    data = part['body']['data']
                                else:
                                    att_id = part['body']['attachmentId']
                                    att = service.users().messages().attachments().get(userId='me', messageId=msg['id'],id=att_id).execute()
                                    data = att['data']
                                    print("        attachmentId={}".format(att_id))
                                    print("        len(att['data'])={}".format(len(data)))

                                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                                print("        len(file_data)={}".format(len(file_data)))
                                path = os.path.join(attachment_folder, file_name) if attachment_folder is not None else file_name

                                print("    Saving attachment: path={}", path)
                                with open(path, 'wb') as f:
                                    f.write(file_data)
                        else:
                            print("getEmails(): data not present in partId={}".format(part['partId']))
                else:
                    raise RuntimeError("payload['parts'] not found in multipart email")
            else:
                print('    payload.body.keys()={}'.format(list(payload_body.keys())))
                data = payload_body['data']
                data = data.replace("-","+").replace("_","/")
                bytes = base64.b64decode(data)
                body_text = bytes.decode('utf-8')

            # Process remaining payload
            payload = {}
            for k,v in txt_payload.items():
                if k != 'headers' and k != 'body':
                    payload[k] = v

            email = {}
            email['headers'] = headers
            email['body_text'] = body_text
            email['payload'] = payload

            emails.append(email)

            count += 1

        return emails

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
