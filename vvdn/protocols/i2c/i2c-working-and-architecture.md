# I2C Protocol: Working Mechanism, Electrical Principles & Hardware Architecture

This document provides a comprehensive, deep-dive technical analysis of the **I2C (Inter-Integrated Circuit) Physical Layer and Working Mechanisms**. It explores the electrical open-drain topology, the Wired-AND property, bidirectional level translation, clock synchronization, hardware clock stretching, non-destructive multi-master arbitration, input glitch filtering, and bus fault recovery.

---

## 1. Physical Layer: Open-Drain / Open-Collector Bus

Unlike standard digital interfaces (such as SPI or UART) that utilize **push-pull** output drivers, I2C devices connect to the bus using **open-drain** (for CMOS devices) or **open-collector** (for BJT devices) output stages.

### 1.1 Internal Driver Topology

In an open-drain stage, the output pin is connected exclusively to the drain of an internal N-channel MOSFET (NMOS). The source of the MOSFET is tied to Ground ($V_{SS}$).

```text
       Controller / Target Internal Silicon                  Physical Bus Line (SDA or SCL)
      ┌───────────────────────────────────────────────┐                  │
      │                                               │                  │
      │   Output Data ───┐                            │                  │
      │                  ▼                            │                  │
      │                ┌───┐                          │                  │
      │   Gate Driver  │   ├─────── Gate              │                  │
      │                └───┘          │               │                  │
      │                             ──┴──             │                  │
      │                        NMOS ──┬── Drain ──────┼──────────────────┘
      │                               │               │
      │                             Source            │
      │                               │               │
      │                              GND              │
      │                                               │
      │   Input Buffer (Schmitt Trigger)              │
      │                ┌───┐                          │
      │   Bus Sense ◄──┤   ├──────────────────────────┼──────────────────┐
      │                └───┘                          │                  │
      └───────────────────────────────────────────────┘                  │
                                                                         │
```

- **Driving Logic LOW ('0')**: The device turns ON the internal NMOS transistor. The transistor saturates, sinking current from the bus directly to Ground. The bus voltage drops to $V_{OL}$ (typically $< 0.4\,\text{V}$).
- **Driving Logic HIGH ('1')**: The device turns OFF the internal NMOS transistor. The transistor enters a high-impedance (High-Z) cut-off state. The device does not actively drive high voltage. Instead, it **releases the line**, allowing an external passive pull-up resistor ($R_p$) to pull the voltage up to $V_{DD}$.

### 1.2 The Wired-AND Principle

Because no device actively drives the bus HIGH, multiple device pins can be tied directly together without risk of hardware damage.

```text
                  +VDD (e.g., +3.3V)
                    │
                   [Rp] (Pull-Up Resistor)
                    │
  Bus Voltage (Vbus)├────────────────┬────────────────┬──────────────
                    │                │                │
                 Drain            Drain            Drain
                 ──┴── NMOS       ──┴── NMOS       ──┴── NMOS
                 ──┬── Device A   ──┬── Device B   ──┬── Device C
                   │                │                │
                  GND              GND              GND
```

This arrangement creates a physical **Wired-AND** logic function:
$$\text{Bus State} = \text{Device A} \ \text{AND} \ \text{Device B} \ \text{AND} \ \text{Device C}$$

1. If **all devices** release the line (all NMOS OFF), no current flows to ground. The pull-up resistor pulls the bus to $V_{DD}$ ($\text{Bus} = \text{HIGH} = 1$).
2. If **any single device** turns its NMOS ON, current flows from $V_{DD}$ through $R_p$ and the NMOS to Ground, pulling the entire bus LOW ($\text{Bus} = \text{LOW} = 0$).

> [!WARNING]
> **Push-Pull Danger**: If standard push-pull drivers were used in I2C, a condition where Device A drives HIGH ($3.3\,\text{V}$) while Device B drives LOW ($0\,\text{V}$) would form a low-impedance short-circuit across the supply rails. The resulting shoot-through current ($> 50\text{--}100\,\text{mA}$) would destroy the output transistors. The open-drain Wired-AND architecture fundamentally prevents bus contention damage.

