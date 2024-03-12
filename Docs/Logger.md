# Logger Config:

* you configure the logger in the loggerConfig.yml, which can be renamed and looks like this:

```
version: 1
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: simple
    stream: ext://sys.stdout
  file_handler:
    class: logging.FileHandler
    filename: logfile.log # Set logfile 
    level: DEBUG          # Set LogLevel
    formatter: simple
loggers:
  sampleLogger:
    level: DEBUG
    handlers: [console, file_handler]  # Add 'file_handler' here
    propagate: no
root:
  level: DEBUG
  handlers: [console, file_handler]  # Add 'file_handler' here
```

* The class is in the libs/loggerClass.py file and reads the config-file makes sure that the version tag is given and provides handler and formatter objects:
```
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
        if 'version' not in config:
            config['version'] = 1
        logging.config.dictConfig(config)
except Exception as e:
         print(f"Error loading logging configuration: {e}")


# Set up the handlers and formatters
handlers = config['handlers']
formatters = config['formatters']

for handler_config in handlers:
     handler_name = handler_config['name']
     handler_class = eval(handler_config['class'])
     handler = handler_class(*handler_config.get('args', []))
     handler.setLevel(handler_config['level'])
     handler.setFormatter(logging.Formatter(formatters[handler_config['formatter']]['format']))
     logging.getLogger().addHandler(handler)

# Test Logging

logger = logging.getLogger(__name__)
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')
```
* the Logger can be implemented like in the Exemplefile runLogger.py file
```
import loggerClass as log

log.logger.debug('This is a debug message')
log.logger.info('This is an info message')
log.logger.warning('This is a warning message')
log.logger.error('This is an error message')
log.logger.critical('This is a critical message')
```
