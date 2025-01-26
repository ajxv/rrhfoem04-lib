# RRHFOEM04 Python Library
[![PyPI](https://img.shields.io/pypi/v/rrhfoem04-lib?label=pypi)](https://pypi.org/project/rrhfoem04-lib/)
[![License](https://img.shields.io/pypi/l/mkdocs-badges)](https://github.com/ajxv/rrhfoem04-lib/blob/main/LICENSE)

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
if reader.buzzer_on().success:
    print("Buzzer activated")

# Get reader information
result = reader.getReaderInfo()
print(f"getReaderInfo result: {result}")

# Perform an ISO15693 inventory scan
result = reader.ISO15693_singleSlotInventory()
print(f"ISO15693_singleSlotInventory result: {result}")

# Close the reader connection
reader.close()
```

> **Note:**
>
> The `hidapi` module (dependency to interact with hid modules) requires superuser privilage to run. Therefore, run your python script with `sudo` if you are using linux based system. eg: `sudo python3 script.py`


## Contributing

Contributions are welcome! Please refer to the docs folder for more details on the library's internals and how to contribute.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries or support, please open an issue on the [GitHub repository](https://github.com/ajxv/rrhfoem04-lib).
