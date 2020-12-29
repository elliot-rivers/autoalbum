'''Defines a convenience API for Google Photos for the needs of this project
'''
from autoalbum.auth import get_service

class API:
    '''Basic, convenience API for required Google Photos functionality

    Probably construct this with :meth:`autoalbum.API.new`. That's what it's there for.

    Args:
        service: The service instance from :func:`autoalbum.auth.get_service`
        creds: The login credentials object from :func:`autoalbum.auth.get_service`
    '''

    @staticmethod
    def new(client_config, scopes=None):
        '''Static factory method for API

        Args:
            client_config (dict): Contents of a client_secret.json (or similarly named) file from
                the Google API Console.
            scopes (list, optional): A list of scope strings for which to authenticate.
                (Default: :data:`autoalbum.auth.DEFAULT_SCOPES`)
                See: https://developers.google.com/photos/library/guides/authorization

        Returns:
            API: API instance
        '''
        return API(*get_service(client_config, scopes))

    def __init__(self, service, creds):
        self.service = service
        self.creds = creds

    def list_albums(self, is_shared=False, page_token=None):
        '''Get a list of albums and metadata

        Args:
            is_shared (bool, optional): True if you want to get albums shared with you rather than
                ones you own. Default False
            page_token (str): Continuation token to get the next page of results

        Returns:
            list: List of albums' metadata (and pageToken, if present)
        '''
        album_attr = 'sharedAlbums' if is_shared else 'albums'
        albums = getattr(self.service, album_attr)().list(pageToken=page_token).execute()
        return albums

    def list_all_albums(self, is_shared=False):
        '''Get a list of all albums and metadata

        Args:
            is_shared (bool, optional): True if you want to get albums shared with you rather than
                ones you own. Default False

        Returns:
            list: List of albums' metadata
        '''
        albums = []
        page_token = None
        album_attr = 'sharedAlbums' if is_shared else 'albums'

        while True:
            # Could have done fancy stuff with a generator I guess :shrug:
            albums_page = self.list_albums(is_shared, page_token)
            albums += albums_page[album_attr]
            if 'pageToken' in albums_page:
                page_token = albums_page['pageToken']
            else:
                break
        return albums

    def create_album(self, album_title):
        '''Create a new album by title

        Args:
            album_title (str): Title to assign to new album

        Returns:
            dict: New album metadata
        '''
        album = self.service.albums().create(body={'album': {'title':album_title}}).execute()
        return album
