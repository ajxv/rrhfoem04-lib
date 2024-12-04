"""RRHFOEM04 RFID/NFC Reader Interface Library"""

from .core import RRHFOEM04
from .exceptions import (
    RRHFOEMError,
    ConnectionError,
    CommandError,
    CommunicationError,
    ValidationError,
    TagError,
    AuthenticationError
)

__all__ = [
    'RRHFOEM04',
    'RRHFOEMError',
    'ConnectionError',
    'CommandError',
    'CommunicationError',
    'ValidationError',
    'TagError',
    'AuthenticationError'
]