---

## 2. Asymmetric Edge Transitions: Active Fall vs. Passive Rise

Because driving LOW is active (low-resistance NMOS path to Ground) and driving HIGH is passive (high-resistance RC charging path), I2C signal edges are fundamentally asymmetric:

```text
Voltage
 ^
 │       Active Fall (Fast)            Passive Rise (RC Curve)
Vdd ───┐     │                                  . - - - 
 │     │     │                                . '
 │     │     ▼                             . '
 │     │   ┌───┐                         . ' (Slow exponential rise)
 │     │   │   │                       . '
0V ────┴───┘   └──────────────────────'─────────────────► Time
```

1. **Falling Edge ($t_f$)**: The internal NMOS turns on with an on-resistance $R_{DS(on)}$ of typically $10\text{--}50\,\Omega$. Bus capacitance ($C_b$) discharges rapidly to ground. Fall times are typically very fast ($< 20\text{--}50\,\text{ns}$).
2. **Rising Edge ($t_r$)**: The NMOS turns off. The bus voltage rises according to the classic first-order RC charging curve:
   $$V(t) = V_{DD} \left(1 - e^{-\frac{t}{R_p C_b}}\right)$$
   Where $R_p$ is typically $1\,\text{k}\Omega\text{ to }10\,\text{k}\Omega$ and $C_b$ is $50\text{--}400\,\text{pF}$. The rise time is orders of magnitude slower than the fall time.

> [!IMPORTANT]
> Because the rise time is determined strictly by the $R_p \times C_b$ time constant, adding more devices or longer PCB traces increases $C_b$, slowing the rise time. If the rise time is too slow, the clock or data signal fails to reach the logic threshold $V_{IH}$ before the bit sampling window closes, leading to bus corruption.

---

## 3. Bus Voltages & Bidirectional Level Shifting

Modern embedded systems frequently connect microcontrollers operating at $3.3\,\text{V}$ or $1.8\,\text{V}$ with legacy sensors or peripheral chips operating at $5.0\,\text{V}$.

### 3.1 Logic Threshold Rules
According to the I2C specification:
- **Maximum LOW-level input voltage ($V_{IL}$)**: $0.3 \times V_{DD}$ (e.g., $0.99\,\text{V}$ for $3.3\,\text{V}$; $1.5\,\text{V}$ for $5.0\,\text{V}$).
- **Minimum HIGH-level input voltage ($V_{IH}$)**: $0.7 \times V_{DD}$ (e.g., $2.31\,\text{V}$ for $3.3\,\text{V}$; $3.5\,\text{V}$ for $5.0\,\text{V}$).
- **Maximum Output LOW level ($V_{OL}$)**: Typically $0.4\,\text{V}$ at nominal sink current ($3\,\text{mA}$).

### 3.2 Discrete MOSFET Bidirectional Level Shifter Circuit

To bridge two bus sections at different voltages (e.g., $V_{DD1} = 1.8\,\text{V}$ or $3.3\,\text{V}$, and $V_{DD2} = 5.0\,\text{V}$), the standard industry circuit uses an N-channel MOSFET (such as BSS138) with an integrated body diode:

```text
             +VDD1 (3.3V)                   +VDD2 (5.0V)
                  │                              │
                 [Rp1]                          [Rp2]
                  │                              │
  Low-Voltage ────┼────────── Source             │
  Side (SDA1)     │             ──┬──            │
                  │          NMOS ──┴── Drain ───┼────────── High-Voltage
                  │               │              │           Side (SDA2)
                  │             Gate             │
                  │               │              │
                  │             +VDD1            │
                  │             (3.3V)           │
                  │                              │
```

#### Operational States of the Level Shifter:

1. **State 1: Both Sides High (Idle State)**
   - Neither side is driving LOW.
   - SDA1 is pulled to $3.3\,\text{V}$ by $R_{p1}$.
   - Gate is tied to $V_{DD1}$ ($3.3\,\text{V}$).
   - $V_{GS} = V_G - V_S = 3.3\,\text{V} - 3.3\,\text{V} = 0\,\text{V}$.
   - The MOSFET is **OFF**.
   - SDA2 is pulled to $5.0\,\text{V}$ by $R_{p2}$.
   - Both bus segments remain at their respective HIGH logic voltages.

