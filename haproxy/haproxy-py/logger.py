import logging
import inspect
"""
This class represent a logger object and logging the application actions.
"""
class Logger:
    # initialize a new logger object and set the log file based on the log_file param.
    def __init__(self,log_file=None):
        self.log_file = r'/var/log/haproxy-py.log' if log_file == None else log_file #log file
    # create and return a new logger object
    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - Line: %(lineno)d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def function_name(self):
        frame = inspect.currentframe().f_back.f_back
        caller_function_name = frame.f_code.co_name
        return caller_function_name
    
    def log_reformat(self,log):
        return f'{self.function_name()} - {log}'



