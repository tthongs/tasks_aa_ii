# I2C Data Frame Anatomy, Packet Sequences & Protocol Decoding

This document provides an exhaustive, bit-level breakdown of **I2C Data Frames, Packet Structures, and Protocol Decoding**. It covers the fundamental framing conditions (START, STOP, Repeated START), the 9-bit transmission unit, 7-bit and 10-bit addressing frames, ACK/NACK signaling rules, reserved address maps, standard transaction archetypes, and logic analyzer frame decoding.

---

## 1. Bit-Level Framing Conditions

In I2C, control signaling (START, STOP, and Repeated START) and data transfers occur on the exact same two wires (**SDA** and **SCL**). Hardware state machines distinguish between control commands and data bits using the **Data Validity Rule**.

### 1.1 The Data Validity Rule

During standard data byte and address transmission:
- **SDA must remain static and stable** whenever **SCL is HIGH**.
- **SDA state changes** are only permitted when **SCL is LOW**.

```text
SCL:      ──────┐               ┌───────────────┐               ┌──────
                │               │               │               │
                └───────────────┘               └───────────────┘
                                ▲               ▲
                                │  DATA VALID   │
                                └───────────────┘
                                 (Must Not Change)
                 ┌───────────────┐
SDA:      ───────┼───────────────┼───────────────────────────────
                 │ Changes only  │
                 │ when SCL=LOW  │
                 └───────────────┘
```

If the SDA line toggles while SCL is HIGH, the physical layer interprets this as an asynchronous **Framing Control Event** (START or STOP).

---

### 1.2 START Condition ($S$)

A **START condition** signals to all peripherals that a controller is taking control of the bus to begin a transaction.

- **Definition**: A **HIGH-to-LOW transition on SDA** while **SCL remains HIGH**.
- Initiated exclusively by the Controller.
- The bus is considered **BUSY** immediately after a START condition.

```text
SCL:      ────────────────────────┐
                                  │
                                  └───────────
SDA:      ────────┐
                  │
                  └───────────────────────────
                  ▲
                  │ START (S) Condition
```

---

### 1.3 STOP Condition ($P$)

A **STOP condition** terminates a transaction and releases the bus back to the IDLE state.

- **Definition**: A **LOW-to-HIGH transition on SDA** while **SCL remains HIGH**.
- Initiated exclusively by the Controller.
- The bus is considered **FREE (IDLE)** after the bus free time ($t_{BUF}$) following a STOP condition.

```text
SCL:      ────────────────────────┐
                                  │
          ────────────────────────┘
SDA:                              ┌───────────
                                  │
          ────────────────────────┘
                                  ▲
                                  │ STOP (P) Condition
```

---

### 1.4 REPEATED START Condition ($S_r$)

A **REPEATED START condition** (denoted as **$S_r$**) occurs when a controller generates a new START condition without first releasing the bus with a STOP condition.

```text
SCL:   ───┐   ┌───┐   ┌───────┐       ┌───┐
          └───┘   └───┘       │       │   └───
            ACK / NACK        │       │
                              ▼       ▼
SDA:   ───────────────┐       ┌───────┐
                      └───────┘       └───────
                              ▲
                              │ Repeated START (Sr)
                              (SDA falls while SCL is HIGH)
```

#### Why Repeated START is Essential:
1. **Multi-Master Atomicity**: In a multi-controller environment, issuing a STOP condition surrenders bus ownership. Another controller could seize the bus before the original controller finishes a sequence. A Repeated START retains exclusive bus control across multiple operations.
2. **Direction Turnaround (Write then Read)**: Most I2C peripherals (e.g., sensors, RTCs, EEPROMs) require the controller to first write the internal register address, then read the data from that register. Using a Repeated START allows seamless switching from Controller-Transmitter to Controller-Receiver without a bus-release gap.
3. **Target Switching**: Allows the controller to address a completely different target chip without freeing the bus to other potential masters.

---

## 2. The 9-Bit Transmission Unit (Byte + ACK/NACK)

Every byte transferred on the I2C bus consists of **9 SCL clock pulses**:
- **Bits 1 to 8**: 8 bits of payload data (transferred **MSB first**).
- **Bit 9**: 1 bit of in-band **Acknowledgement (ACK / NACK)**.