2. **State 2: Low-Voltage Side Drives LOW ($3.3\,\text{V}$ side pulls to $0\,\text{V}$)**
   - Controller or sensor on SDA1 activates internal NMOS, pulling SDA1 to $0\,\text{V}$.
   - Gate is at $3.3\,\text{V}$, Source drops to $0\,\text{V}$.
   - $V_{GS} = 3.3\,\text{V} - 0\,\text{V} = 3.3\,\text{V} > V_{GS(th)}$ (threshold is typically $\sim 1.2\,\text{V}$).
   - The MOSFET turns **ON** hard.
   - The conducting channel shorts Drain to Source, discharging SDA2 to $0\,\text{V}$.
   - Result: Both sides become LOW ($0\,\text{V}$).

3. **State 3: High-Voltage Side Drives LOW ($5.0\,\text{V}$ side pulls to $0\,\text{V}$)**
   - Target on SDA2 activates internal NMOS, pulling SDA2 to $0\,\text{V}$.
   - The MOSFET body diode (anode at Source/SDA1, cathode at Drain/SDA2) becomes forward-biased.
   - SDA1 is initially pulled down through the body diode to $\sim 0.6\,\text{V}$.
   - As SDA1 falls to $0.6\,\text{V}$, $V_{GS} = 3.3\,\text{V} - 0.6\,\text{V} = 2.7\,\text{V} > V_{GS(th)}$.
   - The MOSFET turns **ON** fully, shorting Drain and Source.
   - SDA1 is pulled down completely to Ground ($V_{OL} \approx 0.1\text{--}0.2\,\text{V}$).
   - Result: Both sides become LOW ($0\,\text{V}$).

> [!TIP]
> For production PCBA designs, integrated level-shifter ICs (such as **PCA9306**, **TCA9803**, or **TXS0102**) package these matched MOSFETs and gate-bias networks into compact TSSOP/VSSOP packages with integrated ESD protection and rise-time accelerators.

---

## 4. Controller & Target (Master & Slave) Roles

In modern I2C terminology (formally updated by NXP, IEEE, and OSHWA):
- **Controller** (formerly *Master*): The device that initiates transactions, generates clock pulses on SCL, sends addressing frames, and terminates transactions.
- **Target** (formerly *Slave*): The device addressed by the controller. It responds to instructions, acknowledges bytes, and transmits or receives payload data.

### Responsibilities Matrix:

| Operational Phase | Controller Responsibility | Target Responsibility |
| :--- | :--- | :--- |
| **Bus Initialization** | Configures clock speed, drives initial HIGH state | Listens to bus, initializes internal registers |
| **Transaction Start** | Drives START condition ($S$) | Detects falling SDA edge while SCL is HIGH |
| **Addressing** | Broadcasts 7-bit / 10-bit address + R/W bit | Matches address against internal hardware register |
| **Address Acknowledge** | Releases SDA, clocks 9th SCL pulse, samples ACK | If address matches, pulls SDA LOW during 9th clock |
| **Write Transfer** | Drives 8 data bits onto SDA, clocks SCL | Latches data on SCL rising edge, pulls SDA LOW for ACK |
| **Read Transfer** | Generates SCL clocks, asserts ACK/NACK | Drives data bits on SDA when SCL is LOW |
| **Clock Pacing** | Regulates nominal SCL clock frequency | May hold SCL LOW (Clock Stretching) if busy |
| **Transaction Stop** | Drives STOP condition ($P$) to free the bus | Resets state machine to IDLE, releases all lines |

---

## 5. Clock Synchronization via Wired-AND

In multi-controller networks or when slow targets are present, multiple devices may attempt to influence the SCL clock line simultaneously. SCL synchronization relies on the **Wired-AND** property:

```text
Controller 1 SCL internal: ───┐       ┌───────────┐       ┌───────
                              └───────┘           └───────┘
Controller 2 SCL internal: ───────┐   ┌───────────────┐   ┌───────
                                  └───┘               └───┘
                                      │                   │
Physical SCL Bus (Wired-AND): ────┐   ┌───────────┐   ┌───┐
                                  └───┘           └───┘   └───
                                  ▲                   ▲
                           (Longest LOW)        (Shortest HIGH)
```

1. **Synchronizing the LOW Period**: 
   - When any device's internal clock transitions from HIGH to LOW, it turns on its NMOS, pulling SCL LOW.
   - Devices whose internal clocks were still HIGH sense SCL falling LOW and immediately transition their internal state machines to the LOW phase.
   - The physical SCL line stays LOW until the device with the **longest internal LOW period** turns off its NMOS and releases SCL.
2. **Synchronizing the HIGH Period**:
   - Once all devices release SCL, the pull-up resistor pulls SCL to $V_{DD}$.
   - All devices monitor SCL. As soon as SCL crosses $V_{IH}$, each device starts counting its internal HIGH period timer.
   - The device with the **shortest internal HIGH period** finishes first and pulls SCL LOW again.
3. **Conclusion**:
   - The resulting synchronized clock has a **LOW period governed by the slowest device**, and a **HIGH period governed by the fastest device**.

---

## 6. Hardware Clock Stretching (Flow Control)

**Clock Stretching** is a hardware-level flow control mechanism built into the I2C physical layer. It allows a target to temporarily throttle communication if it cannot keep up with the controller's clock rate.

### 6.1 Mechanical Walkthrough

```text
SCL Controller: ───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐
                   └───┘   └───┘   └───┘   └───┘   └───
                                     │
Target Holds SCL:                    └─────────────┐ (Target holds NMOS ON)
                                                   │
Physical SCL:   ───┐   ┌───┐   ┌───┐               ┌───┐
                   └───┘   └───┘   └───[ STRETCHED ]───┘
                                       ▲           ▲
                                   Wait State   Released
```

1. The controller finishes clocking a byte (e.g., after the 8th or 9th bit) and drives SCL LOW.
2. The target device is busy (e.g., storing data into internal non-volatile EEPROM, executing an ADC conversion, or servicing a high-priority CPU interrupt).
3. The target's internal hardware pulls the SCL line LOW and keeps its NMOS turned ON.
4. When the controller attempts to release SCL to generate the next HIGH clock pulse, it senses the physical line voltage.
5. Because the target is holding SCL LOW, the controller detects that $\text{SCL} < V_{IH}$.
6. The controller pauses its state machine and enters a wait state.
7. Once the target completes its internal processing, it turns off its NMOS, releasing SCL.
8. The pull-up resistor pulls SCL to $V_{DD}$. The controller senses the rising edge and resumes normal clocking.

### 6.2 Clock Stretching Hazards & Industry Workarounds

While clock stretching is an official feature of I2C, it is one of the most frequent causes of embedded system lockups:

> [!CAUTION]
> **Silicon Errata & Lockups**:
> - **Raspberry Pi BCM2835 Clock-Stretch Bug**: Broadcom silicon on older Raspberry Pi models had a hardware bug where clock stretching during an ACK bit caused bit corruption and frozen transfers.
> - **Infinite Stretch (Bus Freeze)**: If a buggy sensor hangs while holding SCL LOW, no other transactions can occur on the entire bus.
> - **SMBus Comparison**: The SMBus (System Management Bus) specification resolves this by enforcing a hard **35 ms maximum clock low timeout** ($t_{TIMEOUT} = 25\text{--}35\,\text{ms}$). If SCL is held LOW for longer than 35 ms, SMBus devices reset their bus interface. Pure I2C does not mandate a timeout, meaning microcontroller firmware must implement software watchdog timers to abort stalled transactions.

---

## 7. Multi-Master Bus Arbitration (Collision Avoidance)

I2C supports true multi-controller operation where two or more controllers can initiate communication on the same bus without requiring arbitration lines or causing packet corruption.

Arbitration occurs **on the SDA line** while the SCL line is HIGH. It relies on the principle that:
$$\text{A LOW bit ('0') dominates a HIGH bit ('1') on a Wired-AND bus}$$

