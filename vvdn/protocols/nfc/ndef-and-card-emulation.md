# NFC Data Exchange Format (NDEF) & Card Emulation Architecture

## 1. High-Level Data Architecture

The **NFC Forum** standardizes how high-level application data (URLs, contact vCards, Wi-Fi credentials, payment tokens) is packaged so that any NFC-enabled smartphone (Android / iOS) can seamlessly read and execute actions regardless of the underlying silicon tag manufacturer:

```text
               +-------------------------------------------------------+
               |                 Application Layer                     |
               |        (Web Browser, Wi-Fi Connect, Apple Wallet)     |
               +-------------------------------------------------------+
                                           |
               +-------------------------------------------------------+
               |           NDEF (NFC Data Exchange Format)             |
               |           (URI, Text, MIME, Smart Poster)             |
               +-------------------------------------------------------+
                                           |
               +-------------------------------------------------------+
               |        NFC Forum Tag Types & Capability Container     |
               |          (Type 1, Type 2, Type 3, Type 4, Type 5)     |
               +-------------------------------------------------------+
                                           |
               +-------------------------------------------------------+
               |               Lower Transport Protocols               |
               |   (ISO 14443-3/4 Type A & B, JIS X 6319-4, ISO 15693) |
               +-------------------------------------------------------+
```

---

## 2. NFC Forum Tag Types Comparison Matrix

The NFC Forum classifies physical tags into five distinct memory and protocol types:

| Metric / Parameter | Type 1 Tag | Type 2 Tag | Type 3 Tag | Type 4 Tag | Type 5 Tag |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Reference Silicon** | Innovision Topaz | NXP NTAG21x, MIFARE Ultralight | Sony FeliCa Lite-S | NXP DESFire, Smart MX | NXP ICODE SLIX, ST25TV |
| **Air Standard** | ISO 14443A | ISO 14443A | JIS X 6319-4 | ISO 14443-4 (T=CL) | ISO/IEC 15693 (Vicinity) |
| **Over-the-Air Baud** | 106 kbps | 106 kbps | 212 / 424 kbps | 106, 212, 424, 848 kbps| 26.48 kbps |
| **Memory Size** | 96 B – 2 KB | 48 B – 2 KB | Up to 1 MB | Up to 32 KB | 64 B – 8 KB |
| **Memory Addressing** | Byte / Block | 4-byte Pages | 16-byte Blocks | ISO 7816-4 File System | 4-byte / 8-byte Blocks |
| **Read Range** | Up to 4 cm | Up to 4 cm | Up to 4 cm | Up to 4 cm | **Up to 1 meter (Vicinity)** |
| **Crypto / Security** | None | Lock bytes, optional PWD | Hardware MAC | **Hardware 3DES, AES, ECC** | Lock blocks, AFI / DSFID |
| **Host Card Emulation**| No | No | Rare | **Universal Standard (HCE)** | No |

---

## 3. Type 2 Tag Memory Structure (NTAG213 / 215 / 216)

Type 2 is the most prevalent NFC tag silicon deployed worldwide (smart posters, product labels, NFC stickers). Memory is organized strictly into **4-byte pages**:

```text
 Page    Byte 0       Byte 1       Byte 2       Byte 3       Description
-----------------------------------------------------------------------------------------
 0x00    SN0          SN1          SN2          BCC0         UID Segment 1 (Manufacturer)
 0x01    SN3          SN4          SN5          SN6          UID Segment 2
 0x02    BCC1         Internal     Lock0        Lock1        BCC1 + Static Lock Bytes
 0x03    E1h          10h          12h          00h          Capability Container (CC)
-----------------------------------------------------------------------------------------
 0x04    03h          LEN          NDEF Data Byte 0 ...      NDEF Message TLV Block
 0x05    ...          ...          ...          ...          Payload
 ...     ...          ...          ...          ...          Payload
 0x0F    ...          ...          ...          FEh          Terminator TLV (0xFE)
-----------------------------------------------------------------------------------------
 Last    Dynamic Lock Configuration, Password, & PACK
```

### 3.1 The Capability Container (CC) — Page 0x03

