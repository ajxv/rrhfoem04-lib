
# RRHFOEM04 Communication Protocol

## Request Frame Length / Response Frame Length

- **Request Frame Length**: It is the number of bytes that shall be calculated by adding the total number of bytes starting from the "Command Code" field to the "Cyclic Redundancy Check (CRC)" field. If a specific request is not having any data, the frame length for request and response will vary accordingly.
- **Response Frame Length**: Calculated similarly to the request frame, depending on the presence or absence of data.

---

## Command Code

- The command code specifies the action to be performed. Below are the command codes supported:

### ISO 15693 Command Codes:

| Sr. No. | Command Code | Description                           |
|---------|--------------|---------------------------------------|
| 1       | 1001Hex      | Single Slot Inventory                |
| 2       | 1002Hex      | 16 Slot Inventory                    |
| 3       | 1003Hex      | Select                               |
| 4       | 1004Hex      | Quiet                                |
| 5       | 1005Hex      | Reset                                |
| 6       | 1006Hex      | Read Single Block                    |
| 7       | 1007Hex      | Write Single Block                   |
| 8       | 1008Hex      | Lock Block                           |
| 9       | 1009Hex      | Read Multiple Blocks                 |
| 10      | 100AHex      | Write AFI Flag                       |
| 11      | 100BHex      | Lock AFI Flag                        |
| 12      | 100CHex      | Write DSFID Flag                     |
| 13      | 100DHex      | Lock DSFID Flag                      |
| 14      | 100EHex      | Get System Information               |
| 15      | 100FHex      | Get Multiple Block Security Status   |
| 16      | 1101Hex      | Read EAS Flag                        |
| 17      | 1102Hex      | Set EAS Flag                         |
| 18      | 1103Hex      | Reset EAS Flag                       |
| 19      | 1104Hex      | Lock EAS Flag                        |
| 20      | 1201Hex      | Write Two Blocks (TAGIT)             |
| 21      | 1202Hex      | Lock Two Blocks (TAGIT)              |
| 22      | 1F02Hex      | Write Multiple Blocks                |

---

### ISO 14443A Command Codes:

| Sr. No. | Command Code | Description                  |
|---------|--------------|------------------------------|
| 1       | 2001Hex      | Request                     |
| 2       | 2002Hex      | Wake up                     |
| 3       | 2006Hex      | Anti-collision              |
| 4       | 2004Hex      | Select                      |
| 5       | 2005Hex      | Halt                        |
| 6       | 2101Hex      | Mifare Authenticate         |
| 7       | 2102Hex      | Mifare Read                 |
| 8       | 2103Hex      | Mifare Write                |
| 9       | 2201Hex      | Mifare UL Read              |
| 10      | 2202Hex      | Mifare UL Write             |
| 11      | 2F01Hex      | Inventory                   |
| 12      | 2F02Hex      | Select Card                 |

---

### RFID System Level Command Codes:

| Sr. No. | Command Code | Description                  |
|---------|--------------|------------------------------|
| 1       | 0001Hex      | Low Power Mode              |
| 2       | 0002Hex      | Normal Power Mode           |
| 3       | 0003Hex      | Set RF Power                |
| 4       | 0004Hex      | RF Turn ON                  |
| 5       | 0005Hex      | RF Turn OFF                 |

---

### RR System Level Command Codes:

| Sr. No. | Command Code | Description                            |
|---------|--------------|----------------------------------------|
| 1       | F000Hex      | Get Reader Information                |
| 2       | F001Hex      | Buzzer (Beep)                         |
| 3       | F002Hex      | Additional Frame (Valid for USB only) |
| 4       | FF03Hex      | Reset Device / Restart Device         |

---

## Flags

- **Flags** specify the action to be performed by the tag (VICC) and whether the corresponding fields are present or not.

| Sr. No. | Flag Value | Flag Type          |
|---------|------------|--------------------|
| 1       | 02Hex      | Data Rate Flag     |
| 2       | 20Hex      | Address Flag       |
| 3       | 10Hex      | Select Flag        |
| 4       | 40Hex      | Option Flag        |
| 5       | 04Hex      | Inventory Flag     |

---

## Cyclic Redundancy Check (CRC)

- **CRC** is used to ensure no data loss during communication. It is calculated from the "Request Frame Length" field up to the "Custom Request Data" field.

### CRC Structure:

| Bit Position | Description |
|--------------|-------------|
| LSB (8 bits) | Least Significant Byte |
| MSB (8 bits) | Most Significant Byte |

### CRC Logic (Pseudocode):

```c
unsigned short CalcCRC(unsigned char data[], unsigned char len) {
    unsigned short crc = 0xFFFF;
    unsigned char count, bitCount;

    for (count = 0; count < len; count++) {
        crc ^= data[count];
        for (bitCount = 0; bitCount < 8; bitCount++) {
            crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : (crc << 1);
        }
    }
    return (~crc);
}
```
# Basic Communication Frame Format

## Request

| Sr. No. | Parameter               | Length | Data        |
|---------|-------------------------|--------|-------------|
| 1       | Request Frame Length    | 1      | XXHex       |
| 2       | Command Code            | 2      | XXXXHex     |
| 3       | Custom Request Data     | X      | XX...XXHex  |
| 4       | Cyclic Redundancy Check | 2      | XXXXHex     |

## Response

| Sr. No. | Parameter               | Length | Data        |
|---------|-------------------------|--------|-------------|
| 1       | Response Frame Length   | 1      | 01 to FFHex |
| 2       | Command Code            | 2      | XXXXHex     |
| 3       | Error Code              | 2      | XXXXHex     |
| 4       | Custom Response Data    | X      | XX...XXHex  |
| 5       | Cyclic Redundancy Check | 2      | XXXXHex     |

# ISO 15693 Commands

## Single Slot Inventory

### Request (With AFI)

| Sr. No. | Parameter               | Length (Byte) | Data     |
|---------|-------------------------|---------------|----------|
| 1       | Request Frame Length    | 1             | 05Hex    |
| 2       | Command Code            | 2             | 1001Hex  |
| 3       | Flags                   | 1             | 36Hex    |
| 4       | AFI                     | 1             | XXHex    |
| 5       | Cyclic Redundancy Check | 2             | XXXXHex  |

### Request (Without AFI)

| Sr. No. | Parameter               | Length (Byte) | Data     |
|---------|-------------------------|---------------|----------|
| 1       | Request Frame Length    | 1             | 04Hex    |
| 2       | Command Code            | 2             | 1001Hex  |
| 3       | Flags                   | 1             | 26Hex    |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex  |

### Response

| Sr. No. | Parameter               | Length (Byte) | Data                     |
|---------|-------------------------|---------------|--------------------------|
| 1       | Response Frame Length   | 1             | XXHex                   |
| 2       | Command Code            | 2             | 1001Hex                 |
| 3       | Error Code              | 2             | XXXXHex                 |
| 4       | Total no. of Received UID | 1           | XXHex                   |
| 5       | UID                     | X             | XXXX...XXXXHex (8 bytes) |
| 6       | Cyclic Redundancy Check | 2             | XXXXHex                 |

**Error Code:** If error code is `FFFFHex`, then the length will be limited to 05Hex, and fields 4 & 5 will be absent; otherwise, the error code is `0000Hex`.

**Total no. of Received UID:** The total number of cards that exist in the reading area.

**UID:** UID of cards that are detected (Total no. of Received UIDs × 8 bytes).

## 16 Slot Inventory

### Request (With AFI)

| Sr. No. | Parameter               | Length (Byte) | Data     |
|---------|-------------------------|---------------|----------|
| 1       | Request Frame Length    | 1             | 05Hex    |
| 2       | Command Code            | 2             | 1002Hex  |
| 3       | Flags                   | 1             | 16Hex    |
| 4       | AFI                     | 1             | XXHex    |
| 5       | Cyclic Redundancy Check | 2             | XXXXHex  |

### Request (Without AFI)

| Sr. No. | Parameter               | Length (Byte) | Data     |
|---------|-------------------------|---------------|----------|
| 1       | Request Frame Length    | 1             | 04Hex    |
| 2       | Command Code            | 2             | 1002Hex  |
| 3       | Flags                   | 1             | 06Hex    |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex  |

### Response

| Sr. No. | Parameter               | Length (Byte) | Data                     |
|---------|-------------------------|---------------|--------------------------|
| 1       | Response Frame Length   | 1             | XXHex                   |
| 2       | Command Code            | 2             | 1002Hex                 |
| 3       | Error Code              | 2             | XXXXHex                 |
| 4       | Total No. of Received UID | 1           | XXHex                   |
| 5       | UID                     | X             | XXXX...XXXXHex (8 bytes) |
| 6       | Cyclic Redundancy Check | 2             | XXXXHex                 |

**Error Code:** If error code is `FFFFHex`, then the length will be limited to 05Hex, and fields 4 and 5 will be absent; otherwise, the error code is `0000Hex`.

**Total no. of Received UID:** The total number of cards that exist in the reading area.

**UID:** UID of cards which are detected (Total no. of Received UIDs × 8 bytes).

## Read Single Block

### Request

| Sr. No. | Parameter               | Length (Byte) | Data               |
|---------|-------------------------|---------------|--------------------|
| 1       | Request Frame Length    | 1             | 06Hex             |
| 2       | Command Code            | 2             | 1006Hex           |
| 3       | Flags                   | 1             | 02Hex or 42Hex    |
| 4       | Block Length            | 1             | XXHex             |
| 5       | Block Number            | 1             | XXHex             |
| 6       | Cyclic Redundancy Check | 2             | XXXXHex           |

### Request (With Select Flag)

| Sr. No. | Parameter               | Length (Byte) | Data               |
|---------|-------------------------|---------------|--------------------|
| 1       | Request Frame Length    | 1             | 06Hex             |
| 2       | Command Code            | 2             | 1006Hex           |
| 3       | Flags                   | 1             | 12Hex or 52Hex    |
| 4       | Block Length            | 1             | XXHex             |
| 5       | Block Number            | 1             | XXHex             |
| 6       | Cyclic Redundancy Check | 2             | XXXXHex           |

### Request (With Address Flag)

| Sr. No. | Parameter               | Length (Byte) | Data               |
|---------|-------------------------|---------------|--------------------|
| 1       | Request Frame Length    | 1             | 0EHex             |
| 2       | Command Code            | 2             | 1006Hex           |
| 3       | Flags                   | 1             | 22Hex or 62Hex    |
| 4       | UID                     | 8             | XXXXXXXXHex       |
| 5       | Block Length            | 1             | XXHex             |
| 6       | Block Number            | 1             | XXHex             |
| 7       | Cyclic Redundancy Check | 2             | XXXXHex           |

### Response

| Sr. No. | Parameter               | Length (Byte) | Data               |
|---------|-------------------------|---------------|--------------------|
| 1       | Response Frame Length   | 1             | XXHex             |
| 2       | Command Code            | 2             | 1006Hex           |
| 3       | Error Code              | 2             | XXXXHex           |
| 4       | Response Flag           | 1             | XXHex             |
| 5       | Block Security Status   | 1             | XXHex             |
| 6       | Data                    | X             | XX...XX Hex       |
| 7       | Cyclic Redundancy Check | 2             | XXXXHex           |

**Block Length:** Number of bytes to be read.

**Block Number:** Block to be read. (Value lies between 00Hex to FFHex).

**Error Code:** If error code is `FFFFHex`, then the length will be limited to 05Hex, and fields 4, 5, 6 will be absent; otherwise, the error code is `0000Hex`.

**UID:** UID of the card to be read (only if address flag is set).

**Response Flag:** By default, value is 00.

**Block Security Status:** This appears only when Option flag (0x40) is set.

## Write Single Block

### Request

| Sr. No. | Parameter               | Length (Byte)       | Data               |
|---------|-------------------------|---------------------|--------------------|
| 1       | Request Frame Length    | 1                   | 06 + Block Len Hex |
| 2       | Command Code            | 2                   | 1007Hex           |
| 3       | Flags                   | 1                   | 02Hex or 42Hex    |
| 4       | Block Length            | 1                   | XXHex             |
| 5       | Block Number            | 1                   | XXHex             |
| 6       | Data                    | X                   | XX...XX Hex       |
| 7       | Cyclic Redundancy Check | 2                   | XXXXHex           |

### Request (With Select Flag)

| Sr. No. | Parameter               | Length (Byte)       | Data               |
|---------|-------------------------|---------------------|--------------------|
| 1       | Request Frame Length    | 1                   | 06 + Block Len Hex |
| 2       | Command Code            | 2                   | 1007Hex           |
| 3       | Flags                   | 1                   | 12Hex or 52Hex    |
| 4       | Block Length            | 1                   | XXHex             |
| 5       | Block Number            | 1                   | XXHex             |
| 6       | Data                    | X                   | XX...XX Hex       |
| 7       | Cyclic Redundancy Check | 2                   | XXXXHex           |

### Request (With Address Flag)

| Sr. No. | Parameter               | Length (Byte)       | Data               |
|---------|-------------------------|---------------------|--------------------|
| 1       | Request Frame Length    | 1                   | 0E + Block Len Hex |
| 2       | Command Code            | 2                   | 1007Hex           |
| 3       | Flags                   | 1                   | 22Hex or 62Hex    |
| 4       | UID                     | 8                   | XXXXXXXXHex       |
| 5       | Block Length            | 1                   | XXHex             |
| 6       | Block Number            | 1                   | XXHex             |
| 7       | Data                    | X                   | XX...XX Hex       |
| 8       | Cyclic Redundancy Check | 2                   | XXXXHex           |

### Response

| Sr. No. | Parameter               | Length (Byte) | Data               |
|---------|-------------------------|---------------|--------------------|
| 1       | Response Frame Length   | 1             | 05Hex             |
| 2       | Command Code            | 2             | 1007Hex           |
| 3       | Error Code              | 2             | XXXXHex           |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex           |

#### Descriptions:

- **Block Length:** Number of bytes to be written.
- **Block Number:** Block to be written (Value lies between 00Hex to FFHex).
- **Data:** The data to be written.
- **UID:** UID of the card to write (only if address flag is set).
- **Error Code:** If an error occurs, the value is `FFFFHex`; otherwise, it is `0000Hex`.


## Read Multiple Blocks

### Request

| Sr. No. | Parameter               | Length (Byte) | Data            |
|---------|-------------------------|---------------|-----------------|
| 1       | Request Frame Length    | 1             | 07Hex          |
| 2       | Command Code            | 2             | 1009Hex        |
| 3       | Flags                   | 1             | 02Hex or 42Hex |
| 4       | Block Length            | 1             | XXHex          |
| 5       | Block Number            | 1             | XXHex          |
| 6       | Total Block             | 1             | XXHex          |
| 7       | Cyclic Redundancy Check | 2             | XXXXHex        |

### Request (With Select Flag)

| Sr. No. | Parameter               | Length (Byte) | Data            |
|---------|-------------------------|---------------|-----------------|
| 1       | Request Frame Length    | 1             | 07Hex          |
| 2       | Command Code            | 2             | 1009Hex        |
| 3       | Flags                   | 1             | 12Hex or 52Hex |
| 4       | Block Length            | 1             | XXHex          |
| 5       | Block Number            | 1             | XXHex          |
| 6       | Total Block             | 1             | XXHex          |
| 7       | Cyclic Redundancy Check | 2             | XXXXHex        |

### Request (With Address Flag)

| Sr. No. | Parameter               | Length (Byte) | Data            |
|---------|-------------------------|---------------|-----------------|
| 1       | Request Frame Length    | 1             | 0FHex          |
| 2       | Command Code            | 2             | 1009Hex        |
| 3       | Flags                   | 1             | 22Hex or 62Hex |
| 4       | UID                     | 8             | XXXXXXXXHex    |
| 5       | Block Length            | 1             | XXHex          |
| 6       | Block Number            | 1             | XXHex          |
| 7       | Total Block             | 1             | XXHex          |
| 8       | Cyclic Redundancy Check | 2             | XXXXHex        |

### Response

| Sr. No. | Parameter               | Length (Byte)             | Data               |
|---------|-------------------------|---------------------------|--------------------|
| 1       | Response Frame Length   | 1                         | 6 + (Block No. * Block Len) Hex |
| 2       | Command Code            | 2                         | 1009Hex           |
| 3       | Error Code              | 2                         | XXXXHex           |
| 4       | Flags                   | 1                         | XXHex             |
| 5       | Data                    | X                         | XX...XX Hex       |
| 6       | Cyclic Redundancy Check | 2                         | XXXXHex           |

