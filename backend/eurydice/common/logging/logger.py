import logging

from django.conf import settings

LOG_KEY = "log_key"


class DictLogger:
    def __init__(self, name: str):
        logging.config.dictConfig(settings.LOGGING)  # type: ignore
        self.logger = logging.getLogger(name)

    def log(self, level: int, record: dict, *args, **kwargs):
        if not isinstance(record, dict):
            raise ValueError("Log record must be a dictionary.")

        if LOG_KEY not in record:
            raise ValueError("Log record must contain a 'log_key' key.")

        self.logger.log(level, record, *args, **kwargs)

    def debug(self, record: dict[str, str | int], *args, **kwargs):
        """Log a debug message."""
        self.log(logging.DEBUG, record, *args, **kwargs)

    def info(self, record: dict[str, str | int], *args, **kwargs):
        """Log an info message."""
        self.log(logging.INFO, record, *args, **kwargs)

    def warning(self, record: dict[str, str | int], *args, **kwargs):
        """Log a warning message."""
        self.log(logging.WARNING, record, *args, **kwargs)

    def error(self, record: dict[str, str | int], *args, **kwargs):
        """Log an error message."""
        self.log(logging.ERROR, record, *args, **kwargs)

    def exception(self, record: dict[str, str | int], *args, **kwargs):
        self.log(logging.ERROR, record, *args, exc_info=True, **kwargs)


logger = DictLogger(__name__)
