import logging
class Logger:
    def __init__(self, name='root', level=logging.DEBUG, log_file="logfile.log"):
        #if not self.__shared_state:
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level)
            self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)

            # File handler (if log_file is provided)
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(level)
                file_handler.setFormatter(self.formatter)
                self.logger.addHandler(file_handler)
        # else:
        #     self.__dict__ = self.__shared_state           
    def getLogger(self):
        return self.logger

# Example usage:
# new_rootlogger = Logger()
# logger_instance = new_rootlogger.getLogger()

# logger_instance.info('This is an info message')
# logger_instance.debug('This is a debug message')

# new_otherlogger = Logger(name='other_logger', level=logging.DEBUG, log_file='otherlog.log')
# logger_instance = new_otherlogger.getLogger()

# logger_instance.info('This is an info message')
# logger_instance.debug('This is a debug message')
