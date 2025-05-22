class EurydiceError(Exception):
    """Base class for Eurydice custom exceptions."""


class FileNotFoundError(EurydiceError):
    """Error raised when attempted to get from filesystem an object that
    doesn't exist."""
