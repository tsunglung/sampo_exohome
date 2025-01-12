"""Define package errors."""


class ExohomeError(Exception):
    """Define a base error."""


class RequestError(ExohomeError):
    """Define an error related to invalid requests."""


class InvalidCredentialsError(ExohomeError):
    """Define an error for unauthenticated accounts."""