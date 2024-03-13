# loggerClass:

* can be configured seperately for each instance and called as follows:
```
# Default confiruration
new_rootlogger = Logger()
logger_instance = new_rootlogger.getLogger()

# now you can log the four categories:
logger_instance.info('This is an info message')
logger_instance.debug('This is a debug message')
logger_instance.warning('This is a warning message')
logger_instance.error('This is a error message')
```
* the output is stored in logfile.log looks like this:
```
2024-03-12 15:58:49,810 - root - INFO - This is an info message
2024-03-12 15:58:49,811 - root - DEBUG - This is a debug message
2024-03-12 15:58:49,811 - root - WARNING - This is an warning message
2024-03-12 15:58:49,812 - root - ERROR - This is a error message
```

* if you want to specify your output and logger name, you can insert these parameters
 to set the Loglevel, you should set this within the class, otherwise you would have to import logging into your module
```
new_otherlogger = Logger(name='other_logger', level=logging.DEBUG, log_file='otherlog.log')
logger_instance = new_otherlogger.getLogger()

logger_instance.info('This is an info message')
logger_instance.debug('This is a debug message')
```
* the output is stored inotherlog.log
```
2024-03-12 16:09:22,906 - other_logger - INFO - This is an info message
2024-03-12 16:09:22,906 - other_logger - DEBUG - This is a debug message
``` 