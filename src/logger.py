import logging


class ColoredFormatter(logging.Formatter):
    BLUE = "\x1b[34;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    COLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED
    }

    def get_level_name(self, level):
        return self.COLORS[level] + "%(levelname)s" + self.RESET
    
    def format(self, record: logging.LogRecord) -> str:
        fmt = f"{self.get_level_name(record.levelno)}: %(name)s:\t%(message)s"
        formatter = logging.Formatter(fmt)
        return formatter.format(record)


def setup_logging():
    logger = logging.getLogger("src")
    logger.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = ColoredFormatter()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
