# ISO/IEC 14443 Protocol Framing, Anti-Collision & Transport Guide

## 1. ISO/IEC 14443 Architecture & State Transition Diagram

Communication between an NFC reader (PCD) and a proximity card (PICC) is governed by a strict hierarchical state machine defined in **ISO/IEC 14443-3** (Initialization & Anti-Collision) and **ISO/IEC 14443-4** (Transmission Protocol T=CL).

```text
                                  +-----------------------+
                                  |       POWER-OFF       | (No RF Carrier Field)
                                  +-----------------------+
                                              |
                                              | PCD Activates RF Carrier (13.56 MHz)
                                              | Mandatory Guard Delay: T_guard >= 5.0 ms
                                              v
                                  +-----------------------+
                     +----------->|         IDLE          |<-----------+
                     |            +-----------------------+            |
                     |                        |                        |
                     |                        | REQA (0x26) or         |
                     |                        | WUPA (0x52)            |
                     |                        v                        |
                     |            +-----------------------+            |
                     |            |        READY 1        |            |
                     |            | (Cascade Level 1: 0x93|            |
                     |            +-----------------------+            |
                     |                        |                        |
                     |                        | UID not complete       |
                     |                        | (SAK Bit 2 = 1, CT=0x88|
                     |                        v                        |
                     |            +-----------------------+            |
                     |            |        READY 2        |            |
                     |            | (Cascade Level 2: 0x95|            |
                     |            +-----------------------+            |
                     |                        |                        |
                     |                        | Full UID Resolved      |
                     |                        | (SAK Bit 2 = 0)        |
                     |                        v                        |
                     |            +-----------------------+            |
                     |            |        ACTIVE         |            |
                     |            +-----------------------+            |
                     |                        |                        |
                     |       +----------------+----------------+       |
                     |       |                                 |       |
                     |       | SAK Bit 5 = 1                   | SAK Bit 5 = 0
                     |       | (ISO 14443-4 Compliant)         | (Proprietary / MIFARE)
                     |       v                                 v       |
                     |   +-----------------------+    +--------------+ |
                     |   |   PROTOCOL (T=CL)     |    | Memory Tag   | |
                     |   |   (RATS / APDU Exch)  |    | Auth / R/W   | |
                     |   +-----------------------+    +--------------+ |
                     |               |                       |         |
                     |               | HLTA (0x50 0x00)      |         |
                     |               +-----------+-----------+         |
                     |                           |                     |
                     |                           v                     |
                     |               +-----------------------+         |
                     +---------------|         HALT          |---------+
                       RF Reset /    +-----------------------+   WUPA (0x52)
                       Power Cycle                               Only!
```

---

## 2. RF Field Activation & Initial Guard Time ($T_{guard}$)

When an SPI host microcontroller commands the NFC transceiver to turn on its RF field (e.g. setting the `TxControlReg` in MFRC522 or executing `RFConfiguration` on PN532):

```text
Host MCU SPI: [Turn On RF Field]
RF Carrier:  ______/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                   |<- T_guard >= 5.0 ms (MANDATORY) ->|<-- First REQA Frame -->
Tag VDD:     ______/-------------------------------------\/\/\/\/\/\/\/\/\/\/\/\/\-
                   (Tag capacitor charging curve)
```

> [!IMPORTANT]
> **The 5.0 ms Guard Time Rule ($T_{guard}$)**:
> ISO/IEC 14443-3 Section 5.1 mandates a minimum delay of **$T_{guard} \ge 5.0\text{ ms}$** between RF field activation and the transmission of the first polling command (REQA/WUPA).
>
> **Why firmware fails if this is omitted**: A passive RFID/NFC tag contains an internal reservoir capacitor that must harvest energy from the unmodulated 13.56 MHz carrier, charge its internal power rails, and release its internal Power-On Reset (POR) circuit. If the host transmits a REQA before $5.0\text{ ms}$ has elapsed, the tag is unpowered and will not respond, leading to false "No Tag Found" errors.

---

## 3. The Polling Phase: REQA & WUPA (7-Bit Short Frames)

Polling begins with the reader transmitting a single-byte request frame:
- **REQA (`0x26` = `0010 0110b`)**: Request Command. Invokes tags that are currently in the **IDLE** state. Tags in the **HALT** state ignore REQA.
- **WUPA (`0x52` = `0101 0010b`)**: Wake-Up Command. Invokes all tags in the field, including tags that were explicitly placed into the **HALT** state by a previous transaction.

### 3.1 The 7-Bit Short Frame Mystery