### 7.1 Arbitration Step-by-Step Example

Suppose Controller 1 and Controller 2 both detect an idle bus and simultaneously generate a START condition. Both attempt to transmit to different target addresses:
- **Controller 1** wants to transmit address: `0b1010001` (`0x51`)
- **Controller 2** wants to transmit address: `0b1010100` (`0x54`)

```text
Bit Position:     Bit 7   Bit 6   Bit 5   Bit 4   Bit 3   Bit 2   Bit 1   Bit 0
Controller 1:       1       0       1       0       0       0       1      (R/W)
Controller 2:       1       0       1       0       1       0       0      (R/W)
                                                    ▲
                                            Arbitration Lost!
                                            Ctrl 2 wants HIGH,
                                            Ctrl 1 pulls LOW.
```

```text
Clock (SCL): ──┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐
               └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───
                 1       2       3       4       5       6       7
                                                 │
Ctrl 1 SDA:  ──────┐       ┌───────┐             │
                   └───────┘       └─────────────┼───────────────── (Asserts LOW: '0')
Ctrl 2 SDA:  ──────┐       ┌───────┐       ┌─────┼───────────────── (Asserts HIGH: '1')
                   └───────┘       └───────┘     │
                                                 ▼
Physical SDA:──────┐       ┌───────┐             ┌───────────────── (Physical wire is LOW)
                   └───────┘       └─────────────┘
                                                 ▲
                                     Ctrl 2 reads SDA=0,
                                     wants SDA=1 -> BACKS OFF!
```

#### What Happens during the Arbitration Phase:
1. **Bit 7 (`1`)**: Both controllers release SDA. Wire is HIGH. Both read HIGH. Match.
2. **Bit 6 (`0`)**: Both pull SDA LOW. Wire is LOW. Both read LOW. Match.
3. **Bit 5 (`1`)**: Both release SDA. Wire is HIGH. Both read HIGH. Match.
4. **Bit 4 (`0`)**: Both pull SDA LOW. Wire is LOW. Both read LOW. Match.
5. **Bit 3**:
   - **Controller 1** wants to send `0`: It activates its NMOS, driving SDA **LOW**.
   - **Controller 2** wants to send `1`: It turns off its NMOS, expecting the line to float **HIGH**.
   - Because Controller 1 is pulling LOW, the physical wire voltage is **LOW ($0\,\text{V}$)**.
   - Every controller samples the physical SDA line whenever SCL is HIGH.
   - Controller 2 samples SDA and sees **LOW ($0\,\text{V}$)** even though its internal register was outputting **HIGH ($1$)**.
   - **Controller 2 detects an immediate arbitration loss!**
6. **Action Taken by Losing Controller (Controller 2)**:
   - Controller 2 turns off its SDA output driver immediately.
   - It does not generate clock pulses on SCL anymore.
   - It seamlessly transitions into **Target receiver mode** in case Controller 1 was actually addressing Controller 2.
7. **Zero Corrupted Bits**:
   - Controller 1 never noticed any conflict. The physical wire maintained Controller 1's intended bit pattern (`0`) without interruption.
   - The transaction proceeds to completion with zero lost packets and zero retries required on the winning side.

---

## 8. Input Stage: Schmitt Triggers & Spike Filters

The electrical environment on high-density PCBs and over off-board wiring introduces noise, inductive ground bounce, and EMI spikes onto the SDA and SCL lines.

To guarantee noise immunity, the I2C physical specification mandates two stages of hardware filtering at the input pins of every compliant device:

```text
                  ┌────────────────────┐    ┌─────────────────┐
  Physical Pin ──►│ 50 ns Spike Filter ├───►│ Schmitt Trigger ├───► Internal I2C Logic
  (SDA or SCL)    │ (Glitch Rejection) │    │  (Hysteresis)   │
                  └────────────────────┘    └─────────────────┘
```

