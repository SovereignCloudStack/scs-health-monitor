import logging
import logging.config

logging.config.fileConfig(fname='config.ini', disable_existing_loggers=False)

# Get the logger specified in the file
logger = logging.getLogger(__name__)

logger.debug('This is a debug message')


# import logging.config
# from configparser import ConfigParser

# # Load configuration from config.ini
# config = ConfigParser()
# config.read('config.ini')

# # Configure logging
# logging.config.dictConfig(config._sections['logging'])

# # Get handlers and set up the formatter
# handlers = config._sections['handlers']
# formatters = config._sections['formatters']

# for handler_name, handler_params in handlers.items():
#     handler_class = eval(handler_params['class'])
#     handler = handler_class(*eval(handler_params.get('args', '()')))
#     handler.setLevel(eval(handler_params['level']))
#     handler.setFormatter(logging.Formatter(formatters[handler_params['formatter']]['format']))
#     logging.getLogger().addHandler(handler)

# # Test the logger
# logger = logging.getLogger(__name__)
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')