# CAN Protocol: Timing Calculations, Bitrates & Hardware Engineering

## 1. Bit Timing Architecture & Time Quanta

In synchronous buses (such as SPI or I2C), an explicit clock line paces every bit transfer. Because CAN operates without an external clock line, every node on the network must independently generate and synchronize its bit sampling clock.

To achieve microsecond-precise sampling across multi-meter cable runs with varying propagation delays, CAN divides every single bit time into discrete integer units called **Time Quanta (t_q)**.

---

### 1.1 The Four Bit Time Segments

According to ISO 11898-1, every **Nominal Bit Time (NBT)** consists of four separate, contiguous functional segments:

```text
 ┌──────────┬─────────────────────────┬─────────────────────────┬─────────────────────────┐
 │ Sync_Seg │        Prop_Seg         │       Phase_Seg1        │       Phase_Seg2        │
 ├──────────┼─────────────────────────┼─────────────────────────┼─────────────────────────┤
 │   1 Tq   │       1 .. 8 Tq         │       1 .. 8 Tq         │       2 .. 8 Tq         │
 └──────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┘
                                                                ▲
                                                           Sample Point
 |<---------------------- TSEG1 (Prop + Phase1) --------------->|<-------- TSEG2 -------->|
 |<---------------------------------- Total NBT (8 .. 25 Tq) ----------------------------->|
```

1. **Synchronization Segment (Sync_Seg) — Exactly 1 t_q**:
   - The first segment of every bit. An edge on the bus is expected to occur within this segment during normal synchronization.
2. **Propagation Time Segment (Prop_Seg) — 1 ... 8 t_q**:
   - Compensates for the physical signal delay across the network.
   - Must cover twice the physical line delay (2 * t_bus) plus the transmitting and receiving transceiver internal loopback delays (2 * t_transceiver).
3. **Phase Buffer Segment 1 (Phase_Seg1) — 1 ... 8 t_q**:
   - Absorbs positive edge phase errors caused by oscillator frequency drift or signal degradation.
   - May be lengthened dynamically by the resynchronization engine.
4. **Phase Buffer Segment 2 (Phase_Seg2) — 2 ... 8 t_q**:
   - Absorbs negative edge phase errors.
   - May be shortened dynamically during resynchronization.

> [!NOTE]
> Microcontroller hardware register manuals (e.g., STM32, NXP S32K, Microchip MCP2515) commonly combine Prop_Seg and Phase_Seg1 into a single register parameter termed **TSEG1**, while Phase_Seg2 is configured as **TSEG2**:
> ```
TSEG1 = Prop_Seg + Phase_Seg1
```
> ```
TSEG2 = Phase_Seg2
```

---

### 1.2 Mathematical Derivations & Register Formulas

Given a CAN peripheral peripheral clock frequency (f_can_clk) and a target bitrate (BR):

#### Step 1: Nominal Bit Time (NBT)
```
NBT = 1 / BR
```

Where:
- NBT: Nominal Bit Time duration (s)
- BR: Nominal CAN bus baud rate (bps)
*Example*: At 500 kbps:
```
NBT = 1 / 500,000 Hz = 2.0 µs = 2000 ns
```

#### Step 2: Time Quantum Duration (t_q)
The CAN Baud Rate Prescaler (BRP) divides down the controller clock:
```
t_q = BRP / f_can_clk
```

Where:
- t_q: Time quantum duration (s)
- BRP: Baud Rate Prescaler integer divisor value
- f_can_clk: Clock frequency supplied to the CAN peripheral controller (Hz)

#### Step 3: Total Number of Time Quanta per Bit (N_tq)
```
N_tq = NBT / t_q = Sync_Seg + Prop_Seg + Phase_Seg1 + Phase_Seg2
```

Where:
- N_tq: Total number of time quanta per nominal bit time
- NBT: Nominal Bit Time (s)
- t_q: Time quantum duration (s)
- Sync_Seg: Synchronization Segment, always fixed at 1 t_q
- Prop_Seg: Propagation Segment compensating for physical wire and transceiver delays (t_q)
- Phase_Seg1: Phase Buffer Segment 1 (t_q)
- Phase_Seg2: Phase Buffer Segment 2 (t_q)
The ISO specification requires 8 <= N_tq <= 25 for Classical CAN.