The 4-byte CC page informs the reader whether NDEF data is present and how much memory is available:
- **Byte 0 (`Magic Number = 0xE1`)**: Identifies compliance with NFC Forum Type 2 Tag specification.
- **Byte 1 (`Version Number`)**: High nibble = Major version (`0x1`), Low nibble = Minor version (`0x0`) $\rightarrow$ `0x10`.
- **Byte 2 (`Memory Size Multiplier, T2T_SIZE`)**: Defines total user data memory:
  $$\text{User Memory (Bytes)} = \text{T2T\_SIZE} \times 8$$
  - Example: `0x12` ($18\text{ decimal}$) $\implies 18 \times 8 = 144\text{ bytes}$ of user space (NTAG213).
  - Example: `0x3E` ($62\text{ decimal}$) $\implies 62 \times 8 = 496\text{ bytes}$ (NTAG215).
  - Example: `0x6D` ($109\text{ decimal}$) $\implies 109 \times 8 = 872\text{ bytes}$ (NTAG216).
- **Byte 3 (`Read/Write Access`)**: `0x00` indicates read and write allowed without authentication; `0x0F` indicates read-only.

### 3.2 Type-Length-Value (TLV) Data Structure

User memory is wrapped in TLV blocks:
- **`T = 0x00` (Null TLV)**: 1-byte padding; ignored by reader.
- **`T = 0x03` (NDEF Message TLV)**:
  - If $L \le 254$: Length is 1 byte ($L$).
  - If $L \ge 255$: Length is encoded as 3 bytes: `0xFF [LEN_HIGH] [LEN_LOW]`.
  - Value contains the raw binary NDEF message.
- **`T = 0xFE` (Terminator TLV)**: 1 byte (`0xFE`); marks the end of valid data in tag memory.

---

## 4. Type 4 Tag Architecture & ISO 7816-4 File System

Type 4 tags use smart-card operating systems running over ISO 14443-4 (T=CL). The reader accesses NDEF data by issuing **ISO 7816-4 APDU commands** to select dedicated file identifiers:

```text
Host Reader (SPI Controller)                                     Type 4 Tag / HCE Phone
     |                                                                     |
     |--- Select NDEF Application: [00 A4 04 00 07 D2760000850101 00] ---->|
     |<-- Success Response: [90 00] ---------------------------------------|
     |                                                                     |
     |--- Select CC File: [00 A4 00 0C 02 E1 03] ------------------------->|
     |<-- Success Response: [90 00] ---------------------------------------|
     |                                                                     |
     |--- Read CC File: [00 B0 00 00 0F] --------------------------------->|
     |<-- CC Data: [00 0F 20 00 3B 00 34 04 06 E1 04 08 00 00 00] [90 00] -|
     |                                                                     |
     |--- Select NDEF Data File: [00 A4 00 0C 02 E1 04] ------------------->|
     |<-- Success Response: [90 00] ---------------------------------------|
     |                                                                     |
     |--- Read NDEF File Length (First 2 Bytes): [00 B0 00 00 02] --------->|
     |<-- Length Bytes: [00 1E] [90 00] (Payload is 30 bytes) -------------|
     |                                                                     |
     |--- Read NDEF Data Payload: [00 B0 00 02 1E] ------------------------>|
     |<-- Binary NDEF Message Bytes [90 00] -------------------------------|
```

- **NDEF Application ID (AID)**: `D2 76 00 00 85 01 01` (NFC Forum standard).
- **Capability Container File ID**: `E1 03`.
- **NDEF Data File ID**: `E1 04` (typically, as pointed to by the CC file).

---

## 5. NDEF (NFC Data Exchange Format) Specification

An NDEF Message consists of one or more **NDEF Records**. Each record encapsulates a typed payload.

```text
                  NDEF RECORD BYTE-LEVEL LAYOUT
 +-------------------------------------------------------------------+
 | Byte 0: Header Flags (MB, ME, CF, SR, IL, TNF)                    |
 +-------------------------------------------------------------------+
 | Byte 1: Type Length (1 Byte)                                      |
 +-------------------------------------------------------------------+
 | Byte 2 .. [2 or 5]: Payload Length (1 Byte if SR=1, 4 B if SR=0)  |
 +-------------------------------------------------------------------+
 | [Optional]: ID Length (1 Byte, present only if IL=1)              |
 +-------------------------------------------------------------------+
 | Type Field: Identifier (e.g. 'U', 'T', 'text/vcard')              |
 +-------------------------------------------------------------------+
 | [Optional] ID Field: Payload Identifier                           |
 +-------------------------------------------------------------------+
 | Payload Data: Raw application data                                |
 +-------------------------------------------------------------------+
```