```text
SCL:   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐
     ──┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───
         1       2       3       4       5       6       7       8       9
        MSB     Bit 6   Bit 5   Bit 4   Bit 3   Bit 2   Bit 1   LSB     ACK/NACK
                                                                          │
SDA:  ──[ B7 ]───[ B6 ]───[ B5 ]───[ B4 ]───[ B3 ]───[ B2 ]───[ B1 ]───[ B0 ]───[ A/N ]
        ◄──────────────────── 8 Data Bits ─────────────────────► ◄─ 1-Bit ─►
```

### 2.1 The ACK (Acknowledge) Mechanism
- During the 9th clock pulse, the **transmitter releases the SDA line** (allowing it to float HIGH).
- The **receiver pulls SDA LOW** and holds it LOW during the entire HIGH period of the 9th SCL clock pulse.
- When the transmitter samples SDA during the 9th clock pulse and reads **LOW ($0\,\text{V}$)**, an **ACK (0)** is registered.

### 2.2 The NACK (Not-Acknowledge) Mechanism
- The transmitter releases SDA during the 9th clock cycle.
- The receiver **leaves SDA HIGH** (does not pull it LOW).
- When the transmitter samples SDA and reads **HIGH ($V_{DD}$)**, a **NACK (1)** is registered.

### 2.3 Summary of NACK Scenarios

| Scenario | Transmitter | Receiver | Reason for NACK | Controller Recovery Action |
| :--- | :--- | :--- | :--- | :--- |
| **No Device at Address** | Controller | Target | No peripheral matches the 7-bit address; bus pull-up keeps SDA HIGH. | Issue STOP ($P$) and report `ENODEV` (Device Not Found). |
| **Target Device Busy** | Controller | Target | Target is executing internal write cycle (e.g. EEPROM programming) and cannot process incoming commands. | Issue STOP ($P$) or Repeated START ($S_r$) and retry after a short delay (ACK polling). |
| **Target Buffer Full** | Controller | Target | Target's internal FIFO or memory buffer is full. Cannot accept more data bytes. | Issue STOP ($P$) and re-transmit remaining bytes after target drains buffer. |
| **Invalid Command/Data**| Controller | Target | Target received an unrecognized opcode or out-of-range register offset. | Issue STOP ($P$) and log firmware error. |
| **End of Master Read**  | Target | Controller | **Normal Protocol Flow**: Controller has received the last requested byte and deliberately sends NACK to target. | Controller follows the NACK with a STOP ($P$) to terminate the read stream cleanly. |

---

## 3. 7-Bit Address Frame Anatomy

Following a START condition, the controller MUST transmit an **Address Byte**. In standard 7-bit addressing, the address byte is formatted as follows:

```text
Bit:    7       6       5       4       3       2       1       0
    ┌───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┐
    │  A6   │  A5   │  A4   │  A3   │  A2   │  A1   │  A0   │ R/W#  │
    └───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘
    ◄────────────── 7-Bit Target Address ───────────────►   ▲
                                                            │
                                            0 = Write (Master Transmits)
                                            1 = Read  (Master Receives)
```

- **Bits [7:1]**: The unique 7-bit physical hardware address of the target device ($0\text{x}00\text{ to }0\text{x}7\text{F}$).
- **Bit [0]**: The **R/W# Direction Bit**:
  - `0` (**Write**): The controller will transmit subsequent data bytes to the target.
  - `1` (**Read**): The controller will receive subsequent data bytes from the target.

### 3.1 The "7-Bit vs. 8-Bit Address" Firmware Trap

One of the most frequent sources of driver bugs in embedded systems is confusing a pure **7-bit address** with the **8-bit wire byte**:

```text
Example Device: Microchip 24LC256 EEPROM (Hardware Address = 0x50 / 0b1010000)

Pure 7-bit Address:               0b 1 0 1 0 0 0 0           = 0x50

8-bit Write Byte (Address << 1 | 0): 0b 1 0 1 0 0 0 0 0      = 0xA0
8-bit Read Byte  (Address << 1 | 1): 0b 1 0 1 0 0 0 0 1      = 0xA1
```

> [!WARNING]
> **API Differences**:
> - **Linux I2C Subsystem (`i2c-dev`) & Arduino (`Wire.beginTransmission`)**: Expect the **pure 7-bit address** (e.g., `0x50`). The kernel/library driver shifts the address left by 1 bit and appends the R/W bit automatically.
> - **STM32 HAL (`HAL_I2C_Master_Transmit`)**: Expects the **pre-shifted 8-bit address** (e.g., `0xA0` or `0x50 << 1`). Passing `0x50` directly will cause the HAL to transmit address `0x28`, resulting in an immediate NACK!

