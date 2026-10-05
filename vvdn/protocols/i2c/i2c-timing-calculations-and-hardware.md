# I2C AC Timing Specifications, Pull-Up Calculations & Hardware Engineering

This document provides a comprehensive hardware and firmware engineering reference for **I2C AC Timing Specifications, Pull-Up Resistor Calculations, Bus Capacitance Budgeting, PCB Layout, and Signal Integrity Troubleshooting**.

---

## 1. Complete I2C AC Timing Specifications

The electrical performance of an I2C bus is governed by the official NXP I2C Specification (UM10204). The table below details all AC timing parameters across Standard, Fast, and Fast-mode Plus operating tiers:

```text
       ┌───┐                                                 ┌───┐
SCL  ──┘   └───┐                                         ┌───┘   └───
               │◄────── tLOW ──────►│◄───── tHIGH ──────►│
               │                    │                    │
SDA  ──────────┼────────────────────┼──────────[ DATA ]──┼───────────
               │                    │◄─ tSU;DAT ─►│      │
               │◄──── tHD;DAT ─────►│             │      │
```

| Parameter Symbol | Parameter Description | Standard-mode (Sm) (100 kHz) | Fast-mode (Fm) (400 kHz) | Fast-mode Plus (Fm+) (1.0 MHz) | Unit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| f_SCL | SCL Clock Frequency | 0 to 100 | 0 to 400 | 0 to 1000 | kHz |
| t_BUF | Bus Free Time Between STOP and START | >= 4.7 | >= 1.3 | >= 0.5 | µs |
| t_HD;STA | Hold Time for START / Repeated START | >= 4.0 | >= 0.6 | >= 0.26 | µs |
| t_LOW | SCL Clock LOW Period | >= 4.7 | >= 1.3 | >= 0.5 | µs |
| t_HIGH | SCL Clock HIGH Period | >= 4.0 | >= 0.6 | >= 0.26 | µs |
| t_SU;STA | Setup Time for Repeated START (S_r) | >= 4.7 | >= 0.6 | >= 0.26 | µs |
| t_HD;DAT | Data Hold Time | >= 0 (typ 300 ns) | >= 0 (typ 300 ns) | >= 0 | µs |
| t_SU;DAT | Data Setup Time | >= 250 | >= 100 | >= 50 | ns |
| t_r | Rise Time of SDA and SCL (30\%-> 70\%) | <= 1000 | <= 300 | <= 120 | ns |
| t_f | Fall Time of SDA and SCL (70\%-> 30\%) | <= 300 | <= 300 | <= 120 | ns |
| t_SU;STO | Setup Time for STOP Condition | >= 4.0 | >= 0.6 | >= 0.26 | µs |
| t_SP | Pulse Width of Suppressed Spikes | N/A | >= 50 | >= 50 | ns |
| C_b | Maximum Allowed Capacitive Load per Line| <= 400 | <= 400 | <= 550 | pF |
| I_OL | Output Fall Sink Current (V_OL=0.4 V)| >= 3.0 | >= 3.0 | >= 20.0 | mA |

---

## 2. Mathematical Pull-Up Resistor (R_p) Sizing

Selecting the correct pull-up resistor is the single most critical hardware design step for an I2C bus. The value of R_p is strictly bounded by two physical constraints:
1. **R_p(max)**: Set by the **maximum allowable rise time (t_r)** and **bus capacitance (C_b)**.
2. **R_p(min)**: Set by the **maximum sink current (I_OL)** of the internal NMOS drivers and the supply voltage (V_DD).

```text
              0 Ω                                                            Infinite Ω
               ◄──────────────────────────────┬──────────────────────────────►
                                              │
              [ ILLEGAL: Too Low ]     [ SAFE OPERATING WINDOW ]     [ ILLEGAL: Too High ]
              ────────────────────     ─────────────────────────     ─────────────────────
              NMOS Sink Overcurrent    Complies with all I2C Specs   Rise Time Too Slow (Violation)
              Vol > 0.4V (Bad Low)     Clean edges, low power        Clock rounding, Bit errors
                                       │                       │
                                       ▲                       ▲
                                    Rp(min)                 Rp(max)
```

---

### 2.1 Derivation of Maximum Pull-Up Resistance (R_p(max))

