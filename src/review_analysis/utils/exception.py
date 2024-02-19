import sys
from review_analysis import logger

def error_message_detail(error: str):
    '''
    Extract details about the given error.

    Args
    ---
    - error(str): error message.

    Return
    ---
    - str: formated error message with details.
    '''
    _, _, exc_tb = sys.exc_info()

    file_name = ''
    line_number = ''

    if exc_tb is not None:
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno

    error_message = f'In python script name [{file_name}] line number [{line_number}], error message: {error}'

    return error_message

class CustomException(Exception):
    '''
    Custom exception with formatted error message that includes more details about the error.
    '''
    def __init__(self, error_message: str) -> None:
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message)
        
        logger.error(self.error_message)

        def __str__(self):
            return self.error_message