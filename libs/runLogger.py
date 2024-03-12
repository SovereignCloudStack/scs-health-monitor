from loggerClass import Logger

class AnotherClass:
    def __init__(self):
        # Create an instance of Logger within AnotherClass
        self.log = Logger(name='another_logger', log_file='another.log')

    def some_method(self):
        logger_instance = self.log.logger  # Access the logger directly
        logger_instance.info('Logging from AnotherClass')
        logger_instance.debug('Debug message from AnotherClass')

# Example usage:
if __name__ == "__main__":
    another_instance = AnotherClass()
    another_instance.some_method()