# CAN Protocol: Timing Calculations, Bitrates & Hardware Engineering

## 1. Bit Timing Architecture & Time Quanta

In synchronous buses (such as SPI or I2C), an explicit clock line paces every bit transfer. Because CAN operates without an external clock line, every node on the network must independently generate and synchronize its bit sampling clock.

To achieve microsecond-precise sampling across multi-meter cable runs with varying propagation delays, CAN divides every single bit time into discrete integer units called **Time Quanta ($t_q$)**.

---

### 1.1 The Four Bit Time Segments

According to ISO 11898-1, every **Nominal Bit Time ($NBT$)** consists of four separate, contiguous functional segments:

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

1. **Synchronization Segment ($Sync\_Seg$) — Exactly $1\,t_q$**:
   - The first segment of every bit. An edge on the bus is expected to occur within this segment during normal synchronization.
2. **Propagation Time Segment ($Prop\_Seg$) — $1 \dots 8\,t_q$**:
   - Compensates for the physical signal delay across the network.
   - Must cover twice the physical line delay ($2 \times t_{bus}$) plus the transmitting and receiving transceiver internal loopback delays ($2 \times t_{transceiver}$).
3. **Phase Buffer Segment 1 ($Phase\_Seg1$) — $1 \dots 8\,t_q$**:
   - Absorbs positive edge phase errors caused by oscillator frequency drift or signal degradation.
   - May be lengthened dynamically by the resynchronization engine.
4. **Phase Buffer Segment 2 ($Phase\_Seg2$) — $2 \dots 8\,t_q$**:
   - Absorbs negative edge phase errors.
   - May be shortened dynamically during resynchronization.

> [!NOTE]
> Microcontroller hardware register manuals (e.g., STM32, NXP S32K, Microchip MCP2515) commonly combine $Prop\_Seg$ and $Phase\_Seg1$ into a single register parameter termed **$TSEG1$**, while $Phase\_Seg2$ is configured as **$TSEG2$**:
> $$TSEG1 = Prop\_Seg + Phase\_Seg1$$
> $$TSEG2 = Phase\_Seg2$$

---

### 1.2 Mathematical Derivations & Register Formulas

Given a CAN peripheral peripheral clock frequency ($f_{can\_clk}$) and a target bitrate ($BR$):

#### Step 1: Nominal Bit Time ($NBT$)
$$NBT = \frac{1}{BR}$$
*Example*: At $500\,\text{kbps}$:
$$NBT = \frac{1}{500,000\,\text{Hz}} = 2.0\,\mu\text{s} = 2000\,\text{ns}$$

#### Step 2: Time Quantum Duration ($t_q$)
The CAN Baud Rate Prescaler ($BRP$) divides down the controller clock:
$$t_q = \frac{BRP}{f_{can\_clk}}$$

#### Step 3: Total Number of Time Quanta per Bit ($N_{tq}$)
$$N_{tq} = \frac{NBT}{t_q} = Sync\_Seg + Prop\_Seg + Phase\_Seg1 + Phase\_Seg2$$
The ISO specification requires $8 \le N_{tq} \le 25$ for Classical CAN.

#### Step 4: Sample Point ($SP$) Calculation
The exact instant within the bit period where the receiver captures the logic state of the bus:
$$\text{Sample Point (\%)} = \frac{Sync\_Seg + Prop\_Seg + Phase\_Seg1}{N_{tq}} \times 100\% = \frac{1 + TSEG1}{N_{tq}} \times 100\%$$

| Speed Class | CiA Standard Target Sample Point | Acceptable Engineering Tolerance |
| :--- | :--- | :--- |
| **1000 kbps (1 Mbps)** | **75.0%** | $70.0\% \dots 80.0\%$ |
| **500 kbps** | **87.5%** | $85.0\% \dots 90.0\%$ |
| **250 kbps** | **87.5%** | $85.0\% \dots 90.0\%$ |
| **125 kbps** | **87.5%** | $85.0\% \dots 90.0\%$ |

---

