# CAN Protocol: Working Mechanism & Electrical Architecture

## 1. Physical Layer Architecture (ISO 11898-2)

The physical layer of CAN uses a balanced, two-wire differential signaling bus consisting of **CAN_H (CAN High)** and **CAN_L (CAN Low)**. Differential transmission confers near-total immunity to automotive common-mode electromagnetic noise and ground potential shifts between distant ECUs.

---

### 1.1 Differential Logic States: Recessive vs. Dominant

Unlike single-ended buses (UART, LIN, I2C), CAN represents binary states using the differential voltage $V_{DIFF}$:
$$V_{DIFF} = V_{CAN\_H} - V_{CAN\_L}$$

The bus supports two distinct electrical states:
1. **Recessive State (Logic 1)**:
   - High-impedance state. Both $CAN\_H$ and $CAN\_L$ lines are weakly biased to the nominal common-mode voltage of approximately **$2.5\,\text{V}$**.
   - Differential voltage is approximately **$0\,\text{V}$** (ISO spec: $-0.5\,\text{V} \le V_{DIFF} \le +0.05\,\text{V}$).
   - The bus defaults to Recessive when all nodes are idle or transmitting a '1'.
2. **Dominant State (Logic 0)**:
   - Actively driven state. The transmitting transceiver drives $CAN\_H$ up to **$+3.5\,\text{V}$** and pulls $CAN\_L$ down to **$+1.5\,\text{V}$**.
   - Differential voltage is approximately **$+2.0\,\text{V}$** (ISO spec: $+1.5\,\text{V} \le V_{DIFF} \le +3.0\,\text{V}$).
   - **Wired-AND Electrical Law**: If any single node drives a Dominant bit, the bus is forced into the Dominant state, overriding any number of nodes driving a Recessive bit.

```text
  Voltage (V)
   +3.5V ──────────┐                 ┌────────────────────── CAN_H (Dominant)
                   │                 │
   +2.5V ──────────┼─────────────────┼────────────────────── Recessive Bias (CAN_H & CAN_L)
                   │                 │
   +1.5V ──────────┴─────────────────┴────────────────────── CAN_L (Dominant)
                   |                 |
                   |<-- Dominant --->|<---- Recessive ------>|
                   |   (Logic '0')   |     (Logic '1')       |
                   |   Vdiff = 2.0V  |     Vdiff = 0.0V      |
```

### 1.2 Electrical Threshold Voltage Matrix

| Parameter | Symbol | Dominant (Logic 0) | Recessive (Logic 1) | Unit |
| :--- | :--- | :--- | :--- | :--- |
| **CAN_H Bus Voltage** | $V_{CAN\_H}$ | $2.75\,\text{V} \dots 4.5\,\text{V}$ (Typ: $3.5\,\text{V}$) | $2.0\,\text{V} \dots 3.0\,\text{V}$ (Typ: $2.5\,\text{V}$) | V |
| **CAN_L Bus Voltage** | $V_{CAN\_L}$ | $0.5\,\text{V} \dots 2.25\,\text{V}$ (Typ: $1.5\,\text{V}$) | $2.0\,\text{V} \dots 3.0\,\text{V}$ (Typ: $2.5\,\text{V}$) | V |
| **Differential Voltage** | $V_{DIFF}$ | $+1.5\,\text{V} \dots +3.0\,\text{V}$ (Typ: $+2.0\,\text{V}$) | $-0.5\,\text{V} \dots +0.05\,\text{V}$ (Typ: $0.0\,\text{V}$) | V |
| **Receiver Threshold** | $V_{TH(rx)}$ | $V_{DIFF} > 0.9\,\text{V}$ | $V_{DIFF} < 0.5\,\text{V}$ | V |
| **Receiver Hysteresis** | $V_{HYS}$ | Typical $150\,\text{mV}$ margin prevents jitter | — | mV |
| **Common-Mode Range** | $V_{CM}$ | $-2.0\,\text{V} \dots +7.0\,\text{V}$ (Extended: $-12\,\text{V} \dots +12\,\text{V}$) | — | V |

---

## 2. Transceiver Architecture & Circuit Interfacing

The CAN Transceiver acts as the physical bridge between the digital logic levels ($3.3\,\text{V}$ or $5\,\text{V}$ CMOS/TTL on TXD and RXD) of the CAN Controller and the differential analog voltages on the physical bus.

