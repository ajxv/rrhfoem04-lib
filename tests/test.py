import sys
sys.path.insert(0, 'src/')

import unittest
from rrhfoem04 import RRHFOEM04
import time

class TestRRHFOEM04(unittest.TestCase):

    def setUp(self):
        """Set up the RFID reader before each test"""
        self.reader = RRHFOEM04()
        time.sleep(0.2)  # Allow device to initialize

    def tearDown(self):
        """Close the RFID reader after each test"""
        if self.reader:
            time.sleep(0.1)  # Wait before closing
            self.reader.close()

    def test_buzzer_beep(self):
        """Test the buzzer"""
        try:
            result = self.reader.buzzer_beep()
            
            print(result)
            self.assertTrue(result.success, "Buzzer test failed")            

        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_buzzer_on(self):
        """Test buzzer on"""
        try:
            result = self.reader.buzzer_on()
            
            print(result)
            self.assertTrue(result.success, "Buzzer on test failed")
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_buzzer_off(self):
        """Test buzzer off"""
        try:
            result = self.reader.buzzer_off()
            
            print(result)
            self.assertTrue(result.success, "Buzzer off test failed")
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_getReaderInfo(self):
        """Test getting reader information"""
        try:
            print("Getting reader information...")
            result = self.reader.getReaderInfo()
            
            print(result)
            self.assertTrue(result.success, "Could not get reader information")

        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_ISO15693_singleSlotInventory(self):
        """Test ISO15693 single slot inventory scan"""
        try:
            result = self.reader.ISO15693_singleSlotInventory()

            print(result)
            self.assertTrue(result.success, "ISO15693 Single slot inventory failed")

        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO15693_16SlotInventory(self):
        """Test ISO15693 16 slot inventory scan"""
        try:
            result = self.reader.ISO15693_16SlotInventory()

            print(result)
            self.assertTrue(result.success, "ISO15693 16 slot inventory failed")

        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO14443A_Inventory(self):
        """Test ISO14443A inventory scan"""
        try:
            result = self.reader.ISO14443A_Inventory()

            print(result)
            self.assertTrue(result.success, "No tags detected")
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO15693_readSingleBlock(self):
        """Test ISO15693_readSingleBlock"""
        try:
            block_number = 0
            # block_data = self.reader.ISO15693_readSingleBlock(block_number, uid="A86E33E8080802E0")
            # block_data = self.reader.ISO15693_readSingleBlock(block_number, with_select_flag=True)
            result = self.reader.ISO15693_readSingleBlock(block_number)

            print(result)
            self.assertTrue(result.success, "Error Reading ISO15693 single block data")
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO15693_writeSingleBlock(self):
        """Test ISO15693_writeSingleBlock"""
        try:
            block_number = 0
            data = "ACC"
            # write_success = self.reader.ISO15693_writeSingleBlock(block_number, data, uid="A86E33E8080802E0")
            # write_success = self.reader.ISO15693_writeSingleBlock(block_number, data, with_select_flag=True)
            result = self.reader.ISO15693_writeSingleBlock(block_number, data)
            print(result)
            self.assertTrue(result.success, "Error Writing ISO15693 single block")
            
            print(f"Successfully written data: [{data}] at block: [{block_number}]")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO15693_writeMultipleBlocks(self):
        """Test ISO15693_writeMultipleBlocks"""
        try:
            start_block_number = 0
            data = "ACC12345"
            # write_success = self.reader.ISO15693_writeMultipleBlock(start_block_number, data, uid="A86E33E8080802E0")
            # write_success = self.reader.ISO15693_writeMultipleBlock(start_block_number, data, with_select_flag=True)
            result = self.reader.ISO15693_writeMultipleBlocks(start_block_number, data)

            print(result)
            self.assertTrue(result.success, "Error Writing ISO15693 Multiple block")
            
            print(f"Successfully written data: [{data}] starting from block: [{start_block_number}]")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_ISO15693_readMultipleBlocks(self):
        """Test ISO15693_readMultipleBlocks"""
        try:
            block_number = 0
            total_blocks = 2

            # block_data = self.reader.ISO15693_readMultipleBlocks(block_number,total_blocks=total_blocks, uid="A86E33E8080802E0")
            # block_data = self.reader.ISO15693_readMultipleBlocks(block_number,total_blocks=total_blocks, with_select_flag=True)

            result = self.reader.ISO15693_readMultipleBlocks(block_number, total_blocks=total_blocks)
            print(result)
            self.assertTrue(result.success, "Error Reading ISO15693 Multiple block data")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_ISO14443A_mifareAuthenticate(self):
        """Test ISO14443A_mifareAuthenticate"""
        try:
            block_number = 5

            uid = self.reader.ISO14443A_Inventory().data
            uid = uid if uid else "000000"
            result = self.reader.ISO14443A_mifareAuthenticate(uid, block_number=block_number)

            print(result)
            self.assertTrue(result.success, "ISO14443A_mifareAuthenticate test failed")
           
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_ISO14443A_mifareRead(self):
        """Test ISO14443A mifare read"""
        try:
            block_number = 4

            result = self.reader.ISO14443A_mifareRead(block_number=block_number)

            print(result)
            self.assertTrue(result.success, "No data read")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO14443A_mifareWrite(self):
        """Test ISO14443A mifare read"""
        try:
            block_number = 4
            # uid = self.reader.ISO14443A_Inventory().data
            # uid = uid if uid else "000000"
            data = "KJ000F00#"

            result = self.reader.ISO14443A_mifareWrite(data=data, block_number=block_number)
            print(result)
            self.assertTrue(result.success, "Failed to write data")

            print(f"Successfully written data: [{data}] to block: [{block_number}]")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_ISO15693_writeAFI(self):
        """Test ISO15693_writeAFI"""
        try:
            afi = 7
            # write_success = self.reader.ISO15693_writeAFI(afi=afi, uid="A86E33E8080802E0")
            # write_success = self.reader.ISO15693_writeAFI(afi=afi, with_select_flag=True)
            result = self.reader.ISO15693_writeAFI(afi=afi)
            print(result)
            self.assertTrue(result.success, "Error Writing ISO15693 AFI Flag")
            
            print(f"Successfully written afi flag: [{afi}]")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

if __name__ == "__main__":
    tests = [
        "test_buzzer_beep",
        "test_buzzer_on",
        "test_buzzer_off",
        "test_getReaderInfo",
        "test_ISO15693_singleSlotInventory",
        "test_ISO15693_16SlotInventory",
        "test_ISO15693_readSingleBlock",
        "test_ISO15693_writeSingleBlock",
        "test_ISO15693_writeMultipleBlocks",
        "test_ISO15693_readMultipleBlocks",
        "test_ISO15693_writeAFI",
        "test_ISO14443A_Inventory",
        "test_ISO14443A_mifareAuthenticate",
        "test_ISO14443A_mifareRead",
        "test_ISO14443A_mifareWrite",
    ]
    
    if len(sys.argv) > 1:
        test_index = int(sys.argv[1]) - 1
    else:
        print("Select a test to run:")
        for idx, test in enumerate(tests, 1):
            print(f"{idx}. {test}")

        test_index = int(input("Enter the test number to run: ")) - 1

    print("\n")

    if 0 <= test_index < len(tests):
        suite = unittest.TestSuite()
        suite.addTest(TestRRHFOEM04(tests[test_index]))
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        print("Invalid test number")