"""Core implementation of the RRHFOEM04 RFID/NFC reader interface."""

import time
from typing import List, Optional, Dict
import hid
import re
import traceback

from .constants import *
from .exceptions import *

class RRHFOEM04:
    """Interface for RRHFOEM04 RFID/NFC reader."""

    def __init__(self, auto_connect: bool = True):
        self.device: Optional[hid.device] = None
        self._last_command_time = 0
        if auto_connect:
            self.connect()


    def connect(self) -> bool:
        try:
            self.device = hid.device()
            self.device.open(VENDOR_ID, PRODUCT_ID)
            self.device.set_nonblocking(1)
            # Add initialization delay
            time.sleep(0.1)
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {str(e)}")


    def _calc_crc(self, data: List[int]) -> int:
        """Calculate CRC-16 for command data.
        
        Args:
            data: List of command bytes
            
        Returns:
            int: Calculated CRC value
        """
        crc = 0xFFFF
        for byte in data:   # loop each byte
            crc ^= byte     # calc crc main logic
            for _ in range(8):
                crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
        return (~crc)       # invert crc before returning


    def _send_command(self, cmd_data: List[int]) -> Optional[str]:
        """Send command and receive response with improved timing control."""
        if not self.device:
            raise ConnectionError("Device not connected")

        try:
            # Ensure minimum time between commands
            elapsed = time.time() - self._last_command_time
            if elapsed < 0.1:  # 100ms minimum between commands
                time.sleep(0.1 - elapsed)

            # Calculate CRC and prepare command
            crc = self._calc_crc(cmd_data)
            cmd = bytes([0x00] + cmd_data + [(crc >> 8) & 0xFF, crc & 0xFF] + [0] * (BUFFER_SIZE - len(cmd_data) - 3))

            # Clear any pending data
            while self.device.read(BUFFER_SIZE):
                pass

            # Send command
            self.device.write(cmd)
            
            # Update last command time
            self._last_command_time = time.time()
            
            # Wait for response
            time.sleep(DEFAULT_TIMEOUT)

            # Read response with retries
            for _ in range(3):  # Try up to 3 times
                response = self.device.read(BUFFER_SIZE)
                if response:
                    return re.findall('..?', self._byte_list_to_hex_string(response)) # return response as hex string
                
                time.sleep(0.02)  # Short delay between retries

            return None

        except Exception as e:
            raise CommunicationError(f"Communication error: {str(e)}")

    def _byte_list_to_hex_string(self, data: List[int]) -> str:
        return ''.join(f"{x:02X}" for x in data)
    
    def buzzer(self) -> bool:
        """Activate buzzer with proper timing control."""
        try:
            # Add delay before buzzer command
            time.sleep(0.1)
            
            response = self._send_command(CMD_BUZZER)
            
            # Just in case. Response is almost always empty
            if response and response[3:5] != STATUS_SUCCESS :
                print(f"Error sounding buzzer: {response[3:5]}")
                return False
            
            # Add delay after buzzer command
            time.sleep(0.1)

            # Return True as long as command didn't raise an exception
            # The empty response is normal for this command
            return True
        except RRHFOEMError:
            return False


    def getReaderInfo(self) -> Optional[Dict]:
        """
        Get device information from the RFID reader.
        
        Returns:
        - A dictionary containing 'model' and 'serial' if the information is successfully retrieved
        - None if no response is received or an error occurs
        """
        try:
            # Send command to get reader information
            response = self._send_command(CMD_GET_READER_INFO)
            if not response:
                print("No response received from get_reader_info command")
                return None
            
            # Check if the status in the response is successful
            if response[3:5] != STATUS_SUCCESS:
                print(f"Error getting Reader Information: {response[3:5]}")
                return None
            
            # Extract the relevant part of the response containing reader information
            reader_info_part = response[5:21]

            # Find the end of the model string (assumed to be marked by '-')
            model_end = reader_info_part.index('2D')  # '-' is represented as 0x2D in ASCII
            
            # Convert the model part to a string
            model = bytes.fromhex(''.join(reader_info_part[:model_end])).decode()
            
            # Extract the serial number from the last 3 bytes of the reader info part
            serial = ''.join(reader_info_part[-3:])

            # Return the extracted model and serial number in a dictionary
            return {
                'model': model,
                'serial': serial
            }
            
        except Exception as e:
            # Handle any exceptions that occur during the process
            print(f"Error in get_reader_info: {e}")
            return None


    def ISO15693_singleSlotInventory(self) -> Optional[List]:
        """
        Perform an ISO15693 single slot inventory scan to detect nearby RFID tags.
        
        Returns:
        - A list of tag UIDs (unique identifiers) if tags are found
        - None if no tags are detected or an error occurs
        """
        try:
            # Send inventory command 
            # 0x04 = Frame length
            # 0x10, 0x02 = Command code and flags for single slot inventory
            # 0x26 = Default flag value for inventory without AFI
            response = self._send_command(CMD_ISO15693_SINGLE_SLOT_INVENTORY)

            if response[3:5] != STATUS_SUCCESS :
                print(f"Error getting ISO15693 inventory: {response[3:5]}")
                return None
            
            # no of tags detected
            total_tags = int(response[5])

            if total_tags == 0:
                print("No tags detected")
                return []
            
            # Parse UIDs 
            # Each UID is 8 bytes long, starting from byte 5, ie. index 6
            tag_uids = []

            for i in range(total_tags):
                # Extract UID, reverse byte order (little-endian to big-endian)
                start_index = 6 + (i * 8)
                uid = ''.join(response[start_index:start_index + 8][::-1])
                tag_uids.append(uid)

            return tag_uids
            
        except Exception as e:
            print(f"Error in ISO15693 inventory scan: {str(e)}")
            return None


    def ISO15693_16SlotInventory(self) -> Optional[List]:
        """
        Perform an ISO15693 16 slot inventory scan to detect nearby RFID tags.
        
        Returns:
        - A list of tag UIDs (unique identifiers) if tags are found
        - None if no tags are detected or an error occurs
        """
        try:
            response = self._send_command(CMD_ISO15693_16_SLOT_INVENTORY)

            if response[3:5] != STATUS_SUCCESS :
                print(f"Error getting ISO15693 inventory: {response[3:5]}")
                return None
            
            # no of tags detected
            total_tags = int(response[5])

            if total_tags == 0:
                print("No tags detected")
                return []
            
            # Parse UIDs 
            # Each UID is 8 bytes long, starting from byte 5, ie. index 6
            tag_uids = []

            for i in range(total_tags):
                # Extract UID, reverse byte order (little-endian to big-endian)
                start_index = 6 + (i * 8)
                uid = ''.join(response[start_index:start_index + 8][::-1])
                tag_uids.append(uid)

            return tag_uids
            
        except Exception as e:
            print(f"Error in ISO15693 inventory scan: {str(e)}")
            return None


    def ISO14443A_Inventory(self) -> Optional[str]:
        try:
            response = self._send_command(CMD_ISO14443A_INVENTORY)

            if response[3:5] != STATUS_SUCCESS :
                print(f"Error getting ISO14443A inventory: {response[3:5]}")
                return None

            # length of uid detected
            uid_length = int(response[5])

            # Extract UID
            start_index = 6
            uid = ''.join(response[start_index:start_index + uid_length])

            return uid
        except Exception as e:
            print(f"Error in ISO14443A inventory scan: {str(e)}")
            return None


    def ISO15693_readSingleBlock(self, block_number: int, block_size: int = 4, with_select_flag: bool = False, uid: str = None) -> Optional[str]:
        """
        Read a single block from an ISO15693 tag.
        
        Args:
            block_number: The block number to read (0-255)
            with_select_flag: If True, uses the Select flag for previously selected tags
            uid: If provided, uses Address flag to target a specific tag by UID
            
        Returns:
            The data read from the block, or None if the read failed
            
        Note: According to the protocol, you must either:
        - Use no flags (reads any tag in field)
        - Use the Select flag (reads previously selected tag)
        - Use the Address flag with UID (reads specific tag)
        """
        try:
            # Validate block number
            if not 0 <= block_number <= 255:
                raise ValueError("Block number must be between 0 and 255")
            
            # Determine flags and command structure based on mode
            if uid:
                # Convert UID string to bytes and reverse for little-endian
                uid_bytes = bytes.fromhex(uid)[::-1]

                cmd = CMD_ISO15693_READ_SINGLE_BLOCK_WITH_ADDRESS_FLAG
                cmd.extend([*uid_bytes])
            
            else:
                if with_select_flag:
                    cmd = CMD_ISO15693_READ_SINGLE_BLOCK_WITH_SELECT_FLAG
                else:
                    cmd = CMD_ISO15693_READ_SINGLE_BLOCK
                
            # common part to be appended to cmd
            cmd.extend([block_size, block_number])

            response = self._send_command(cmd)

            if response[3:5] != STATUS_SUCCESS :
                print(f"Error in ISO15693_readSingleBlock: {response[3:5]}")
                return None
            
            block_data = response[6: 6 + block_size]

            return ''.join(block_data[::-1])

        except Exception as e:
            print(f"Error in ISO15693_readSingleBlock: {str(e)}")
            return None


    def ISO15693_writeSingleBlock(self, block_number: int, data: str, block_size: int = 4, with_select_flag: bool = False, uid: str = None) -> bool:
        """
        Write to a single block of an ISO15693 tag.
        
        Args:
            block_number: The block number to write to (0-255)
            data: Data to be written
            with_select_flag: If True, uses the Select flag for previously selected tags
            uid: If provided, uses Address flag to target a specific tag by UID
            
        Returns:
            True if data successfully written to block, or False if the write failed
            
        Note: According to the protocol, you must either:
        - Use no flags (reads any tag in field)
        - Use the Select flag (reads previously selected tag)
        - Use the Address flag with UID (reads specific tag)
        """
        try:
            # Validate block number
            if not 0 <= block_number <= 255:
                raise ValueError("Block number must be between 0 and 255")
            
            # Convert data string to bytes and reverse for little-endian
            data_bytes = bytes(data, "utf-8")
            
            # Determine flags and command structure based on mode
            if uid:
                # Convert UID string to bytes and reverse for little-endian
                uid_bytes = bytes.fromhex(uid)[::-1]

                cmd = CMD_ISO15693_WRITE_SINGLE_BLOCK_WITH_ADDRESS_FLAG
                cmd.extend([*uid_bytes])
            
            else:
                if with_select_flag:
                    cmd = CMD_ISO15693_WRITE_SINGLE_BLOCK_WITH_SELECT_FLAG
                else:
                    cmd = CMD_ISO15693_WRITE_SINGLE_BLOCK
                
            # common part to be appended to cmd
            cmd[0] += block_size
            cmd.extend([block_size, block_number, *data_bytes])

            response = self._send_command(cmd)

            if response[3:5] != STATUS_SUCCESS :
                print(f"Error in ISO15693_writeSingleBlock: {response[3:5]}")
                return False

            return True

        except Exception as e:
            print(f"Error in ISO15693_writeSingleBlock: {str(e)}")
            return False


    def ISO15693_writeMultipleBlocks(self, start_block_number: int, data: str, delimiter: str = "", block_size: int = 4, with_select_flag: bool = False, uid: str = None) -> bool:
        """
        Write to multiple blocks of an ISO15693 tag.
        
        Args:
            start_block_number: The block number to start writing from (0-255)
            data: Data to be written
            with_select_flag: If True, uses the Select flag for previously selected tags
            uid: If provided, uses Address flag to target a specific tag by UID
            
        Returns:
            True if data successfully written to block, or False if the write failed
            
        Note: According to the protocol, you must either:
        - Use no flags (reads any tag in field)
        - Use the Select flag (reads previously selected tag)
        - Use the Address flag with UID (reads specific tag)
        """
        try:
            # Validate block start number
            if not 0 <= start_block_number <= 255:
                raise ValueError("Start block number must be between 0 and 255")

            # Convert data string to bytes and reverse for little-endian
            data_bytes = bytes(data + delimiter, "utf-8")

            data_chunks_per_block = [data_bytes[i: i + block_size] for i in range(0, len(data_bytes), block_size)]

            # Validate block end number
            if not start_block_number <= start_block_number + len(data_chunks_per_block) <= 255:
                raise ValueError("End block number must be between start_block_number and 255")
            
            # Pad the last chunk if it's less than the block size
            if data_chunks_per_block and len(data_chunks_per_block[-1]) < block_size:
                data_chunks_per_block[-1] = data_chunks_per_block[-1].ljust(block_size, b'\x00')

            # Determine flags and command structure based on mode
            if uid:
                # Convert UID string to bytes and reverse for little-endian
                uid_bytes = bytes.fromhex(uid)[::-1]

                cmd = CMD_ISO15693_WRITE_SINGLE_BLOCK_WITH_ADDRESS_FLAG
                cmd.extend([*uid_bytes])
            
            else:
                if with_select_flag:
                    cmd = CMD_ISO15693_WRITE_SINGLE_BLOCK_WITH_SELECT_FLAG
                else:
                    cmd = CMD_ISO15693_WRITE_SINGLE_BLOCK
                

            cmd[0] += block_size

            # write each blocks of data to data blocks
            for i, data_chunk in enumerate(data_chunks_per_block):
                # common part to be appended to cmd
                cmd.extend([block_size, start_block_number + (i), *data_chunk])

                response = self._send_command(cmd)

                if response[3:5] != STATUS_SUCCESS :
                    print(f"Error in ISO15693_writeMultipleBlock: {response[3:5]}")
                    return False
                
                # remove appended part from cmd
                cmd = cmd[:-6]       

            return True

        except Exception as e:
            print(f"Error in ISO15693_writeMultipleBlock: {str(e)}")
            return False


    def ISO15693_readMultipleBlock(self, start_block_number: int, total_blocks: int = 5, block_size: int = 4, with_select_flag: bool = False, uid: str = None) -> Optional[str]:
        """
        Read multiple blocks from an ISO15693 tag.
        
        Args:
            block_number: The block number to read (0-255)
            total_blocks: The number of simultaneous blocks to read
            with_select_flag: If True, uses the Select flag for previously selected tags
            uid: If provided, uses Address flag to target a specific tag by UID
            
        Returns:
            The data read from the blocks, or None if the read failed
            
        Note: According to the protocol, you must either:
        - Use no flags (reads any tag in field)
        - Use the Select flag (reads previously selected tag)
        - Use the Address flag with UID (reads specific tag)
        """
        try:
            # Validate block number
            if not 0 <= start_block_number <= 255:
                raise ValueError("Block number must be between 0 and 255")
            
            # Determine flags and command structure based on mode
            if uid:
                # Convert UID string to bytes and reverse for little-endian
                uid_bytes = bytes.fromhex(uid)[::-1]

                cmd = CMD_ISO15693_READ_MULTIPLE_BLOCK_WITH_ADDRESS_FLAG
                cmd.extend([*uid_bytes])
            
            else:
                if with_select_flag:
                    cmd = CMD_ISO15693_READ_MULTIPLE_BLOCK_WITH_SELECT_FLAG
                else:
                    cmd = CMD_ISO15693_READ_MULTIPLE_BLOCK
                
            # common part to be appended to cmd
            cmd.extend([block_size, start_block_number, total_blocks])

            response = self._send_command(cmd)

            if response[3:5] != STATUS_SUCCESS :
                print(f"Error in ISO15693_readMultipleBlock: {response[3:5]}")
                return None
            
            block_data_read = response[6: 6 + (block_size * (total_blocks + 1))]
            data_blocks = [''.join(block_data_read[i: i + block_size][::-1]) for i in range(0, len(block_data_read), block_size)]

            return ''.join(data_blocks)

        except Exception as e:
            print(f"Error in ISO15693_readMultipleBlock: {str(e)}")
            return None

        
    def close(self) -> None:
        """Close the connection to the device."""
        if self.device:
            try:
                self.device.close()
            finally:
                self.device = None


    def __enter__(self):
        """Context manager entry."""
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()