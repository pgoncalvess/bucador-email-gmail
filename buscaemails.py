
from __future__ import print_function
import httplib2
import os
import mysql.connector
import datetime

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python BuscaEmails'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-buscaemails.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    userId = 'me'
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().messages().list(userId=userId, q='pedrinho label:inbox', maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found.')
    else:
      print('Messages:')
      cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='testeInternalSistem')
      cursor = cnx.cursor()

      for message in messages:
        result = service.users().messages().get(userId=userId, id=message['id']).execute()
        headers = result['payload'].get('headers', [])
        data, origem, assunto, idMensagem = '', '', '', ''

        for header in headers:
            if header['name'] == 'Date':
                data = header['value']
            elif header['name'] == 'From':
                origem = header['value']
            elif header['name'] == 'Subject':
                assunto = header['value']

        data = data.split(" -")[0]
        print('Id: ' + idMensagem)
        print('Data: ' + data)
        print('Origem: ' + origem)
        print('Assunto: ' + assunto)

        dt = datetime.strptime(data, "%a, %d %b %Y %H:%M:%S")

        cursor.execute("INSERT INTO email (email_id, data_recebimento, origem, assunto) values (%s, %s, %s, %s)", (message['id'], dt, origem, assunto))

    cnx.commit()
    cursor.close()
    cnx.close()


if __name__ == '__main__':
    main()