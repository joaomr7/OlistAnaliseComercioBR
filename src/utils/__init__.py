import os
import sys
import logging
from datetime import datetime

LOG_FORMAT = '[ %(asctime)s ] %(lineno)d %(filename)s - %(levelname)s - %(message)s'

LOG_DIR = 'logs'
LOG_FILE = f'{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}.log'
LOG_FILEPATH = os.path.join(LOG_DIR, LOG_FILE)

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt='%m-%d-%Y %I:%M:%S %p',

    handlers=[
        logging.FileHandler(LOG_FILEPATH),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger()