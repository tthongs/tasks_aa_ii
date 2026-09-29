# LIN Protocol: Frame Data & Protocol Analysis

## 1. Bit-Level Anatomy of a LIN Frame

A complete LIN communication transaction is termed a **Frame**. Every LIN frame is strictly divided into two logical sections:
1. **Frame Header**: Generated and transmitted exclusively by the **Master Node**.
2. **Frame Response**: Generated and transmitted by a designated **Slave Node** (or by the Master itself when broadcasting commands).

```text
 |<------------------- Master Header ------------------>|<----------------- Slave Response ----------------->|
 ┌──────────────────────┬─────────────┬─────────────────┬────────────────┬────────────────┬─────────────────┐
 │   Synch Break Field  │ Synch Byte  │  Protected ID   │  Data Byte 1   │  Data Byte N   │  Checksum Byte  │
 ├──────────┬───────────┼─────────────┼─────────────────┼────────────────┼────────────────┼─────────────────┤
 │ Dominant │ Delimiter │    0x55     │  6-bit ID + 2P  │ 1 Start, 8 Data│ 1 Start, 8 Data│ 1 Start, 8 Data │
 │ >= 13 b  │ >= 1 bit  │ 8-N-1 UART  │   8-N-1 UART    │   1 Stop bit   │   1 Stop bit   │   1 Stop bit    │
 └──────────┴───────────┴─────────────┴─────────────────┴────────────────┴────────────────┴─────────────────┘
 |                      |<------- Inter-byte Space ---->|<------- Inter-byte Space ------>|
```

---

### 1.1 The Master Header Components

#### A. Synch Break Field (Break)
- **Dominant Period**: The Master holds the bus Dominant for a minimum of **13 bit periods** (typically $13 \dots 26$ bit times). Because standard UART bytes cannot hold a zero longer than 9 or 10 bit times (Start + 8 data zeros before the mandatory Stop bit), a $\ge 13$-bit dominant pulse is a deliberate framing violation that alerts every slave that a new frame has commenced.
- **Break Delimiter**: Immediately follows the dominant break with at least **1 bit period of Recessive ('1')**.

#### B. Synch Byte Field
- Transmitted as a standard 8-N-1 UART character with value **`0x55`** (`01010101b`).
- In UART transmission (LSB first with a dominant Start bit and recessive Stop bit), `0x55` generates **5 identical falling edges**:

```text
 UART Line:  Idle ──┐  0  ┌── 1  ┌── 0  ┌── 1  ┌── 0  ┌── 1  ┌── 0  ┌── 1  ┌── Stop (1)
                    │     │     │     │     │     │     │     │     │     │
 Falling Edges:     └──1──┘     └──2──┘     └──3──┘     └──4──┘     └──5──┘
                    |<----------------- Exactly 8 Bit Periods ---------------->|
```

- **Dynamic Auto-Baud**: Slaves measure the precise elapsed time between Edge 1 (falling edge of the Start bit) and Edge 5 (falling edge of bit 7). Dividing this interval by 8 yields the Master's exact bit period ($T_{bit}$), allowing slaves with cheap RC oscillators to lock their baud rates!

---

#### C. Protected Identifier (PID) Field

The PID is an 8-bit byte containing a **6-bit Frame Identifier (`ID0` to `ID5`)** and **2 Parity Bits (`P0`, `P1`)**:

```text
 Bit:    7     6     5     4     3     2     1     0
      ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
      │ P1  │ P0  │ ID5 │ ID4 │ ID3 │ ID2 │ ID1 │ ID0 │
      └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
      |<-- Parity ->|<----------- 6-bit ID ------------>|
```

#### Parity Calculation Equations:
- **Parity Bit 0 ($P0$)** is an **even parity** over bits 0, 1, 2, and 4:
  $$P0 = ID0 \oplus ID1 \oplus ID2 \oplus ID4$$
- **Parity Bit 1 ($P1$)** is an **inverted odd parity** over bits 1, 3, 4, and 5:
  $$P1 = \overline{ID1 \oplus ID3 \oplus ID4 \oplus ID5} = 1 \oplus (ID1 \oplus ID3 \oplus ID4 \oplus ID5)$$

