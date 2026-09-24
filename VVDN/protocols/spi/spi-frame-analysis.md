# SPI Data Frame Anatomy, Packet Structures & Protocol Analysis

This document provides a comprehensive technical breakdown of **SPI Data Frames**: physical vs logical framing, command-response architectures, dummy cycle mechanics, device-specific packet archetypes (Flash, IMUs, ADCs, Automotive Safe SPI), CRC verification, and logic analyzer frame decoding.

---

## 1. Physical vs. Logical SPI Framing

Unlike UART (which specifies an exact 10-bit physical hardware frame) or I2C (which defines explicit START, ADDRESS, ACK/NACK, and STOP conditions on the wire), raw physical SPI is **pure bit streaming**. 

To build reliable embedded systems, engineers distinguish between **Physical Framing** and **Logical Framing**:

```text
  PHYSICAL LAYER:  CS# Assert ──> [Clock Pulses & Dual Shift Registers] ──> CS# Deassert
                                                │
                                                ▼
  LOGICAL LAYER:   [Opcode / CMD] [Address / Reg] [Turnaround / Dummy] [Data Payload] [CRC]
```

### 1.1 Physical Framing Boundaries
- **Frame Initiation**: The Controller drives Chip Select ($\overline{\text{CS}}$) from HIGH to LOW. This resets the peripheral's internal bit counter and state machine, and enables its MISO output driver.
- **Clocking & Shifting**: SCLK pulses transmit data bidirectionally between the Controller and Peripheral shift registers.
- **Frame Termination**: The Controller drives $\overline{\text{CS}}$ from LOW to HIGH. This:
  - Latches received commands or written data into internal device registers.
  - Returns the peripheral's MISO pin to High-Z (tri-state).
  - Resets state logic to prepare for the next transaction.

> [!IMPORTANT]
> **Chip Select is the Word & Packet Boundary**: If $\overline{\text{CS}}$ does not toggle between independent commands, many SPI peripherals (such as EEPROMs and ADCs) will fail to execute commands, misinterpret opcodes, or permanently ignore subsequent clock cycles.

---

### 1.2 Word Size vs. Packet Size
- **Word Size (Bits per Word)**: The atomic unit clocked in one continuous chunk. Standard microcontrollers support **8-bit**, **16-bit**, or **32-bit** word lengths. Many precision instrumentation converters use non-standard sizes (**10-bit, 12-bit, 14-bit, or 24-bit**).
- **Packet Size (Transaction Length)**: The total number of bytes transferred between $\overline{\text{CS}}$ falling and rising. A single packet can range from **1 byte** (e.g. Write Enable opcode `0x06`) to **256+ bytes** (e.g. Flash page programming) or **several kilobytes** in DMA burst transfers.

---

## 2. Universal Anatomy of a Logical SPI Frame

A generalized SPI command-response data frame contains up to five distinct functional phases:

```text
CS#   ──────┐                                                                                                         ┌──────
            └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
MOSI:       |  Phase 1: Command  |   Phase 2: Address   |   Phase 3: Turnaround   |      Phase 4: Data Payload    |  Phase 5: CRC  |
            |  (Opcode / R/W)    |   (Register / Mem)   |   (Dummy Wait Clocks)   |      (Write Bytes / 0x00)     |  (Optional)    |
MISO:       |  Don't Care / Echo |   Don't Care / Echo  |   High-Z / Pipelining   |      (Read Response Bytes)    |  (Optional)    |
```

### Phase 1: Instruction / Command Phase (Opcode)
- Always driven by the Controller on MOSI.
- Identifies the operation to perform: Read, Write, Erase, Read Status, Reset, etc.
- In many sensor ICs (accelerometers, gyroscopes), the command byte integrates the **R/W direction bit** and **Auto-Increment / Burst bit** directly into the upper bits.

### Phase 2: Address Phase
- Identifies the destination register address (sensors) or 16-bit / 24-bit / 32-bit memory address (Flash/EEPROM).
- Transmitted MSB-first. 
- For devices exceeding 16 MB (128 Mb) capacity, modern SPI Flash utilizes a **4-byte (32-bit) addressing mode** instead of legacy 3-byte (24-bit) addressing.

