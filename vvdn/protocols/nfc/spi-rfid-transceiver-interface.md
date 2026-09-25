# SPI-Based RFID/NFC Transceiver Interface Architecture

## 1. Why SPI is the Interface of Choice for NFC Frontends

Modern NFC transceivers must bridge high-speed over-the-air RF bitstreams to a host microcontroller. While some chips offer auxiliary I2C or UART interfaces, **SPI (Serial Peripheral Interface)** is the industry standard for production embedded systems for the following engineering reasons:

1. **Bandwidth & Latency**:
   - Contactless smart card protocols (ISO/IEC 14443-4) support data rates of **106, 212, 424, and 848 kbps**.
   - At 848 kbps, payload data arrives at $\sim 106\text{ KB/s}$. An I2C bus at standard 100 kHz (effective $\sim 10\text{ KB/s}$) or Fast Mode 400 kHz (effective $\sim 36\text{ KB/s}$) cannot keep pace without massive on-chip buffering, causing internal FIFO overflows.
   - An SPI bus running at **5 MHz to 10 MHz** transfers data at $\sim 600\text{ to }1200\text{ KB/s}$, draining transceiver FIFOs in microseconds.
2. **Deterministic Full-Duplex Streaming**:
   - SPI has zero bus arbitration overhead, zero in-band 7-bit addressing, and zero clock-stretching delays.
3. **Interrupt Latency Tolerance**:
   - Small hardware FIFOs (typically 64 bytes in MFRC522 or PN532) fill in less than $600\ \mu\text{s}$ at 848 kbps. High-speed SPI allows burst reads during interrupt service routines (ISRs) before buffer overrun occurs.

---

## 2. Hardware Pinout & Electrical Interconnect

A robust SPI-based NFC subsystem requires the standard 4-wire SPI bus plus **two to three dedicated hardware sideband GPIO lines**:

```text
+-------------------+                                       +-------------------------+
|     Host MCU      |                                       |   NFC Transceiver IC    |
|                   |----------- SCLK (Max 10 MHz) -------->| SCK / SCLK              |
|                   |----------- MOSI / COPI -------------->| MOSI / SDI              |
|                   |<---------- MISO / CIPO ---------------| MISO / SDO              |
|                   |----------- CS# / NSS ---------------->| NSS / CS#               |
|                   |                                       |                         |
|                   |<---------- IRQ (Interrupt Line) ------| IRQ (TxDone, RxDone, WL)|
|                   |----------- RSTPD# / RESET ----------->| RSTPD / RST (Hard Reset)|
|                   |<---------- BUSY / READY (Optional) ---| BUSY (Handshake Line)   |
+-------------------+                                       +-------------------------+
```

### 2.1 Signal Definitions & Design Rules

1. **$\overline{\text{CS}}$ / NSS (Slave Select / Chip Select)**:
   - Driven active-LOW by the Host MCU.
   - **Crucial Rule**: The host must explicitly deassert CS (drive HIGH) between commands or burst transfers to reset the transceiver's internal SPI bit counters.
2. **SCLK (Serial Clock)**:
   - Driven by Host MCU. Transceivers typically support $f_{SCLK}$ up to **10 MHz** (MFRC522, ST25R3916) or **5 MHz** (PN532).
3. **MOSI / SDI (Master Out, Slave In)**:
   - Serial command/data stream from Host to Transceiver.
4. **MISO / SDO (Master In, Slave Out)**:
   - Serial status/data stream from Transceiver to Host. Enters High-Z (tri-state) when $\overline{\text{CS}}$ is HIGH.
5. **IRQ (Interrupt Request)**:
   - **Essential for Non-Blocking Firmware**: Driven by the transceiver to notify the host of critical events (`TxDone`, `RxDone`, `FIFOLevel` watermark, `Idle`, `Err`, `Timer`, `RFFieldDetect`).
   - Can be configured as active-LOW open-drain or active-HIGH push-pull depending on register settings.
6. **$\overline{\text{RSTPD}}$ / RST (Reset / Power-Down)**:
   - Hard reset and low-power sleep control. Driving this pin LOW shuts down internal analog oscillators, PLLs, and RF drivers, cutting quiescent current from $\sim 30\text{ mA}$ down to $< 5\ \mu\text{A}$.
7. **BUSY / READY (PN532 Handshake)**:
   - Used in intelligent controllers to indicate internal processor execution state.

### 2.2 Level Shifting Considerations

