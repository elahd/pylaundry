"""pylaundry exceptions."""


class MessagePackerError(Exception):
    """Problem with encoding/decoding or encrypting/decrypting."""


class ResponseFormatError(Exception):
    """API response in wrong format."""


class CommunicationError(Exception):
    """Could not reach server."""


class Rejected(Exception):
    """Server understood but rejected the request."""


class UnexpectedError(Exception):
    """Something bad happened that we didn't expect."""


class NotLoggedIn(Exception):
    """User attempted to perform an action before logging in."""


class AuthenticationError(Exception):
    """User submitted invalid credentials."""
