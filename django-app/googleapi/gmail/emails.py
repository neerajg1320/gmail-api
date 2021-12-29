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

        for index, msg in enumerate(messages):
            msg = service.users().messages().get(userId='me', id=msg['id']).execute()
            msg_payload = msg['payload']

            payload_headers = msg_payload['headers']
            payload_body = msg_payload['body']
            payload_parts = msg_payload.get('parts', None)
            payload_mime_type = msg_payload['mimeType']

            # Process headers
            headers = {}
            body_text = ''
            for d in payload_headers:
                if headers_all or d['name'] in read_headers:
                        headers[d['name']] = d['value']

            print('\nSubject={}'.format(headers['Subject']))
            print('mimeType={}'.format(payload_mime_type))

            if debug:
                print("  msg.keys()={}".format(list(msg.keys())))
                print("  payload.keys()={}".format(list(msg_payload.keys())))
                print("  payload_headers.keys()={}".format(list(map(lambda ent: ent['name'], payload_headers))))
                print("  payload_body.keys()={}".format(list(payload_body.keys())))

            email_attachment_folder = os.path.join(attachment_folder, "email{}".format(index))
            # Process body
            if 'multipart' in payload_mime_type:
                if payload_parts is not None:
                    for part in payload_parts:
                        body_text, part_body_file_name = process_part(part, service, index, msg, email_attachment_folder)
                        print("    len(body_text)={}  part_body_file_name={}".format(len(body_text), part_body_file_name))
                        if part_body_file_name is not None:
                            save_body_file(body_text, email_attachment_folder, part_body_file_name)
            else:
                print('    payload.body.keys()={}'.format(list(payload_body.keys())))
                data = payload_body['data']
                data = data.replace("-","+").replace("_","/")
                bytes = base64.b64decode(data)
                body_text = bytes.decode('utf-8')

                body_extn = get_extn_from_mime_type(payload_mime_type)
                body_file_name = "email{}_body_noparts.{}".format(index, body_extn)
                save_body_file(body_text, email_attachment_folder, body_file_name)

            # Process remaining payload
            payload = {}
            for k,v in msg_payload.items():
                if k != 'headers' and k != 'body':
                    payload[k] = v

            email = {}
            email['headers'] = headers
            email['body_text'] = body_text
            email['payload'] = payload



            emails.append(email)

        return emails

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def save_body_file(body_text, email_attachment_folder, part_body_file_name):
    if not os.path.exists(email_attachment_folder):
        os.makedirs(email_attachment_folder)
    path = os.path.join(email_attachment_folder,
                        part_body_file_name) if email_attachment_folder is not None else part_body_file_name
    print("    Saving body: path={} ", path)
    with open(path, 'w') as f:
        f.write(body_text)


def process_part(part, service, index, msg, email_attachment_folder):
    part_keys = list(part.keys())
    print("    partId={} filename='{}' part.keys()={}".format(
        part['partId'], part['filename'], part_keys
    ))

    part_headers = part['headers']
    p_headers = {}
    for d in part_headers:
        p_headers[d['name']] = d['value']
    print("        part['headers'].keys={}  part['headers'].values={}".format(
        p_headers.keys(), p_headers.values()
    ))

    part_content_type = p_headers['Content-Type']
    part_content_encoding = p_headers.get('Content-Transfer-Encoding', None)
    body_extn = get_extn_from_content_type(part_content_type)
    body_file_name = "email{}_part{}.{}".format(index, part['partId'], body_extn)

    body_text = ''

    if 'parts' in part_keys:
        sub_parts = part['parts']
        print("    ** We have a part which has parts. len(part['parts']={})".format(len(sub_parts)))
        for spart in sub_parts:
            body_text, body_file_name = process_part(spart, service, index, msg, email_attachment_folder)

    if 'body' in part_keys:
        part_body = part['body']
        part_body_keys = list(part_body.keys())
        print('    part_body_keys={}'.format(part_body_keys))
        print("        part['body']['size']={}  part['filename']={}".format(
            part_body['size'], part_body.get('filename', None)
        ))

        if 'data' in part_body:
            data = part_body['data']
            data = data.replace("-","+").replace("_","/")
            bytes = base64.b64decode(data)
            body_text += bytes.decode('utf-8')

        # Process attachments
        # if part_body.get('attachmentId', None):
        if part['filename'] or part_body.get('attachmentId', None):
            body_file_name = None
            if part['filename']:
                file_name = part['filename']
            else:
                part_content_type = p_headers['Content-Type']
                # print("part_content_type={}".format(part_content_type))
                extn = get_extn_from_content_type(part_content_type)
                file_name = "email{}_part{}.{}".format(index, part['partId'], extn)

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
            path = os.path.join(email_attachment_folder, file_name) if email_attachment_folder is not None else file_name

            print("    Saving attachment: path={}", path)
            path_dir = os.path.dirname(path)
            if not os.path.exists(path_dir):
                os.makedirs(path_dir)
            with open(path, 'wb') as f:
                f.write(file_data)
    else:
        print("getEmails(): data not present in partId={}".format(part['partId']))

    return body_text, body_file_name


def get_extn_from_content_type(content_type):
    return content_type.split(";")[0].split("/")[1]


def get_extn_from_mime_type(mime_type):
    return mime_type.split('/')[1]