```text
                   +5V (Vcc)
                     │
              ┌──────┴──────────────────────┐
              │      CAN Transceiver        │
              │   (e.g., TJA1042 / TCAN1042)│
  MCU TXD ───>│ Dominant Driver             ├──── CAN_H ───> Bus
              │   (Push-Pull Output)        │
              │                             ├──── CAN_L ───> Bus
  MCU RXD <───┤ Differential Receiver       │
              │   (High-CMRR Comparator)    │
  MCU STB ───>│ Mode Control / Sleep Logic  │
              └─────────────────────────────┘
```

### 2.1 Critical Transceiver Internal Subsystems

1. **High-Impedance Receiver Stage**:
   - The differential comparator continuously senses $V_{CAN\_H} - V_{CAN\_L}$. If $V_{DIFF} > 0.9\,\text{V}$, the receiver drives `RXD = 0`. If $V_{DIFF} < 0.5\,\text{V}$, it pulls `RXD = 1`.
   - Even when powered down ($V_{CC} = 0\,\text{V}$), transceiver pins must present extremely high input impedance ($> 20\,\text{k}\Omega$) to prevent loading the active bus.
2. **TXD Dominant Clamp / Dominant Timeout**:
   - If a microcontroller firmware lockup or hardware latchup holds the `TXD` pin permanently LOW (driving continuous Dominant), the entire automotive network would freeze.
   - Modern transceivers incorporate an internal hardware watchdog timer ($t_{dom\_to} \approx 1.5\,\text{ms} - 5\,\text{ms}$). If `TXD` remains LOW longer than $t_{dom\_to}$, the transmitter stage is automatically disabled, releasing the bus back to Recessive.
3. **Loopback Propagation Delay ($t_{loop}$)**:
   - When a controller drives a bit on `TXD`, the signal travels through the transmitter output stage, drives the physical bus, returns through the internal receiver comparator, and outputs on `RXD`.
   - The total round-trip transceiver delay ($t_{loop} = t_{tx\_delay} + t_{rx\_delay}$) standardly ranges between **$100\,\text{ns}$ and $250\,\text{ns}$**. This loop delay is a primary constraint when calculating maximum bus length and bit timing.

### 2.2 Termination Schemes: Parallel vs. Split Termination

To prevent high-frequency transmission-line signal reflections, the CAN bus requires termination matching the nominal cable characteristic impedance ($Z_0 = 120\,\Omega$).

```text
Standard Termination (120Ω)             Split Termination (60Ω + 60Ω + 4.7nF)
      CAN_H ──────┬──────                     CAN_H ──────┬──────
                  │                                       │
                 [120Ω]                                  [60Ω]
                  │                                       ├──────||───── GND
      CAN_L ──────┴──────                                [60Ω]   (4.7nF)
                                                          │
                                              CAN_L ──────┴──────
```

- **Standard Parallel Termination**: A single $120\,\Omega$ ($\pm 1\%$, 0.25W) metal-film resistor placed across CAN_H and CAN_L at each extreme end of the linear bus trunk. Total parallel DC bus resistance:
  $$R_{bus} = 120\,\Omega \parallel 120\,\Omega = 60\,\Omega$$
- **Split Termination (Automotive Standard)**: Two $60\,\Omega$ ($\pm 1\%$) precision resistors in series with a central capacitor ($C_L = 4.7\,\text{nF}$ rated $\ge 50\,\text{V}$) connected to Ground.
  - *Engineering Advantage*: Acts as a low-pass filter for high-frequency common-mode noise without altering the differential DC termination ($60\,\Omega + 60\,\Omega = 120\,\Omega$). It dramatically reduces radiated electromagnetic emissions (EMI) and stabilizes the recessive bus bias point.

---

## 3. Non-Destructive Bitwise Arbitration (CSMA/CR)

CAN uses **Carrier Sense Multiple Access with Collision Resolution (CSMA/CR)**. It guarantees that bus collisions never result in lost bandwidth or packet destruction.

### 3.1 The Arbitration Mechanism

1. **Carrier Sense**: Any node wishing to transmit listens to the bus. If the bus is Recessive for at least 11 consecutive bit times (**Bus Idle**), transmission may begin immediately with a Dominant **Start of Frame (SOF)** bit.
2. **Concurrent Transmission**: If two or more nodes begin transmitting simultaneously, each node begins transmitting its **Identifier** field MSB first.
3. **Continuous RX Monitoring**: While a node drives its bit onto `TXD`, its internal receiver simultaneously reads the resulting actual bus voltage from `RXD`.
4. **Collision Detection & Preemption**:
   - As long as all competing nodes transmit identical bits, their transmitted bits match the bus.
   - As soon as **Node A** transmits a **Recessive (1)** bit while **Node B** transmits a **Dominant (0)** bit, the Wired-AND property forces the physical bus to **Dominant (0)**.
   - Node A observes `TXD = 1` but `RXD = 0`. Node A detects that it has lost arbitration!
   - Node A immediately halts transmission of all further bits and instantaneously switches to pure receiver mode.
   - Node B never realizes an arbitration conflict occurred; its frame continues transmission completely uncorrupted and without a nanosecond of delay!

