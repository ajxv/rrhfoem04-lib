"""Custom exceptions for the RRHFOEM04 library."""

class RRHFOEMError(Exception):
    """Base exception for all RRHFOEM04 errors."""
    pass

class ConnectionError(RRHFOEMError):
    """Raised when connection to the device fails."""
    pass

class CommandError(RRHFOEMError):
    """Raised when a command fails to execute properly."""
    pass

class CommunicationError(RRHFOEMError):
    """Raised when there's an error in device communication."""
    pass