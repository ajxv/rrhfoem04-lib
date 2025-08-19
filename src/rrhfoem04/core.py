"""
Core implementation of the RRHFOEM04 RFID/NFC reader interface.

This module provides a Python interface for interacting with RRHFOEM04 RFID/NFC readers.
It supports multiple RFID protocols including ISO15693 and ISO14443A, implementing various
card operations such as inventory scanning, reading, and writing. The implementation
follows the manufacturer's protocol specification while adding robust error handling
and timing controls for reliable communication.
"""

import time
from typing import List, Optional
import hid  # Hardware Interface Device library for USB communication
import re
import logging

from .constants import *
from .exceptions import *
from .utils import RRHFOEM04Result

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rrhfoem04.log"),
        logging.StreamHandler()
    ]
)

class RRHFOEM04:
    """
    Interface class for RRHFOEM04 RFID/NFC reader.

    This class provides methods to interact with RRHFOEM04 RFID/NFC readers through USB HID.
    It handles device connection, command transmission, and response parsing while
    implementing proper timing controls and error handling for reliable operation.
    """

    def __init__(self, auto_connect: bool = True):
        """
        Initialize the RRHFOEM04 reader interface.
        
        Args:
            auto_connect: If True, automatically attempts to connect to the device
                        during initialization.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing RRHFOEM04 interface")
        self.device: Optional[hid.device] = None
        self._last_command_time = 0  # Tracks timing between commands
        # Add tracking for Mifare card state
        self._mifare_selected_uid = None
        self._mifare_auth_blocks = {}  # Track authenticated sectors by UID

        if auto_connect:
            self._connect()

    def _connect(self) -> bool:
        """
        Establish connection with the RFID reader device.
        
        The connection process involves:
        1. Creating a new HID device instance
        2. Opening the device using vendor and product IDs
        3. Setting non-blocking mode for improved response handling
        4. Adding initialization delay for device stability
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If connection fails for any reason
        """
        self.logger.debug("Attempting to connect to the device")
        try:
            self.device = hid.device()
            self.device.open(VENDOR_ID, PRODUCT_ID)
            self.device.set_nonblocking(1)  # Enable non-blocking mode for better timing control
            time.sleep(0.1)  # Allow device to stabilize after connection
            self.logger.info("Device connected successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to device: {str(e)}")
            raise ConnectionError(f"Failed to connect to device: {str(e)}")

    def _calc_crc(self, data: List[int]) -> int:
        """
        Calculate CRC-16 checksum for command data using CCITT-16 polynomial.
        
        The CRC calculation uses the following parameters:
        - Polynomial: 0x1021 (CCITT-16)
        - Initial Value: 0xFFFF
        - Final XOR: Inverted
        
        Args:
            data: List of command bytes to calculate CRC for
            
        Returns:
            int: Calculated CRC value (16 bits)
        """
        crc = 0xFFFF  # Initial CRC value
        for byte in data:
            crc ^= byte  # XOR byte into CRC
            for _ in range(8):  # Process each bit
                # If MSB is 1, shift left and XOR with polynomial
                crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
        return (~crc)  # Return inverted CRC

    def _send_command(self, cmd_data: List[int]) -> Optional[List[str]]:
        """
        Send command to device and receive response with robust error handling.

        This method implements the complete command transmission protocol:
        1. Ensures proper timing between commands
        2. Calculates and appends CRC
        3. Formats command according to protocol specifications
        4. Handles device communication with retries
        5. Processes and validates response

        The command format follows the structure:
        [0x00][Command Data][CRC][Padding to 64 bytes]
        
        Args:
            cmd_data: List of command bytes to send
            
        Returns:
            Optional[List[str]]: Response as a list of uppercase hex byte strings (e.g., ["AA","BB",...])
            if successful, or None if no response is received within the timeout
            
        Raises:
            ConnectionError: If device is not connected
            CommunicationError: If transmission fails
        """
        if not self.device:
            self.logger.error("Device not connected")
            raise ConnectionError("Device not connected")

        try:
            # Implement minimum command interval for device stability
            elapsed = time.time() - self._last_command_time
            if elapsed < COMMAND_INTERVAL:
                time.sleep(COMMAND_INTERVAL - elapsed)

            # Prepare command packet with CRC
            crc = self._calc_crc(cmd_data)
            cmd = bytes([0x00] + cmd_data + [(crc >> 8) & 0xFF, crc & 0xFF] + 
                       [0] * (BUFFER_SIZE - len(cmd_data) - 3))

            # Quickly drain any stale data without busy-waiting
            for _ in range(4):  # cap drain attempts to avoid long spins
                if not self.device.read(BUFFER_SIZE):
                    break
                time.sleep(0.001)

            # Send command and update timing
            self.device.write(cmd)
            self._last_command_time = time.time()

            # Poll for response up to DEFAULT_TIMEOUT with small sleeps
            deadline = time.time() + DEFAULT_TIMEOUT
            response = None
            while time.time() < deadline:
                response = self.device.read(BUFFER_SIZE)
                if response:
                    break
                time.sleep(RETRY_DELAY)

            # If still nothing, try a few quick extra retries (for jitter)
            if not response:
                for _ in range(MAX_RETRIES):
                    response = self.device.read(BUFFER_SIZE)
                    if response:
                        break
                    time.sleep(RETRY_DELAY)

            if response:
                # Faster hex conversion without regex
                return [f"{b:02X}" for b in response]

            self.logger.warning("No response received after retries")
            return None

        except ConnectionError:
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error during command transmission: {str(e)}")
            raise CommunicationError(f"Unexpected error during command transmission: {str(e)}")

    def _byte_list_to_hex_string(self, data: List[int]) -> str:
        """
        Convert a list of bytes to a continuous hex string.
        
        Args:
            data: List of bytes to convert
            
        Returns:
            str: Continuous uppercase hex string
        """
        return ''.join(f"{x:02X}" for x in data)

    def buzzer_beep(self) -> RRHFOEM04Result:
        """
        Activate the reader's buzzer with proper timing control.
        
        The buzzer provides audible feedback for successful operations.
        Proper timing delays are implemented before and after the buzzer
        activation to ensure reliable operation.
        
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """
        try:
            # Pre-buzzer delay prevents interference with previous operations
            time.sleep(COMMAND_INTERVAL)
        
            response = self._send_command(CMD_BUZZER_BEEP)
            
            # Empty response is normal for buzzer command, but check status if present
            if response and response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Error activating buzzer: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")
            
            # Post-buzzer delay ensures complete sound generation
            time.sleep(COMMAND_INTERVAL)
            self.logger.info("Buzzer activated successfully")
            return RRHFOEM04Result(success=True, message="Operation Successful")
        
        except Exception as e:
            self.logger.error(f"Error in buzzer activation: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")
    
    def buzzer_on(self) -> RRHFOEM04Result:
        """
        Activate the reader's buzzer.

        The buzzer provides audible feedback for successful operations.

        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """

        try:
        
            response = self._send_command(CMD_BUZZER_ON)
            
            # Empty response is normal for buzzer command, but check status if present
            if response and response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Error activating buzzer: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")

            return RRHFOEM04Result(success=True, message="Operation Successful")
        
        except Exception as e:
            self.logger.error(f"Error in buzzer activation: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")

    def buzzer_off(self) -> RRHFOEM04Result:
        """
        Deactivate the reader's buzzer.

        The buzzer provides audible feedback for successful operations.

        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """

        try:
        
            response = self._send_command(CMD_BUZZER_OFF)
            
            # Empty response is normal for buzzer command, but check status if present
            if response and response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Error deactivating buzzer: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")

            return RRHFOEM04Result(success=True, message="Operation Successful")
        
        except Exception as e:
            self.logger.error(f"Error in buzzer deactivation: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")
        
    def getReaderInfo(self) -> RRHFOEM04Result:
        """
        Retrieve device information from the RFID reader.
        
        This method queries the reader's model and serial number information.
        The response format follows the manufacturer's specification:
        - Bytes 5-20: Reader information (model number + serial)
        - Model number is ASCII encoded, terminated by '-' (0x2D)
        - Serial number occupies the last 3 bytes
        
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """
        try:
            response = self._send_command(CMD_GET_READER_INFO)
            if not response:
                self.logger.error("No response received from get_reader_info command")
                return RRHFOEM04Result(success=False, message="No Response")
            
            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Error getting reader information: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")
            
            # Extract and parse reader information section
            reader_info_part = response[5:21]
            model_end = reader_info_part.index('2D')  # Find '-' delimiter
            
            # Convert model number from hex to ASCII string
            model = bytes.fromhex(''.join(reader_info_part[:model_end])).decode()
            
            # Extract serial number (last 3 bytes)
            serial = ''.join(reader_info_part[-3:])

            return RRHFOEM04Result(success=True, message="Operation Successful", data={'model': model, 'serial': serial}) 
            
        except Exception as e:
            self.logger.error(f"Error in get_reader_info: {e}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")

    # === ISO15693 Protocol Implementation ===

    def ISO15693_singleSlotInventory(self) -> RRHFOEM04Result:
        """
        Perform an ISO15693 single slot inventory scan.
        
        This method implements the ISO15693 inventory process with single slot
        collision resolution. It's more efficient for detecting a single tag
        but may have collisions with multiple tags.
        
        The command structure:
        - 0x04: Frame length
        - 0x10: ISO15693 protocol identifier
        - 0x01: Inventory command
        - 0x26: Flags (no AFI, single slot)
        
        Response format:
        - Byte 5: Number of tags found
        - Bytes 6+: UIDs, 8 bytes per tag (little-endian)
        
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """
        try:
            response = self._send_command(CMD_ISO15693_SINGLE_SLOT_INVENTORY)

            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Error in inventory scan: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")
            
            tag_uids = []
            total_tags = int(response[5])
            
            # Extract and format UIDs from response
            # UIDs are 64-bit (8 bytes) stored in little-endian format
            for i in range(total_tags):
                start_index = 6 + (i * 8)
                # Convert UID to big-endian format for standard representation
                uid = ''.join(response[start_index:start_index + 8][::-1])
                tag_uids.append(uid)

            return RRHFOEM04Result(success=True, message="Operation Successful", data=tag_uids)
            
        except Exception as e:
            self.logger.error(f"Error in ISO15693 inventory scan: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")
    
    def ISO15693_16SlotInventory(self) -> RRHFOEM04Result:
        """
        Perform an ISO15693 16-slot inventory scan to detect multiple RFID tags.
        
        This method implements the more robust 16-slot anti-collision algorithm
        specified in ISO15693-3. Unlike single-slot inventory, this approach is
        optimized for detecting multiple tags simultaneously by using a time-slot
        based collision resolution mechanism:
        
        1. Reader sends inventory request with 16-slot flag
        2. Each tag generates a random number (0-15) selecting its response slot
        3. Tags respond only in their chosen time slot
        4. Reader collects responses from all 16 possible slots
        
        This approach significantly reduces collision probability compared to
        single-slot inventory when multiple tags are present in the field.
        
        Response format:
        - Byte 5: Number of tags detected
        - Bytes 6+: Sequence of 8-byte UIDs (little-endian format)

        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """
        try:
            response = self._send_command(CMD_ISO15693_16_SLOT_INVENTORY)

            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"16-slot inventory scan failed: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")
            
            tag_uids = []
            # Extract number of tags found
            total_tags = int(response[5])
            
            # Process and format each detected tag's UID
            for i in range(total_tags):
                # UIDs start at byte 6, each UID is 8 bytes
                start_index = 6 + (i * 8)
                # Convert from little-endian to standard format
                uid = ''.join(response[start_index:start_index + 8][::-1])
                tag_uids.append(uid)

            return RRHFOEM04Result(success=True, message="Operation Successful", data=tag_uids)
            
        except Exception as e:
            self.logger.error(f"Error in 16-slot inventory scan: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")

    def ISO15693_readSingleBlock(self, block_number: int, block_size: int = 4, with_select_flag: bool = False, uid: str = None) -> RRHFOEM04Result:
        """
        Read a single block from an ISO15693 tag.
        
        ISO15693 memory is organized in blocks (typically 4 bytes each).
        This method supports three addressing modes:
        1. Non-addressed (any tag in field responds)
        2. Select flag (previously selected tag responds)
        3. Addressed (specific tag by UID responds)
        
        Args:
            block_number: Memory block to read (0-255)
            block_size: Size of each block in bytes (default 4)
            with_select_flag: Use select flag mode
            uid: Target specific tag by UID
            
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """
        try:
            if not 0 <= block_number <= 255:
                raise ValueError("Block number must be between 0 and 255")
            
            # Build command based on addressing mode
            if uid:
                uid_bytes = bytes.fromhex(uid)[::-1]  # Convert to little-endian
                cmd = CMD_ISO15693_READ_SINGLE_BLOCK_WITH_ADDRESS_FLAG.copy()
                cmd.extend([*uid_bytes])
            else:
                cmd = (CMD_ISO15693_READ_SINGLE_BLOCK_WITH_SELECT_FLAG.copy() 
                      if with_select_flag else CMD_ISO15693_READ_SINGLE_BLOCK.copy())
                
            cmd.extend([block_size, block_number])

            response = self._send_command(cmd)
            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Read operation failed: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")
            
            # Extract and reverse block data (convert from little-endian)
            block_data = response[6:6 + block_size]

            return RRHFOEM04Result(success=True, message="Operation Successful", data=''.join(block_data[::-1]))

        except Exception as e:
            self.logger.error(f"Error in ISO15693_readSingleBlock: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")

    def ISO15693_writeSingleBlock(self, block_number: int, data: str, block_size: int = 4, with_select_flag: bool = False, uid: str = None) -> RRHFOEM04Result:
        """
        Write data to a single block of an ISO15693 tag.
        
        This method handles the complex process of writing data to RFID memory.
        The operation must carefully consider:
        1. Data formatting (converting to appropriate byte format)
        2. Block size limitations
        3. Proper addressing mode selection
        4. Error handling and verification
        
        The write process follows ISO15693 specifications, with the data being
        written in little-endian format to match the tag's memory organization.
        
        Args:
            block_number: Target memory block (0-255)
            data: Data to write (will be encoded as UTF-8)
            block_size: Size of memory block in bytes (default 4)
            with_select_flag: Use select flag for previously selected tag
            uid: Target specific tag by UID
            
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """
        try:
            if not 0 <= block_number <= 255:
                raise ValueError("Block number must be between 0 and 255")
            
            # Convert input data to bytes for transmission
            data_bytes = bytes(data, "utf-8")

            # Pad data bytes if necessary
            if data_bytes and len(data_bytes) < block_size:
                data_bytes = data_bytes.ljust(block_size, b'\x00')
            
            # Select appropriate command based on addressing mode
            if uid:
                uid_bytes = bytes.fromhex(uid)[::-1]  # Convert to little-endian
                cmd = CMD_ISO15693_WRITE_SINGLE_BLOCK_WITH_ADDRESS_FLAG.copy()
                cmd.extend([*uid_bytes])
            else:
                cmd = (CMD_ISO15693_WRITE_SINGLE_BLOCK_WITH_SELECT_FLAG.copy()
                      if with_select_flag else CMD_ISO15693_WRITE_SINGLE_BLOCK.copy())
                
            # Update command length and append write parameters
            cmd[0] += block_size  # Adjust command length byte
            cmd.extend([block_size, block_number, *data_bytes])

            response = self._send_command(cmd)
            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Write operation failed with status: {response[3:5]}")
                raise CommandError(f"Write operation failed with status: {response[3:5]}")

            return RRHFOEM04Result(success=True, message="Operation Successful")

        except Exception as e:
            self.logger.error(f"Error in ISO15693_writeSingleBlock: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")

    def ISO15693_readMultipleBlocks(self, start_block_number: int, total_blocks: int = 5, block_size: int = 4, with_select_flag: bool = False, uid: str = None) -> RRHFOEM04Result:
        """
        Read multiple consecutive blocks from an ISO15693 tag in a single operation.
        
        This method implements an optimized multi-block read operation that:
        1. Reduces overall communication overhead compared to single block reads
        2. Maintains data consistency by reading blocks in one transaction
        3. Supports various addressing modes for different security needs
        
        The multi-block read process:
        1. Validates block numbers and counts
        2. Selects appropriate command mode (non-addressed/selected/addressed)
        3. Sends extended read command with block count
        4. Processes response containing multiple block data
        
        Memory Organization Note:
        ISO15693 tags typically organize memory in 4-byte blocks. When reading
        multiple blocks, the data is returned as a continuous sequence of blocks
        in little-endian format.
        
        Args:
            start_block_number: First block to read (0-255)
            total_blocks: Number of consecutive blocks to read
            block_size: Size of each memory block in bytes (default 4)
            with_select_flag: Use select flag for previously selected tag
            uid: Target specific tag by UID
            
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
            
        The returned data string contains all blocks concatenated in order,
        with each block's data converted from little-endian to standard format.
        
        Example:
            Reading 2 blocks starting at block 5 might return:
            "0123456789ABCDEF" (representing 8 bytes across 2 blocks)
        """
        try:
            # Validate start block number
            if not 0 <= start_block_number <= 255:
                raise ValueError("Start block number must be between 0 and 255")
            
            # Ensure total blocks won't exceed memory boundaries
            if not 0 <= start_block_number + total_blocks <= 256:
                raise ValueError(f"Cannot read {total_blocks} blocks starting at {start_block_number}")
            
            # Select appropriate command based on addressing mode
            if uid:
                # Convert UID to bytes in little-endian format
                uid_bytes = bytes.fromhex(uid)[::-1]
                cmd = CMD_ISO15693_READ_MULTIPLE_BLOCKS_WITH_ADDRESS_FLAG.copy()
                cmd.extend([*uid_bytes])
            else:
                cmd = (CMD_ISO15693_READ_MULTIPLE_BLOCKS_WITH_SELECT_FLAG.copy()
                      if with_select_flag else CMD_ISO15693_READ_MULTIPLE_BLOCKS.copy())
            
            # Append read parameters to command
            cmd.extend([block_size, start_block_number, total_blocks])

            response = self._send_command(cmd)
            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Multiple block read failed: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")
            
            # Process the multi-block response
            # Skip first 6 bytes (command header and status)
            # Each block's data needs to be byte-reversed due to little-endian format
            block_data = response[6:6 + (block_size * (total_blocks + 1))]
            
            # Process each block individually to maintain proper byte ordering
            data_blocks = []
            for i in range(0, len(block_data), block_size):
                # Extract and reverse each block's bytes
                block = block_data[i:i + block_size]
                data_blocks.append(''.join(block[::-1]))
            
            # Concatenate all blocks into final result
            return RRHFOEM04Result(success=True, message="Operation Successful", data=''.join(data_blocks)) 

        except Exception as e:
            self.logger.error(f"Error in multiple block read: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")
        
    def ISO15693_writeMultipleBlocks(self, start_block_number: int, data: str, block_size: int = 4, with_select_flag: bool = False, uid: str = None) -> RRHFOEM04Result:
        
        """
        Write data across multiple blocks of an ISO15693 tag.
        
        Args:
            start_block_number: First block to write to (0-255)
            data: Complete data string to write
            block_size: Size of each memory block
            with_select_flag: Use select flag mode
            uid: Target specific tag by UID
            
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """

        try:
            if not 0 <= start_block_number <= 255:
                raise ValueError("Start block number must be between 0 and 255")

            # Prepare data by converting to bytes
            data_bytes = bytes(data, "utf-8")

            # Calculate padding length
            padding_length = (block_size - len(data_bytes) % block_size) % block_size

            # Pad data_bytes with 0 if necessary
            if padding_length > 0:
                data_bytes = data_bytes + (b'\x00' * padding_length)

            total_blocks = len(data_bytes) // block_size

            # Prepare base command structure
            if uid:
                uid_bytes = bytes.fromhex(uid)[::-1]
                cmd = CMD_ISO15693_WRITE_MULTIPLE_BLOCK_WITH_ADDRESS_FLAG.copy()
                cmd.extend([*uid_bytes])
            else:
                cmd = (CMD_ISO15693_WRITE_MULTIPLE_BLOCK_WITH_SELECT_FLAG.copy()
                      if with_select_flag else CMD_ISO15693_WRITE_MULTIPLE_BLOCK.copy())
            
            cmd[0] += len(data_bytes)  # Adjust command length

            cmd.extend([block_size, start_block_number, total_blocks, *data_bytes])

            response = self._send_command(cmd)

            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Write operation failed with status: {response[3:5]}")
                raise CommandError(f"Write operation failed with status: {response[3:5]}")

            return RRHFOEM04Result(success=True, message="Operation Succesful")

        except Exception as e:
            self.logger.error(f"Error in ISO15693_writeMultipleBlocks: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")
        
    def ISO15693_writeAFI(self, afi: int, with_select_flag: bool = False, uid: str = None) -> RRHFOEM04Result:
        """
        Write the Application Family Identifier (AFI) to an ISO15693 tag.
        
        The AFI is a single byte used to identify the type or application family of the tag.
        This method handles the process of writing the AFI, ensuring compliance with ISO15693 
        specifications. It also provides options for targeting specific tags or using the 
        select flag for previously selected tags.
        
        Args:
            afi: The Application Family Identifier, a single byte (e.g., `b'\x00'`).
            with_select_flag: Whether to use the select flag for a previously selected tag.
            uid: Optionally, specify the unique identifier of the target tag. If not provided, 
                the operation targets the selected tag.

        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """

        try:
            if not 0 <= afi <= 255:
                raise ValueError("AFI must be an integer between 0 and 255.")
            
            # Convert AFI to a single byte for ISO15693 operations
            afi_byte = afi.to_bytes(1, byteorder="little")
            
            # Select appropriate command based on addressing mode
            if uid:
                uid_bytes = bytes.fromhex(uid)[::-1]  # Convert to little-endian
                cmd = CMD_ISO15693_WRITE_AFI_WITH_ADDRESS_FLAG.copy()
                cmd.extend([*uid_bytes])
            else:
                cmd = (CMD_ISO15693_WRITE_AFI_WITH_SELECT_FLAG.copy()
                      if with_select_flag else CMD_ISO15693_WRITE_AFI.copy())
                
            # append write parameters
            cmd.extend([*afi_byte])

            response = self._send_command(cmd)
            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"AFI Write operation failed with status: {response[3:5]}")
                raise CommandError(f"AFI Write operation failed with status: {response[3:5]}")

            return RRHFOEM04Result(success=True, message="Operation Successful")

        except Exception as e:
            self.logger.error(f"Error in ISO15693_writeAFI: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")
        
    # === ISO14443A Protocol Implementation ===

    def ISO14443A_Inventory(self) -> RRHFOEM04Result:
        """
        Perform an ISO14443A inventory scan to detect nearby cards.
        
        ISO14443A is a protocol commonly used by contactless smart cards and NFC devices.
        Unlike ISO15693, ISO14443A is designed for closer-range communication (typically <10cm)
        and supports more complex security features.
        
        The inventory process follows the ISO14443A anti-collision procedure:
        1. Send REQA (Request Type A) command
        2. Perform anti-collision loop
        3. Receive unique identifier (UID) from responding card
        
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """
        try:
            response = self._send_command(CMD_ISO14443A_INVENTORY)

            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Inventory scan failed: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")

            # Extract UID length and data
            uid_length = int(response[5])
            uid = ''.join(response[6:6 + uid_length])
            
            # the tag is autoselected on inventory
            self._mifare_selected_uid = uid
            return RRHFOEM04Result(success=True, message="Operation Successful", data=uid)
            
        except Exception as e:
            self.logger.error(f"Error in ISO14443A inventory scan: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")

    def ISO14443A_selectCard(self, uid: str, uid_length: int = 4) -> RRHFOEM04Result:
        """
        Select a specific ISO14443A card for further operations.
        
        Card selection is a crucial step in ISO14443A operations as it:
        1. Ensures communication with a specific card when multiple are present
        2. Puts the card in an active state for subsequent operations
        3. Establishes the communication channel for secure operations
        
        The selection process follows the ISO14443A-3 standard:
        1. Send SELECT command with card's UID
        2. Receive and verify Select Acknowledge (SAK)
        3. Card enters ACTIVE state if successful
        
        Args:
            uid: Card's unique identifier in hex string format
            uid_length: Length of UID (usually 4 or 7 bytes)
            
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """
        try:
            # Convert UID from hex string to bytes
            uid_bytes = bytes.fromhex(uid)

            # Prepare and send select command
            cmd = CMD_ISO14443A_SELECT_CARD.copy()
            cmd.extend([uid_length, *uid_bytes])
            response = self._send_command(cmd)

            if not response:
                self.logger.error("No response from card during selection")
                return RRHFOEM04Result(success=False, message="No Response")
                
            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Card selection failed: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")

            self._mifare_selected_uid = uid
            return RRHFOEM04Result(success=True, message="Operation Successful")
    
        except Exception as e:
            self.logger.error(f"Error in card selection: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")

    def ISO14443A_mifareAuthenticate(self, uid: str, block_number: int, key_type: str = 'A', key: str = "FFFFFFFFFFFF") -> RRHFOEM04Result:
        """
        Authenticate with a Mifare Classic card using specified key.
        
        Mifare Classic authentication uses a mutual three-pass authentication:
        1. Reader sends authentication command with key type
        2. Card responds with random number (challenge)
        3. Reader calculates response using authentication key
        4. Card verifies and grants access if correct
        
        Security Note: This implementation uses the default key (FFFFFFFFFFFF).
        In production, proper key management should be implemented.
        
        Args:
            uid: Card's unique identifier in hex format
            block_number: Memory block to authenticate (0-255)
            key_type: 'A' or 'B' (Mifare Classic has two keys per sector)
            key: Authentication key in hex format (12 chars / 6 bytes)
            
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        
        Raises:
            ValidationError: If parameters are invalid
            AuthenticationError: If authentication fails
            TagError: If card is not present or responsive
        """
        try:
            # Input validation
            if not 0 <= block_number <= 255:
                raise ValidationError("Block number must be between 0 and 255")
                
            if key_type not in ['A', 'B']:
                raise ValidationError("Key type must be 'A' or 'B'")
                
            if len(key) != 12:  # 6 bytes = 12 hex characters
                raise ValidationError("Key must be 6 bytes (12 hex characters)")
            
            # Convert key type to command byte (0x60 for A, 0x61 for B)
            key_type_byte = 0x60 if key_type == 'A' else 0x61
                
            try:
                # Convert UID and key to bytes
                uid_bytes = bytes.fromhex(uid)
                key_bytes = bytes.fromhex(key)
            except ValueError:
                raise ValidationError("Invalid UID or key format (must be hex string)")

            # Select card before authentication
            # Check if we need to select the card
            if self._mifare_selected_uid != uid:
                if not self.ISO14443A_selectCard(uid).success:
                    self.logger.error("Card not present or cannot be selected")
                    raise TagError("Card not present or cannot be selected")
                
                # Update selected card and clear previous authentication cache
                self._mifare_selected_uid = uid
                self._mifare_auth_blocks.clear()

            # Build authentication command:
            # [Command][UID][Block][KeyType][Key]
            cmd = CMD_ISO14443A_MIFARE_AUTHENTICATE.copy()
            cmd.extend([*uid_bytes, block_number, key_type_byte, *key_bytes])
            
            response = self._send_command(cmd)
            
            if not response:
                self.logger.error("No response during authentication")
                raise AuthenticationError("No response during authentication")
                
            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Authentication failed with status: {response[3:5]}")
                raise AuthenticationError(f"Authentication failed with status: {response[3:5]}")

            # Cache successful authentication
            if uid not in self._mifare_auth_blocks:
                self._mifare_auth_blocks[uid] = set()
            self._mifare_auth_blocks[uid].add(block_number)
            
            return RRHFOEM04Result(success=True, message="Operation Successful")
            
        except (ValidationError, TagError, AuthenticationError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during authentication: {str(e)}")
            raise AuthenticationError(f"Unexpected error during authentication: {str(e)}")

    def ISO14443A_mifareRead(self, uid: Optional[str] = None, block_number: int = 0) -> RRHFOEM04Result:
        """
        Read a block from an authenticated Mifare Classic card.
        
        Mifare Classic cards organize memory in 16-byte blocks grouped into sectors.
        Each sector is protected by two keys (A and B). Reading requires:
        1. Prior authentication with appropriate key
        2. Proper access rights for the block
        3. Active connection maintained since authentication
        
        Args:
        uid: Card's unique identifier. If not provided, the method will attempt to fetch the UID of a nearby card.
            block_number: Memory block to read (0-255)
            
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """
        try:
            if not 0 <= block_number <= 255:
                raise ValueError("Block number must be between 0 and 255")
            
            # Fetch UID if not provided
            if not uid:
                inventory_result = self.ISO14443A_Inventory()
                if not inventory_result.success or not inventory_result.data:
                    return RRHFOEM04Result(success=False, message="No card found")
                uid = inventory_result.data          
            
            # Authenticate block before reading
            auth_result = self.ISO14443A_mifareAuthenticate(uid=uid, block_number=block_number)
            if not auth_result.success:
                return RRHFOEM04Result(success=False, message="Mifare Authenticate Failed")
            
            # Prepare and send read command
            cmd = CMD_ISO14443A_MIFARE_READ.copy()
            cmd.append(block_number)

            response = self._send_command(cmd)
            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Read operation failed: {response[3:5]}")
                return RRHFOEM04Result(success=False, message="Operation Failed")

            # Extract 16 bytes of block data
            block_data = response[5:5 + MIFARE_BLOCK_SIZE]

            return RRHFOEM04Result(success=True, message="Operation Successful", data=''.join(block_data))
        
        except Exception as e:
            self.logger.error(f"Error reading Mifare block: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")
    
    def ISO14443A_mifareWrite(self, data: str, uid: Optional[str] = None, block_number: int = 1) -> RRHFOEM04Result:
        """
        Write data to a specific block on an authenticated Mifare Classic card.
        
        Mifare Classic cards organize memory in 16-byte blocks grouped into sectors.
        Each sector is protected by two keys (A and B). Writing requires:
        1. Prior authentication with an appropriate key
        2. Proper access rights for the block
        3. Active connection maintained since authentication
        
        Args:
            data: Data to write to the block, provided as a 16-byte string (32 hex characters).
            uid: Card's unique identifier.
            block_number: Memory block to write (0-255). Defaults to 1 since block 0 is typically reserved 
                        for manufacturer data.
        
        Returns:
            RRHFOEM04Result: A RRHFOEM04Result object containing success status, message and response data
        """

        try:
            if not 0 <= block_number <= 255:
                raise ValueError("Block number must be between 0 and 255")

            # Convert input data to bytes for transmission
            data_bytes = bytes(data, "utf-8")

            # Pad data bytes if necessary
            if data_bytes and len(data_bytes) < MIFARE_BLOCK_SIZE:
                data_bytes = data_bytes.ljust(MIFARE_BLOCK_SIZE, b'\x00')

            # Fetch UID if not provided
            if not uid:
                inventory_result = self.ISO14443A_Inventory()
                if not inventory_result.success or not inventory_result.data:
                    return RRHFOEM04Result(success=False, message="No card found")
                uid = inventory_result.data       

            # Authenticate block before writing
            # Check if this block is already authenticated
            if uid not in self._mifare_auth_blocks or block_number not in self._mifare_auth_blocks[uid]:
                if not self.ISO14443A_mifareAuthenticate(uid=uid, block_number=block_number).success:
                    # Clear state on authentication failure
                    self.logger.error("Authentication failed before write")
                    self._mifare_selected_uid = None
                    self._mifare_auth_blocks.clear()
                    return RRHFOEM04Result(success=False, message="Mifare Authentication Failed")

                # Cache successful authentication
                if uid not in self._mifare_auth_blocks:
                    self._mifare_auth_blocks[uid] = set()
                self._mifare_auth_blocks[uid].add(block_number)

            # Prepare and send write command
            cmd = CMD_ISO14443A_MIFARE_WRITE.copy()
            cmd.extend([block_number, *data_bytes])

            response = self._send_command(cmd)
            if response[3:5] != STATUS_SUCCESS:
                self.logger.error(f"Write operation failed with status: {response[3:5]}")
                raise CommandError(f"Write operation failed with status: {response[3:5]}")

            return RRHFOEM04Result(success=True, message="Operation Successful")

        except Exception as e:
            self.logger.error(f"Error writing Mifare block: {str(e)}")
            return RRHFOEM04Result(success=False, message=f"Operation Failed: <{str(e)}>")
        
    def close(self) -> None:
        """
        Close the connection to the RFID reader device.
        
        This method ensures proper cleanup of system resources by:
        1. Closing the HID connection
        2. Releasing the device handle
        3. Resetting the device reference
        """
        self.logger.debug("Closing device connection")
        if self.device:
            try:
                self.device.close()
                self.logger.info("Device connection closed")
            finally:
                self.device = None

    def __enter__(self):
        """
        Context manager entry method.
        
        Enables use of 'with' statement for automatic resource management:
        with RRHFOEM04() as reader:
            # Device automatically connected here
            reader.getReaderInfo()
            # Device automatically closed after block
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method.
        
        Ensures device is properly closed even if an exception occurs
        during operations within the 'with' block.
        """
        self.close()