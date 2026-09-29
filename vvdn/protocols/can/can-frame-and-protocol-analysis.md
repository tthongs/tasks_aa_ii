# CAN Protocol: Frame Data & Protocol Analysis

## 1. Bit-Level CAN Frame Anatomy

CAN frames are tightly packed serial bitstreams designed for zero overhead and maximum fault detection. The CAN standard defines four fundamental frame types:
1. **Data Frame**: Carries real-time application data payload from transmitter to receivers.
2. **Remote Frame**: Transmitted by a node to solicit data from another node without transmitting data itself.
3. **Error Frame**: Driven by any node upon detecting an electrical, framing, or protocol violation.
4. **Overload Frame**: Used to request an internal delay between frames (rarely required in modern MCUs).

---

### 1.1 Classical CAN 2.0A Standard Data Frame (11-bit Identifier)

The Standard Data Frame consists of seven primary logical fields occupying between 44 and 108 bits (excluding bit stuffing):

```text
 ┌───┬─────────────┬─────┬─────┬────┬─────┬──────────────┬────────┬───┬─────┬───┬───────┬─────┐
 │SOF│ Identifier  │ RTR │ IDE │ r0 │ DLC │  Data Field  │ CRC-15 │CD │ ACK │AD │  EOF  │ IFS │
 ├───┼─────────────┼─────┼─────┼────┼─────┼──────────────┼────────┼───┼─────┼───┼───────┼─────┤
 │ 1 │   11 bits   │  1  │  1  │ 1  │  4  │  0 - 8 Bytes │15 bits │ 1 │  1  │ 1 │7 bits │3 bit│
 └───┴─────────────┴─────┴─────┴────┴─────┴──────────────┴────────┴───┴─────┴───┴───────┴─────┘
 |<---------------- Bit Stuffed Fields ---------------->|固定|<-- Unstuffed Fields -->|
```

#### Field-by-Field Breakdown:
1. **Start of Frame (SOF) — 1 bit**:
   - Single **Dominant ('0')** bit.
   - Falling edge synchronizes the internal baud rate clocks of all connected bus receivers (**Hard Synchronization**).
2. **Identifier (Arbitration Field) — 11 bits**:
   - Transmitted MSB first (`ID10` down to `ID0`).
   - Dictates frame content and bus access priority.
3. **Remote Transmission Request (RTR) — 1 bit**:
   - **Dominant ('0')**: Indicates a Data Frame carrying a payload.
   - **Recessive ('1')**: Indicates a Remote Frame requesting data.
4. **Identifier Extension (IDE) — 1 bit**:
   - **Dominant ('0')**: Standard CAN 2.0A (11-bit ID).
   - **Recessive ('1')**: Extended CAN 2.0B (29-bit ID).
5. **Reserved Bit (r0) — 1 bit**:
   - Always driven Dominant ('0') by the transmitter.
6. **Data Length Code (DLC) — 4 bits**:
   - Encodes payload length in bytes (0 to 8 bytes, `0000b` to `1000b`).
7. **Data Field — 0 to 64 bits (0 to 8 Bytes)**:
   - Payload data, transmitted byte-by-byte, MSB first within each byte.
8. **Cyclic Redundancy Check (CRC Field) — 16 bits**:
   - **CRC Sequence (15 bits)**: Generated via generator polynomial:
     $$P(x) = x^{15} + x^{14} + x^{10} + x^8 + x^7 + x^4 + x^3 + 1$$
   - **CRC Delimiter (1 bit)**: Always **Recessive ('1')**. Marks end of bit stuffing.
9. **Acknowledgment Field (ACK Field) — 2 bits**:
   - **ACK Slot (1 bit)**: Transmitter transmits a **Recessive ('1')** bit. Every node on the bus that received the frame without error forces this bit to **Dominant ('0')** on the wire.
   - **ACK Delimiter (1 bit)**: Always **Recessive ('1')**.
10. **End of Frame (EOF) — 7 bits**:
    - 7 consecutive **Recessive ('1')** bits.
11. **Interframe Space (IFS) — 3 bits minimum**:
    - Consists of **Intermission (ITM)**: 3 consecutive Recessive bits before a node may transmit again.

---

### 1.2 Extended CAN 2.0B Data Frame (29-bit Identifier)

To accommodate complex networks (such as commercial vehicles adhering to SAE J1939), CAN 2.0B expands the arbitration identifier from 11 bits to 29 bits.