### 5.1 NDEF Record Header Byte (Byte 0) Breakdown

```text
 Bit 7   Bit 6   Bit 5   Bit 4   Bit 3   Bit 2   Bit 1   Bit 0
+-------+-------+-------+-------+-------+-------+-------+-------+
|  MB   |  ME   |  CF   |  SR   |  IL   |         TNF           |
+-------+-------+-------+-------+-------+-------+-------+-------+
```

1. **`MB` (Message Begin, Bit 7)**: Set to `1` on the very first record of an NDEF message.
2. **`ME` (Message End, Bit 6)**: Set to `1` on the final record of an NDEF message. (For single-record messages, both `MB = 1` and `ME = 1`).
3. **`CF` (Chunk Flag, Bit 5)**: Set to `1` if the payload is fragmented across multiple chunks.
4. **`SR` (Short Record, Bit 4)**:
   - `SR = 1`: **Short Record**. Payload length is encoded as a **single byte** ($0\text{ to }255\text{ bytes}$).
   - `SR = 0`: **Normal Record**. Payload length is encoded as a **4-byte big-endian integer** (up to $4.29\text{ GB}$).
5. **`IL` (ID Length Present, Bit 3)**:
   - `IL = 1`: The 1-byte `ID Length` field and the `ID` string are present.
   - `IL = 0`: `ID Length` and `ID` fields are omitted.
6. **`TNF` (Type Name Format, Bits 2:0)**:

| TNF Value | Meaning | Description / Use Case |
| :--- | :--- | :--- |
| **`0x00`** | Empty | Record contains no type and no payload. |
| **`0x01`** | **NFC Forum Well-Known** | Standardized RTDs: URI (`'U'`), Text (`'T'`), Smart Poster (`'Sp'`). |
| **`0x02`** | **MIME Media-Type** | Standard RFC 2046 MIME types (e.g. `text/vcard`, `application/json`). |
| **`0x03`** | Absolute URI | Full URI defined in RFC 3986 (e.g. `https://vvdntech.com`). |
| **`0x04`** | External Type | Custom domain namespaced types (e.g. `android.com:pkg`). |
| **`0x05`** | Unknown | Undefined payload format. |
| **`0x06`** | Unchanged | Used in chunked records for intermediate segments. |

---

## 6. Well-Known Record Type Definitions (RTD)

### 6.1 URI Record Type (`Type = 'U'`, 0x55)

The URI record compresses popular URL prefixes into a single **URI Identifier Code** byte:

```text
Record Payload:
 +----------------------------+-------------------------------------+
 | Byte 0: URI Identifier Code| Byte 1 .. N: URI String Suffix      |
 +----------------------------+-------------------------------------+
```

#### Standard URI Identifier Prefix Table:
| Code | Prefix String | Code | Prefix String |
| :--- | :--- | :--- | :--- |
| `0x00` | No prefix (raw URI) | `0x07` | `ftp://anonymous:anonymous@` |
| `0x01` | `http://www.` | `0x08` | `ftp://ftp.` |
| `0x02` | `https://www.` | `0x09` | `ftps://` |
| `0x03` | `http://` | `0x0A` | `sftp://` |
| `0x04` | `https://` | `0x0D` | `tel:` |
| `0x05` | `telnet://` | `0x0E` | `mailto:` |
| `0x06` | `mailto:` | `0x1D` | `file://` |

#### Concrete Byte Dump Example: Encoding `https://vvdntech.com`
```text
D1 01 0D 55 04 76 76 64 6E 74 65 63 68 2E 63 6F 6D
```
- `D1`: Header (`MB=1, ME=1, CF=0, SR=1, IL=0, TNF=0x01 Well-Known`).
- `01`: Type Length = 1 byte.
- `0D`: Payload Length = 13 bytes (`0x0D`).
- `55`: Type Field = ASCII `'U'` (`0x55` for URI).
- `04`: Prefix Code = `0x04` (`https://`).
- `76 76 64 6E ...`: ASCII string `"vvdntech.com"`.