- Most modern Host MCUs operate at **$3.3\text{V}$ or $1.8\text{V}$** I/O logic.
- NFC transceivers frequently power their RF transmitter stage (`TVDD` or `AVDD`) from **$5.0\text{V}$** to maximize magnetic field strength ($H$), but supply their digital logic (`DVDD`, `VDD_IO`) from **$3.3\text{V}$**.
- Always verify that `VDD_IO` is tied to the Host MCU supply rail to eliminate the need for external level shifters.

---

## 3. Archetype 1: Direct Register-Driven Transceivers (MFRC522, ST25R3916, CLRC663)

In register-driven transceivers, the chip has no internal general-purpose microprocessor. The host MCU directly manipulates hardware state machines, analog registers, and a hardware FIFO over SPI.

```text
               REGISTER-DRIVEN SPI FRAME FORMAT (MFRC522 EXAMPLE)
    Byte 0: Address & Control Byte             Byte 1 .. N: Data Bytes
  +---+---+---+---+---+---+---+---+          +---+---+---+---+---+---+---+---+
  | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |          | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
  +---+---+---+---+---+---+---+---+          +---+---+---+---+---+---+---+---+
    |   <------- 6 Bits -------> |             <------ Data Payload -------->
    |         Reg Address        |
    |                            +---> Fixed '0'
    +---> Read/Write Bit:
          0 = Write to Register
          1 = Read from Register
```

### 3.1 SPI Bus Configuration
- **SPI Mode**: **Mode 0** ($\text{CPOL} = 0, \text{CPHA} = 0$) — Clock idles LOW, data sampled on the rising edge, shifted on the falling edge.
- **Bit Order**: **MSB-First** (Most Significant Bit transmitted first).
- **Max Clock Speed**: Typically $10\text{ MHz}$.

### 3.2 Register Addressing Protocol
1. **Single Register Write**:
   - Assert $\overline{\text{CS}}$ LOW.
   - Send Byte 0: `(Address << 1) & 0x7E` (Bit 7 = `0` for Write; Bit 0 = `0`).
   - Send Byte 1: Data value to write.
   - Deassert $\overline{\text{CS}}$ HIGH.
2. **Single Register Read**:
   - Assert $\overline{\text{CS}}$ LOW.
   - Send Byte 0: `((Address << 1) & 0x7E) | 0x80` (Bit 7 = `1` for Read; Bit 0 = `0`).
   - Send Dummy Byte (`0x00`), simultaneously read Data value on MISO.
   - Deassert $\overline{\text{CS}}$ HIGH.
3. **Continuous Burst FIFO Read / Write**:
   - To read/write the 64-byte FIFO without repeating address bytes:
   - Assert $\overline{\text{CS}}$ LOW.
   - Send Byte 0: FIFO address (`0x09` on MFRC522 $\rightarrow$ Read Byte: `(0x09 << 1) | 0x80 = 0x92`).
   - Continue sending dummy bytes (read) or payload bytes (write) while holding $\overline{\text{CS}}$ LOW. The transceiver automatically streams bytes into or out of the internal FIFO ring buffer.
   - Deassert $\overline{\text{CS}}$ HIGH.

### 3.3 The Bit Framing Engine (`BitFramingReg` / `TxLastBits`)

Standard SPI hardware is strictly byte-oriented (transfers in multiples of 8 bits). However, NFC air interfaces require sending **non-byte-aligned frames**:
- **REQA / WUPA** frames are exactly **7 bits** long (`0x26` or `0x52`).
- **Anti-Collision frames** can end on arbitrary bit boundaries (e.g. 23 bits, 31 bits).

To handle this, register-driven chips contain a **Bit Framing Engine**:
- **`BitFramingReg` (Address `0x0D` on MFRC522)**:
  - Bits `2:0` (`TxLastBits`): Defines the number of valid bits to transmit for the final byte in the FIFO (`0` = all 8 bits, `1` = 1 bit, ..., `7` = 7 bits).
  - Bits `6:4` (`RxAlign`): Defines the bit position for the first received bit.
  - Bit `7` (`StartSend`): When set, immediately starts RF transmission from FIFO.

---

## 4. Archetype 2: Packet-Oriented Intelligent NFC Controllers (NXP PN532, PN7160)

The NXP PN532 contains an internal 8051 microcontroller running proprietary ROM firmware that executes the ISO 14443-3 and ISO 14443-4 state machines internally. Communication over SPI occurs via a **Handshake Packet Protocol**.