```text
 ┌───┬─────────┬─────┬─────┬──────────┬─────┬────┬────┬─────┬──────────┬────────┬───┬─────┬───┬─────┐
 │SOF│Base ID  │ SRR │ IDE │ Ext ID   │ RTR │ r1 │ r0 │ DLC │   Data   │ CRC-15 │CD │ ACK │AD │ EOF │
 ├───┼─────────┼─────┼─────┼──────────┼─────┼────┼────┼─────┼──────────┼────────┼───┼─────┼───┼─────┤
 │ 1 │ 11 bits │  1  │  1  │ 18 bits  │  1  │ 1  │ 1  │  4  │ 0 - 8 B  │15 bits │ 1 │  1  │ 1 │  7  │
 └───┴─────────┴─────┴─────┴──────────┴─────┴────┴────┴─────┴──────────┴────────┴───┴─────┴───┴─────┘
```

- **Base Identifier (11 bits)**: Corresponds to standard ID bits `ID28` down to `ID18`.
- **Substitute Remote Request (SRR) — 1 bit**: Always driven **Recessive ('1')**. Ensures that if a Standard frame and an Extended frame share the same first 11 bits, the Standard frame (`RTR=0`) wins arbitration over the Extended frame (`SRR=1`).
- **Identifier Extension (IDE) — 1 bit**: Driven **Recessive ('1')** to signal an extended 29-bit format.
- **Extended Identifier (18 bits)**: Bits `ID17` down to `ID0`.
- **Total Identifier Space**: $2^{29} = 536,870,912$ unique IDs.

---

### 1.3 CAN FD (Flexible Data-rate) Frame Architecture

Standardized under **ISO 11898-1:2015**, CAN FD introduces two revolutionary enhancements:
1. **Payload Expansion**: Increases maximum payload from 8 bytes to **64 bytes**.
2. **Dual Bitrate (Bit Rate Switch - BRS)**: Switches to a higher clock rate (e.g., 2 Mbps to 5 Mbps) during the transmission of the data payload and CRC fields, reverting to the nominal bitrate (e.g., 500 kbps) for arbitration and ACK.

```text
              Arbitration Phase                          Data Phase (Fast Clock)                 Arbitration Phase
  ┌───┬────────────┬─────┬─────┬─────┬─────┬─────┬────┬─────────────────────┬──────────────┬────┬───┬───┬─────┐
  │SOF│ Identifier │ RRS │ IDE │ FDF │ res │ BRS │ESI │ DLC (0-15 = 0-64 B) │ Data (0-64B) │CRC │CD │ACK│AD │ EOF │
  └───┴────────────┴─────┴─────┴─────┴─────┴─────┴────┴─────────────────────┴──────────────┴────┴───┴───┴─────┘
  |<---- Nominal Bitrate (e.g., 500 kbps) ------->|<---- Fast Bitrate (e.g., 2.0 - 5.0 Mbps) ------>|<-- Nom. -->|
```

#### New CAN FD Control Bits:
- **FDF / EDL (Extended Data Length) — 1 bit**: Driven **Recessive ('1')** to designate a CAN FD frame (Classical CAN nodes see this as dominant reserve bit `r0` and flag a form error; hence, classical nodes cannot coexist on a CAN FD bus without FD-tolerant transceivers).
- **BRS (Bit Rate Switch) — 1 bit**:
  - **Recessive ('1')**: The transmission clock switches to the high-speed data phase bitrate at the BRS sample point.
  - **Dominant ('0')**: The frame remains at the nominal arbitration bitrate throughout.
- **ESI (Error State Indicator) — 1 bit**:
  - Driven Dominant ('0') if the transmitting node is in **Error Active** mode.
  - Driven Recessive ('1') if the node is in **Error Passive** mode.

#### CAN FD DLC Encoding Table:
Unlike Classical CAN where DLC directly matches byte count, CAN FD uses non-linear mapping for values above 8:

| DLC Code (Binary) | Classical CAN Payload | CAN FD Payload |
| :--- | :--- | :--- |
| `0000b` – `1000b` ($0 - 8$) | $0 - 8$ Bytes | $0 - 8$ Bytes |
| `1001b` ($9$) | 8 Bytes | **12 Bytes** |
| `1010b` ($10$) | 8 Bytes | **16 Bytes** |
| `1011b` ($11$) | 8 Bytes | **20 Bytes** |
| `1100b` ($12$) | 8 Bytes | **24 Bytes** |
| `1101b` ($13$) | 8 Bytes | **32 Bytes** |
| `1110b` ($14$) | 8 Bytes | **48 Bytes** |
| `1111b` ($15$) | 8 Bytes | **64 Bytes** |

