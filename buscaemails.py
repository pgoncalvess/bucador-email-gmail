
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

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Buscador de Emails'

def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'buscador-email.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)

        print('Storing credentials to ' + credential_path)
    return credentials

def get_service():
   credentials = get_credentials()
   http = credentials.authorize(httplib2.Http())
   return discovery.build('gmail', 'v1', http=http)

def main():
    #Parametros do email
    userId = 'me'
    query = 'DevOps label:inbox'

    #Parametros de conexao
    connection_string = {
        'user': 'root',
        'password': '',
        'host': '127.0.0.1',
        'database': 'testeInternalSistem',
        'port': '3306'
    }

    print('Buscando os e-mails. Parametro de busca: ' + query)
    service = get_service()
    results = service.users().messages().list(userId=userId, q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print('Nenhuma mensagem encontrada.')
    else:
        print(str(len(messages)) + ' mensagens encontradas')
        print('Salvando mensagens')
        try:
          cnx = mysql.connector.connect(**connection_string)
          cursor = cnx.cursor()

          for message in messages:
            result = service.users().messages().get(userId=userId, id=message['id']).execute()
            headers = result['payload'].get('headers', [])

            data, origem, assunto = '', '', ''
            for header in headers:
                if header['name'] == 'Date':
                    data = header['value']
                elif header['name'] == 'From':
                    origem = header['value']
                elif header['name'] == 'Subject':
                    assunto = header['value']

            dt = data.split(" -")[0]
            dt = dt.split(" +")[0]
            insert_clause = ("INSERT INTO email (email_id, data_recebimento, origem, assunto) VALUES (%s, %s, %s, %s)")
            values = (message['id'], datetime.strptime(dt, "%a, %d %b %Y %H:%M:%S"), origem, assunto)

            cursor.execute(insert_clause, values)

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Usuario ou senha parecem estar errados")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("O banco que voce esta tentando acessar nao existe")
            else:
                print(err)
        else:
            cnx.commit()
            cursor.close()
            cnx.close()
            print('Todas as mensagens foram salvas')


if __name__ == '__main__':
    main()