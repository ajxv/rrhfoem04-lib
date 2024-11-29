"""Test script for RRHFOEM04 RFID reader with improved command sequencing."""

import sys
sys.path.insert(0, 'src/')

from rrhfoem04 import RRHFOEM04, ConnectionError
import time


def main():
    reader = None
    try:
        print("Connecting to RRHFOEM04 reader...")
        reader = RRHFOEM04()
        
        # Allow device to initialize
        time.sleep(0.2)
        
        print("Getting reader information...")
        info = reader.get_reader_info()
        
        if info:
            print(f"Connected to reader:")
            print(f"  Model: {info['model']}")
            print(f"  Version: {info['version']}")
            print(f"  Serial: {info['serial']}")
            
            # Wait before buzzer test
            time.sleep(0.2)
            
            print("\nTesting buzzer...")
            if reader.buzzer():
                print("Buzzer test successful!")
            else:
                print("Buzzer test failed")
        else:
            print("Warning: Could not get reader information")
            
    except ConnectionError as e:
        print(f"Error connecting to reader: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if reader:
            # Wait before closing
            time.sleep(0.1)
            print("\nClosing connection...")
            reader.close()
            print("Connection closed")

if __name__ == "__main__":
    main()