#### Descriptions:

- **Block Length:** Number of bytes to be read.
- **Block Number:** Blocks to be read. (Value lies between 00 to FFHex).
- **Total Block:** Number of simultaneous block to read.
- **Data:** The data which is read from blocks.
- **UID:** UID of card to be read (only if address flag is set).
- **Error Code:** If error code is `FFFFHex` then the length will be limited to 05Hex and also field 4, 5 will be absent.

## Write AFI Flag

### Request

| Sr. No. | Parameter               | Length (Byte) | Data            |
|---------|-------------------------|---------------|-----------------|
| 1       | Request Frame Length    | 1             | 05Hex          |
| 2       | Command Code            | 2             | 1004Hex        |
| 3       | Flags                   | 1             | 02Hex or 42Hex |
| 4       | AFI                     | 1             | XXHex          |
| 5       | Cyclic Redundancy Check | 2             | XXXXHex        |

### Request (With Select Flag)

| Sr. No. | Parameter               | Length (Byte) | Data            |
|---------|-------------------------|---------------|-----------------|
| 1       | Request Frame Length    | 1             | 05Hex          |
| 2       | Command Code            | 2             | 1004Hex        |
| 3       | Flags                   | 1             | 12Hex or 52Hex |
| 4       | AFI                     | 1             | XXHex          |
| 5       | Cyclic Redundancy Check | 2             | XXXXHex        |

### Request (With Address Flag)

| Sr. No. | Parameter               | Length (Byte) | Data            |
|---------|-------------------------|---------------|-----------------|
| 1       | Request Frame Length    | 1             | 0DHex          |
| 2       | Command Code            | 2             | 1004Hex        |
| 3       | Flags                   | 1             | 22Hex or 62Hex |
| 4       | UID                     | 8             | XXXXXXXXHex    |
| 5       | AFI                     | 1             | XXHex          |
| 6       | Cyclic Redundancy Check | 2             | XXXXHex        |

### Response

| Sr. No. | Parameter               | Length (Byte) | Data            |
|---------|-------------------------|---------------|-----------------|
| 1       | Response Frame Length   | 1             | 05Hex          |
| 2       | Command Code            | 2             | 1004Hex        |
| 3       | Error Code              | 2             | XXXXHex        |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex        |

#### Notes:
- **UID**: UID of the card whose AFI needs to be written (only if the address flag is set).
- **Error Code**: If an error occurs, it returns `FFFFHex`; otherwise, `0000Hex`.

## Get System Information

### Request

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Request Frame Length    | 1             | 04Hex     |
| 2       | Command Code            | 2             | 100EHex   |
| 3       | Flags                   | 1             | 02Hex     |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex   |

### Request (With Select Flag)

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Request Frame Length    | 1             | 04Hex     |
| 2       | Command Code            | 2             | 100EHex   |
| 3       | Flags                   | 1             | 12Hex     |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex   |

### Request (With Address Flag)

| Sr. No. | Parameter               | Length (Byte) | Data          |
|---------|-------------------------|---------------|---------------|
| 1       | Request Frame Length    | 1             | 0CHex         |
| 2       | Command Code            | 2             | 100EHex       |
| 3       | Flags                   | 1             | 22Hex         |
| 4       | UID                     | 8             | XXXXXXXXHex   |
| 5       | Cyclic Redundancy Check | 2             | XXXXHex       |

### Response

| Sr. No. | Parameter               | Length (Byte)        | Data             |
|---------|-------------------------|----------------------|------------------|
| 1       | Response Frame Length   | 1                    | 06 + Info Len Hex |
| 2       | Command Code            | 2                    | 100EHex          |
| 3       | Error Code              | 2                    | XXXXHex          |
| 4       | Flags                   | 1                    | XXHex            |
| 5       | Data                    | X                    | XX...XXHex       |
| 6       | Cyclic Redundancy Check | 2                    | XXXXHex          |

#### Notes:
- **UID**: UID of the card which is placed near the reader.
- **Error Code**: If error code is `FFFFHex`, then the length will be limited to `05Hex` and also fields 4 and 5 will be absent; else, error code is `0000Hex`.
- **Data**: It contains UID and status of AFI & DSFID flags.