### Phase 3: Turnaround & Dummy Wait States
- **The Turnaround Problem**: In high-speed read transactions ($> 25\,\text{MHz}$), internal memory arrays and ADCs cannot fetch internal data cells fast enough to output valid data on the very next clock edge following the address.
- **The Solution**: The Controller transmits a fixed number of **Dummy Cycles** (typically 1 to 8 clock cycles / 1 byte) where MOSI outputs `0x00` or `0xFF`.
- During these dummy cycles, the peripheral retrieves data from its internal array and prepares its output shift register. Data appears on MISO immediately following the dummy phase.

```text
SCLK:       ... ──┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐ ...
                  └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘
MOSI:       ... ────< Address Bit 0 >───<       DUMMY BYTE (Host clocks wire)       >─── ...
MISO:       ... ────<    High-Z     >───< Array Access >───< Data Bit 7 (Valid Output) > ...
                                        |<-- t_access ->|  ▲ First valid read bit
```

### Phase 4: Data Payload Phase
- **For Write Transactions**: MOSI carries user data bytes; MISO echoes dummy bytes, device status flags, or prior register contents.
- **For Read Transactions**: MOSI supplies clocking dummy bytes (`0x00` or `0xFF`); MISO drives the requested data bytes.

### Phase 5: Frame Integrity / Checksum Phase (Optional)
- Used in safety-critical, automotive, and industrial peripherals (AEC-Q100, ISO 26262 ASIL).
- Carries an 8-bit or 16-bit CRC calculated over all preceding bytes in the frame.
- If the calculated CRC does not match, the peripheral rejects the write command and asserts an error flag in its status register.

---

## 3. Real-World SPI Frame Archetypes & Case Studies

### 3.1 Archetype A: SPI NOR Flash Memory (e.g. Winbond W25Q128 / Macronix MX25)

Serial NOR Flash chips are the most common SPI devices in embedded systems, serving as boot media for Linux SoCs and firmware storage for microcontrollers.

#### 1. JEDEC Identification Read Frame (`0x9F`)
Reads manufacturer code, memory type, and capacity. Total packet length: **4 bytes**.

```text
CS#   ──────┐                                                                             ┌──────
            └─────────────────────────────────────────────────────────────────────────────┘
SCLK:       [ 8 Clocks: Byte 0 ] [ 8 Clocks: Byte 1 ] [ 8 Clocks: Byte 2 ] [ 8 Clocks: Byte 3 ]
MOSI:       ──[ 0x9F (Command) ]──[ 0x00 (Dummy)    ]──[ 0x00 (Dummy)    ]──[ 0x00 (Dummy)    ]──
MISO:       ──[ Stale / High-Z ]──[ 0xEF (Mfg ID)   ]──[ 0x40 (Mem Type) ]──[ 0x18 (Capacity) ]──
                                  (0xEF = Winbond)    (SPI / QSPI)        (0x18 = 128 Mbit)
```

#### 2. Standard Read (`0x03`) vs. High-Speed Fast Read (`0x0B`)
- **Standard Read (`0x03`)**: Maximum clock speed limited to $\approx 33 - 50\,\text{MHz}$. Frame: `[0x03] + [24-bit Address] + [Data Bytes...]`. No dummy byte.
- **Fast Read (`0x0B`)**: Allows operation up to $104 - 133\,\text{MHz}$. Requires **1 Dummy Byte (8 dummy clocks)** after the address to accommodate array access latency:

```text
MOSI: ──[ 0x0B ]──[ Addr[23:16] ]──[ Addr[15:8] ]──[ Addr[7:0] ]──[ DUMMY (0x00) ]──[ 0x00 ]──[ 0x00 ]...
MISO: ──[  XX  ]──[     XX      ]──[     XX     ]──[     XX     ]──[     WAIT     ]──[ D0   ]──[ D1   ]...
```

#### 3. Page Program (Write) Frame (`0x02`)
Flash writes require a two-step sequence:
1. First Frame: Issue **Write Enable (`0x06`)** (1-byte frame, $\overline{\text{CS}}$ toggled).
2. Second Frame: Issue **Page Program (`0x02`)** with 24-bit address and 1 to 256 payload bytes:

```text
Frame 1:  CS# ──┐         ┌──
          MOSI: └──[0x06]──┘  (WEL bit set in Status Register)

Frame 2:  CS# ──┐                                                                              ┌──
          MOSI: └──[ 0x02 ]──[ Addr MSB ]──[ Addr MID ]──[ Addr LSB ]──[ Data 0 ]...[ Data 255 ]──┘
          MISO: ───[  XX  ]──[    XX    ]──[    XX    ]──[    XX    ]──[   XX   ]...[   XX   ]───
```

---

### 3.2 Archetype B: Digital Sensors & IMUs (e.g. ADXL345, BMI160, ICM-42688)

Digital motion and environmental sensors use compact register-mapped framing. To optimize bandwidth, the command byte packs addressing and control flags into a single 8-bit word.

#### Frame Format Breakdown (e.g. ADXL345 3-Axis Accelerometer):
- **Bit 7 ($\text{R}/\overline{\text{W}}$)**: `1` = Read operation; `0` = Write operation.
- **Bit 6 ($\text{MB}$)**: Multiple-Byte / Auto-Increment bit (`1` = Stream multiple sequential registers; `0` = Single byte).
- **Bits [5:0] ($\text{Reg Addr}$)**: 6-bit register address (`0x00` to `0x3F`).

```text
Command Byte Bit Layout:
┌───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┐
│ Bit 7 │ Bit 6 │ Bit 5 │ Bit 4 │ Bit 3 │ Bit 2 │ Bit 1 │ Bit 0 │
├───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┤
│  R/W# │   MB  │                  Register Address [5:0]       │
└───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘
```

#### Multi-Byte Burst Read Example (Reading X, Y, Z Acceleration Atomically):
To prevent axis skew where $X$ is sampled at time $T_0$ and $Z$ at time $T_1$, all 6 data registers (`DATAX0` to `DATAZ1`, registers `0x32` to `0x37`) must be read in a **single continuous $\overline{\text{CS}}$ window**:

```text
MOSI Byte 0: 0xC0 | 0x32 = 0xF2 (Bit 7=1 for Read, Bit 6=1 for Multi-Byte, Bits 5:0 = 0x32)

CS#   ──────┐                                                                                                         ┌──────
            └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
MOSI:       ──[ 0xF2 (CMD) ]──[ 0x00 (Dummy) ]──[ 0x00 (Dummy) ]──[ 0x00 ]──[ 0x00 ]──[ 0x00 ]──[ 0x00 (Dummy) ]──
MISO:       ──[ Stale / XX ]──[ DATAX0 (0x32)]──[ DATAX1 (0x33)]──[ DATAY0]──[ DATAY1]──[ DATAZ0]──[ DATAZ1 (0x37)]──
```
During this single frame, the sensor's internal address pointer auto-increments after each byte without requiring repeated command headers.

---

### 3.3 Archetype C: Precision Analog-to-Digital Converters (ADCs)

Many high-speed precision ADCs (e.g. Microchip MCP3008, Texas Instruments ADS7886, Analog Devices AD7928) use **arbitrary bit-length framing** that does not align with standard 8-bit byte boundaries.

#### Case Study: MCP3008 10-Bit 8-Channel ADC Frame
The MCP3008 requires a **24-clock-cycle (3-byte) transfer** to configure the channel multiplexer and clock out a 10-bit analog conversion:

```text
MOSI (Host -> ADC):
Byte 0:  0 0 0 0 0 0 0 1       (Start Bit: 0x01)
Byte 1:  S D2 D1 D0 0 0 0 0    (S=Single/Diff, D2:D0=Channel Select, e.g. 0x80 for CH0 Single)
Byte 2:  0 0 0 0 0 0 0 0       (Don't Care / Dummy: 0x00)

MISO (ADC -> Host):
Byte 0:  X X X X X X X X       (High-Z / Undefined)
Byte 1:  X X X X X 0 B9 B8     (Bits [7:3] High-Z; Bit 2 = Null Bit; Bits [1:0] = MSB Bits 9 & 8)
Byte 2:  B7 B6 B5 B4 B3 B2 B1 B0 (Data Bits 7 down to 0)
```

