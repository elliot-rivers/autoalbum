'''Entrypoint for autoalbum

Run autoalbum.configurator first. You'll need the config file
'''

import argparse
import importlib
from pathlib import Path

import autoalbum
from autoalbum.util import load_json

def main(behavior, conf, unknown_args):
    if conf.is_dir():
        # If we are given a directory, append default config file name
        conf /= 'config.json'
    conf_data = load_json(conf)

    # Load user-provided module
    mod = importlib.import_module(behavior)

    # Build new API instance
    api = autoalbum.API.new(conf_data['auth'], mod.SCOPES)

    # Parse the module's arguments and execute its logic
    args = mod.parse_args(unknown_args)
    mod.run(api, conf_data, **vars(args))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='AutoAlbum executor')
    parser.add_argument('behavior', type=str, default='autoalbum.behavior.n_most_recent',
        nargs='?', help='Python module of desired behavior to run (must be on path already)')
    parser.add_argument('--conf', '-c', type=Path, default=Path(),
        help='The file or directory location of the AutoAlbum config file. Default ./conf.json')

    args, unknowns = parser.parse_known_args()
    main(args.behavior, args.conf, unknowns)