```c
/* C Implementation of LIN PID Parity Generation */
uint8_t lin_calculate_pid(uint8_t raw_id) {
    uint8_t id = raw_id & 0x3F;
    uint8_t id0 = (id >> 0) & 1;
    uint8_t id1 = (id >> 1) & 1;
    uint8_t id2 = (id >> 2) & 1;
    uint8_t id3 = (id >> 3) & 1;
    uint8_t id4 = (id >> 4) & 1;
    uint8_t id5 = (id >> 5) & 1;

    uint8_t p0 = id0 ^ id1 ^ id2 ^ id4;
    uint8_t p1 = !(id1 ^ id3 ^ id4 ^ id5);

    return (uint8_t)((p1 << 7) | (p0 << 6) | id);
}
```

> [!NOTE]
> The parity bits guarantee that all 1-bit bit errors in the identifier are detected and 2-bit bit errors cannot result in a false PID match.

---

### 1.2 LIN 64-Identifier Allocation Map

The 6-bit identifier yields 64 total values ($0x00 \dots 0x3F$), strictly cataloged by the LIN specification:

| Raw ID Range | PID Values | Frame Type / Designation | Usage & Characteristics |
| :--- | :--- | :--- | :--- |
| **`0x00` – `0x3B`** ($0 - 59$) | `0x00` – `0xBB` | **Unconditional Frames** | Carries normal real-time sensor/actuator payload ($1 \dots 8$ bytes). |
| **`0x3C`** ($60$) | **`0x3C`** ($P0=0, P1=0$) | **Master Request Frame** | Carries diagnostic commands, node configuration, and sleep requests from Master. Always uses Classic Checksum. |
| **`0x3D`** ($61$) | **`0x7D`** ($P0=1, P1=0$) | **Slave Response Frame** | Designated slave transmits diagnostic telemetry or EOL configuration responses. Always uses Classic Checksum. |
| **`0x3E`** ($62$) | **`0xFE`** ($P0=1, P1=1$) | **User-Defined Extension** | OEM-specific proprietary test harness frame. |
| **`0x3F`** ($63$) | **`0xBF`** ($P0=0, P1=1$) | **Reserved** | Reserved for future protocol enhancements. |

---

## 2. Slave Response & Checksum Mathematics

The response consists of **1 to 8 Data Bytes** followed by an **8-bit Checksum**. Data is transmitted LSB first in standard UART bytes (1 Start bit, 8 Data bits, 1 Stop bit).

### 2.1 Classic vs. Enhanced Checksum Algorithms

| Checksum Type | Specification | Included Fields | Used By |
| :--- | :--- | :--- | :--- |
| **Classic Checksum** | **LIN 1.3** | Inverted 8-bit sum of **Data Bytes ONLY** | Legacy LIN 1.3 slaves, and **Diagnostic Frames (`0x3C`, `0x3D`)** in all versions. |
| **Enhanced Checksum** | **LIN 2.x & ISO 17987** | Inverted 8-bit sum of **PID + Data Bytes** | Modern LIN 2.x / ISO 17987 unconditional and sporadic frames. |

### 2.2 Mathematical Algorithm (One's Complement Carry Addition)

