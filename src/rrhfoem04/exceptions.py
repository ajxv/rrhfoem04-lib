"""
Custom exceptions for the RRHFOEM04 RFID/NFC reader library.

This module defines a hierarchy of exceptions specific to RFID/NFC operations,
enabling precise error handling and debugging. Each exception type corresponds
to a specific category of errors that can occur during device operations.
"""

class RRHFOEM04Error(Exception):
    """
    Base exception class for all RRHFOEM04-related errors.
    
    This serves as the parent class for all custom exceptions in the library,
    allowing applications to catch all RRHFOEM04-specific errors with a single
    except clause if desired.
    """
    pass

class ConnectionError(RRHFOEM04Error):
    """
    Raised when device connection operations fail.
    
    This includes scenarios such as:
    - Device not found
    - USB communication initialization failure
    - Device disconnection during operation
    - Permission errors when accessing the device
    """
    pass

class CommandError(RRHFOEM04Error):
    """
    Raised when a command fails to execute properly.
    
    This covers errors like:
    - Invalid command parameters
    - Command timing violations
    - Protocol errors
    - Failed card operations (read/write/authenticate)
    """
    def __init__(self, message: str, command: str = None, status: str = None):
        """
        Initialize with optional command and status details.
        
        Args:
            message: Error description
            command: The command that failed (if available)
            status: Status code returned by device (if available)
        """
        self.command = command
        self.status = status
        super().__init__(f"{message} (Command: {command}, Status: {status})" if command 
                        else message)

class CommunicationError(RRHFOEM04Error):
    """
    Raised when device communication fails after connection.
    
    This includes:
    - Transmission errors
    - Reception timeouts
    - Invalid responses
    - CRC verification failures
    """
    pass

class ValidationError(RRHFOEM04Error):
    """
    Raised when input parameters fail validation.
    
    This covers:
    - Invalid block numbers
    - Invalid data lengths
    - Incorrect parameter types
    - Out-of-range values
    """
    pass

class TagError(RRHFOEM04Error):
    """
    Raised for tag-specific errors.
    
    This includes:
    - No tag present
    - Multiple tags detected when single expected
    - Tag removal during operation
    - Unsupported tag types
    """
    pass

class AuthenticationError(RRHFOEM04Error):
    """
    Raised when card authentication fails.
    
    This covers:
    - Invalid keys
    - Failed authentication process
    - Authentication timeout
    - Access permission violations
    """
    pass