## Write Multiple Blocks

### Request

| Sr. No. | Parameter               | Length (Byte) | Data          |
|---------|-------------------------|---------------|---------------|
| 1       | Request Frame Length    | 1             | XXHex         |
| 2       | Command Code            | 2             | 1F02Hex       |
| 3       | Flags                   | 1             | 02Hex or 42Hex|
| 4       | Block Length            | 1             | XXHex         |
| 5       | Block Address           | 1             | XXHex         |
| 6       | Total Block             | 1             | XXHex         |
| 7       | Data                    | X             | XX...XXHex    |
| 8       | Cyclic Redundancy Check | 2             | XXXXHex       |

### Request (With Select Flag)

| Sr. No. | Parameter               | Length (Byte) | Data          |
|---------|-------------------------|---------------|---------------|
| 1       | Request Frame Length    | 1             | XXHex         |
| 2       | Command Code            | 2             | 1F02Hex       |
| 3       | Flags                   | 1             | 12Hex or 52Hex|
| 4       | Block Length            | 1             | XXHex         |
| 5       | Block Address           | 1             | XXHex         |
| 6       | Total Block             | 1             | XXHex         |
| 7       | Data                    | X             | XX...XXHex    |
| 8       | Cyclic Redundancy Check | 2             | XXXXHex       |

### Request (With Address Flag)

| Sr. No. | Parameter               | Length (Byte) | Data          |
|---------|-------------------------|---------------|---------------|
| 1       | Request Frame Length    | 1             | XXHex         |
| 2       | Command Code            | 2             | 1F02Hex       |
| 3       | Flags                   | 1             | 22Hex or 62Hex|
| 4       | UID                     | 8             | XXXXXXXXHex   |
| 5       | Block Length            | 1             | XXHex         |
| 6       | Block Address           | 1             | XXHex         |
| 7       | Total Block             | 1             | XXHex         |
| 8       | Data                    | X             | XX...XXHex    |
| 9       | Cyclic Redundancy Check | 2             | XXXXHex       |

### Response

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Response Frame Length   | 1             | 05Hex     |
| 2       | Command Code            | 2             | 1F02Hex   |
| 3       | Error Code              | 2             | XXXXHex   |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex   |


#### Notes:
- **Block Length**: Number of bytes to be written.
- **Block Number**: Number of block from which to be written (Value lies between 00 to FFHex).
- **Total Block**: Number of simultaneous blocks to be written.
- **Data**: The data need be written.
- **UID**: UID of card to be written (only if address flag is set).
- **Error Code**: If error occurs, then it returns `FFFFHex`, otherwise `0000Hex`.

# ISO 14443A Commands

## Request Command

### Request

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Request Frame Length    | 1             | 04Hex     |
| 2       | Command Code            | 2             | 2001Hex   |
| 3       | Custom Data             | 1             | 26Hex     |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex   |

### Response

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Response Frame Length   | 1             | 07Hex     |
| 2       | Command Code            | 2             | 2001Hex   |
| 3       | Error Code              | 2             | XXXXHex   |
| 4       | Response                | 2             | XXXXHex   |
| 5       | Cyclic Redundancy Check | 2             | XXXXHex   |


#### Notes:
- **Custom Data**: It is set to `26` (26 is the request idle command in short frame format).
- **Error Code**: If an error occurs, then it returns an error code as `FFFFHex`, and also field 4 is absent. Else, the error code is `0000Hex`.
- **Response**: Contains two bytes ATQ (Answer To Request) response from the card.

## Mifare Read

### Request

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Request Frame Length    | 1             | 04Hex     |
| 2       | Command Code            | 2             | 2102Hex   |
| 3       | Block No.               | 1             | XXHex     |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex   |

### Response

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Response Frame Length   | 1             | 14Hex     |
| 2       | Command Code            | 2             | 2102Hex   |
| 3       | Error Code              | 2             | XXXXHex   |
| 4       | Data                    | 16            | XX..XXHex |
| 5       | Cyclic Redundancy Check | 2             | XXXXHex   |


#### Notes:
- **Block No.**: Number of the block to read.
- **Error Code**: If an error occurs, it returns an error code as `FFFFHex`, and field 4 is absent. Otherwise, the error code is `0000Hex`.
- **Data**: Data to be read from the card.