---

## 4. 10-Bit Addressing Protocol Frame

To accommodate systems with more than 120 devices, the I2C specification provides an optional **10-bit addressing mode**. 10-bit addressing is completely backward-compatible with 7-bit devices on the same bus.

A 10-bit address consists of two consecutive address header bytes:

```text
First Address Byte:
Bit:    7   6   5   4   3    2    1     0
      ┌───┬───┬───┬───┬───┬────┬────┬───────┐
      │ 1 │ 1 │ 1 │ 1 │ 0 │ A9 │ A8 │ R/W#  │  (Prefix 11110 + Upper 2 bits of 10-bit addr)
      └───┴───┴───┴───┴───┴────┴────┴───────┘

Second Address Byte:
Bit:    7    6    5    4    3    2    1    0
      ┌────┬────┬────┬────┬────┬────┬────┬────┐
      │ A7 │ A6 │ A5 │ A4 │ A3 │ A2 │ A1 │ A0 │  (Lower 8 bits of 10-bit addr)
      └────┴────┴────┴────┴────┴────┴────┴────┘
```

### 4.1 10-Bit Write Transaction Flow
1. Controller sends START ($S$).
2. Controller sends First Byte: `1111 0` + `A9:A8` + `R/W# = 0` (Write).
3. All targets with matching $A9:A8$ acknowledge with ACK.
4. Controller sends Second Byte: `A7:A0`.
5. Only the specific target matching the full 10-bit address acknowledges with ACK.
6. Controller transmits payload data bytes as normal.
7. Controller terminates with STOP ($P$).

```text
┌───┬───────────────────┬───┬───────────────────┬───┬──────────────┬───┬───┐
│ S │ 1111 0 A9 A8 [W]  │ACK│    A7 ... A0      │ACK│  DATA BYTE   │ACK│ P │
└───┴───────────────────┴───┴───────────────────┴───┴──────────────┴───┴───┘
```

### 4.2 10-Bit Read Transaction Flow
Because the read direction bit must be combined with the target address, a read requires a **Repeated START ($S_r$)** sequence:

1. Controller sends START ($S$).
2. Controller sends First Byte with `R/W# = 0` (Write) + `A9:A8`. Target ACKs.
3. Controller sends Second Byte (`A7:A0`). Target ACKs.
4. Controller sends Repeated START ($S_r$).
5. Controller re-sends First Byte with `R/W# = 1` (Read) + `A9:A8`.
6. Matching target recognizes its address and sends ACK.
7. Target transmits data bytes to controller.
8. Controller acknowledges each byte, sends NACK on the last byte, followed by STOP ($P$).

```text
┌───┬─────────────────┬───┬───────────┬───┬────┬─────────────────┬───┬──────────────┬────┬───┐
│ S │ 1111 0 A9 A8 [W]│ACK│  A7 .. A0 │ACK│ Sr │ 1111 0 A9 A8 [R]│ACK│  DATA BYTE   │NACK│ P │
└───┴─────────────────┴───┴───────────┴───┴────┴─────────────────┴───┴──────────────┴────┴───┘
```

---

## 5. Reserved & Special I2C Addresses

Certain 7-bit address patterns are reserved by the NXP specification and must never be assigned to standard peripheral ICs:

| 7-Bit Address (Bin) | 7-Bit (Hex) | 8-Bit Equivalent | Purpose / Function | Description |
| :--- | :--- | :--- | :--- | :--- |
| `0000 000` | `0x00` | `0x00` (W) / `0x01` (R) | **General Call / START Byte** | Broadcast to all devices on bus (`R/W=0`) or hardware wake-up (`R/W=1`). |
| `0000 001` | `0x01` | `0x02` (W) / `0x03` (R) | **CBUS Address** | Legacy bus compatibility (not used in modern designs). |
| `0000 010` | `0x02` | `0x04` (W) / `0x05` (R) | **Reserved for Different Bus** | Reserved for alternative bus formats. |
| `0000 011` | `0x03` | `0x06` (W) / `0x07` (R) | **Reserved for Future Use** | Unassigned. |
| `0000 1XX` | `0x04` – `0x07` | `0x08` – `0x0F` | **High-Speed Master Code** | Broadcast at $\le 400\,\text{kHz}$ to switch bus to $3.4\,\text{Mbps}$ mode. |
| `1111 0XX` | `0x78` – `0x7B` | `0xF0` – `0xF7` | **10-bit Target Addressing** | Two-byte 10-bit address prefix. |
| `1111 1XX` | `0x7C` – `0x7F` | `0xF8` – `0xFF` | **Device ID / Reserved** | Query manufacturer, part number, and silicon revision code. |

