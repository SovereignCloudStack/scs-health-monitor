# loggerClass:

* can be configured seperately for each instance as follows:
```
new_rootlogger = Logger()
logger_instance = new_rootlogger.getLogger()

logger_instance.info('This is an info message')
logger_instance.debug('This is a debug message')

new_otherlogger = Logger(name='other_logger', level=logging.DEBUG, log_file='otherlog.log')
logger_instance = new_otherlogger.getLogger()

logger_instance.info('This is an info message')
logger_instance.debug('This is a debug message')
```
* the output looks like this:
```
logfile.log:
2024-03-12 15:58:49,810 - root - INFO - This is an info message
2024-03-12 15:58:49,811 - root - DEBUG - This is a debug message
2024-03-12 16:09:22,905 - root - INFO - This is an info message
2024-03-12 16:09:22,905 - root - DEBUG - This is a debug message

otherlog.log:
2024-03-12 16:09:22,906 - other_logger - INFO - This is an info message
2024-03-12 16:09:22,906 - other_logger - DEBUG - This is a debug message
``` 