```text
Bit Period:       SOF   ID10   ID9    ID8    ID7 (Collision!)
Node 1 (ID 0x120):  0     0      0      1      0 (Dominant)  ──> Continues transmitting (WINS)
Node 2 (ID 0x124):  0     0      0      1      1 (Recessive) ──> Detects bus is '0', loses & yields!
Actual Bus Line:    0     0      0      1      0 (Dominant)
```

> [!IMPORTANT]
> **Priority Axiom**: Because a Dominant bit ($0$) overrides a Recessive bit ($1$), **lower numerical CAN Identifiers have higher priority**.
> - ID `0x001` (Emergency Braking / Airbag) preempts ID `0x100` (Engine RPM).
> - ID `0x100` preempts ID `0x500` (HVAC / Ambient Temperature).

---

## 4. Error Detection & Confinement Mechanics

CAN achieves an extraordinary undetected error rate ($< 4.7 \times 10^{-13}$) through five distinct hardware error detection mechanisms running concurrently on every node.

### 4.1 The Five Error Detection Types

| Error Type | Layer | Detected By | Detection Mechanism |
| :--- | :--- | :--- | :--- |
| **1. Bit Error** | Physical | Transmitter Only | The transmitter compares its driven bit on `TXD` with the sampled bit on `RXD`. A Bit Error is flagged if the read bit does not match the driven bit. *(Exceptions: During arbitration where Recessive '1' may be overridden, or during ACK Slot).* |
| **2. Stuff Error** | Framing | All Nodes | A Stuff Error is flagged if $6$ consecutive bits of identical polarity are detected within the bit-stuffed zone (SOF through CRC sequence). |
| **3. CRC Error** | Data Integrity | Receivers Only | Receivers independently calculate the CRC-15 polynomial ($x^{15} + x^{14} + x^{10} + x^8 + x^7 + x^4 + x^3 + 1$) over the incoming bit stream. An error is flagged if the calculated CRC does not match the transmitted CRC field. |
| **4. Form Error** | Frame Format | All Nodes | Flagged when a fixed-form delimiter field contains an illegal bit value (e.g., CRC Delimiter, ACK Delimiter, or End-of-Frame containing a dominant '0' instead of recessive '1'). |
| **5. ACK Error** | Handshake | Transmitter Only | Flagged when the transmitting node drives a Recessive bit in the ACK Slot but reads back a Recessive '1' because no receiver acknowledged the frame with a Dominant '0'. |

---

### 4.2 Error Signaling: Error Flags

When any node detects one of the five errors, it immediately interrupts frame transmission by driving an **Error Flag**:
- **Active Error Flag**: 6 consecutive **Dominant** bits driven on the bus. This intentionally violates the bit-stuffing rule, causing every other node on the network to detect a Stuff Error and discard the corrupted frame simultaneously.
- **Passive Error Flag**: 6 consecutive **Recessive** bits. Sent only by nodes in the Error Passive state to notify the network without destroying bus traffic.
- **Error Delimiter**: 8 consecutive **Recessive** bits following the Error Flag, allowing all nodes to re-synchronize before the next frame attempt.

---

### 4.3 Fault Confinement State Machine: TEC & REC

To prevent a malfunctioning ECU from corrupting the entire vehicle network, every CAN controller maintains two internal 8-bit diagnostic hardware counters:
- **TEC (Transmit Error Counter)**
- **REC (Receive Error Counter)**

```text
                  ┌──────────────────────────────────────────────┐
                  │                 ERROR ACTIVE                 │
                  │             (TEC < 128, REC < 128)           │
                  │   - Normal operation                         │
                  │   - Drives Active Error Flags (6 dominant)   │
                  └───────┬──────────────────────────────▲───────┘
                          │                              │
                    TEC >= 128                     TEC <= 127
                    or REC >= 128                  and REC <= 127
                          │                              │
                          ▼                              │
                  ┌──────────────────────────────────────┴───────┐
                  │                ERROR PASSIVE                 │
                  │            (TEC >= 128 or REC >= 128)        │
                  │   - Can transmit & receive                   │
                  │   - Drives Passive Error Flags (6 recessive) │
                  │   - Must wait 8-bit Suspend Transmission     │
                  └───────┬──────────────────────────────────────┘
                          │
                      TEC > 255
                          │
                          ▼
                  ┌──────────────────────────────────────────────┐
                  │                   BUS-OFF                    │
                  │                 (TEC > 255)                  │
                  │   - Output drivers completely isolated       │
                  │   - No transmission or reception             │
                  │   - Auto-recovery: 128 × 11 recessive bits   │
                  └──────────────────────────────────────────────┘
```