### 5.1 General Call Address (`0x00`)

When a controller broadcasts address `0x00` with $R/W\# = 0$, every target capable of handling general calls asserts an ACK.

```text
┌───┬───────────────────┬───┬───────────────────┬───┬───┐
│ S │ 0000 000 0 [W]    │ACK│ Second Byte (CMD) │ACK│ P │
└───┴───────────────────┴───┴───────────────────┴───┴───┘
```

- **Second Byte = `0x06` (Software Reset)**: Forces all connected peripherals that support general call reset to reload their default power-on register configurations.
- **Second Byte = `0x04` (Hardware Address Programming)**: Used during factory automated board calibration.

---

## 6. Standard Transaction Flow Archetypes

Below are the five canonical I2C transaction sequences used across embedded firmware drivers:

### Archetype 1: Controller Single-Byte Write
Writing a single configuration byte or command opcode to a target:

```text
┌───┬───────────────────┬───┬───────────────────┬───┬───┐
│ S │ Target Addr + [W] │ACK│    Data Byte      │ACK│ P │
└───┴───────────────────┴───┴───────────────────┴───┴───┘
```
- **Controller drives**: START, Address+W, Data Byte, STOP.
- **Target drives**: Address ACK, Data ACK.

---

### Archetype 2: Controller Multi-Byte / Burst Write
Writing multiple bytes into an internal register or EEPROM page:

```text
┌───┬───────────────────┬───┬───────────────────┬───┬──────────────┬───┬──────────────┬───┬───┐
│ S │ Target Addr + [W] │ACK│ Register Pointer  │ACK│ Data Byte 1  │ACK│ Data Byte 2  │ACK│ P │
└───┴───────────────────┴───┴───────────────────┴───┴──────────────┴───┴──────────────┴───┴───┘
```
- The first transmitted byte is typically the internal **Register Sub-Address**.
- Subsequent bytes are written into consecutive memory locations via internal auto-incrementing address pointers.

---

### Archetype 3: Controller Direct Read
Reading continuous data from a device with an implicit register pointer (such as an ADC streaming conversions):

```text
┌───┬───────────────────┬───┬──────────────┬───┬──────────────┬────┬───┐
│ S │ Target Addr + [R] │ACK│ Data Byte 1  │ACK│ Data Byte 2  │NACK│ P │
└───┴───────────────────┴───┴──────────────┴───┴──────────────┴────┴───┘
```
- **Controller drives**: START, Address+R, Clock pulses, Data 1 ACK, Data 2 **NACK**, STOP.
- **Target drives**: Address ACK, Data Byte 1, Data Byte 2.
- **Crucial Rule**: The controller **MUST send NACK** on the final received byte to notify the target that no more bytes are requested. If the controller sends ACK, the target will continue to drive the next byte onto SDA, potentially causing a collision when the controller attempts to generate a STOP condition.

---

### Archetype 4: Combined Transaction / Random Register Read
**The most common transaction in embedded drivers** (used by virtually all accelerometers, gyroscopes, temperature sensors, and RTCs):

```text
Phase 1: Set Register Pointer (Write)          Phase 2: Read Register Data (Read)
┌───┬───────────────────┬───┬──────────────────┬───┬────┬───────────────────┬───┬──────────────┬────┬───┐
│ S │ Target Addr + [W] │ACK│ Register Address │ACK│ Sr │ Target Addr + [R] │ACK│ Data Byte    │NACK│ P │
└───┴───────────────────┴───┴──────────────────┴───┴────┴───────────────────┴───┴──────────────┴────┴───┘
```

1. Controller sends START ($S$).
2. Controller sends Target Address + Write bit (`0`). Target sends ACK.
3. Controller sends target register address (e.g. `0x75` for `WHO_AM_I`). Target sends ACK.
4. Controller issues **Repeated START ($S_r$)** (does NOT release the bus).
5. Controller re-addresses target with Read bit (`1`). Target sends ACK.
6. Target outputs content of register `0x75`.
7. Controller sends **NACK** on the byte.
8. Controller issues STOP ($P$).

---

## 7. Protocol Decoding & Logic Analyzer Walkthrough

