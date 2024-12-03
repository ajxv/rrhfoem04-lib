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

    def test_buzzer(self):
        """Test the buzzer"""
        try:
            result = self.reader.buzzer()
            self.assertTrue(result, "Buzzer test failed")
            if result:
                print("Buzzer test successful!")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_getReaderInfo(self):
        """Test getting reader information"""
        try:
            print("Getting reader information...")
            info = self.reader.getReaderInfo()
            
            self.assertIsNotNone(info, "Could not get reader information")
            if info:
                print(f"Model: {info['model']}")
                print(f"Serial: {info['serial']}")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_ISO15693_singleSlotInventory(self):
        """Test ISO15693 single slot inventory scan"""
        try:
            uids = self.reader.ISO15693_singleSlotInventory()
            self.assertIsNotNone(uids, "No tags detected")
            if uids:
                # Print detected UIDs
                print(f"No. of tags detected: {len(uids)}")
                for uid in uids:
                    print(f"Detected Tag UID: {uid}")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO15693_16SlotInventory(self):
        """Test ISO15693 16 slot inventory scan"""
        try:
            uids = self.reader.ISO15693_16SlotInventory()
            self.assertIsNotNone(uids, "No tags detected")
            if uids:
                # Print detected UIDs
                print(f"No. of tags detected: {len(uids)}")
                for uid in uids:
                    print(f"Detected Tag UID: {uid}")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO14443A_Inventory(self):
        """Test ISO14443A inventory scan"""
        try:
            uid = self.reader.ISO14443A_Inventory()
            self.assertIsNotNone(uid, "No tags detected")
            if uid:
                print(f"Detected Tag UID: {uid}")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO15693_readSingleBlock(self):
        """Test ISO15693_readSingleBlock"""
        try:
            block_number = 0
            # block_data = self.reader.ISO15693_readSingleBlock(block_number, uid="A86E33E8080802E0")
            # block_data = self.reader.ISO15693_readSingleBlock(block_number, with_select_flag=True)
            block_data = self.reader.ISO15693_readSingleBlock(block_number)
            self.assertIsNotNone(block_data, "Error Reading ISO15693 single block data")
            
            if block_data:
                print(f"Data read at block [{block_number}]: {block_data}")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_ISO15693_writeSingleBlock(self):
        """Test ISO15693_writeSingleBlock"""
        try:
            block_number = 0
            data = "ACC1"
            # write_success = self.reader.ISO15693_writeSingleBlock(block_number, data, uid="A86E33E8080802E0")
            # write_success = self.reader.ISO15693_writeSingleBlock(block_number, data, with_select_flag=True)
            write_success = self.reader.ISO15693_writeSingleBlock(block_number, data)
            self.assertTrue(write_success, "Error Writing ISO15693 single block")
            
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
            write_success = self.reader.ISO15693_writeMultipleBlocks(start_block_number, data, delimiter='#')
            self.assertTrue(write_success, "Error Writing ISO15693 Multiple block")
            
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
            block_data = self.reader.ISO15693_readMultipleBlocks(block_number, total_blocks=total_blocks)
            self.assertIsNotNone(block_data, "Error Reading ISO15693 Multiple block data")
            
            if block_data:
                print(f"Data read at block [{block_number}]: {block_data}")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

if __name__ == "__main__":
    tests = [
        "test_buzzer",
        "test_getReaderInfo",
        "test_ISO15693_singleSlotInventory",
        "test_ISO15693_16SlotInventory",
        "test_ISO14443A_Inventory",
        "test_ISO15693_readSingleBlock",
        "test_ISO15693_writeSingleBlock",
        "test_ISO15693_writeMultipleBlocks",
        "test_ISO15693_readMultipleBlocks",
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