#### Step 4: Sample Point (SP) Calculation
The exact instant within the bit period where the receiver captures the logic state of the bus:
```
Sample Point (\%) = (Sync_Seg + Prop_Seg + Phase_Seg1) / N_tq * 100\% = (1 + TSEG1) / N_tq * 100\%
```

| Speed Class | CiA Standard Target Sample Point | Acceptable Engineering Tolerance |
| :--- | :--- | :--- |
| **1000 kbps (1 Mbps)** | **75.0%** | 70.0\% ... 80.0\% |
| **500 kbps** | **87.5%** | 85.0\% ... 90.0\% |
| **250 kbps** | **87.5%** | 85.0\% ... 90.0\% |
| **125 kbps** | **87.5%** | 85.0\% ... 90.0\% |

---

### 1.3 Worked Numerical Example: 500 kbps on STM32 (48 MHz Clock)

Given:
- Peripheral Clock: f_can_clk = 48 MHz
- Target Bitrate: BR = 500 kbps (NBT = 2000 ns)
- Desired Sample Point: 87.5\%

1. Choose Prescaler BRP = 6:
   ```
t_q = 6 / 48 MHz = 125 ns
```
2. Calculate total quanta:
   ```
N_tq = 2000 ns / 125 ns = 16 t_q
```
3. Target Sample Point at 87.5\%:
   ```
Sample Instant = 16 * 0.875 = 14 t_q
```
4. Allocate segments:
   - Sync_Seg = 1 t_q
   - TSEG1 = 14 - 1 = 13 t_q (e.g., Prop_Seg = 7 t_q, Phase_Seg1 = 6 t_q)
   - TSEG2 = 16 - 14 = 2 t_q (Phase_Seg2 = 2 t_q)
   - Actual Sample Point:
     ```
SP = (1 + 13) / 16 * 100\% = 14 / 16 * 100\% = 87.50\% (Exact 0.00\% error)
```
5. Synchronization Jump Width (SJW):
   ```
SJW = min(4, Phase_Seg1, Phase_Seg2) = min(4, 6, 2) = 2 t_q
```

---

## 2. Synchronization Jump Width (SJW) & Clock Tolerance

To maintain alignment despite oscillator frequency tolerances and propagation delays across disparate nodes, CAN incorporates continuous dynamic resynchronization.

### 2.1 Hard Synchronization vs. Resynchronization
- **Hard Synchronization**: Occurs exclusively on the falling edge of a **Start of Frame (SOF)** after the bus has been idle. The internal bit time counter of every receiver is reset immediately to Sync_Seg.
- **Resynchronization**: Occurs on any subsequent recessive-to-dominant edge throughout the frame. The receiver calculates the phase error e:
  - If the edge falls **after Sync_Seg** (positive phase error), Phase_Seg1 is lengthened by up to SJW.
  - If the edge falls **before Sync_Seg** (negative phase error), Phase_Seg2 is shortened by up to SJW.

### 2.2 Maximum Oscillator Tolerance Condition

For two CAN nodes to communicate reliably without experiencing bit-stuffing errors, their oscillator frequency deviation (Δ f / f) must satisfy:

```
(Δ f) / f <= SJW / (2 * 10 * N_tq)
```
```
(Δ f) / f <= (min(Phase_Seg1, Phase_Seg2)) / (2 * (13 * N_tq - Phase_Seg2))
```

> [!CAUTION]
> Ceramic resonators (> ± 0.5\% tolerance) are marginal for 500 kbps and strictly prohibited for CAN FD. **Automotive grade quartz crystals (± 50 ppm to ± 100 ppm)** must be selected for CAN FD designs.

---

## 3. CAN FD Dual-Bitrate Timing & Transmitter Delay Compensation (TDC)

In CAN FD, data payload bytes are transmitted at elevated speeds (e.g., 2 Mbps or 5 Mbps), where a single bit time shrinks to:
- At 2 Mbps: T_bit = 500 ns
- At 5 Mbps: T_bit = 200 ns

### 3.1 The High-Speed Loop Delay Problem

A physical CAN transceiver has an internal round-trip loopback delay (t_loop = t_tx_delay + t_rx_delay) typically between **100 ns and 200 ns**, plus cable propagation delay.