The checksum algorithm performs an 8-bit modulo-256 addition where every overflow carry bit is immediately added back into the least significant bit (known as an **end-around carry** or one's complement sum):

$$\text{Sum} = \text{PID (if Enhanced)} + \sum_{i=1}^{N} \text{Data}_i + \text{Carries}$$
$$\text{Checksum} = \neg (\text{Sum} \ \& \ \text{0xFF}) = (\sim\text{Sum}) \ \& \ \text{0xFF}$$

#### Verification at Receiver:
Adding the received checksum to the calculated sum must equal **`0xFF`**:
$$\text{Sum} + \text{Received\_Checksum} = 0\text{xFF}$$

```c
/* Production-Grade LIN Checksum Implementation in C */
uint8_t lin_calculate_checksum(uint8_t pid, const uint8_t *data, uint8_t length, bool is_classic) {
    uint16_t sum = 0;

    /* Enhanced checksum includes PID; Classic does not */
    if (!is_classic) {
        sum += pid;
    }

    for (uint8_t i = 0; i < length; i++) {
        sum += data[i];
        /* If 8-bit overflow occurred, wrap carry into LSB */
        if (sum > 0xFF) {
            sum = (sum & 0xFF) + 1;
        }
    }

    /* Bitwise NOT (one's complement inversion) */
    return (uint8_t)(~sum & 0xFF);
}
```

---

## 3. LIN Communication Frame Types

1. **Unconditional Frames**:
   - The standard communication vehicle. The Master sends a header with PID $0x00 \dots 0x3B$. The designated slave (or master) immediately responds in the same time slot.
2. **Event-Triggered Frames**:
   - Allows multiple slave nodes to share a single scheduled time slot to report infrequent events (e.g., any door lock status changing).
   - If only one slave responds, the Master receives the frame normally.
   - If two slaves respond simultaneously, their data collides on the wire, resulting in a **Checksum Error**.
   - The Master detects the checksum mismatch and automatically invokes a **Collision-Resolving Schedule Table**, polling each participating slave individually via unconditional frames.
3. **Sporadic Frames**:
   - Slots reserved by the Master for frames that are only transmitted when new data is available. If no update exists, the slot remains empty/idle.
4. **Diagnostic Frames (`0x3C` & `0x3D`)**:
   - Carries ISO 14229 UDS or node configuration payloads using the **LIN Transport Layer (LIN TP)**.

---

## 4. LIN Transport Layer (LIN TP / ISO 17987-2)

When diagnostic or calibration data exceeds 8 bytes, the LIN Transport Layer segments the payload across multiple consecutive frames using a **Protocol Control Information (PCI)** byte:

```text
 ┌──────────┬──────────┬──────────┬──────────┬────────────────────────────┐
 │   NAD    │   PCI    │  SID /   │  Param 1 │          Param N           │
 │ (1 Byte) │ (1 Byte) │ D1 Byte  │ (1 Byte) │         (4 Bytes)          │
 └──────────┴──────────┴──────────┴──────────┴────────────────────────────┘
```

- **Single Frame (SF)**: PCI byte `0x01` to `0x06` indicates payload fits in 1 to 6 bytes.
- **First Frame (FF)**: PCI byte `0x1_` indicates the start of a multi-frame transfer, encoding total byte length.
- **Consecutive Frame (CF)**: PCI byte `0x2_` carries subsequent data segments with a rolling sequence counter.

---

## 5. Oscilloscope / Logic Analyzer Waveform Walkthrough

The following trace illustrates a captured LIN frame transmitting PID `0xA3` (raw ID `0x23`), payload `[0x01, 0x02]`, and Enhanced Checksum `0x59`:

```text
Line State:
           |<- Break (>=13b) ->| Delim |<--- Sync (0x55) --->|   |<--- PID (0xA3) ---->|   |<-- Data 0x01 -->|  |<-- Chk 0x59 -->|
12V (VBAT):──────┐             ┌───────┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌───┐   ┌───┐   ┌─┐ ┌─────────┐   ┌───┐             ┌──┐ ┌─┐ ┌───┐ ┌───
                 │             │       │ │ │ │ │ │ │ │ │ │   │   │   │   │ │ │         │   │   │             │  │ │ │ │   │ │
GND (0V):        └─────────────┘       └─┴─┴─┴─┴─┴─┴─┴─┴─┘   └───┘   └───┴─┴─┘         └───┘   └─────────────┴──┴─┴─┴─┘   └─┴───
Bits:            0000000000000    1     0 1 0 1 0 1 0 1 0 1   0   11000101 (0xA3)   1   0   10000000   1   0  10011010  1
Fields:          Dominant Break   Delim  Start, 0x55,    Stop  St.   P1 P0 ID5..ID0   Stop St.   0x01      Stop St. 0x59     Stop
Decoded:         [ BREAK FIELD ]        [ SYNCHRONIZATION ]   [ PROTECTED IDENTIFIER]  [ PAYLOAD BYTE 1 ] [ ENHANCED CHKSUM ]
```

---

## 6. Microcontroller Firmware Implementation (UART Driver)

Standard microcontrollers (STM32, NXP S32K, Microchip AVR/PIC) utilize hardware UART/USART peripherals configured for LIN mode:

```c
/* stm32_lin_master.c - Transmitting a LIN Frame Header using Hardware UART */
#include "stm32f4xx_hal.h"

extern UART_HandleTypeDef huart1;

void LIN_Master_SendHeader(uint8_t lin_id) {
    uint8_t sync_byte = 0x55;
    uint8_t pid = lin_calculate_pid(lin_id);

    /* 1. Request Hardware LIN Break Transmission (generates 13-bit dominant break) */
    HAL_LIN_SendBreak(&huart1);

    /* 2. Transmit Sync Byte (0x55) */
    HAL_UART_Transmit(&huart1, &sync_byte, 1, 10);

    /* 3. Transmit Protected Identifier (PID) */
    HAL_UART_Transmit(&huart1, &pid, 1, 10);

    /* Master header complete. Designated slave now responds on the bus. */
}
```