```text
Timing Waveform:
CS#   ──────┐                                                                             ┌──────
            └─────────────────────────────────────────────────────────────────────────────┘
SCLK:       | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |10 |11 |12 |13 |14 |15 |16 |17 ... 23 |24 |
MOSI:       ──[ 0   0   0   0   0   0   0   1 ] [ S  D2  D1  D0  0   0   0   0 ] [ 0 ... 0 ]──
MISO:       ────────────────────────────[High-Z]──────[Sample] [Null| B9  B8 ] [ B7 ... B0 ]──
                                                                 ▲
                                                          Null Bit = Always 0
```

#### Decoding Formula:
$$\text{Raw ADC Value (10-bit)} = ((\text{Byte1} \ \&\ 0x03) \ll 8) \ | \ \text{Byte2}$$
$$\text{Measured Voltage} = \frac{\text{Raw Value}}{1024} \times V_{REF}$$

---

### 3.4 Archetype D: Safe SPI with Hardware CRC (Automotive & Industrial)

In automotive powertrain, braking, and airbag systems (AEC-Q100 / ISO 26262), corrupted SPI frames caused by EMI, electric motor switching, or wiring faults can have catastrophic consequences. Peripherals implement **Safe SPI** where every frame contains a hardware-calculated **CRC-8** field.

```text
Standard 32-Bit Safe SPI Command Frame:
┌───────────────┬───────────────┬───────────────────────────────┬───────────────┐
│ Bits [31:30]  │ Bits [29:24]  │         Bits [23:8]           │  Bits [7:0]   │
├───────────────┼───────────────┼───────────────────────────────┼───────────────┤
│ Opcode (R/W)  │ Register Addr │       Data Payload (16-bit)   │  CRC-8 Field  │
└───────────────┴───────────────┴───────────────────────────────┴───────────────┘

Matching 32-Bit Safe SPI Response Frame:
┌───────────────┬───────────────┬───────────────────────────────┬───────────────┐
│ Bits [31:30]  │ Bits [29:24]  │         Bits [23:8]           │  Bits [7:0]   │
├───────────────┼───────────────┼───────────────────────────────┼───────────────┤
│ Global Status │ Echoed Addr   │       Read Data / Echo        │  CRC-8 Field  │
└───────────────┴───────────────┴───────────────────────────────┴───────────────┘
```

#### CRC-8 Mathematical Specification:
- **Standard Polynomial**: $P(x) = x^8 + x^2 + x^1 + 1$ (`0x07`) or SAE J1850 ($x^8 + x^4 + x^3 + x^2 + 1$ / `0x1D`).
- **Initial Seed**: Typically `0xFF` or `0x00`.
- **Validation Rule**: The peripheral computes the CRC across bits [31:8]. If the calculated CRC does not match bits [7:0], the hardware **drops the write**, asserts a `CRC_ERR` flag in the Global Status bits of the response frame, and triggers an interrupt to the host MCU.

---

## 4. Multi-Segment Transactions in Software (`struct spi_ioc_transfer`)

In real-world embedded Linux, complex frames (e.g. Command + Address at 10 MHz followed by streaming data payload at 40 MHz) are executed atomically using an array of `struct spi_ioc_transfer` structs passed to `ioctl(SPI_IOC_MESSAGE(N))`.

### 4.1 Linux Atomic Multi-Transfer Architecture