## Mifare Write

### Request

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Request Frame Length    | 1             | 14Hex     |
| 2       | Command Code            | 2             | 2103Hex   |
| 3       | Block No.               | 1             | XXHex     |
| 4       | Data                    | 16            | XX..XXHex |
| 5       | Cyclic Redundancy Check | 2             | XXXXHex   |

### Response

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Response Frame Length   | 1             | 05Hex     |
| 2       | Command Code            | 2             | 2103Hex   |
| 3       | Error Code              | 2             | XXXXHex   |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex   |


#### Notes:
- **Block No.**: Number of the block to be written.
- **Data**: Data written to the card.
- **Error Code**: If an error occurs, it returns an error code as `FFFFHex`. Otherwise, the error code is `0000Hex`.

## Inventory (14443A)

### Request

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Request Frame Length    | 1             | 03Hex     |
| 2       | Command Code            | 2             | 2F01Hex   |
| 3       | Cyclic Redundancy Check | 2             | XXXXHex   |


### Response

| Sr. No. | Parameter               | Length (Byte) | Data           |
|---------|-------------------------|---------------|----------------|
| 1       | Response Frame Length   | 1             | XXHex          |
| 2       | Command Code            | 2             | 2F01Hex        |
| 3       | Error Code              | 2             | XXXXHex        |
| 4       | UID Length              | 1             | XXHex          |
| 5       | UID                     | X             | XXXX..XXXHex   |
| 6       | Cyclic Redundancy Check | 2             | XXXXHex        |


#### Notes:
- **UID Length**: 
  - UID Length = 4 for 4-byte UID.
  - UID Length = 7 for 7-byte UID.
  - UID Length = 10 for 10-byte UID.
- **UID**: Contains the UID of the card near the reader.
- **Error Code**: If an error occurs, it returns `FFFFHex`. If fields 4 & 5 are absent, the error code is `0000Hex`.

# RR System Level Command

## Get Reader Information

### Request

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Request Frame Length    | 1             | 03Hex     |
| 2       | Command Code            | 2             | F000Hex   |
| 3       | Cyclic Redundancy Check | 2             | XXXXHex   |


### Response

| Sr. No. | Parameter               | Length (Byte) | Data        |
|---------|-------------------------|---------------|-------------|
| 1       | Response Frame Length   | 1             | 15Hex       |
| 2       | Command Code            | 2             | F000Hex     |
| 3       | Error Code              | 2             | XXXXHex     |
| 4       | Serial Number           | 16            | XX...XXHex  |
| 5       | Cyclic Redundancy Check | 2             | XXXXHex     |


#### Notes:
- **Error Code**: If an error occurs, the length will be limited to `05Hex`, and field 4 will be absent. The error code will be `FFFFHex`.
- **Serial Number**: It is 16 bytes and contains data including software version, hardware version, and serial number of the reader.

## Buzzer (Beep)

### Request

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Request Frame Length    | 1             | 03Hex     |
| 2       | Command Code            | 2             | F001Hex   |
| 3       | Cyclic Redundancy Check | 2             | XXXXHex   |


### Response

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Response Frame Length   | 1             | 05Hex     |
| 2       | Command Code            | 2             | F001Hex   |
| 3       | Error Code              | 2             | XXXXHex   |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex   |


#### Notes:
- **Error Code**: If an error occurs, it returns `FFFFHex`; otherwise, it returns `0000Hex`.


## Reset Device / Restart Device

### Request

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Request Frame Length    | 1             | 03Hex     |
| 2       | Command Code            | 2             | FF03Hex   |
| 3       | Cyclic Redundancy Check | 2             | XXXXHex   |


### Response

| Sr. No. | Parameter               | Length (Byte) | Data      |
|---------|-------------------------|---------------|-----------|
| 1       | Response Frame Length   | 1             | 05Hex     |
| 2       | Command Code            | 2             | FF03Hex   |
| 3       | Error Code              | 2             | XXXXHex   |
| 4       | Cyclic Redundancy Check | 2             | XXXXHex   |


#### Notes:
- **Error Code**: If an error occurs, it returns `FFFFHex`; otherwise, it returns `0000Hex`.
