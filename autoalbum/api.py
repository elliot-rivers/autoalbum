'''Defines a convenience API for Google Photos for the needs of this project
'''
from autoalbum.auth import get_service

def _get_paged_data(method, attr, *args):
    '''Utility function to get paged data by repeating calls to provided method

    Args:
        method: A bound method to invoke until we run out of pages. This method's final argument
            must be page_token. Preceding arguments are handled by *args.
        attr (str): The attr we're interested in aggregating
        args: Further arguments are forwarded straight to `method`
    '''
    data = []
    page_token = None

    while True:
        page = method(*args, page_token) # Assumes page_token is last
        data += page[attr]
        if 'pageToken' in page:
            page_token = page['pageToken']
        else:
            break

    return data

def _run_batched_album_job(method, batch_these, batch_size, *args):
    for batch in (batch_these[i:i+batch_size] for i in range(0, len(batch_these), batch_size)):
        method(batch, *args)


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
        album_attr = 'sharedAlbums' if is_shared else 'albums'
        return _get_paged_data(self.list_albums, album_attr, is_shared)

    def get_album_contents(self, album_id, page_token=None):
        '''Get an album by id

        Args:
            album_title (str): Title to assign to new album

        Returns:
            dict: New album metadata
        '''
        body = {'albumId': album_id}
        if page_token:
            body['pageToken'] = page_token

        results = self.service.mediaItems().search(body=body).execute()
        return results

    def get_all_album_contents(self, album_id):
        '''Get a list of all media items in a specified album

        Args:
            album_id (str): The ID of the album you want to enumerate

        Returns:
            list: List of albums' media items
        '''
        return _get_paged_data(self.get_album_contents, 'mediaItems', album_id)

    def create_album(self, album_title):
        '''Create a new album by title

        Args:
            album_title (str): Title to assign to new album

        Returns:
            dict: New album metadata
        '''
        album = self.service.albums().create(body={'album': {'title':album_title}}).execute()
        return album

    def remove_album_media_contents(self, album_id, media_ids):
        '''Run (potentially batched) calls to remove media from an album
        '''
        _run_batched_album_job(self._remove_album_media_batch, media_ids, 50, album_id)

    def _remove_album_media_batch(self, media_ids, album_id):
        self.service.albums().batchRemoveMediaItems(
            albumId=album_id,
            body={'mediaItemIds': media_ids},
        ).execute()

    def add_album_media_contents(self, album_id, media_ids):
        '''Run (potentially batched) calls to add media to an album
        '''
        _run_batched_album_job(self._add_album_media_batch, media_ids, 50, album_id)

    def _add_album_media_batch(self, media_ids, album_id):
        self.service.albums().batchAddMediaItems(
            albumId=album_id,
            body={'mediaItemIds': media_ids},
        ).execute()
