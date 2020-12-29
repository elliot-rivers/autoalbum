'''Google OAuth2 utilities

TODO sources
'''

import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata',
    'https://www.googleapis.com/auth/photoslibrary.appendonly',
    'https://www.googleapis.com/auth/photoslibrary.readonly',
]

def get_service(client_config, scopes=None):
    '''Create an authenticated google APIClient service

    Args:
        client_config (dict): Contents of a client_secret.json (or similarly named) file from the
            Google API Console.
        scopes (list, optional): A list of scope strings for which to authenticate.
            (Default: :data:`autoalbum.auth.DEFAULT_SCOPES`)
            See: https://developers.google.com/photos/library/guides/authorization

    Returns:
        tuple: The service instance and login credentials object used for authentication
    '''
    scopes = scopes or DEFAULT_SCOPES

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_config, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('photoslibrary', 'v1', credentials=creds)
    return service, creds
