'''AutoAlbum configuration utility

Run this module to generate the config file for use by AutoAlbum

TODO more instructions later
'''

import argparse
from pathlib import Path

import PyInquirer
from PyInquirer import prompt

import autoalbum
from autoalbum.util import load_json, save_json

def is_album_shared(source_or_dest, default=False):
    '''Ask the user if the specified album is owned or shared

    Args:
        source_or_dest (str): A string to poke into the question: "Do you own the {} album?"
            Typically one of "source" or "destination"

    Returns:
        bool: True if the user specifies "shared", else False
    '''
    choices = [
        {'name': 'Yes; I own it', 'value': False},
        {'name': "No; It's shared with me", 'value': True},
    ]

    if default:
        # PyInquirer bug necessitates this for defaults working "correctly"
        choices.reverse()

    question = [
        {
            'type': 'list',
            'name': 'is_shared',
            'message': 'Do you own the {} album?'.format(source_or_dest),
            'choices': choices,
        }
    ]
    return prompt(question)['is_shared']

def prompt_for_album(source_or_dest, albums, default=None):
    '''Ask the user to select one from a list of albums

    Args:
        source_or_dest (str): A string to poke into the question: "Which album is the {}?"
            Typically one of "source" or "destination"
        albums (list): List of albums to put in a big PyInquirer list.
            Typically, this list is populated from `:meth:autoalbum.api.API.list_all_albums`

    Returns:
        dict: The album that the user selected
    '''
    # If a default exists, figure out which index to start at
    default_album = None
    if default:
        for idx, album in enumerate(albums):
            if album['value'].get('id', None) == default:
                default_album = idx
                break
        # Shuffle the list because of a PyInquirer bug
        # Otherwise, I'd have solved this with list-comp
        if PyInquirer.__version__ <= '1.0.3':
            albums.insert(0, albums.pop(default_album))

    question = [
        {
            'type': 'list',
            'name': 'album',
            'message': 'Which album is the {}?'.format(source_or_dest),
            'choices': albums,
            'default': default_album, # I believe this option to be currently ignored :/
        }
    ]
    return prompt(question)['album']

def format_album_choices(all_albums):
    '''Create PyInquirer-formatted album list from one provided by API

    Args:
        all_albums (list):

    Returns:
        list: list of mapped name/value mappings for PyInquirer

        If possible, the elements of the list are of the form:
            {all_albums[n]['title'] : all_albums[n]}
        If the album is untitled, we make some stuff up.
    '''
    return [{
        'name': a.get('title', '<Unnamed Album with size {}>'.format(a.get('mediaItemsCount', 0))),
        'value': a
        } for a in all_albums]

def main(conf_path, secret_file=None):
    '''Main entrypoint for this configurator

    Args:
        conf_path (PathLike): Path to configuration file
        secret_file (PathLike, optional): Path to secret file from Google API Console
    '''
    conf = {'source': {}, 'destination': {}}

    if conf_path.is_dir():
        # If we are given a directory, append default config file name
        conf_path /= 'config.json'

    if conf_path.is_file():
        # If the file already exists, see what user wants to do about it
        print('Configuration file exists at this location: "{}"'.format(conf_path))
        is_file_questions = [
            {
                'type': 'list',
                'name': 'delete',
                'message': 'What would you like to do?',
                'choices': [
                    {'name': 'Delete existing configuration', 'value': True},
                    {'name': 'Amend existing configuration', 'value': False},
                ],
            },
        ]
        ans = prompt(is_file_questions)

        if ans['delete']:
            # User wants this file deleted. Continue with empty configuration
            conf_path.unlink()
        else:
            # User wants to carry on with existing configuration
            conf = load_json(conf_path)

    # First things first: get the secret file
    if 'auth' in conf:
        auth_override_questions = [
            {
                'type': 'confirm',
                'name': 'replace',
                'message': 'Would you like to replace your client secrets?',
                'default': False,
            },
        ]
        ans = prompt(auth_override_questions)
        if 'confirm' in ans and ans['confirm']:
            del conf['auth']

    if 'auth' not in conf:
        if secret_file:
            print('Provided client secret file from: {}'.format(secret_file))
            conf['auth'] = load_json(secret_file)
        else:
            secret_file_questions = [
                {
                    'type': 'input',
                    'name': 'secret_file',
                    'message': 'Provide path to new secret file:',
                    'default': './client_secret.json',
                    'filter': Path,
                },
            ]
            ans = prompt(secret_file_questions)
            secret_file = ans['secret_file']
            conf['auth'] = load_json(ans['secret_file'])

    # Now that we have that, we can use the actual API to get information about albums
    api = autoalbum.API.new(conf['auth'])
    all_albums = {}

    ## Source album information
    # Figure out if it's a shared album or not
    source_is_shared = is_album_shared('source', conf['source'].get('is_shared', None))
    # Grab all albums of that type and store them, formatted for PyInquirer
    options = all_albums[source_is_shared] = \
        format_album_choices(api.list_all_albums(source_is_shared))
    # Ask the user which they want as the source:
    conf['source']['is_shared'] = source_is_shared
    conf['source']['id'] = \
        prompt_for_album('source', options, conf['source'].get('id', None)).get('id', None)

    ## Destination album information
    # Figure out if it's a shared album or not
    dest_is_shared = is_album_shared('destination', conf['destination'].get('is_shared', None))
    # Grab all albums of that type and store them, formatted for PyInquirer
    if dest_is_shared not in all_albums:
        options = all_albums[dest_is_shared] = \
            format_album_choices(api.list_all_albums(dest_is_shared))
    # In the destination case, we can create a new album, if not shared
    if not dest_is_shared:
        options.insert(0, {'name': '<Create New Album>', 'value': {}})
    # Ask the user which they want as the destination:
    conf['destination']['is_shared'] = dest_is_shared
    conf['destination']['id'] = \
        prompt_for_album('destination', options, conf['destination'].get('id',None)).get('id',None)

    # One more step if the user wanted to create a new album
    if not conf['destination']:
        source_name = conf['source_album'].get('title', '...')
        album_name_questions = [
            {
                'type': 'input',
                'name': 'album_title',
                'message': 'What would you like to call your new album?',
                'default': '[AUTO] ' + source_name,
            },
        ]
        ans = prompt(album_name_questions)
        conf['dest_album'] = api.create_album(ans['album_title'])

    save_json(conf_path, conf)
    print('Wrote configuration file to:', conf_path)
    if secret_file:
        print('It is safe to delete or relocate your secret file ({})'.format(secret_file))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='AutoAlbum Configuration utility')
    parser.add_argument('--secret_file', type=Path, default=None,
        help='Client secret file from Google API Console')
    parser.add_argument('conf_path', type=Path, default=Path(), nargs='?',
        help='The file or directory location for the resulting configuration')
    args = parser.parse_args()
    main(args.conf_path, args.secret_file)
