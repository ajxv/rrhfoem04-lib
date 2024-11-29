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
            cmd = bytes([0x00] + cmd_data + 
                      [(crc >> 8) & 0xFF, crc & 0xFF] + 
                      [0] * (BUFFER_SIZE - len(cmd_data) - 3))

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

    def buzzer(self) -> bool:
        """Activate buzzer with proper timing control."""
        try:
            # Add delay before buzzer command
            time.sleep(0.1)
            
            response = self._send_command(CMD_BUZZER)
            
            # Add delay after buzzer command
            time.sleep(0.1)

            # Return True as long as command didn't raise an exception
            # The empty response is normal for this command
            return True
        except RRHFOEMError:
            return False

    def get_reader_info(self) -> Optional[Dict]:
        """Get device information with improved error handling."""
        try:
            response = self._send_command(CMD_GET_INFO)
            if not response:
                print("No response received from get_reader_info command")
                return None
            
            if len(response) < 23:  # Check minimum required length
                print(f"Response too short: {len(response)} bytes")
                return None

            try:
                model = bytes(response[5:14]).decode().rstrip('\x00')
                version = f"{response[15]}.{response[16]}"
                serial = ''.join(f"{x:02X}" for x in response[19:23])

                return {
                    'model': model,
                    'version': version,
                    'serial': serial
                }
            except UnicodeDecodeError as e:
                print(f"Error decoding model: {e}")
                # Try alternative encoding
                model = bytes(response[5:14]).decode('cp437').rstrip('\x00')
                return {
                    'model': model,
                    'version': version,
                    'serial': serial
                }
                
        except Exception as e:
            print(f"Error in get_reader_info: {str(e)}")
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