```c
#include <linux/spi/spidev.h>
#include <sys/ioctl.h>

int spi_read_flash_fast(int fd, uint32_t addr, uint8_t *rx_buf, size_t len) {
    uint8_t cmd_hdr[5];
    cmd_hdr[0] = 0x0B;                 // Fast Read Opcode
    cmd_hdr[1] = (addr >> 16) & 0xFF;  // Address MSB
    cmd_hdr[2] = (addr >> 8)  & 0xFF;  // Address MID
    cmd_hdr[3] = addr & 0xFF;         // Address LSB
    cmd_hdr[4] = 0x00;                 // Dummy Byte

    struct spi_ioc_transfer xfer[2];
    memset(xfer, 0, sizeof(xfer));

    // Segment 1: Header (Command + 24-bit Addr + Dummy Byte)
    xfer[0].tx_buf = (unsigned long)cmd_hdr;
    xfer[0].rx_buf = 0;                // Don't care about incoming data during header
    xfer[0].len = 5;
    xfer[0].speed_hz = 25000000;       // 25 MHz
    xfer[0].cs_change = 0;             // CRITICAL: Keep CS LOW between segments!

    // Segment 2: Data Payload Burst Read
    xfer[1].tx_buf = 0;                // Kernel clocks out 0x00 automatically
    xfer[1].rx_buf = (unsigned long)rx_buf;
    xfer[1].len = len;
    xfer[1].speed_hz = 50000000;       // Run data phase at 50 MHz
    xfer[1].cs_change = 0;             // Raise CS at conclusion of transaction

    // Atomic execution: Kernel holds CS continuously low across both segments
    return ioctl(fd, SPI_IOC_MESSAGE(2), xfer);
}
```

> [!CAUTION]
> **The `cs_change` Trap**:
> - If `cs_change == 0`: $\overline{\text{CS}}$ remains **asserted (LOW)** until the entire array of transfers completes.
> - If `cs_change == 1`: $\overline{\text{CS}}$ is **deasserted (toggled HIGH)** momentarily between transfer segments. 
> Setting `cs_change = 1` before the data phase will prematurely terminate the memory read command and corrupt the payload!

---

## 5. Software Implementation: Safe SPI CRC-8 Verification

The following production Python module demonstrates packet construction, CRC-8 generation, and frame verification for an industrial sensor:

```python
#!/usr/bin/env python3
"""
Industrial SPI Frame Formatter and CRC-8 Validator
Implements SAE J1850 CRC-8 (Polynomial: 0x1D, Initial: 0xFF)
"""

def compute_crc8(data: bytes, poly: int = 0x1D, init_val: int = 0xFF) -> int:
    """Calculates an 8-bit CRC over arbitrary byte sequences."""
    crc = init_val
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ poly) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc

def pack_safe_spi_frame(rw: int, addr: int, payload: int) -> bytes:
    """
    Constructs a 32-bit Safe SPI Command Frame:
    [Bit 31: R/W] [Bits 30-24: Addr] [Bits 23-8: Payload] [Bits 7-0: CRC8]
    """
    header = ((rw & 0x01) << 7) | (addr & 0x7F)
    payload_msb = (payload >> 8) & 0xFF
    payload_lsb = payload & 0xFF
    
    body = bytes([header, payload_msb, payload_lsb])
    crc = compute_crc8(body)
    
    frame = body + bytes([crc])
    return frame

def parse_safe_spi_response(raw_bytes: bytes) -> dict:
    """Parses and verifies a received 4-byte SPI response frame."""
    if len(raw_bytes) != 4:
        raise ValueError(f"Invalid frame length: expected 4 bytes, got {len(raw_bytes)}")
    
    body = raw_bytes[:3]
    received_crc = raw_bytes[3]
    expected_crc = compute_crc8(body)
    
    is_valid = (received_crc == expected_crc)
    status_byte = raw_bytes[0]
    payload = (raw_bytes[1] << 8) | raw_bytes[2]
    
    return {
        "valid": is_valid,
        "status_flags": hex(status_byte),
        "payload": hex(payload),
        "crc_expected": hex(expected_crc),
        "crc_received": hex(received_crc)
    }

if __name__ == "__main__":
    # Test frame assembly: Write 0xABCD to Register 0x14
    tx_frame = pack_safe_spi_frame(rw=0, addr=0x14, payload=0xABCD)
    print("Transmitted Safe SPI Frame :", [hex(b) for b in tx_frame])
    print(f"Computed CRC               : 0x{tx_frame[3]:02X}")
    
    # Test frame validation: Simulated response
    simulated_rx = bytes([0x00, 0x12, 0x34, 0x00])
    valid_rx = simulated_rx[:3] + bytes([compute_crc8(simulated_rx[:3])])
    result = parse_safe_spi_response(valid_rx)
    print("Parsed Response Status     :", result)
```

