import os
from pathlib import Path
from typing import List
import pickle
import bz2

import yaml
from box import ConfigBox

from src.utils import logger
from src.utils.exception import CustomException

def read_yaml(path_to_yaml: Path) -> ConfigBox:
    '''
    Reads a yaml file at the given path and return it as a ConfigBox.

    Args
    ----
    path_to_yaml : Path
        Path to yaml file.

    Returns
    -------
    ConfigBox
        ConfigBox type.
    '''

    try:
        with open(path_to_yaml, encoding='utf-8') as f:
            content = yaml.safe_load(f)
            logger.info(f'yaml file: {path_to_yaml} loaded successfully')
            return ConfigBox(content)

    except Exception as e:
        raise CustomException(e)
    
def create_directories(path_to_directories: List[Path], verbose=True):
    '''
    Create the given directories.

    Args
    ----
    path_to_directories : List[Path]
        List of path to directories.
    verbose : bool
        Enable verbose.
    '''

    try:
        for path in path_to_directories:
            os.makedirs(path, exist_ok=True)
            if verbose:
                logger.info(f'created directory at: {path}')

    except Exception as e:
        raise CustomException(e)
    
def save_obj(file_path: Path, obj: any):
    '''
    Serialize the given object and save at the given path.

    Args
    ----
    file_path : Path
        Path to save obj at.

    obj : any
        Object to serialize and save.
    '''
    try:
        dir_path = os.path.dirname(file_path)
        create_directories([dir_path])

        with bz2.BZ2File(file_path, 'wb') as file:
            pickle.dump(obj, file)

    except Exception as e:
        raise CustomException(f'failed saving object to {file_path}: {e}')
    
def load_object(file_path: Path) -> any:
    '''
    Load serialized obj from given path.

    Args
    ----
    file_path : Path
        Path to load obj from.

    Returns
    -------
    any
        The loaded object.
    '''
    try:
        with bz2.BZ2File(file_path, 'rb') as file:
            return pickle.load(file)
    
    except Exception as e:
        raise CustomException(f'failed loading object from {file_path}: {e}')