In standard UART or SPI communication, all frames are multiples of 8 bits. In ISO/IEC 14443 Type A, however, **REQA and WUPA are transmitted as 7-bit unaligned short frames without CRC and without parity**:

```text
                  REQA SHORT FRAME (7 BITS, LSB FIRST)
              Bit 0   Bit 1   Bit 2   Bit 3   Bit 4   Bit 5   Bit 6
             +-------+-------+-------+-------+-------+-------+-------+
             |   0   |   1   |   1   |   0   |   0   |   1   |   0   |
             +-------+-------+-------+-------+-------+-------+-------+
             Value = 0x26 (Binary 0100110b, transmitted LSB first)
```

#### How the SPI Host Configures the Hardware Transceiver:
Because SPI controllers cannot shift 7 bits natively, the host programs the transceiver's internal **Bit Framing Engine**:
1. Host writes `0x26` to `FIFODataReg`.
2. Host writes `0x07` to `BitFramingReg` (setting `TxLastBits = 7`).
3. Host sets the `StartSend` bit.
4. The transceiver's digital state machine shifts out exactly 7 bits over the RF modulator, suppresses the parity bit, and waits for the tag's response.

### 3.2 ATQA (Answer to Request Type A)

Any tag present in the RF field responds to REQA/WUPA within exactly **$128\text{ etu}$ (Frame Delay Time, $FDT \approx 86.4\ \mu\text{s}$)** with a 2-byte **ATQA** frame (`b16` to `b1`):

```text
Byte 2 (High Byte)                  Byte 1 (Low Byte)
 b16 b15 b14 b13 b12 b11 b10  b9     b8  b7  b6  b5  b4  b3  b2  b1
+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+
| Proprietary Coding|  UID Size |   | 0 | 0 | 0 | Bit Frame Anti-Col|
+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+
```

- **UID Size Field (Bits `b8:b7`)**:
  - `00b`: **Single UID (4 bytes)** (e.g. MIFARE Classic 1K, older cards).
  - `01b`: **Double UID (7 bytes)** (e.g. NTAG213/215/216, MIFARE Ultralight, DESFire).
  - `10b`: **Triple UID (10 bytes)** (rare specialized smart cards).
- **Bit Frame Anti-Collision Field (Bits `b5:b1`)**:
  - Exactly one bit must be set to `1` (typically `00001b` = `0x01` or `00100b` = `0x04`) to signal support for the ISO 14443-3 bit-oriented anti-collision loop.

---

## 4. The Bit-Oriented Anti-Collision Loop (Cascade Levels 1–3)

When multiple cards are present in the reader's RF field, they all receive the REQA command and respond with their ATQA simultaneously. The reader must isolate each card's Unique Identifier (UID) without electrical contention.

```text
                  CASCADE ANTI-COLLISION COMMAND FRAME
 +--------+--------+----------------------------+--------+---------------+
 |  SEL   |  NVB   | UID Data Bytes (0 to 4 B)  |  BCC   | CRC_A (2 B)   |
 |  1 B   |  1 B   | (Known prefix bits)        |  1 B   | (Only if NVB=0x70)
 +--------+--------+----------------------------+--------+---------------+
```

### 4.1 Select Codes (SEL) and Cascade Levels

| Cascade Level | SEL Code | Target UID Segment |
| :--- | :--- | :--- |
| **Cascade Level 1 (CL1)** | `0x93` | Resolves Bytes `UID0`, `UID1`, `UID2`, `UID3` |
| **Cascade Level 2 (CL2)** | `0x95` | Resolves Bytes `UID4`, `UID5`, `UID6`, `UID7` |
| **Cascade Level 3 (CL3)** | `0x97` | Resolves Bytes `UID8`, `UID9`, `UID10`, `UID11` |

### 4.2 The NVB (Number of Valid Bits) Byte

The `NVB` byte communicates how many bits in the transmission are valid and driven by the reader:
$$\text{NVB} = (\text{Byte Count} \ll 4) \ | \ (\text{Bit Count})$$
- **High Nibble (`Bits 7:4`)**: Number of complete bytes transmitted by the reader (including `SEL` and `NVB` themselves). Minimum value is `2` (`SEL` + `NVB`).
- **Low Nibble (`Bits 3:0`)**: Number of additional fractional bits ($0\text{ to }7$).
- **`NVB = 0x20`**: Initiates anti-collision. Reader sends only `SEL` and `NVB` ($2\text{ bytes} = 16\text{ bits}$), requesting all cards to transmit their complete 40-bit UID segment.
- **`NVB = 0x70`**: Selection finalization. Reader transmits the complete 40 bits ($5\text{ bytes}$ of UID + BCC) plus a 2-byte `CRC_A`. Only the matching card answers with its **SAK**.

