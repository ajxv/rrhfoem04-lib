# RRHFOEM04 Python Library

A Python Library for interfacing with the RRHFOEM04 RFID Reader.


## CRC Calculation

The protocol uses CRC-16 for error detection with the following specifications:
* Initial value (CRC_INIT): 0xFFFF
* Polynomial (CRC_POLY): 0x1021
* Width: 16 bits
* Final XOR value: CRC is inverted (~CRC)
* Calculation covers all bytes from Command Code to any custom data

The algorithm works as follows:
1. Initialize CRC to 0xFFFF
2. For each byte in the data:
   * XOR the byte with the CRC
   * For each bit (8 times):
      * If CRC & 0x8000 is set:
         * Shift CRC left by 1 and XOR with 0x1021
      * Else:
         * Shift CRC left by 1
      * Keep only lower 16 bits (AND with 0xFFFF)
3. Invert the final CRC value

## Command Reference

### Get Reader Information
* Command code: 0xF000
* Request format:
   * Frame length: 0x03
   * Command code: [0xF0, 0x00]
   * CRC: 2 bytes
* Response format:
   * Frame length: Variable
   * Command code: [0xF0, 0x00]
   * Error code: 2 bytes (0x0000 = success)
   * Serial number: 16 bytes
   * Data: Model, version, and additional info
   * CRC: 2 bytes

### Sound Buzzer
* Command code: 0xF001
* Request format:
   * Frame length: 0x03
   * Command code: [0xF0, 0x01]
   * CRC: 2 bytes
* Response format:
   * Frame length: 0x05
   * Command code: [0xF0, 0x01]
   * Error code: 2 bytes
   * CRC: 2 bytes

## ISO15693 Operations

### Inventory (Single Slot)
* Command code: 0x1001
* Request format options:
   1. With AFI:
      * Frame length: 0x05
      * Command code: [0x10, 0x01]
      * Flags: 0x36 (Data rate + AFI)
      * AFI value: 1 byte
      * CRC: 2 bytes
   2. Without AFI:
      * Frame length: 0x04
      * Command code: [0x10, 0x01]
      * Flags: 0x26 (Data rate only)
      * CRC: 2 bytes
* Response format:
   * Frame length: Variable
   * Command code: [0x10, 0x01]
   * Error code: 2 bytes
   * Number of cards: 1 byte
   * Card UIDs: 8 bytes per card
   * CRC: 2 bytes

### Read Single Block
* Command code: 0x1006
* Request format:
   * Frame length: 0x06
   * Command code: [0x10, 0x06]
   * Flags: 0x02/0x42 (Data rate, optional high-speed)
   * Block length: 1 byte
   * Block number: 1 byte
   * CRC: 2 bytes
* Response format:
   * Frame length: Variable
   * Command code: [0x10, 0x06]
   * Error code: 2 bytes
   * Response flag: 1 byte
   * Block security status: 1 byte (if option flag set)
   * Block data: Variable length
   * CRC: 2 bytes

### Write Single Block
* Command code: 0x1007
* Request format:
   * Frame length: Variable (6 + data length)
   * Command code: [0x10, 0x07]
   * Flags: 0x02/0x42
   * Block length: 1 byte
   * Block number: 1 byte
   * Data: Variable length
   * CRC: 2 bytes
* Response format:
   * Frame length: 0x05
   * Command code: [0x10, 0x07]
   * Error code: 2 bytes
   * CRC: 2 bytes

## AFI Operations

### Write AFI
* Command code: 0x100A
* Request format:
   * Frame length: 0x05
   * Command code: [0x10, 0x0A]
   * Flags: 0x02/0x42
   * AFI value: 1 byte
   * CRC: 2 bytes
* Response format:
   * Frame length: 0x05
   * Command code: [0x10, 0x0A]
   * Error code: 2 bytes
   * CRC: 2 bytes

## ISO14443A Operations

### Inventory
* Command code: 0x2F01
* Request format:
   * Frame length: 0x03
   * Command code: [0x2F, 0x01]
   * CRC: 2 bytes
* Response format:
   * Frame length: Variable
   * Command code: [0x2F, 0x01]
   * Error code: 2 bytes
   * UID length: 1 byte (4/7/10)
   * UID: Variable length
   * CRC: 2 bytes

### Read Block (Mifare)
* Command code: 0x2102
* Request format:
   * Frame length: 0x04
   * Command code: [0x21, 0x02]
   * Block number: 1 byte
   * CRC: 2 bytes
* Response format:
   * Frame length: 0x14
   * Command code: [0x21, 0x02]
   * Error code: 2 bytes
   * Block data: 16 bytes
   * CRC: 2 bytes

### Write Block (Mifare)
* Command code: 0x2103
* Request format:
   * Frame length: 0x14
   * Command code: [0x21, 0x03]
   * Block number: 1 byte
   * Data: 16 bytes
   * CRC: 2 bytes
* Response format:
   * Frame length: 0x05
   * Command code: [0x21, 0x03]
   * Error code: 2 bytes
   * CRC: 2 bytes

### Key notes for all commands:
* All multi-byte values are in big-endian format
* Error code 0x0000 indicates success
* Frame length includes all fields except itself
* CRC is calculated over all fields except frame length and CRC itself
* Response data validity should be checked via error code and CRC verification

## License

This project is licensed under the MIT License - see the LICENSE file for details.