When an I2C device releases SDA or SCL, the line charges through R_p according to the classic first-order RC charging equation:
```
V(t) = V_DD * [ 1 - exp(-t / (R_p * C_b)) ]
```

Where:
- V(t): Instantaneous line voltage at elapsed time t (V)
- V_DD: I2C bus pull-up rail voltage (V)
- t: Time elapsed since the open-drain transistor released the line (s)
- R_p: Pull-up resistor value (Ω)
- C_b: Total bus capacitance to ground (F)

The I2C specification defines the **rise time (t_r)** as the time required for the voltage to transition from V_IL = 0.3 * V_DD to V_IH = 0.7 * V_DD.

#### Step-by-Step Derivation:
1. Find time t_1 when V(t_1) = 0.3 * V_DD:
   ```
0.3 * V_DD = V_DD (1 - e^-t_1 / (R_p C_b))
```
   ```
e^-t_1 / (R_p C_b) = 1 - 0.3 = 0.7 => -t_1 / (R_p C_b) = ln(0.7) => t_1 = -R_p C_b ln(0.7) ≈ 0.3567 * R_p C_b
```

2. Find time t_2 when V(t_2) = 0.7 * V_DD:
   ```
0.7 * V_DD = V_DD (1 - e^-t_2 / (R_p C_b))
```
   ```
e^-t_2 / (R_p C_b) = 1 - 0.7 = 0.3 => -t_2 / (R_p C_b) = ln(0.3) => t_2 = -R_p C_b ln(0.3) ≈ 1.2040 * R_p C_b
```

3. The total rise time t_r is t_2 - t_1:
   ```
t_r = t_2 - t_1 = R_p C_b [ln(0.7) - ln(0.3)] = R_p C_b ln(0.7 / 0.3) = R_p C_b ln(7 / 3)
```
   ```
ln(7 / 3) ≈ 0.84729786 ≈ 0.8473
```
   ```
t_r = 0.8473 * R_p * C_b
```

4. Rearranging for R_p(max):
   ```
mathbf{R_p(max) = t_r(max) / (0.8473 * C_b)}
```

---

### 2.2 Derivation of Minimum Pull-Up Resistance (R_p(min))

When any device asserts a logic LOW, its internal NMOS sinks current from V_DD through R_p:
```
I_sink = (V_DD - V_OL) / R_p
```

To guarantee that the LOW-level voltage remains below the maximum allowable threshold (V_OL(max) = 0.4 V) while staying within the driver's rated sink capacity (I_OL, typically 3.0 mA for Standard/Fast mode):

```
mathbf{R_p(min) = (V_DD - V_OL(max)) / I_OL}
```

---

### 2.3 Worked Numerical Design Examples

#### Case 1: 3.3V Fast-mode (400 kHz) System with C_b = 180 pF
- **Given Parameters**:
  - V_DD = 3.3 V
  - Speed: Fast-mode (400 kHz) => t_r(max) = 300 ns, I_OL = 3.0 mA, V_OL = 0.4 V
  - Total estimated bus capacitance: C_b = 180 pF

1. **Calculate R_p(min)**:
   ```
R_p(min) = (3.3 V - 0.4 V) / (3.0 * 10^-3 A) = 2.9 V / 0.003 A ≈ 966.7 Ω
```

2. **Calculate R_p(max)**:
   ```
R_p(max) = (300 * 10^-9 s) / (0.8473 * (180 * 10^-12 F)) = (300 * 10^-9) / (1.5251 * 10^-10) ≈ 1967 Ω \ (1.97 kΩ)
```

3. **Engineering Selection**:
   - The valid resistor window is **967 Ω <= R_p <= 1967 Ω**.
   - Standard E24 Resistors in this window: 1.0 kΩ, 1.1 kΩ, 1.2 kΩ, 1.3 kΩ, 1.5 kΩ, 1.6 kΩ, 1.8 kΩ.
   - **Recommended Choice: 1.5 kΩ or 1.8 kΩ**.
   - With R_p = 1.5 kΩ:
     ```
t_r = 0.8473 * 1500 * (180 * 10^-12) = 228.8 ns (< 300 ns spec, PASS)
```
     ```
I_sink = (3.3 - 0.4) / 1500 = 1.93 mA (< 3.0 mA spec, PASS)
```

---

