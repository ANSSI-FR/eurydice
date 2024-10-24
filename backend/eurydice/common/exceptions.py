class EurydiceError(Exception):
    """Base class for Eurydice custom exceptions."""


class S3ObjectNotFoundError(EurydiceError):
    """Error raised when attempted to get from S3 storage an object that
    doesn't exist."""
