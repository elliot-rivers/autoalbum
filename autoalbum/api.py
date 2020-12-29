'''Defines a convenience API for Google Photos for the needs of this project
'''

class API:
    '''Basic, convenience API for required Google Photos functionality

    Probably construct this with :meth:`autoalbum.API.new`. That's what it's
    there for.

    Args:
        service: The service instance from :func:`autoalbum.auth.get_service`
        creds: The login credentials object from
            :func:`autoalbum.auth.get_service`
    '''

    @staticmethod
    def new(scopes=None, cred_file=None):
        '''Static factory method for API

        Args:
            scopes (list, optional): A list of scope strings for which to
                authenticate. (Default: :data:`autoalbum.auth.DEFAULT_SCOPES`)
                See: https://developers.google.com/photos/library/guides/authorization
            cred_file (str / PathLike, optional): Path to a client_secret.json
                (or similarly named) file from the Google API Console. Default
                is './client_secret.json'

        Returns:
            API: API instance
        '''
        from autoalbum.auth import get_service
        return API(*get_service(scopes, cred_file))

    def __init__(self, service, creds):
        self.service = service
        self.creds = creds

    def get_albums(self, is_shared=False):
        '''Get a list of albums and metadata

        Args:
            is_shared (bool, optional): True if you want to get albums shared
                with you rather than ones you own. Default False

        Returns:
            list: List of albums' metadata
        '''
        album_attr = 'sharedAlbums' if is_shared else 'albums'
        albums = getattr(self.service, album_attr)().list().execute()
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