### 8.1 50 ns Spike Suppression Glitch Filter ($t_{SP}$)
- In Fast-mode ($400\,\text{kHz}$) and higher, input stages incorporate an analog low-pass RC spike suppression filter.
- Any pulse on SDA or SCL with a duration **$< 50\,\text{ns}$** is completely suppressed and ignored by the internal silicon.
- This prevents high-frequency inductive switching spikes (e.g. from nearby DC-DC converters or motor PWM lines) from being falsely interpreted as clock edges or START conditions.

### 8.2 Schmitt Trigger Hysteresis ($V_{hys}$)
- I2C inputs must exhibit built-in hysteresis:
  $$V_{hys} \ge 0.05 \times V_{DD} \quad (\text{typically } 0.1 \times V_{DD} \approx 330\,\text{mV at } 3.3\,\text{V})$$
- Slow RC rising edges pass through the logic transition threshold ($0.5 \times V_{DD}$) slowly. Without hysteresis, high-frequency noise superimposed on a slow rising edge would cause the digital input buffer to toggle rapidly between 0 and 1, creating multiple false clock pulses. The Schmitt trigger eliminates this chatter.

---

## 9. Bus Faults & Dynamic Recovery Procedures

The most pervasive hardware failure mode in I2C systems is the **"Stuck Bus"** or **"Hung SDA Line"**.

### 9.1 Root Cause: Interrupted Read Transaction
1. A controller initiates a read transaction from a sensor.
2. The sensor begins shifting out an 8-bit data payload. Bit 3 happens to be a logic `0`, so the sensor turns on its internal NMOS to pull SDA LOW.
3. Suddenly, the controller suffers an unexpected reset (e.g., watchdog reset, Brown-Out Reset, or firmware crash) before finishing the clock pulses.
4. The controller reboots and re-initializes its I2C peripheral as a Controller.
5. The controller samples SDA and finds it **stuck permanently LOW**.
6. The controller cannot generate a valid START condition because a START requires SDA to transition from HIGH to LOW while SCL is HIGH. If SDA is already LOW, no falling edge can be generated.
7. The sensor is completely frozen waiting for its next SCL clock pulse.

```text
Sensor State:    Awaiting Clock Pulse to finish Bit 3 (Driving SDA LOW)
Controller State:Rebooted, waiting for SDA to go HIGH before starting.
Result:          DEADLOCK! The bus is frozen forever.
```

### 9.2 The 9-Clock Pulse Bus Recovery Algorithm

To break this deadlock without power-cycling the board, the microcontroller firmware must implement the **Standard I2C Bus Recovery Routine**:

```text
Step 1: Disable MCU Hardware I2C Peripheral.
Step 2: Configure SCL and SDA pins as general-purpose GPIOs (Open-Drain output with pull-up).
Step 3: Sample SDA. If SDA == HIGH, bus is free. Jump to Step 7.
Step 4: Clock SCL up to 9 times:
        FOR pulse = 1 to 9:
            Drive SCL LOW;
            Delay 5 µs;
            Release SCL HIGH;
            Delay 5 µs;
            IF SDA == HIGH:
                BREAK; // Sensor has released SDA
Step 5: Generate a manual STOP condition:
        Drive SDA LOW;
        Delay 5 µs;
        Release SCL HIGH;
        Delay 5 µs;
        Release SDA HIGH;
Step 6: Re-enable the MCU Hardware I2C Peripheral.
```

```text
SCL Pulses:    ──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐      ┌──────
                 └─┘  └─┘  └─┘  └─┘  └─┘  └─┘  └─┘  └─┘  └──────┘
                  1    2    3    4    5    6    7    8    9      STOP
                                                            │
Target Releases:                                            │
SDA Line:      ─────────────────────────────────────────────┴──────────► HIGH
```

#### Why 9 Pulses Work:
- The target device can be at most 8 bits away from completing the current byte transfer.
- By providing 9 clock pulses on SCL, the target shifts out all remaining data bits until it reaches the 9th bit (the ACK phase).
- In the ACK phase, the target releases SDA so that the master can acknowledge.
- Generating a manual STOP condition immediately after releasing SDA resets the target's internal I2C finite state machine back to the IDLE state.

> [!TIP]
> Always execute this 9-clock recovery routine inside the MCU's `I2C_Init()` driver code prior to configuring the hardware I2C registers during power-on reset.
