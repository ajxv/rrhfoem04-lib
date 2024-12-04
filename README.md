# RRHFOEM04 Python Library

This Python library provides an interface to interact with the RRHFOEM04 RFID/NFC reader. The library supports multiple RFID protocols including ISO15693 and ISO14443A, allowing for various card operations such as inventory scanning, reading, and writing.

## Features

- **Multiple Protocol Support**: Supports ISO15693, ISO14443A, and Mifare.
- **Automatic Connection Management**: Easily manage device connections.
- **Error Handling**: Robust error handling and recovery mechanisms.
- **Timing Controls**: Built-in timing controls for reliable communication.
- **Single and Multi-Block Operations**: Support for single and multiple block read/write operations.

## Usage

Here's a simple example to get started with the RRHFOEM04 reader:

``` python
from rrhfoem04 import RRHFOEM04

# Initialize the reader and connect
reader = RRHFOEM04(auto_connect=True)

# Activate the buzzer
if reader.buzzer_on():
    print("Buzzer activated")

# Get reader information
info = reader.getReaderInfo()
print(f"Reader Model: {info['model']}, Serial: {info['serial']}")

# Perform an ISO15693 inventory scan
tags = reader.ISO15693_singleSlotInventory()
if tags:
    print(f"Detected tags: {tags}")

# Close the reader connection
reader.close()
```

## Contributing

Contributions are welcome! Please refer to the docs folder for more details on the library's internals and how to contribute.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries or support, please open an issue on the [GitHub repository](https://github.com/ajxv/rrhfoem04-lib).