### 4.3 Hardware Collision Detection Mechanics

When two tags transmit differing bits at the exact same microsecond:
1. Tag A load-modulates a '0' (subcarrier pulse in first half of bit period).
2. Tag B load-modulates a '1' (subcarrier pulse in second half of bit period).
3. The reader's analog receiver sees subcarrier energy in **both** halves of the bit period, violating Manchester coding rules.
4. The transceiver's digital bit-framing engine detects this Manchester violation, asserts the **`CollErr`** interrupt flag, and logs the exact colliding bit position in the **`CollPos` register (0 to 31)**.

```text
Tag A:   ---\___/--- (Bit '0')
Tag B:   ___/---\___ (Bit '1')
Receiver: __/---\/--\_ (Collision Detected! Manchester violation at Bit K)
Transceiver asserts IRQ: CollErr = 1, CollPos = K
```

### 4.4 Step-by-Step Anti-Collision Walk Algorithm

1. Host sends `SEL = 0x93`, `NVB = 0x20`.
2. Cards respond with their UID bytes.
3. If no collision occurs (`CollErr == 0`): Host receives 4 UID bytes + 1 BCC byte. Host proceeds directly to Step 6.
4. If a collision occurs at bit $K$ (`CollErr == 1`, `CollPos = K`):
   - The reader chooses a branch (e.g. arbitrarily setting bit $K$ to `0` or `1`).
   - The reader updates its known prefix bits up to bit $K$.
   - The reader recalculates `NVB` (e.g., if collision occurred at bit 12: `NVB = 0x34`, meaning 3 whole bytes plus 4 bits).
   - Reader re-transmits `SEL` + `NVB` + `known bits`. Only cards whose UID matches the known prefix continue responding.
   - Repeat until all 32 bits of the current cascade level are isolated.
5. Once 40 bits are known, reader transmits `SEL = 0x93`, `NVB = 0x70`, `UID0..3`, `BCC`, and `CRC_A`.
6. The selected card responds with **SAK (Select Acknowledge)**.

### 4.5 The Cascade Tag (`CT = 0x88`)

For tags with Double UIDs (7 bytes) or Triple UIDs (10 bytes), the first byte returned at Cascade Level 1 is **`UID0 = 0x88` (Cascade Tag)**.
- When `UID0 == 0x88`, the reader knows this is not a true UID byte, but a marker indicating the UID continues to Cascade Level 2 (`SEL = 0x95`).

### 4.6 SAK (Select Acknowledge) Byte Decoding

The single SAK byte returned by the card reveals its architecture:

```text
 Bit 7   Bit 6   Bit 5   Bit 4   Bit 3   Bit 2   Bit 1   Bit 0
+-------+-------+-------+-------+-------+-------+-------+-------+
|   X   |   X   |   P   |   X   |   X   |   C   |   X   |   X   |
+-------+-------+-------+-------+-------+-------+-------+-------+
                    |                       |
                    |                       +---> Bit 2: Cascade Bit
                    |                             0 = UID complete
                    |                             1 = UID incomplete (proceed to CL2)
                    +---------------------------> Bit 5: Protocol Bit
                                                  0 = ISO/IEC 14443-3 only (Memory tag)
                                                  1 = ISO/IEC 14443-4 compliant (T=CL)
```

**Common SAK Values**:
- `SAK = 0x04`: UID incomplete (proceed to Cascade Level 2; Double UID tag like NTAG213 or Ultralight).
- `SAK = 0x00`: UID complete; MIFARE Ultralight / NTAG21x (ISO 14443-3 only).
- `SAK = 0x08`: UID complete; MIFARE Classic 1K (ISO 14443-3 proprietary Crypto1).
- `SAK = 0x18`: UID complete; MIFARE Classic 4K.
- `SAK = 0x20`: UID complete; **ISO/IEC 14443-4 compliant** (DESFire, Type 4 Tag, Android HCE).

---

## 5. ISO/IEC 14443-4 Protocol (T=CL Half-Duplex Block Transmission)

When a card signals ISO/IEC 14443-4 compliance (`SAK & 0x20 != 0`), the reader activates the **T=CL transmission protocol**.