```text
At 5 Mbps (T_bit = 200 ns):
MCU TXD:          | Bit 0 (200ns) | Bit 1 (200ns) |
Transceiver Loop: ~~~~~ Loopback Delay: 180 ns ~~~~~
MCU RXD:                    | Bit 0 Received (200ns) |
Fixed Sample Point (75%):       ^ (Samples at 150ns: Still reads previous bit!) ---> BIT ERROR!
```

If the controller attempted to sample `RXD` at the standard 75\% sample point (150 ns into the bit period), the transceiver's output would not have arrived yet. The controller would read the *previous* bit state, causing an immediate false **Bit Error** and dropping the node off the bus!

### 3.2 Secondary Sample Point (SSP) Architecture

To solve this physical barrier, CAN FD hardware controllers implement **Transmitter Delay Compensation (TDC)**:
1. When transmitting in the fast data phase, the controller starts an internal counter when driving the falling edge of a transmitted bit on `TXD`.
2. The counter runs until the edge returns on `RXD`, measuring the exact real-time loop delay:
   ```
Measured Delay = t_loop_actual
```
3. The controller dynamically sets a **Secondary Sample Point (SSP)** displaced from the transmitted edge:
   ```
SSP = t_loop_actual + TDCO
```
   *(where TDCO is the Transmitter Delay Compensation Offset, typically set to 50\% - 75\% of the fast bit time).*

```text
 ┌─────────────────────────────────────────────────────────────┐
 │           CAN FD Bit Timing Specification Matrix            │
 ├─────────────────────────┬─────────────────┬─────────────────┤
 │ Parameter               │ Nominal Phase   │ Data Phase      │
 ├─────────────────────────┼─────────────────┼─────────────────┤
 │ Target Bitrate          │ 500 kbps        │ 2.0 Mbps        │
 │ Bit Duration (T_bit)│ 2000 ns         │ 500 ns          │
 │ Peripheral Clock        │ 80 MHz          │ 80 MHz          │
 │ Prescaler (BRP)       │ 10              │ 2               │
 │ Quanta Duration (t_q) │ 125 ns          │ 25 ns           │
 │ Total Quanta (N_tq) │ 16              │ 20              │
 │ Sample Point            │ 87.5%           │ 75.0% (via SSP) │
 └─────────────────────────┴─────────────────┴─────────────────┘
```

---

## 4. Bus Length, Topologies & Capacitive Budgeting

Signal propagation in copper twisted-pair cable travels at approximately **5 ns/meter** (approx. 2/3 the speed of light). Because every transmitting node must be capable of receiving a bit within the propagation segment during bitwise arbitration, the maximum cable length is strictly governed by the bitrate:

```
2 * [ (L_bus * tau_prop) + t_transceiver_loop ] <= Prop_Seg * t_q
```

Where:
- L_bus: Maximum physical bus cable harness length (m)
- tau_prop: Propagation delay of the twisted-pair cable (s/m, typically ~5 ns/m)
- t_transceiver_loop: Round-trip loop delay through the transceiver (s)
- Prop_Seg: Allocated Propagation Segment duration in time quanta
- t_q: Time quantum duration (s)

### 4.1 Bitrate vs. Maximum Cable Length Benchmark

| CAN Bitrate | Bit Time (NBT) | Max Trunk Bus Length (L_bus) | Max Individual Stub Length (L_stub) |
| :--- | :--- | :--- | :--- |
| **1000 kbps (1 Mbps)** | 1000 ns | **25 to 40 meters** | < 0.3 meters |
| **500 kbps** | 2000 ns | **100 meters** | < 1.0 meter |
| **250 kbps** | 4000 ns | **250 meters** | < 2.5 meters |
| **125 kbps** | 8000 ns | **500 meters** | < 5.0 meters |
| **50 kbps** | 20,000 ns | **1,000 meters (1 km)** | < 10.0 meters |

```text
Linear Trunk Topology (Compliant):
[Term]===+==================+==================+===================+===[Term]
         │ (< 0.3m)         │ (< 0.3m)         │ (< 0.3m)          │
       [Node 1]           [Node 2]           [Node 3]            [Node 4]

Star Topology (Non-compliant for high bitrates due to reflection reflections):
                          [Node 1]
                             │
       [Node 2] ────────── [HUB] ────────── [Node 3] (Severe impedance discontinuities!)
                             │
                          [Node 4]
```

---

## 5. Hardware PCB Layout, ESD, Common-Mode Noise & Schematics