#### Counter Adjustment Rules:
- When a transmitter detects an error: $\text{TEC} \leftarrow \text{TEC} + 8$.
- When a receiver detects an error: $\text{REC} \leftarrow \text{REC} + 1$ (or $+8$ if receiver error flag was dominant).
- When a transmitter completes a successful frame: $\text{TEC} \leftarrow \text{TEC} - 1$ (down to 0).
- When a receiver completes a successful frame: $\text{REC} \leftarrow \text{REC} - 1$ (if $1 \le \text{REC} \le 127$; reset to 0 if REC=0).

#### Bus-Off Recovery Protocol:
Once a node transitions to **Bus-Off**, it can only rejoin the network through a controlled recovery sequence:
- The controller monitors the RX line until it observes **128 occurrences of 11 consecutive Recessive bits** (corresponding to 128 idle message periods).
- Upon completion, $\text{TEC}$ and $\text{REC}$ are reset to $0$, and the controller re-enters the **Error Active** state.

---

## 5. Hardware CAN Controller Architecture

Modern microcontrollers (e.g., STM32, NXP S32K, TI TMS570, Microchip SAM) incorporate specialized CAN hardware peripheral engines (e.g., Bosch M_CAN, STM32 bxCAN, NXP FlexCAN) offloading real-time frame filtering, transmission, and reception from the CPU core.

```text
 ┌─────────────────────────────────────────────────────────────┐
 │                    MCU Hardware Peripheral                  │
 │                                                             │
 │   ┌────────────────┐      ┌─────────────────────────────┐   │
 │   │  TX Mailboxes  │      │     Acceptance Filters      │   │
 │   │ [MB0][MB1][MB2]│      │  [Filter 0] ... [Filter 13] │   │
 │   └───────┬────────┘      └──────────────┬──────────────┘   │
 │           │                              │                  │
 │   ┌───────▼────────┐             ┌───────▼──────────────┐   │
 │   │  CAN Protocol  │             │   RX FIFO 0 / FIFO 1 │   │
 │   │ Engine (Bit-   ├─< TXD / RXD >┤  3-stage Hardware   │   │
 │   │ timing, CRC)   │             │       Mailbox        │   │
 │   └────────────────┘             └──────────────────────┘   │
 └─────────────────────────────────────────────────────────────┘
```

### 5.1 Acceptance Filters & Mask Registers

Automotive networks routinely carry thousands of frames per second. To prevent the microcontroller from being interrupted by messages irrelevant to its subsystem (e.g., the Door ECU processing Engine RPM messages), the CAN controller provides **Hardware Acceptance Filters**.

Every filter comprises two 32-bit (or 16-bit) registers:
- **Filter ID Register**: The exact bit pattern the node expects to match.
- **Filter Mask Register**: A bitwise mask specifying which bits matter ("care") and which bits are ignored ("don't care").
  - Mask bit = `1`: The incoming frame's bit **must match** the Filter ID bit exactly.
  - Mask bit = `0`: The incoming frame's bit is **ignored** ("don't care").

#### Acceptance Logic Equation:
$$\text{Match} = \neg \Big( (\text{Incoming\_ID} \oplus \text{Filter\_ID}) \ \& \ \text{Filter\_Mask} \Big) == 0$$

```c
/* Example: C Acceptance Filter Configuration for STM32 bxCAN */
CAN_FilterTypeDef sFilterConfig;

sFilterConfig.FilterBank = 0;
sFilterConfig.FilterMode = CAN_FILTERMODE_IDMASK;
sFilterConfig.FilterScale = CAN_FILTERSCALE_32BIT;

/* We want to receive all IDs from 0x120 to 0x127 (Binary: 001 0010 0xxx) */
sFilterConfig.FilterIdHigh = (0x120 << 5);       // Standard ID shifted to MSB
sFilterConfig.FilterIdLow  = 0x0000;
sFilterConfig.FilterMaskIdHigh = (0x7F8 << 5);   // Care about top 8 bits, ignore lower 3 bits
sFilterConfig.FilterMaskIdLow  = 0x0000;

sFilterConfig.FilterFIFOAssignment = CAN_RX_FIFO0;
sFilterConfig.FilterActivation = ENABLE;
HAL_CAN_ConfigFilter(&hcan1, &sFilterConfig);
```
