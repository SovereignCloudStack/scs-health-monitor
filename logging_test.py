import logging

varname = 'Variable'

# a append insstead of w
logging.basicConfig(level=logging.DEBUG,filename='logfile.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

logging.debug('This is a debug message %s', varname)
logging.info('This is an info message %s', varname)
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')

# def __init__(self):
#     self.__dict__ = self.__shared_state
#     if not self.__shared_state:
#         # noinspection PyArgumentList
#         log_formatter = logging.Formatter(
#             '[%(asctime)s][%(levelname)-7.7s][%(name)-24.24s] %(message)s'
#         )
#         log_file_handler = RotatingFileHandler(filename=f'{Config().paths.current_logs_path}_debug.log')
#         log_file_handler.setFormatter(log_formatter)
#         log_console_handler = logging.StreamHandler()
#         log_console_handler.setFormatter(log_formatter)
#         self._log = logging.getLogger(' acult ')
#         self._log.addHandler(log_file_handler)
#         self._log.addHandler(log_console_handler)
#         log_level = Config().common.log_level
#         self._log.setLevel(log_level)
#         self._log.info(f"Log level set to: {log_level}")

# @property
# def logger(self):
#     return self._log
