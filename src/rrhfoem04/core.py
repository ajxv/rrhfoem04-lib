"""Core implementation of the RRHFOEM04 RFID/NFC reader interface."""

import time
from typing import List, Optional, Dict
import hid
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
        crc = CRC_INIT
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = ((crc << 1) ^ CRC_POLY) if crc & 0x8000 else (crc << 1)
                crc &= 0xFFFF
        return (~crc) & 0xFFFF


    def _send_command(self, cmd_data: List[int]) -> Optional[List[int]]:
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
                    return list(response)
                time.sleep(0.01)  # Short delay between retries

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
                print(f"Error sounding buzzer: {self._byte_list_to_hex_string(response[3:5])}")
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
            response = self._send_command(CMD_GET_INFO)
            if not response:
                print("No response received from get_reader_info command")
                return None
            
            # Check if the status in the response is successful
            if response[3:5] != STATUS_SUCCESS:
                print(f"Error getting Reader Information: {self._byte_list_to_hex_string(response[3:5])}")
                return None

            # Extract the relevant part of the response containing reader information
            reader_info_part = response[5:21]
            
            # Find the end of the model string (assumed to be marked by '-')
            model_end = reader_info_part.index(0x2D)  # '-' is represented as 0x2D in ASCII
            
            # Convert the model part to a string
            model = bytearray(reader_info_part[:model_end]).decode()
            
            # Extract the serial number from the last 3 bytes of the reader info part
            serial = self._byte_list_to_hex_string(reader_info_part[-3:])

            # Return the extracted model and serial number in a dictionary
            return {
                'model': model,
                'serial': serial
            }
            
        except Exception as e:
            # Handle any exceptions that occur during the process
            print(f"Error in get_reader_info: {e}")
            return None


    def ISO15693_inventory(self) -> Optional[List]:
        """
        Perform an ISO15693 inventory scan to detect nearby RFID tags.
        
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
                print(f"Error getting ISO15693 inventory: {self._byte_list_to_hex_string(response[3:5])}")
                return None
            
            # no of tags detected
            total_tags = response[5]

            if total_tags == 0:
                print("No tags detected")
                return []
            
            # Parse UIDs 
            # Each UID is 8 bytes long, starting from byte 5, ie. index 6
            tag_uids = []

            for i in range(total_tags):
                # Extract UID, reverse byte order (little-endian to big-endian)
                start_index = 6 + (i * 8)
                uid = bytes(reversed(response[start_index:start_index + 8]))
                tag_uids.append(uid)

            return tag_uids
            
        except Exception as e:
            print(f"Error in ISO15693 inventory scan: {str(e)}")
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