#### Case 2: 5.0V Standard-mode (100 kHz) High-Capacitance Bus (C_b = 350 pF)
- **Given Parameters**:
  - V_DD = 5.0 V, t_r(max) = 1000 ns, I_OL = 3.0 mA, V_OL = 0.4 V, C_b = 350 pF

1. **Calculate R_p(min)**:
   ```
R_p(min) = (5.0 V - 0.4 V) / 0.003 A = 4.6 V / 0.003 A ≈ 1533 Ω \ (1.53 kΩ)
```

2. **Calculate R_p(max)**:
   ```
R_p(max) = (1000 * 10^-9 s) / (0.8473 * (350 * 10^-12 F)) = (1000 * 10^-9) / (2.9656 * 10^-10) ≈ 3372 Ω \ (3.37 kΩ)
```

3. **Engineering Selection**:
   - Valid window: **1.53 kΩ <= R_p <= 3.37 kΩ**.
   - **Recommended Standard Choice: 2.2 kΩ or 2.7 kΩ**.

---

## 3. Bus Capacitance (C_b) Budgeting

Bus capacitance C_b is the sum of three physical contributors:
```
C_b = C_trace + Sum(C_pin) + C_cable
```

Where:
- C_b: Total bus capacitive load per signal line (pF)
- C_trace: Parasitic capacitance of PCB copper traces (~1.5 to 2.5 pF/inch) (pF)
- Sum(C_pin): Combined input pin capacitance of all connected transceivers and MCUs (pF)
- C_cable: Parasitic capacitance of external wiring harness or cable (~30 to 60 pF/m) (pF)

```text
                                         Bus Line (SDA / SCL)
    ───────────────────────────────────────────┬───────────────────────────┬─────────────
                                               │                           │
                                            [Cpin 1]                    [Cpin 2]
                                               │                           │
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒┴▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒┴▒▒▒▒▒▒▒▒▒▒▒▒▒
    ▲ [Ctrace] Distributed Microstrip Capacitance across FR4 Dielectric to GND Plane
```

1. **PCB Trace Capacitance (C_trace)**:
   - For standard 4-layer FR4 boards (H = 0.1--0.2 mm prepreg, varepsilon_r ≈ 4.2--4.5):
     ```
Trace Capacitance ≈ 1.5 to 2.5 pF per inch \ (0.6 to 1.0 pF per cm)
```
   - A 15 cm (6 inch) PCB routing run contributes ≈ 10--15 pF.
2. **Device Pin Capacitance (C_pin)**:
   - Every IC input pin (controller + all target ICs) contributes internal pad and bond-wire capacitance.
   - Typically **5 to 10 pF per device**.
   - Connecting 8 sensors contributes 8 * 10 pF = 80 pF.
3. **Cables & Connectors (C_cable)**:
   - Off-board wiring, ribbon cables, or harness connections:
     ```
Ribbon Cable / Twisted Pair ≈ 30 to 60 pF per meter
```
   - A 1-meter external cable alone can add 50 pF.

---

## 4. Extending I2C Distance & High-Capacitance Networks

When bus capacitance exceeds the standard 400 pF limit or bus length exceeds 1--2 meters, passive pull-up resistors become ineffective. Use the following hardware solutions:

### 4.1 Active Rise-Time Accelerators (e.g., LTC4311)
- Connects in parallel with the bus lines.
- Detects the start of a rising edge (dV/dt).
- When the bus passes a threshold, it activates a high-current slew-rate boost circuit that injects current directly into the line for sim 30 ns, snapping the rising edge to V_DD in < 50 ns regardless of large C_b (up to 4000 pF).

```text
                  +VDD
                    │
              ┌─────┴─────┐
              │  LTC4311  │ (Monitors dV/dt; injects pulsed current
              │Accelerator│  to defeat high bus capacitance)
              └─────┬─────┘
                    │
  SDA/SCL ──────────┴────────────────────────── (Sharp edges restored)
```

### 4.2 Bidirectional Bus Buffers & Repeaters (e.g., PCA9515A / PCA9600)
- Isolates two segments of the bus electrically.
- Capacitance on Segment A (C_b1) does not load Segment B (C_b2).
- Allows multi-board backplanes and long cable runs.

