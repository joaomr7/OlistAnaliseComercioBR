import os
from pathlib import Path
from typing import List

import yaml
from box import ConfigBox

from src.review_analysis.utils import logger
from src.review_analysis.utils.exception import CustomException

def read_yaml(path_to_yaml: Path) -> ConfigBox:
    '''
    Reads a yaml file at the given path and return it as a ConfigBox.

    Args
    ---
        * path_to_yaml (Path): path to yaml file

    Returns
    ---
        * ConfigBox: ConfigBox type
    '''

    try:
        with open(path_to_yaml) as f:
            content = yaml.safe_load(f)
            logger.info(f'yaml file: {path_to_yaml} loaded successfully')
            return ConfigBox(content)

    except Exception as e:
        raise CustomException(e)
    
def create_directories(path_to_directories: List[Path], verbose=True):
    '''
    Create the given directories.

    Args
    ---
        * path_to_directories (List[Path]): list of path to directories
        * verbose (bool): enable verbose
    '''

    try:
        for path in path_to_directories:
            os.makedirs(path, exist_ok=True)
            if verbose:
                logger.info(f'created directory at: {path}')

    except Exception as e:
        raise CustomException(e)