'''Google OAuth2 utilities

TODO sources
'''

import os
from pathlib import Path
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata',
    'https://www.googleapis.com/auth/photoslibrary.appendonly',
    'https://www.googleapis.com/auth/photoslibrary.readonly',
]

def get_service(scopes=None, cred_file=None):
    '''Create an authenticated google APIClient service

    Args:
        scopes (list, optional): A list of scope strings for which to
            authenticate. (Default: :data:`autoalbum.auth.DEFAULT_SCOPES`)
            See: https://developers.google.com/photos/library/guides/authorization
        cred_file (str / PathLike, optional): Path to a client_secret.json
            (or similarly named) file from the Google API Console. Default
            is './client_secret.json'

    Returns:
        tuple: The service instance and login credentials object used for
            authentication
    '''
    scopes = scopes or DEFAULT_SCOPES
    cred_file = cred_file or Path()/'client_secret.json'

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_file, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('photoslibrary', 'v1', credentials=creds)
    return service, creds