```text
                       Common-Mode Choke
                         (51uH - 100uH)
                        ┌────UUUU────┐
  Transceiver CAN_H ────┤ 1        2 ├────┬─────────────> Bus CAN_H
                        └────────────┘    │
                                         [60Ω] Split Termination
                                          │
                                         ─┴─ 4.7nF (50V)
                                         ─┬─
                                          │
                        ┌────UUUU────┐   [60Ω]
  Transceiver CAN_L ────┤ 4        3 ├────┴─────────────> Bus CAN_L
                        └────────────┘    │
                                         [TVS] PESD2CAN-U
                                          │
                                         GND
```

### 5.1 PCB Layout Best Practices
1. **Differential Characteristic Impedance**: Route CAN_H and CAN_L as a differential pair with Z_diff = 120 Ω ± 10\%.
2. **Trace Length Matching**: Keep trace length mismatch between CAN_H and CAN_L strictly below **2.0 mm** to prevent converting differential signals into common-mode EMI radiation.
3. **Component Placement Priority**:
   - Place TVS protection diodes (e.g., Nexperia `PESD2CAN`) as close as physically possible to the board connector pins before any traces reach the choke or transceiver.
   - Place the Common-Mode Choke (e.g., TDK `ACT45B-510-2P`) directly adjacent to the TVS diodes.
   - Place split termination resistors (60.4 Ω ± 1\%) right at the transceiver side of the choke.
4. **Galvanic Isolation**: For industrial automation and EV battery management systems (BMS) where ground potential differences exceed 5 V, employ isolated transceivers (e.g., TI `ISO1042`, ADI `ADM3053`) with >= 2.5 kV_RMS reinforced isolation.

---

## 6. Root Cause Analysis (RCA) Troubleshooting Matrix

When debugging failed CAN bring-ups on the bench, consult this root-cause diagnostic matrix:

| Observed Symptom | Oscilloscope / Logic Analyzer Signature | Probable Root Cause | Verification & Corrective Action |
| :--- | :--- | :--- | :--- |
| **Node transmits frame, immediately flags ACK Error and retries continuously until Bus-Off.** | Dominant frame is driven cleanly, but the ACK slot remains Recessive (no dominant pulse). Continuous re-transmissions. | **Sole node on the bus** or disconnected receiver. | CAN requires at least one active receiving node to acknowledge frames. Check cable harness or connect a second node/CAN analyzer. |
| **Severe ringing, reflections, and deformed bit edges on oscilloscope.** | Signal edges overshoot > 4 V with underdamped oscillations lasting > 200 ns. | **Missing or double termination resistors**. | Measure DC resistance between CAN_H and CAN_L with power OFF. Correct reading must be **60 Ω** (120 Ω || 120 Ω). If 120 Ω, one terminator is missing. If < 40 Ω, too many terminators are installed. |
| **All transmitted frames result in continuous Stuff Errors after SOF.** | Bus drops to Dominant and stays low for 6 bit times (Error Flag) right after the arbitration field. | **Mismatched Baud Rate** or inverted CAN_H / CAN_L wiring. | Verify baud rate prescalers using `tools/can_calc.py`. Check physical wiring: CAN_H should sit at 2.5 V idle and rise to 3.5 V; CAN_L should drop to 1.5 V. |
| **Communication works at 250 kbps but fails completely at 1 Mbps.** | Bits are decoded incorrectly towards the end of long frames; ACK slot is missed. | **Propagation delay exceeds Prop_Seg budget** or stub lines exceed length limits (> 0.3 m). | Recalculate Time Quanta to shift Sample Point later (75\% - 87.5\%). Shorten stub taps or replace star topology with a daisy-chained linear trunk. |
| **CAN FD frames transmit nominal header but abort with Bit Error at BRS.** | Frame is valid up to the BRS bit, then an immediate Error Frame occurs in the fast data payload phase. | **Transmitter Delay Compensation (TDC) disabled** or SSP offset incorrectly tuned. | Enable TDC in the CAN FD controller registers. Configure TDCO to match transceiver loopback delay (t_loop ≈ 150 ns). |
| **Bus enters Bus-Off state immediately upon connecting new node.** | Bus differential voltage collapses; controller TEC counter jumps past 255. | **Node configured with inverted polarity** or TX pin shorted to Ground. | Verify transceiver TXD is idling HIGH (3.3V or 5V). Check for damaged transceiver driver stage. |