```text
Reader (PCD)                                                    Card (PICC)
     |                                                               |
     |--- RATS (Request for Answer to Select: 0xE0 0x50 ...) ------->|
     |<-- ATS (Answer to Select: TL, T0, TA, TB, TC, Historical) ---|
     |                                                               |
     | [Optional: PPS (Protocol and Parameter Selection) for 848k] ->|
     |<-- PPS Response ----------------------------------------------|
     |                                                               |
     |--- I-Block (ISO 7816-4 APDU Command: SELECT AID) ------------>|
     |<-- I-Block (ISO 7816-4 APDU Response: 0x90 0x00 OK) ----------|
```

### 5.1 RATS Command & ATS Response

The host transmits **RATS** (`0xE0 | FSDI`):
- `FSDI` (Frame Size Device Integer): Declares the reader's maximum receive buffer ($0\text{ to }8$: $0 = 16\text{ B}, 5 = 64\text{ B}, 8 = 256\text{ B}$).

The card responds with **ATS (Answer to Select)**:
- **`TL`**: Total length of ATS.
- **`T0`**: Format byte containing `FSCI` (card's maximum receive buffer) and presence flags for interface bytes `TA(1)`, `TB(1)`, `TC(1)`.
- **`TA(1)`**: Transmission bitrates supported (106, 212, 424, 848 kbps asymmetric PCD $\leftrightarrow$ PICC).
- **`TB(1)`**: Frame Waiting Time Integer (`FWI`) and Start-up Frame Guard Time (`SFGI`).
- **`TC(1)`**: Frame options (NAD and CID support).
- **Historical Bytes**: Card operating system and ROM version info.

### 5.2 Frame Waiting Time (FWT) Calculation

The reader's timeout timer must be programmed according to the card's `FWI` in `TB(1)`:

$$FWT = \left( 256 \times 16 \times 2^{FWI} \right) \cdot \frac{1}{f_c} \approx \frac{4096 \times 2^{FWI}}{13.56 \times 10^6\text{ Hz}}$$

For standard $FWI = 4$:
$$FWT \approx \frac{4096 \times 16}{13.56 \times 10^6} \approx 4.83\text{ ms}$$

### 5.3 Half-Duplex Block Structures

All ISO 14443-4 frames consist of a Prologue, Information Payload (`INF`), and Epilogue (`CRC_A`):

```text
 +-------------------------------+-------------------------+---------------+
 |           PROLOGUE            |       INFORMATION       |   EPILOGUE    |
 | PCB (1 B) | CID (1 B) | NAD (1)|        INF (0 to N B)   |  CRC_A (2 B)  |
 +-------------------------------+-------------------------+---------------+
```

1. **I-Blocks (Information Blocks)**: Carry application data (APDUs).
   - PCB format: `0000 [Chaining] [CID_Present] [NAD_Present] [Block_Number]`.
2. **R-Blocks (Receive Ready / ACK / NACK)**: Report acknowledgment or request retransmission.
   - PCB format: `101 [ACK/NACK] [CID_Present] 0 [Block_Number]`.
3. **S-Blocks (Supervisory Blocks)**: Control exchange state:
   - **WTX (Waiting Time Extension)**: When the card is executing a heavy cryptographic operation (e.g. RSA-2048, ECC sign), it transmits an S-Block with WTX to extend the timeout, preventing reader disconnect.
   - **DESELECT**: Terminate the session cleanly.

---

## 6. ISO/IEC 7816-4 APDU Transport

Inside ISO 14443-4 I-Blocks, application data is structured as standard smart card **APDUs (Application Protocol Data Units)**:

### 6.1 Command APDU Structure

```text
 +-------+-------+-------+-------+-------+--------------------+-------+
 |  CLA  |  INS  |  P1   |  P2   |  Lc   |    Data Payload    |  Le   |
 | Class | Instr | Param | Param | Length|      Lc Bytes      | MaxRx |
 +-------+-------+-------+-------+-------+--------------------+-------+
```

- Example **SELECT AID** Command (Select NDEF Application `D2760000850101`):
  ```text
  00 A4 04 00 07 D2 76 00 00 85 01 01 00
  ```

### 6.2 Response APDU Structure

```text
 +-------------------------------------+-------+-------+
 |            Response Data            |  SW1  |  SW2  |
 |               N Bytes               |Status1|Status2|
 +-------------------------------------+-------+-------+
```

- **`SW1 SW2 = 0x90 0x00`**: Operation successful.
- **`SW1 SW2 = 0x6A 0x82`**: File not found.
- **`SW1 SW2 = 0x69 0x82`**: Security status not satisfied (authentication required).
