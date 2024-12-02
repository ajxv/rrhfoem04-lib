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

    def test_ISO15693_inventory(self):
        """Test ISO15693 inventory scan"""
        try:
            uids = self.reader.ISO15693_inventory()
            self.assertIsNotNone(uids, "No tags detected")
            if uids:
                # Print detected UIDs in hex format
                print(f"No. of tags detected: {len(uids)}")
                for uid in uids:
                    print(f"Detected Tag UID: {uid}")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_buzzer(self):
        """Test the buzzer"""
        try:
            result = self.reader.buzzer()
            self.assertTrue(result, "Buzzer test failed")
            if result:
                print("Buzzer test successful!")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")


if __name__ == "__main__":
    tests = [
        "test_getReaderInfo",
        "test_ISO15693_inventory",
        "test_buzzer",
        "test_ISO15693_ReadSingleBlock",
        "test_ISO15693_WriteSingleBlock"
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