---

## 2. Bit Stuffing Algorithm & Verification

To ensure continuous synchronization of all receiver bit clocks across long sequences of static bits (such as consecutive zeros in an empty payload or identifier), CAN enforces **Bit Stuffing**.

### 2.1 The Bit Stuffing Rule
- Whenever the transmitter hardware detects **5 consecutive bits of identical polarity** (five '0's or five '1's) within the bit-stuffed zone, it **automatically inserts a complementary stuff bit** of the opposite polarity.
- The receiver hardware detects the 5 identical bits, extracts and discards the 6th stuff bit, and reconstructs the original un-stuffed payload.
- **Stuffed Zone**: Starts at the **Start of Frame (SOF)** and ends at the last bit of the **CRC Sequence**.
- **Fixed/Un-stuffed Zone**: The CRC Delimiter, ACK Slot, ACK Delimiter, and EOF fields are fixed form and never stuffed.

```text
Transmitted Raw Data:   1  1  1  1  1  0  0  0  0  0  1
Line After Stuffing:    1  1  1  1  1 [0] 0  0  0  0 [1] 0  1
                                      ^^^            ^^^
                                   Stuff Bit      Stuff Bit
```

### 2.2 Worst-Case Frame Length Formula
In Classical CAN 2.0A with an 8-byte payload:
- Nominal bits = $1\,(\text{SOF}) + 11\,(\text{ID}) + 1\,(\text{RTR}) + 1\,(\text{IDE}) + 1\,(\text{r0}) + 4\,(\text{DLC}) + 64\,(\text{Data}) + 15\,(\text{CRC}) + 1\,(\text{CD}) + 2\,(\text{ACK}) + 7\,(\text{EOF}) + 3\,(\text{IFS}) = 111\,\text{bits}$.
- Bit-stuffed portion = $1 + 11 + 1 + 1 + 1 + 4 + 64 + 15 = 97\,\text{bits}$.
- Theoretical maximum stuff bits:
  $$\text{Max Stuff Bits} = \left\lfloor \frac{97 - 1}{4} \right\rfloor = 24\,\text{bits}$$
- **Absolute Worst-Case Frame Length**:
  $$\text{Total Bits}_{max} = 111 + 24 = 135\,\text{bits}$$

---

## 3. Higher-Layer Automotive Protocol Frameworks

Classical CAN provides only Data Link Layer framing (OSI Layers 1 & 2). Real-world automotive and industrial systems build on standardized higher-layer protocols:

```text
 ┌────────────────────────────────────────────────────────┐
 │           OSI Layer 7: Application Layer               │
 │    SAE J1939 (Heavy Duty) │ CANopen │ UDS (ISO 14229)  │
 ├────────────────────────────────────────────────────────┤
 │     OSI Layer 3/4: Network & Transport Layer           │
 │       J1939-21 (TP BAM/CM) │ ISO 15765-2 (DoCAN TP)    │
 ├────────────────────────────────────────────────────────┤
 │           OSI Layer 2: Data Link Layer                 │
 │             CAN 2.0A/B & CAN FD (ISO 11898-1)          │
 ├────────────────────────────────────────────────────────┤
 │           OSI Layer 1: Physical Layer                  │
 │          Differential Transceiver (ISO 11898-2)        │
 └────────────────────────────────────────────────────────┘
```

### 3.1 SAE J1939 (Commercial Vehicles & Heavy Duty)

Used across trucks, buses, diesel generators, and marine engines, SAE J1939 utilizes the 29-bit CAN Identifier to structure a complete network addressing framework:

```text
 ┌──────────┬─────┬───────────┬────────────┬────────────────────────┬────────────────┐
 │ Priority │ Res │ Data Page │ PDU Format │ PDU Specific (DA or GE)│ Source Address │
 ├──────────┼─────┼───────────┼────────────┼────────────────────────┼────────────────┤
 │  3 bits  │  1  │   1 bit   │   8 bits   │         8 bits         │     8 bits     │
 └──────────┴─────┴───────────┴────────────┴────────────────────────┴────────────────┘
 |<---------------------- Parameter Group Number (PGN, 18 bits) ------------------------>|
```

