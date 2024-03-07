import logging
import logging.config
import yaml

'''
read config yml, set version number if not specified
or print error, open a logger instance and print log messages
'''
try:
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f.read())
        # # Ensure the 'version' key is present
        if 'version' not in config:
            config['version'] = 1
        logging.config.dictConfig(config)
except Exception as e:
         print(f"Error loading logging configuration: {e}")

# # Set up the handlers and formatters
# handlers = config['handlers']
# formatters = config['formatters']

# for handler_config in handlers:
#     handler_name = handler_config['name']
#     handler_class = eval(handler_config['class'])
#     handler = handler_class(*handler_config.get('args', []))
#     handler.setLevel(handler_config['level'])
#     handler.setFormatter(logging.Formatter(formatters[handler_config['formatter']]['format']))
#     logging.getLogger().addHandler(handler)



logger = logging.getLogger(__name__)
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')


