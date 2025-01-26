"""
Constants and protocol definitions for the RRHFOEM04 RFID/NFC reader library.

This module defines all the constants needed for communicating with RRHFOEM04 RFID/NFC readers,
including device identifiers, communication parameters, command codes, and status codes.
The constants follow the manufacturer's protocol specification and ISO standards.
"""

# Device Identification
# The USB Vendor ID and Product ID are unique identifiers assigned by the USB-IF
# that help the operating system recognize and communicate with the RRHFOEM04 device
VENDOR_ID = 0x1781   # Unique manufacturer ID for the device
PRODUCT_ID = 0x0C10  # Specific product ID for RRHFOEM04 model

# Communication Parameters
# These define the basic parameters for USB HID communication with the device
BUFFER_SIZE = 64     # Standard USB HID report size in bytes
DEFAULT_TIMEOUT = 0.5  # Default timeout for commands in seconds

# Command Structure Format:
# Each command is a list of bytes with the following structure:
# [Length, Category, Command, Flags, ...additional data]
# - Length: Total length of the command (excluding CRC)
# - Category: Protocol category (0xF0=System, 0x10=ISO15693, 0x2F=ISO14443A, 0x21=Mifare)
# - Command: Specific operation code
# - Flags: Additional command parameters

# System Commands (Category 0xF0)
CMD_GET_READER_INFO = [0x03, 0xF0, 0x00]    # Get reader model and serial number
CMD_BUZZER_BEEP = [0x03, 0xF0, 0x01]        # Activate reader's buzzer
CMD_BUZZER_ON = [0x03, 0xF0, 0x16]          # Turn on reader's buzzer
CMD_BUZZER_OFF = [0x03, 0xF0, 0x15]         # Turn off reader's buzzer

# ISO15693 Commands (Category 0x10)
# Inventory Commands - Used to detect tags in the field
CMD_ISO15693_SINGLE_SLOT_INVENTORY = [0x04, 0x10, 0x01, 0x26]  # Single slot anti-collision
CMD_ISO15693_16_SLOT_INVENTORY = [0x04, 0x10, 0x02, 0x06]      # 16-slot anti-collision

# ISO15693 Read Commands
# Flag values: 0x02=No flags, 0x12=Select flag, 0x22=Address flag
CMD_ISO15693_READ_SINGLE_BLOCK = [0x06, 0x10, 0x06, 0x02]                    # Read any tag
CMD_ISO15693_READ_SINGLE_BLOCK_WITH_SELECT_FLAG = [0x06, 0x10, 0x06, 0x12]   # Read selected tag
CMD_ISO15693_READ_SINGLE_BLOCK_WITH_ADDRESS_FLAG = [0x0E, 0x10, 0x06, 0x22]  # Read specific tag

# ISO15693 Write Commands
# Write commands follow same flag pattern as read commands
CMD_ISO15693_WRITE_SINGLE_BLOCK = [0x06, 0x10, 0x07, 0x02]                    # Write to any tag
CMD_ISO15693_WRITE_SINGLE_BLOCK_WITH_SELECT_FLAG = [0x06, 0x10, 0x07, 0x12]   # Write to selected tag
CMD_ISO15693_WRITE_SINGLE_BLOCK_WITH_ADDRESS_FLAG = [0x0E, 0x10, 0x07, 0x22]  # Write to specific tag

# ISO15693 read Multiple Blocks
CMD_ISO15693_READ_MULTIPLE_BLOCKS = [0x07, 0x10, 0x09, 0x02]                    # Read multiple blocks
CMD_ISO15693_READ_MULTIPLE_BLOCKS_WITH_SELECT_FLAG = [0x07, 0x10, 0x09, 0x12]   # Read multiple from selected
CMD_ISO15693_READ_MULTIPLE_BLOCKS_WITH_ADDRESS_FLAG = [0x0F, 0x10, 0x09, 0x22]  # Read multiple from specific

# ISO15693 write multiple block: arr[0] frame length should be re-calculated appended dynamically 
CMD_ISO15693_WRITE_MULTIPLE_BLOCK = [0x07, 0x1F, 0x02, 0x02]                    # Write to any tag
CMD_ISO15693_WRITE_MULTIPLE_BLOCK_WITH_SELECT_FLAG = [0x07, 0x1F, 0x02, 0x12]   # Write to selected tag
CMD_ISO15693_WRITE_MULTIPLE_BLOCK_WITH_ADDRESS_FLAG = [0x0F, 0x1F, 0x02, 0x22]  # Write to specific tag

# ISO15693 AFI operations
CMD_ISO15693_WRITE_AFI = [0x05, 0x10, 0x0A, 0x02]                    # Write to any tag
CMD_ISO15693_WRITE_AFI_WITH_SELECT_FLAG = [0x05, 0x10, 0x0A, 0x12]   # Write to selected tag
CMD_ISO15693_WRITE_AFI_WITH_ADDRESS_FLAG = [0x0D, 0x10, 0x0A, 0x22]  # Write to specific tag

# ISO14443A Commands (Category 0x2F)
CMD_ISO14443A_INVENTORY = [0x03, 0x2F, 0x01]     # Detect ISO14443A tags
CMD_ISO14443A_SELECT_CARD = [0x08, 0x2F, 0x02]   # Select specific card for operations

# Mifare Classic Commands (Category 0x21)
CMD_ISO14443A_MIFARE_AUTHENTICATE = [0x0F, 0x21, 0x01]  # Authenticate with key A
CMD_ISO14443A_MIFARE_READ = [0x04, 0x21, 0x02]          # Read 16-byte block (after auth)
CMD_ISO14443A_MIFARE_WRITE = [0x14, 0x21, 0x03]         # Write block (after auth)

# Response Status Codes
# The reader returns these codes to indicate command execution status
STATUS_SUCCESS = ['00', '00']  # Command executed successfully

# Additional timing constants for reliable communication
COMMAND_INTERVAL = 0.1  # Minimum time between commands (seconds)
RETRY_DELAY = 0.02      # Delay between retry attempts (seconds)
MAX_RETRIES = 3         # Maximum number of retry attempts

# Block size constants
DEFAULT_BLOCK_SIZE = 4  # Standard block size for ISO15693 tags
MIFARE_BLOCK_SIZE = 16  # Block size for Mifare Classic cards