### 1.3 Worked Numerical Example: 500 kbps on STM32 (48 MHz Clock)

Given:
- Peripheral Clock: $f_{can\_clk} = 48\,\text{MHz}$
- Target Bitrate: $BR = 500\,\text{kbps}$ ($NBT = 2000\,\text{ns}$)
- Desired Sample Point: $87.5\%$

1. Choose Prescaler $BRP = 6$:
   $$t_q = \frac{6}{48\,\text{MHz}} = 125\,\text{ns}$$
2. Calculate total quanta:
   $$N_{tq} = \frac{2000\,\text{ns}}{125\,\text{ns}} = 16\,t_q$$
3. Target Sample Point at $87.5\%$:
   $$\text{Sample Instant} = 16 \times 0.875 = 14\,t_q$$
4. Allocate segments:
   - $Sync\_Seg = 1\,t_q$
   - $TSEG1 = 14 - 1 = 13\,t_q$ (e.g., $Prop\_Seg = 7\,t_q$, $Phase\_Seg1 = 6\,t_q$)
   - $TSEG2 = 16 - 14 = 2\,t_q$ ($Phase\_Seg2 = 2\,t_q$)
   - Actual Sample Point:
     $$SP = \frac{1 + 13}{16} \times 100\% = \frac{14}{16} \times 100\% = 87.50\% \quad \text{(Exact 0.00\% error)}$$
5. Synchronization Jump Width ($SJW$):
   $$SJW = \min(4, Phase\_Seg1, Phase\_Seg2) = \min(4, 6, 2) = 2\,t_q$$

---

## 2. Synchronization Jump Width ($SJW$) & Clock Tolerance

To maintain alignment despite oscillator frequency tolerances and propagation delays across disparate nodes, CAN incorporates continuous dynamic resynchronization.

### 2.1 Hard Synchronization vs. Resynchronization
- **Hard Synchronization**: Occurs exclusively on the falling edge of a **Start of Frame (SOF)** after the bus has been idle. The internal bit time counter of every receiver is reset immediately to $Sync\_Seg$.
- **Resynchronization**: Occurs on any subsequent recessive-to-dominant edge throughout the frame. The receiver calculates the phase error $e$:
  - If the edge falls **after $Sync\_Seg$** (positive phase error), $Phase\_Seg1$ is lengthened by up to $SJW$.
  - If the edge falls **before $Sync\_Seg$** (negative phase error), $Phase\_Seg2$ is shortened by up to $SJW$.

### 2.2 Maximum Oscillator Tolerance Condition

For two CAN nodes to communicate reliably without experiencing bit-stuffing errors, their oscillator frequency deviation ($\Delta f / f$) must satisfy:

$$\frac{\Delta f}{f} \le \frac{SJW}{2 \times 10 \times N_{tq}}$$
$$\frac{\Delta f}{f} \le \frac{\min(Phase\_Seg1, Phase\_Seg2)}{2 \times (13 \times N_{tq} - Phase\_Seg2)}$$

> [!CAUTION]
> Ceramic resonators ($> \pm 0.5\%$ tolerance) are marginal for 500 kbps and strictly prohibited for CAN FD. **Automotive grade quartz crystals ($\pm 50\,\text{ppm}$ to $\pm 100\,\text{ppm}$)** must be selected for CAN FD designs.

---

## 3. CAN FD Dual-Bitrate Timing & Transmitter Delay Compensation (TDC)

In CAN FD, data payload bytes are transmitted at elevated speeds (e.g., $2\,\text{Mbps}$ or $5\,\text{Mbps}$), where a single bit time shrinks to:
- At $2\,\text{Mbps}$: $T_{bit} = 500\,\text{ns}$
- At $5\,\text{Mbps}$: $T_{bit} = 200\,\text{ns}$

### 3.1 The High-Speed Loop Delay Problem

A physical CAN transceiver has an internal round-trip loopback delay ($t_{loop} = t_{tx\_delay} + t_{rx\_delay}$) typically between **$100\,\text{ns}$ and $200\,\text{ns}$**, plus cable propagation delay.