---

## 6. Decoding & Analyzing Frames on Logic Analyzers

When capturing SPI communication with a logic analyzer (e.g. Saleae Logic, Sigrok PulseView, or Rigol/Keysight DSO):

```text
Protocol Analyzer Trace View:
Time [ms]     Channel      Decoded Value       Annotation
────────────────────────────────────────────────────────────────────────────────────────
0.000000      CS#          Falling Edge        Frame Start (Active LOW)
0.000010      MOSI         0x03                Command: Read Array (3-byte Addr)
0.000090      MOSI         0x10, 0x00, 0x00    Target Address: 0x100000
0.000330      MISO         0x48                Payload Byte 0: 'H'
0.000410      MISO         0x65                Payload Byte 1: 'e'
0.000490      MISO         0x6C                Payload Byte 2: 'l'
0.000570      MISO         0x6C                Payload Byte 3: 'l'
0.000650      MISO         0x6F                Payload Byte 4: 'o'
0.000730      CS#          Rising Edge         Frame End (Deselect / Terminate)
```

### 6.1 Diagnostic Rules for Frame Decode Anomalies

| Analyzer Visual Symptom | Root Cause | Underlying Hardware Mechanism |
| :--- | :--- | :--- |
| **All decoded bytes shifted left by 1 bit** (e.g. `0x9F` decoded as `0x3E`) | Analyzer CPHA configuration inverted. | The analyzer is sampling on the leading edge instead of trailing edge; it captures the bus while the line is still transitioning. |
| **MISO outputs `0x00` during byte 0, real data during byte 1** | Normal SPI Shift Register behavior. | During byte 0 (command phase), the peripheral is receiving the opcode. It cannot output valid response data until byte 1. |
| **Data bytes read correctly, but device does not respond to subsequent writes** | $\overline{\text{CS}}$ not toggled HIGH between frames. | Many flash/EEPROM devices latch data and start internal write cycles only upon the **rising edge of $\overline{\text{CS}}$**. |
| **Decoded hex displays `0xFF` or `0x00` across all bytes** | 1. Slave unpowered.<br>2. Wrong CS routed.<br>3. MISO floating. | When a slave is unselected, its MISO output buffer is in High-Z. A floating line typically drifts to logic HIGH (`0xFF`) or LOW (`0x00`). |
| **Intermittent corrupt bytes during high-speed burst** | Inter-word timing violation ($t_{inter\_byte}$) or lack of dummy clocks. | High-speed memory arrays require dummy wait states to fetch subsequent blocks. |

---

## 7. Frame Analysis Quick-Reference Cheatsheet

```text
+-----------------------+---------------------+-------------------+-------------------------------+
| Device Class          | Typical Word Size   | Typical Frame Len | Key Framing Distinctives       |
+-----------------------+---------------------+-------------------+-------------------------------+
| SPI NOR Flash         | 8-bit               | 1 to 260+ bytes   | Fast Read needs dummy byte;   |
| (W25Q, MX25, AT25)    |                     |                   | Page Program capped at 256 B  |
+-----------------------+---------------------+-------------------+-------------------------------+
| Motion Sensors / IMUs | 8-bit               | 2 to 14 bytes     | Bit 7 = R/W#; Bit 6 = AutoInc |
| (ADXL345, BMI160)     |                     |                   | Multi-byte reads atomic       |
+-----------------------+---------------------+-------------------+-------------------------------+
| Precision ADCs        | 10, 12, 16, 24-bit  | 2 to 4 bytes      | Arbitrary bit alignment;      |
| (MCP3008, ADS7886)    |                     |                   | Null bit preceding MSB data   |
+-----------------------+---------------------+-------------------+-------------------------------+
| Automotive Safe SPI   | 32-bit (fixed)      | Exactly 4 bytes   | 8-bit CRC suffix;             |
| (Motor/Braking ICs)   |                     |                   | Write dropped on CRC mismatch |
+-----------------------+---------------------+-------------------+-------------------------------+
```
