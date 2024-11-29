"""RRHFOEM04 RFID/NFC Reader Interface Library"""

from .core import RRHFOEM04
from .exceptions import (
    RRHFOEMError,
    ConnectionError,
    CommandError,
    CommunicationError
)

__version__ = "0.1.0"
__all__ = [
    'RRHFOEM04',
    'RRHFOEMError',
    'ConnectionError',
    'CommandError',
    'CommunicationError',
]