```text
                  PN532 NORMAL SPI DATA FRAME STRUCTURE
 +----------+-------------+-----+-----+-----+-------------+-----+----------+
 | Preamble |  Start Code | LEN | LCS | TFI | Packet Data | DCS | Postamble|
 |   0x00   | 0x00   0xFF | 1 B | 1 B | 1 B |   N Bytes   | 1 B |   0x00   |
 +----------+-------------+-----+-----+-----+-------------+-----+----------+
                          |<--------->|     |<----------->|
                          LEN + LCS=0        Sum(TFI..Data) + DCS = 0
```

### 4.1 THE INFAMOUS CRITICAL TRAP: LSB-First Bit Order

> [!WARNING]
> **CRITICAL EMBEDDED PITFALL**:
> In 99% of embedded SPI peripherals (Flash, IMUs, ADCs, MFRC522, ST25R), SPI operates **MSB-First**.
> However, the **PN532 hardware SPI controller operates LSB-FIRST** (Least Significant Bit transmitted first, Bit 0 before Bit 7)!
>
> If your microcontroller's SPI hardware does not support runtime hardware LSB-first switching, you **must perform bit-reversal in software on every single byte transmitted and received**, or all commands will be completely rejected by the PN532.

```c
// Software bit-reversal lookup function for MSB-only SPI controllers
static inline uint8_t nfc_reverse_bits(uint8_t b) {
    b = (b & 0xF0) >> 4 | (b & 0x0F) << 4;
    b = (b & 0xCC) >> 2 | (b & 0x33) << 2;
    b = (b & 0xAA) >> 1 | (b & 0x55) << 1;
    return b;
}
```

### 4.2 SPI Handshake Protocol & Flow Control

The PN532 uses three single-byte SPI command opcodes to manage bus handshaking:
1. **`0x01` — Read Status Byte**:
   - Host sends `0x01`, then clocks in 1 byte.
   - Bit 0 is the **`Ready`** bit:
     - `Status & 0x01 == 0x01`: PN532 has finished processing and response data is ready to read.
     - `Status & 0x01 == 0x00`: PN532 is busy; host must poll again or wait for the IRQ pin.
2. **`0x02` — Write Data**:
   - Host sends `0x02`, followed immediately by the command packet frame.
3. **`0x03` — Read Data**:
   - Host sends `0x03`, followed by clocking in the response packet frame.

```text
Host MCU                                                       PN532
   |                                                             |
   |--- CS# LOW ------------------------------------------------>|
   |--- 0x02 (Write Data Opcode) + Command Packet -------------->|
   |--- CS# HIGH ----------------------------------------------->|
   |                                                             |
   |                      (PN532 processes RF / ISO commands...) |
   |                                                             |
   |--- CS# LOW ------------------------------------------------>|
   |--- 0x01 (Read Status Opcode) ------------------------------>|
   |<-- Status Byte: 0x00 (Not Ready, Still Busy) ---------------|
   |--- CS# HIGH ----------------------------------------------->|
   |                                                             |
   |   [Optionally: Wait for PN532 IRQ line to go LOW]           |
   |                                                             |
   |--- CS# LOW ------------------------------------------------>|
   |--- 0x01 (Read Status Opcode) ------------------------------>|
   |<-- Status Byte: 0x01 (READY!) ------------------------------|
   |--- CS# HIGH ----------------------------------------------->|
   |                                                             |
   |--- CS# LOW ------------------------------------------------>|
   |--- 0x03 (Read Data Opcode) -------------------------------->|
   |<-- Response Packet Frame (TFI=0xD5, Data...) ---------------|
   |--- CS# HIGH ----------------------------------------------->|
```

### 4.3 PN532 Packet Frame Fields

1. **Preamble (`0x00`)**: Single synchronizing null byte.
2. **Start Code (`0x00 0xFF`)**: Identifies start of packet.
3. **Length (`LEN`)**: Total count of bytes in the `TFI` + `Packet Data` payload ($1 \le LEN \le 255$).
4. **Length Checksum (`LCS`)**:
   $$(\text{LEN} + \text{LCS}) \ \& \ 0\text{xFF} = 0\text{x}00 \implies \text{LCS} = (\sim\text{LEN} + 1) \ \& \ 0\text{xFF}$$
5. **Target Frame Identifier (`TFI`)**:
   - `0xD4`: Direction = Host MCU $\rightarrow$ PN532.
   - `0xD5`: Direction = PN532 $\rightarrow$ Host MCU.
6. **Data Checksum (`DCS`)**:
   $$\left( \text{TFI} + \sum \text{Data Bytes} + \text{DCS} \right) \ \& \ 0\text{xFF} = 0\text{x}00$$
7. **Postamble (`0x00`)**: Concluding byte.

### 4.4 Standard Handshake Packets