When debugging I2C buses with a digital logic analyzer (e.g., Saleae Logic, Sigrok PulseView) or an oscilloscope with I2C protocol decoding, transactions appear as synchronized channel traces:

```text
        S    0x68 [W]       ACK    0x3B       ACK   Sr   0x68 [R]       ACK   0x14       ACK   0xA2       NACK  P
SCL:  ──┐   ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐   ┌─┐ ┌─┐ ┌─┐ ┌─┐   ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐   ┌─┐ ┌─┐ ┌─┐ ┌─┐   ┌─┐ ┌─┐ ┌─┐ ┌─┐   ┌───
        └───┘ └─┘ └─┘ └─┘ └─┘ └───┘ └─┘ └─┘ └─┘ └───┘ └─┘ └─┘ └─┘ └─┘ └───┘ └─┘ └─┘ └─┘ └───┘ └─┘ └─┘ └─┘ └───┘
        │   │               │     │           │     │   │               │     │           │     │           │     │
SDA:  ──┐   │ 1 1 0 1 0 0 0 │ 0   │ 0 0 1 1 1 │ 0   ┐   │ 1 1 0 1 0 0 1 │ 0   │ 0 0 0 1 0 │ 0   │ 1 0 1 0 0 │ 1   ┌───
        └───┴───────────────┴─┘───┴───────────┴─┘───└───┴───────────────┴─┘───┴───────────┴─┘───┴───────────┴─────┘
        ▲   ◄── Addr: 0x68 ─► ▲   ◄─ Reg:0x3B►▲     ▲   ◄── Addr: 0x68 ─► ▲   ◄─ Accel_X_H► ▲   ◄─ Accel_X_L► ▲   ▲
      START                  ACK             ACK Repeated                ACK               ACK              NACK STOP
                                                START
```

### Trace Step-by-Step Decoding Table:

| Time Index | Event / Packet | Direction | Data Value | Hex Equivalent | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $t_0$ | **START** | Controller $\to$ Bus | SDA $\downarrow$ while SCL $\text{HIGH}$ | $S$ | Bus ownership claimed. |
| $t_1$ | Address + W | Controller $\to$ Bus | `0b11010000` | `0xD0` (`0x68` W) | Addressing 6-DOF IMU (e.g. MPU-6050). |
| $t_2$ | **ACK** | Target $\to$ Controller | SDA pulled $\text{LOW}$ on 9th clock | `0` | IMU recognizes address. |
| $t_3$ | Register Address | Controller $\to$ Bus | `0b00111011` | `0x3B` (`ACCEL_XOUT_H`) | Pointing internal address pointer to high byte. |
| $t_4$ | **ACK** | Target $\to$ Controller | SDA pulled $\text{LOW}$ on 9th clock | `0` | Target latches register pointer. |
| $t_5$ | **Repeated START** | Controller $\to$ Bus | SDA $\downarrow$ while SCL $\text{HIGH}$ | $S_r$ | Retains bus; reverses data direction. |
| $t_6$ | Address + R | Controller $\to$ Bus | `0b11010001` | `0xD1` (`0x68` R) | Addressing IMU in read mode. |
| $t_7$ | **ACK** | Target $\to$ Controller | SDA pulled $\text{LOW}$ on 9th clock | `0` | Target switches to transmit mode. |
| $t_8$ | Payload Byte 1 | Target $\to$ Controller | `0b00010100` | `0x14` | High byte of X-axis accelerometer reading. |
| $t_9$ | **Master ACK** | Controller $\to$ Target | SDA pulled $\text{LOW}$ on 9th clock | `0` | Controller requests next sequential byte. |
| $t_{10}$ | Payload Byte 2 | Target $\to$ Controller | `0b10100010` | `0xA2` | Low byte of X-axis accelerometer reading. |
| $t_{11}$ | **Master NACK** | Controller $\to$ Target | SDA left $\text{HIGH}$ on 9th clock | `1` | Controller signals end of reception stream. |
| $t_{12}$ | **STOP** | Controller $\to$ Bus | SDA $\uparrow$ while SCL $\text{HIGH}$ | $P$ | Bus released to IDLE state. |

**Final Reconstructed Measurement**:
$$\text{Raw Accel X} = (\texttt{0x14} \ll 8) \mid \texttt{0xA2} = \texttt{0x14A2} = +5282 \text{ counts}$$
At standard $\pm 2g$ scale ($16,384\,\text{LSB}/g$):
$$\text{Acceleration}_X = \frac{5282}{16384} \approx +0.322\,g$$