```text
At 5 Mbps (T_bit = 200 ns):
MCU TXD:          | Bit 0 (200ns) | Bit 1 (200ns) |
Transceiver Loop: ~~~~~ Loopback Delay: 180 ns ~~~~~
MCU RXD:                    | Bit 0 Received (200ns) |
Fixed Sample Point (75%):       ^ (Samples at 150ns: Still reads previous bit!) ---> BIT ERROR!
```

If the controller attempted to sample `RXD` at the standard $75\%$ sample point ($150\,\text{ns}$ into the bit period), the transceiver's output would not have arrived yet. The controller would read the *previous* bit state, causing an immediate false **Bit Error** and dropping the node off the bus!

### 3.2 Secondary Sample Point (SSP) Architecture

To solve this physical barrier, CAN FD hardware controllers implement **Transmitter Delay Compensation (TDC)**:
1. When transmitting in the fast data phase, the controller starts an internal counter when driving the falling edge of a transmitted bit on `TXD`.
2. The counter runs until the edge returns on `RXD`, measuring the exact real-time loop delay:
   $$\text{Measured Delay} = t_{loop\_actual}$$
3. The controller dynamically sets a **Secondary Sample Point (SSP)** displaced from the transmitted edge:
   $$SSP = t_{loop\_actual} + TDCO$$
   *(where $TDCO$ is the Transmitter Delay Compensation Offset, typically set to $50\% - 75\%$ of the fast bit time).*

```text
 ┌─────────────────────────────────────────────────────────────┐
 │           CAN FD Bit Timing Specification Matrix            │
 ├─────────────────────────┬─────────────────┬─────────────────┤
 │ Parameter               │ Nominal Phase   │ Data Phase      │
 ├─────────────────────────┼─────────────────┼─────────────────┤
 │ Target Bitrate          │ 500 kbps        │ 2.0 Mbps        │
 │ Bit Duration ($T_{bit}$)│ 2000 ns         │ 500 ns          │
 │ Peripheral Clock        │ 80 MHz          │ 80 MHz          │
 │ Prescaler ($BRP$)       │ 10              │ 2               │
 │ Quanta Duration ($t_q$) │ 125 ns          │ 25 ns           │
 │ Total Quanta ($N_{tq}$) │ 16              │ 20              │
 │ Sample Point            │ 87.5%           │ 75.0% (via SSP) │
 └─────────────────────────┴─────────────────┴─────────────────┘
```

---

## 4. Bus Length, Topologies & Capacitive Budgeting

Signal propagation in copper twisted-pair cable travels at approximately **$5\,\text{ns/meter}$** (approx. $2/3$ the speed of light). Because every transmitting node must be capable of receiving a bit within the propagation segment during bitwise arbitration, the maximum cable length is strictly governed by the bitrate:

$$2 \times \Big( (L_{bus} \times \tau_{prop}) + t_{transceiver\_loop} \Big) \le Prop\_Seg \times t_q$$

### 4.1 Bitrate vs. Maximum Cable Length Benchmark

| CAN Bitrate | Bit Time ($NBT$) | Max Trunk Bus Length ($L_{bus}$) | Max Individual Stub Length ($L_{stub}$) |
| :--- | :--- | :--- | :--- |
| **1000 kbps (1 Mbps)** | $1000\,\text{ns}$ | **25 to 40 meters** | $< 0.3\,\text{meters}$ |
| **500 kbps** | $2000\,\text{ns}$ | **100 meters** | $< 1.0\,\text{meter}$ |
| **250 kbps** | $4000\,\text{ns}$ | **250 meters** | $< 2.5\,\text{meters}$ |
| **125 kbps** | $8000\,\text{ns}$ | **500 meters** | $< 5.0\,\text{meters}$ |
| **50 kbps** | $20,000\,\text{ns}$ | **1,000 meters (1 km)** | $< 10.0\,\text{meters}$ |

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
1. **Differential Characteristic Impedance**: Route CAN_H and CAN_L as a differential pair with $Z_{diff} = 120\,\Omega \pm 10\%$.
2. **Trace Length Matching**: Keep trace length mismatch between CAN_H and CAN_L strictly below **$2.0\,\text{mm}$** to prevent converting differential signals into common-mode EMI radiation.
3. **Component Placement Priority**:
   - Place TVS protection diodes (e.g., Nexperia `PESD2CAN`) as close as physically possible to the board connector pins before any traces reach the choke or transceiver.
   - Place the Common-Mode Choke (e.g., TDK `ACT45B-510-2P`) directly adjacent to the TVS diodes.
   - Place split termination resistors ($60.4\,\Omega \pm 1\%$) right at the transceiver side of the choke.
