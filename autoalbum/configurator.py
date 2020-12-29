'''AutoAlbum configuration utility

Run this module to generate the config file for use by AutoAlbum

TODO more instructions later
'''

import argparse
import json
from pathlib import Path

from PyInquirer import prompt

import autoalbum

def load_json(json_path):
    '''Load JSON utility function

    I think manipulating files is ugly so here's a short utility to do this for me

    Args:
        json_path (PathLike): path to JSON file to load

    Returns:
        dict: Loaded JSON data
    '''
    data = {}
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data

def save_json(json_path, data):
    '''Save JSON utility function

    I think manipulating files is ugly so here's a short utility to do this for me

    Args:
        json_path (PathLike): path to JSON file to write to
        data (dict): data to write to JSON
    '''
    with open(json_path, 'w') as file:
        json.dump(data, file)

def is_album_shared(source_or_dest):
    '''Ask the user if the specified album is owned or shared

    Args:
        source_or_dest (str): A string to poke into the question: "Do you own the {} album?"
            Typically one of "source" or "destination"

    Returns:
        bool: True if the user specifies "shared", else False
    '''
    question = [
        {
            'type': 'list',
            'name': 'is_shared',
            'message': 'Do you own the {} album?'.format(source_or_dest),
            'choices': [
                {'name': 'Yes; I own it', 'value': False},
                {'name': "No; It's shared with me", 'value': True},
            ],
        }
    ]
    return prompt(question)['is_shared']

def prompt_for_album(source_or_dest, albums):
    '''Ask the user to select one from a list of albums

    Args:
        source_or_dest (str): A string to poke into the question: "Which album is the {}?"
            Typically one of "source" or "destination"
        albums (list): List of albums to put in a big PyInquirer list.
            Typically, this list is populated from `:meth:autoalbum.api.API.list_all_albums`

    Returns:
        dict: The album that the user selected
    '''
    question = [
        {
            'type': 'list',
            'name': 'album',
            'message': 'Which album is the {}?'.format(source_or_dest),
            'choices': albums,
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
    conf = {}

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
        if ans['confirm']:
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
            conf['auth'] = load_json(ans['secret_file'])

    # Now that we have that, we can use the actual API to get information about albums
    api = autoalbum.API.new(conf['auth'])
    all_albums = {}

    ## Source album information
    # Figure out if it's a shared album or not
    source_is_shared = is_album_shared('source')
    # Grab all albums of that type and store them, formatted for PyInquirer
    options = all_albums[source_is_shared] = \
        format_album_choices(api.list_all_albums(source_is_shared))
    # Ask the user which they want as the source:
    conf['source_album'] = prompt_for_album('source', options)

    ## Destination album information
    # Figure out if it's a shared album or not
    dest_is_shared = is_album_shared('destination')
    # Grab all albums of that type and store them, formatted for PyInquirer
    if dest_is_shared not in all_albums:
        options = all_albums[dest_is_shared] = \
            format_album_choices(api.list_all_albums(dest_is_shared))
    # In the destination case, we can create a new album, if not shared
    if not dest_is_shared:
        options.insert(0, {'name': '<Create New Album>', 'value': {}})
    # Ask the user which they want as the destination:
    conf['dest_album'] = prompt_for_album('destination', options)

    # One more step if the user wanted to create a new album
    if not conf['dest_album']:
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='AutoAlbum Configuration utility')
    parser.add_argument('--secret_file', type=Path, default=None,
        help='Client secret file from Google API Console')
    parser.add_argument('conf_path', type=Path, default=Path(), nargs='?',
        help='The file or directory location for the resulting configuration')
    args = parser.parse_args()
    main(args.conf_path, args.secret_file)
