"""Constants used throughout the RRHFOEM04 library."""

# Device identification
VENDOR_ID = 0x1781
PRODUCT_ID = 0x0C10

# Communication parameters
BUFFER_SIZE = 64
DEFAULT_TIMEOUT = 0.5  # seconds

# Command codes
CMD_GET_INFO = [0x03, 0xF0, 0x00]
CMD_BUZZER = [0x03, 0xF0, 0x01]
CMD_ISO15693_SINGLE_SLOT_INVENTORY = [0x04, 0x10, 0x01, 0x26]
CMD_ISO15693_16_SLOT_INVENTORY = [0x04, 0x10, 0x02, 0x06]
CMD_ISO14443A_INVENTORY = [0x03, 0x2f, 0x01]

# Response status codes
STATUS_SUCCESS = ['00', '00']