- **Acknowledge (ACK) Packet**: Sent by PN532 immediately after receiving a valid command:
  ```text
  00 00 FF 00 FF 00
  ```
- **Negative Acknowledge (NACK) Packet**: Indicates checksum or framing error:
  ```text
  00 00 FF FF 00 00
  ```

---

## 5. FIFO Buffer Architecture & Interrupt Watermark Mechanics

NFC transceivers rely on internal hardware FIFO buffers to decouple the real-time RF air interface from host SPI processing:

```text
               TRANSCEIVER HARDWARE FIFO MANAGEMENT
 +-------------------------------------------------------------------+
 | 64-Byte FIFO Ring Buffer                                          |
 | [B0][B1][B2][B3] ... [B31] ... [B62][B63]                        |
 +-------------------------------------------------------------------+
         ^                                    ^
         | Write Pointer                      | Read Pointer
         |                                    |
   Air Interface RX                     SPI Burst Read to MCU
   (106 - 848 kbps)                     (5 - 10 MHz)
```

### 5.1 FIFO Watermark Latency Budget Calculation

Let us calculate the critical timing budget to prevent FIFO overflow during an ISO 14443-4 transmission at **848 kbps**:

1. **RF Arrival Rate**:
   $$\text{Bit Rate} = 848\text{ kbps} \implies \text{Byte Rate} = \frac{848,000}{8} = 106,000\text{ bytes/sec} = 106\text{ bytes/ms}$$
2. **Buffer Fill Time**:
   A 64-byte FIFO will completely fill in:
   $$t_{fill} = \frac{64\text{ bytes}}{106\text{ bytes/ms}} \approx 0.603\text{ ms} = 603\ \mu\text{s}$$
3. **Watermark Threshold Setting**:
   If the `WaterLevel` interrupt is programmed to fire at **half-full (32 bytes)**:
   $$t_{margin} = \frac{32\text{ bytes}}{106\text{ bytes/ms}} \approx 301\ \mu\text{s}$$
   **Hard Real-Time Constraint**: The Host MCU must service the external GPIO interrupt and execute an SPI burst read within **$301\ \mu\text{s}$**, or data will be permanently lost due to FIFO overrun!
4. **SPI Read Drain Time**:
   At $f_{SCLK} = 5\text{ MHz}$, transferring 32 bytes over SPI takes:
   $$t_{spi} = \frac{32\text{ bytes} \times 8\text{ bits}}{5\text{ MHz}} = 51.2\ \mu\text{s}$$
   Because $51.2\ \mu\text{s} \ll 301\ \mu\text{s}$, the SPI bus easily drains the FIFO before overflow occurs, provided the host firmware does not block inside higher-priority interrupt handlers.

---

## 6. AC Timing Specifications & Bus Constraints

To ensure data integrity, host firmware and hardware design must strictly adhere to the transceiver's AC switching characteristics:

```text
CS#   \___________________________________________________________/-----\______
      |<-- t_lead -->|                             |<-- t_lag -->|  t_CS_high |
SCLK  ________________/-\_/-\_/-\ ... /-\_/-\_/-\_______________________/-\_/-\
MOSI  -------< Bit 7 >< Bit 6 >   ...   < Bit 0 >-----------------------< Bit 7 >
             |<-t_su->|<-t_h->|
MISO  -------< Bit 7 >< Bit 6 >   ...   < Bit 0 >--------------------------------
```

| Timing Parameter | Symbol | Min Value | Max Value | Description |
| :--- | :--- | :--- | :--- | :--- |
| **SCLK Clock Frequency** | $f_{SCLK}$ | DC | 10 MHz | Maximum SPI clock rate |
| **SCLK Pulse Width High / Low** | $t_{CLKH}, t_{CLKL}$ | 45 ns | — | SCLK duty cycle must stay within 40%–60% |
| **Chip Select Lead Time** | $t_{lead}$ | 50 ns | — | Delay from $\overline{\text{CS}}$ falling edge to first SCLK edge |
| **Chip Select Lag Time** | $t_{lag}$ | 50 ns | — | Delay from last SCLK edge to $\overline{\text{CS}}$ rising edge |
| **Chip Select Deselection Time** | $t_{CS\_high}$ | **100 ns** | — | **Mandatory pause between back-to-back SPI transfers** |
| **Data Setup Time** | $t_{su}$ | 15 ns | — | Input data valid before SCLK sampling edge |
| **Data Hold Time** | $t_h$ | 15 ns | — | Input data held valid after SCLK sampling edge |
| **Output Valid Delay** | $t_{v}$ | — | 25 ns | Delay from SCLK shift edge until MISO data is stable |