### 6.2 Text Record Type (`Type = 'T'`, 0x54)

```text
Record Payload:
 +---------------+--------------------+-----------------------------+
 | Status Byte   | Language Code      | UTF-8 / UTF-16 Text String  |
 | (1 Byte)      | (k Bytes, ASCII)   | (N - 1 - k Bytes)           |
 +---------------+--------------------+-----------------------------+
```
- **Status Byte (Bit 7)**: `0` = UTF-8 encoding; `1` = UTF-16 encoding.
- **Status Byte (Bits 5:0)**: Length of IANA language code string ($k$ bytes, e.g. `'en'` = 2, `'fr'` = 2).

---

## 7. Card Emulation Modes (PICC) via SPI

In Card Emulation mode, the Host MCU and SPI transceiver behave as a passive NFC tag or contactless smart card responding to an external reader (e.g. transit turnstile or smartphone).

```text
=============================================================================================
MODE A: Embedded Secure Element (eSE) / SIM via Single Wire Protocol (SWP)
=============================================================================================
  +------------------+         SWP (1-Wire)         +--------------------+
  | Transceiver IC   |<============================>| Hardware SE / SIM  | (EMVCo Certified)
  +------------------+                              +--------------------+

=============================================================================================
MODE B: Host Card Emulation (HCE) via High-Speed SPI
=============================================================================================
  +------------------+         SPI Bus              +--------------------+
  | Transceiver IC   |<============================>| Host MCU           |
  | (RF Frontend in  |   IRQ: Field Detected        | - ISO 14443-4 T=CL |
  |  PICC / Target   |   IRQ: APDU Received         | - Virtual Type 4 Tag
  |  Mode)           |   SPI Burst: APDU Response   | - Dynamic NDEF Gen |
  +------------------+                              +--------------------+
```

### 7.1 Implementing Host Card Emulation (HCE) over SPI

When using an intelligent controller like the **PN532** in Target / Card Emulation mode:
1. **Initialize as Target**:
   - Host sends command `TgInitAsTarget` (`0x8C`) with target configuration bytes (Mifare parameters, 7-byte UID, ATS parameters).
2. **RF Field Detection**:
   - When an external reader approaches, the transceiver detects the external 13.56 MHz carrier, answers the reader's REQA/WUPA, resolves anti-collision, and responds to RATS autonomously using hardware state machines.
3. **APDU Forwarding over SPI**:
   - The transceiver asserts the `IRQ` pin.
   - Host MCU reads the incoming ISO 7816-4 APDU command from the transceiver FIFO over SPI.
4. **Host Application Processing**:
   - The host parses the APDU (e.g. `SELECT AID`, `READ BINARY`).
   - If the AID matches the host's virtual smart card, the host generates the response payload and appends status word `90 00`.
5. **Transmit Response**:
   - Host sends `TgSetData` (`0x8E`) over SPI to load the APDU response into the transceiver's transmit FIFO.
   - The transceiver modulates the RF carrier back to the external reader using 848 kHz subcarrier load modulation.

---

## 8. Peer-to-Peer (P2P) Communication (ISO/IEC 18092)

NFC P2P enables two active devices (e.g. two smartphones, or an embedded terminal and a smartphone) to exchange data symmetrically:
- **Initiator**: Generates the initial RF field and starts the transaction.
- **Target**: Responds to the initiator.
- **Communication Modes**:
  - **Passive Mode**: Initiator generates the carrier continuously; Target uses load modulation (saves target battery power).
  - **Active Mode**: Both devices generate their own RF field alternately during their respective transmission phases.
- **Protocol Stack**:
  - **LLCP (Logical Link Control Protocol)**: Provides connectionless (unreliable datagram) and connection-oriented (reliable flow-controlled) data links.
  - **SNEP (Simple NDEF Exchange Protocol)**: Transports NDEF messages over LLCP using standard HTTP-like commands (`PUT`, `GET`).
