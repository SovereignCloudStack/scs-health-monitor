import logging


class Logger:
    _instance = None
    def __new__(cls,**kwargs):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, name="root", level=logging.DEBUG, log_file="logfile.log"):
        self.instance = logging.getLogger(name)
        self.instance.setLevel(level)
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(self.formatter)
        self.instance.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(self.formatter)
            self.instance.addHandler(file_handler)

    def log(self, level: int, msg: object):
        self.instance.log(level, msg)

    def log_critical(self, msg: object):
        self.log(logging.CRITICAL, msg)

    def log_error(self, msg: object):
        self.log(logging.ERROR, msg)

    def log_warning(self, msg: object):
        self.log(logging.WARNING, msg)

    def log_info(self, msg: object):
        self.log(logging.INFO, msg)

    def log_debug(self, msg: object):
        self.log(logging.DEBUG, msg)

    def log_not_set(self, msg: object):
        self.log(logging.NOTSET, msg)

    logFatal = log_critical