### 4.3 Differential I2C (e.g., PCA9615)
- Translates single-ended SDA and SCL into **two twisted pairs of differential signals** (DSDA+ / DSDA- and DSCL+ / DSCL-).
- Immunity to severe common-mode EMI noise in automotive and industrial environments.
- Extends reliable I2C operation up to **3 meters at 1 MHz, or 20+ meters at 100 kHz**.

---

## 5. PCB Layout, Signal Integrity & Routing Rules

Follow these layout rules during Altium/KiCad PCB routing:

```text
             INCORRECT (Crosstalk Hazard):
             ───────────────────────────── SCL (Fast clock edges induce noise on SDA)
             ───────────────────────────── SDA

             CORRECT (Ground-Shielded / Separated):
             ───────────────────────────── SCL
             ═════════════════════════════ GND Guard Trace (Shielding)
             ───────────────────────────── SDA
```

1. **Avoid Parallel Close-Coupled SDA and SCL Traces**:
   - Running SDA directly adjacent to SCL over long distances creates mutual capacitive coupling.
   - SCL clock edges will inject capacitive spike transients into SDA, triggering false START or STOP conditions.
   - Maintain a minimum separation of **3 * Trace Width (3W rule)**, or route a grounded guard trace between them.
2. **Series Damping Resistors (R_s)**:
   - Insert series resistors (R_s = 22 Ω to 100 Ω) on SDA and SCL located immediately adjacent to the microcontroller pins.
   - R_s dampens ringing, absorbs reflections caused by fast active falling edges, and provides basic ESD / overcurrent protection for IO pins.
3. **Solid Ground Reference**:
   - Always route I2C traces over an unbroken Ground Plane (Layer 2) to maintain controlled impedance and minimize return path inductance.
   - Never route I2C traces across split ground planes or power plane voids.

---

## 6. Bench RCA Troubleshooting Matrix

The table below diagnoses the root causes of the most common I2C hardware and firmware anomalies encountered during board bring-up:

| Oscilloscope / Analyzer Symptom | Root Cause | Underlying Physics | Corrective Engineering Action |
| :--- | :--- | :--- | :--- |
| **Address NACK (No ACK from peripheral)** | Wrong Address, Device Unpowered, or in Reset | Receiver does not assert ACK (SDA remains HIGH on 9th clock). | 1. Verify 7-bit vs 8-bit shifted address format.<br>2. Check V_DD pin on sensor with DMM.<br>3. Verify RESET pin is pulled HIGH (not held in reset). |
| **Rounded, sluggish rising edges (t_r > 300 ns)** | Pull-Up Resistor (R_p) Too High or Excessive C_b | RC time constant τ = R_p C_b is too large; signal fails to reach V_IH in time. | Lower R_p value (e.g. swap 10 kΩ to 2.2 kΩ or 1.5 kΩ). |
| **Logic LOW voltage (V_OL) is too high (> 0.5 V)** | Pull-Up Resistor (R_p) Too Low | R_p pulls too hard; NMOS cannot sink current without significant I_OL * R_DS(on) voltage drop. | Increase R_p value towards R_p(min) or use driver with higher sink capacity. |
| **Bus Stuck: SDA permanently held LOW (0 V)** | Slave interrupted during read cycle | Target device waiting for clock pulse to shift out bit `0`; MCU reboots into IDLE. | Implement the 9-clock bus recovery sequence in microcontroller `I2C_Init()`. |
| **Bus Stuck: SCL permanently held LOW (0 V)** | Target executing infinite Clock Stretch | Peripheral internal firmware hung or awaiting ADC conversion that never completes. | 1. Check peripheral supply voltage.<br>2. Implement hardware reset line toggle or power cycle via P-MOSFET high-side switch. |
| **Spurious START / STOP glitches mid-byte** | Crosstalk between SCL and SDA | Fast SCL edge injects capacitive spike on SDA that crosses logic threshold while SCL is HIGH. | 1. Separate traces on PCB.<br>2. Add 22 Ω--47 Ω series resistors.<br>3. Verify 50 ns spike filter is enabled in MCU registers. |
| **Severe ringing and overshoot on falling edges** | Long unterminated stub traces | Fast NMOS turn-on induces high dI/dt across trace inductance. | Add 33 Ω to 100 Ω series damping resistors (R_s) close to driver pins. |
