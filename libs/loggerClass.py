import logging


class Logger:
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