4. **Galvanic Isolation**: For industrial automation and EV battery management systems (BMS) where ground potential differences exceed $5\,\text{V}$, employ isolated transceivers (e.g., TI `ISO1042`, ADI `ADM3053`) with $\ge 2.5\,\text{kV}_{RMS}$ reinforced isolation.

---

## 6. Root Cause Analysis (RCA) Troubleshooting Matrix

When debugging failed CAN bring-ups on the bench, consult this root-cause diagnostic matrix:

| Observed Symptom | Oscilloscope / Logic Analyzer Signature | Probable Root Cause | Verification & Corrective Action |
| :--- | :--- | :--- | :--- |
| **Node transmits frame, immediately flags ACK Error and retries continuously until Bus-Off.** | Dominant frame is driven cleanly, but the ACK slot remains Recessive (no dominant pulse). Continuous re-transmissions. | **Sole node on the bus** or disconnected receiver. | CAN requires at least one active receiving node to acknowledge frames. Check cable harness or connect a second node/CAN analyzer. |
| **Severe ringing, reflections, and deformed bit edges on oscilloscope.** | Signal edges overshoot $> 4\,\text{V}$ with underdamped oscillations lasting $> 200\,\text{ns}$. | **Missing or double termination resistors**. | Measure DC resistance between CAN_H and CAN_L with power OFF. Correct reading must be **$60\,\Omega$** ($120\,\Omega \parallel 120\,\Omega$). If $120\,\Omega$, one terminator is missing. If $< 40\,\Omega$, too many terminators are installed. |
| **All transmitted frames result in continuous Stuff Errors after SOF.** | Bus drops to Dominant and stays low for 6 bit times (Error Flag) right after the arbitration field. | **Mismatched Baud Rate** or inverted CAN_H / CAN_L wiring. | Verify baud rate prescalers using `tools/can_calc.py`. Check physical wiring: CAN_H should sit at $2.5\,\text{V}$ idle and rise to $3.5\,\text{V}$; CAN_L should drop to $1.5\,\text{V}$. |
| **Communication works at 250 kbps but fails completely at 1 Mbps.** | Bits are decoded incorrectly towards the end of long frames; ACK slot is missed. | **Propagation delay exceeds Prop_Seg budget** or stub lines exceed length limits ($> 0.3\,\text{m}$). | Recalculate Time Quanta to shift Sample Point later ($75\% - 87.5\%$). Shorten stub taps or replace star topology with a daisy-chained linear trunk. |
| **CAN FD frames transmit nominal header but abort with Bit Error at BRS.** | Frame is valid up to the BRS bit, then an immediate Error Frame occurs in the fast data payload phase. | **Transmitter Delay Compensation (TDC) disabled** or SSP offset incorrectly tuned. | Enable TDC in the CAN FD controller registers. Configure TDCO to match transceiver loopback delay ($t_{loop} \approx 150\,\text{ns}$). |
| **Bus enters Bus-Off state immediately upon connecting new node.** | Bus differential voltage collapses; controller TEC counter jumps past 255. | **Node configured with inverted polarity** or TX pin shorted to Ground. | Verify transceiver TXD is idling HIGH ($3.3\text{V}$ or $5\text{V}$). Check for damaged transceiver driver stage. |
