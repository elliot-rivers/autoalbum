'''Selects the N most recent photos from source and ~synchs them with destination~ does nothing

Mostly this is an over-engineered way to do "most recents in an album" for the sake of relatively
current pictures on a google nest hub.

...or it *WOULD BE* if the API would let me do this.
'''
import argparse
import dateutil.parser

# Scopes required for this behavior
## wellp turns out there's no scope that allows you to actually do any of this
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata',
    'https://www.googleapis.com/auth/photoslibrary.appendonly',
    'https://www.googleapis.com/auth/photoslibrary.readonly',
]

def parse_args(args):
    '''Parse arguments the caller's parser didn't understand

    Args:
        args (list): Forwarded list of arguments from the CLI

    Returns:
        The Namespace object resulting from parse_args
    '''
    parser = argparse.ArgumentParser(description='N most recent photos')
    parser.add_argument('-n', type=int, default=5, help='Number of recent images to synch')
    return parser.parse_args(args)

def run(api, conf_data, n):
    '''Run logic. See module comments

    Args:
        api (autoalbum.api.API): API instance to poke Google with
        conf_data (dict): Configuration data from your configuration file
    '''
    ## Grab contents of source album; filter out videos; sort by date, ascending
    source_media = api.get_all_album_contents(conf_data['source']['id'])
    source_media = [m for m in source_media if m['mimeType'].startswith('image')]
    source_media.sort(key=lambda e: dateutil.parser.isoparse(e['mediaMetadata']['creationTime']))
    # Now only take the latter `n`
    source_media = source_media[-n:]
    # All we're really ultimately interested in is the media IDs (as a set)
    source_ids = {m['id'] for m in source_media}

    ## Less work for the destination album. We assume nobody adds content to it :eyes:
    destination_media = list(api.get_album_contents(conf_data['destination']['id']))
    destination_ids = {m['id'] for m in destination_media}

    ## Now we do some quickmaths to determine what needs to be added to the destination album and
    #  what needs to be removed
    add_these_ids = list(source_ids - destination_ids)
    remove_these_ids = list(destination_ids - source_ids)

    #### AAAnnnnnndddddd that's all folks. Turns out Google Photos' API is severely limited.
    #### Logic beyond this point runs but is disappointing

    print('Removing', len(remove_these_ids), 'images...')
    try:
        api.remove_album_media_contents(conf_data['destination']['id'], remove_these_ids)
    except Exception:
        print("Removal failed because Google's Photos API doesn't let you manage existing data.")

    print('Adding', len(add_these_ids), 'images...')
    try:
        api.add_album_media_contents(conf_data['destination']['id'], add_these_ids)
    except Exception:
        print("Addition failed because Google's Photos API doesn't let you manage existing data.")
