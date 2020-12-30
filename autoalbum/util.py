'''Utility functions mostly'''
import json

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
