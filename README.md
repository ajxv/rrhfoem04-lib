# RRHFOEM04 Python Library
[![PyPI](https://img.shields.io/pypi/v/rrhfoem04-lib?label=pypi)](https://pypi.org/project/rrhfoem04-lib/)
[![License](https://img.shields.io/pypi/l/mkdocs-badges)](https://github.com/ajxv/rrhfoem04-lib/blob/main/LICENSE)

This Python library provides an interface to interact with the RRHFOEM04 RFID/NFC reader. The library supports multiple RFID protocols including ISO15693 and ISO14443A, allowing for various card operations such as inventory scanning, reading, and writing.

## Features

| Capability | Description |
|------------|-------------|
| Multi-Protocol | ISO15693, ISO14443A & Mifare operations |
| Inventory & Tag Ops | Single-slot & 16-slot inventory, select, read, write |
| Robust Timing | Command pacing, retries, non-blocking HID reads |
| Structured Results | All ops return `RRHFOEM04Result(success, message, data)` |
| Error Handling | Custom exception hierarchy + logged context |
| Optional File Logging | `log_to_file=True` adds `rrhfoem04.log` handler |

## Installation

```bash
pip install rrhfoem04-lib
```

System packages (Linux) sometimes required for `hidapi`:
```bash
sudo apt-get update && sudo apt-get install -y libhidapi-hidraw0 libhidapi-libusb0
```

Upgrade:
```bash
pip install -U rrhfoem04-lib
```

## Requirements

- Python >= 3.12
- USB access to RRHFOEM04 device

### Device Permissions (Linux)
Instead of running Python with `sudo`, consider adding a udev rule (example):
```
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="vvvv", ATTRS{idProduct}=="pppp", MODE="0666"
```
Replace `vvvv`/`pppp` with the reader's vendor/product IDs, reload with `udevadm control --reload && udevadm trigger`.

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
> The `hidapi` module may require additional system libraries or device permissions. Prefer udev rules over running entire scripts with sudo.

### Context Manager Example
```python
from rrhfoem04 import RRHFOEM04

with RRHFOEM04(auto_connect=True) as reader:
    inv = reader.ISO15693_singleSlotInventory()
    if inv.success:
        print("Tags:", inv.data)
```

### Result Object
Every high-level call returns `RRHFOEM04Result`:
```python
res = reader.getReaderInfo()
if res.success:
    print(res.data)
else:
    print(res.message)
```


## Contributing

Contributions are welcome! See the [Contributing Guide](docs/CONTRIBUTING.md). For deeper internals and extension guidelines consult the [Maintainers Guide](docs/MaintainersGuide.md).

## Documentation

- [Maintainers Guide](docs/MaintainersGuide.md) – architecture, extension, release & support practices.
- [Protocol Reference](docs/RRHFOEM04_ProtocolReference.md) – frame formats, flags, command tables.
- [Publishing to PyPI](docs/PublishingToPyPI.md) – step-by-step release instructions.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries or support, please open an issue on the [GitHub repository](https://github.com/ajxv/rrhfoem04-lib).