- **PGN (Parameter Group Number)**: 18-bit identifier indexing standard vehicle messages (e.g., PGN `61444` / `0xF004` = Electronic Engine Controller 1, containing Engine Speed).
- **SPN (Suspect Parameter Number)**: Specific sensor or actuator variable embedded within a PGN (e.g., SPN `190` = Engine Speed, resolution $0.125\,\text{rpm/bit}$).
- **Transport Protocol (TP)**: Breaks payloads larger than 8 bytes (up to 1,785 bytes) into multiple frames using **BAM (Broadcast Announce Message)** or **RTS/CTS connection-mode**.

---

### 3.2 UDS (ISO 14229) over CAN (ISO 15765-2 / DoCAN)

Unified Diagnostic Services (UDS) is the universal automotive standard for flashing firmware, reading diagnostic trouble codes (DTCs), and calibrating ECU sensors. Because diagnostic payloads often exceed 8 bytes, **ISO 15765-2 (CAN-TP)** segments messages:

| Frame Type | PCI Nibble | Description |
| :--- | :--- | :--- |
| **Single Frame (SF)** | `0x0_` | Payload fits in 1 to 7 bytes within a single CAN frame. |
| **First Frame (FF)** | `0x1_` | Initiates multi-frame transfer; encodes total 12-bit payload length ($L \le 4095$ bytes). |
| **Consecutive Frame (CF)**| `0x2_` | Carries subsequent data chunks with a 4-bit rolling Sequence Number ($0 \dots 15$). |
| **Flow Control (FC)** | `0x3_` | Sent by receiver to regulate pacing; sets **Block Size (BS)** and **Separation Time ($ST_{min}$)**. |

---

## 4. Logic Analyzer Trace Walkthrough & Linux SocketCAN

### 4.1 Oscilloscope / Logic Analyzer Decoded Waveform

The following timing diagram illustrates a logic analyzer decode of an 11-bit Standard Data Frame transmitting ID `0x123`, DLC `2`, and payload `0xAA 0x55`:

```text
Line State:
           SOF  [    ID = 0x123     ] RTR IDE r0 DLC [ Byte 0 ] [ Byte 1 ]  [ CRC15 ] CD ACK AD [  EOF  ]
CAN_H:  ───┐    ┌──┐  ┌──┐  ┌──┐      ┌──┐        ┌──┬──┬──┐    ┌──┬──┐       ┌──┐     ┌─┐     ┌─┐ ───────
           │    │  │  │  │  │  │      │  │        │  │  │  │    │  │  │       │  │     │ │     │ │
CAN_L:  ───┴────┴──┴──┴──┴──┴──┴──────┴──┴────────┴──┴──┴──┴────┴──┴──┴───────┴──┴─────┴─┴─────┴─┴───────
Values:     0    0  0  1  0  0  1  0  0  0   0   0  0010  10101010  01010101   0x3A21   1  0   1   1111111
Bit Type:  DOM  <--- Arbitration ---> DOM DOM DOM 2Byte  0xAA       0x55       CRC      REC DOM REC End-of-frame
```

---

### 4.2 Linux SocketCAN Application Architecture

Linux integrates CAN directly into the networking subsystem (`AF_CAN`). CAN interfaces are treated like network interfaces (`eth0`, `can0`), allowing standard POSIX socket APIs:

```c
/* socketcan_tx.c - Production SocketCAN Transmit Example */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>

int main(void) {
    int s;
    struct sockaddr_can addr;
    struct ifreq ifr;
    struct can_frame frame;

    /* 1. Open Raw CAN Socket */
    if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
        perror("Socket creation failed");
        return 1;
    }

    /* 2. Bind to can0 interface */
    strcpy(ifr.ifr_name, "can0");
    ioctl(s, SIOCGIFINDEX, &ifr);
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    bind(s, (struct sockaddr *)&addr, sizeof(addr));

    /* 3. Construct Standard 11-bit Frame */
    frame.can_id = 0x123;
    frame.can_dlc = 4;
    frame.data[0] = 0xDE;
    frame.data[1] = 0xAD;
    frame.data[2] = 0xBE;
    frame.data[3] = 0xEF;

    /* 4. Transmit frame over physical bus */
    if (write(s, &frame, sizeof(struct can_frame)) != sizeof(struct can_frame)) {
        perror("CAN write error");
        close(s);
        return 1;
    }

    printf("CAN frame 0x123 sent successfully on can0.\n");
    close(s);
    return 0;
}
```

```bash
# Bring up can0 with 500 kbps nominal and 2 Mbps data bitrate on Linux
sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on
sudo ip link set can0 up

# Monitor traffic in real time with timestamping
candump -tz can0

# Inject diagnostic frame
cansend can0 7DF#0201050000000000
```
