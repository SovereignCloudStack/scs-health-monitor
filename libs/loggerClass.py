import logging
import logging.config
import yaml

'''
read config yml, set version number if not specified
or print error, open a logger instance and print log messages
'''
try:
    with open('libs/loggerConfig.yml', 'r') as f:
        config = yaml.safe_load(f.read())
        if 'version' not in config:
            config['version'] = 1
        logging.config.dictConfig(config)
except Exception as e:
         print(f"Error loading logging configuration: {e}")


logger = logging.getLogger(__name__)
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')


