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
| $f_{SCL}$ | SCL Clock Frequency | $0$ to $100$ | $0$ to $400$ | $0$ to $1000$ | $\text{kHz}$ |
| $t_{BUF}$ | Bus Free Time Between STOP and START | $\ge 4.7$ | $\ge 1.3$ | $\ge 0.5$ | $\mu\text{s}$ |
| $t_{HD;STA}$ | Hold Time for START / Repeated START | $\ge 4.0$ | $\ge 0.6$ | $\ge 0.26$ | $\mu\text{s}$ |
| $t_{LOW}$ | SCL Clock LOW Period | $\ge 4.7$ | $\ge 1.3$ | $\ge 0.5$ | $\mu\text{s}$ |
| $t_{HIGH}$ | SCL Clock HIGH Period | $\ge 4.0$ | $\ge 0.6$ | $\ge 0.26$ | $\mu\text{s}$ |
| $t_{SU;STA}$ | Setup Time for Repeated START ($S_r$) | $\ge 4.7$ | $\ge 0.6$ | $\ge 0.26$ | $\mu\text{s}$ |
| $t_{HD;DAT}$ | Data Hold Time | $\ge 0$ (typ $300\,\text{ns}$) | $\ge 0$ (typ $300\,\text{ns}$) | $\ge 0$ | $\mu\text{s}$ |
| $t_{SU;DAT}$ | Data Setup Time | $\ge 250$ | $\ge 100$ | $\ge 50$ | $\text{ns}$ |
| $t_r$ | Rise Time of SDA and SCL ($30\%\to 70\%$) | $\le 1000$ | $\le 300$ | $\le 120$ | $\text{ns}$ |
| $t_f$ | Fall Time of SDA and SCL ($70\%\to 30\%$) | $\le 300$ | $\le 300$ | $\le 120$ | $\text{ns}$ |
| $t_{SU;STO}$ | Setup Time for STOP Condition | $\ge 4.0$ | $\ge 0.6$ | $\ge 0.26$ | $\mu\text{s}$ |
| $t_{SP}$ | Pulse Width of Suppressed Spikes | N/A | $\ge 50$ | $\ge 50$ | $\text{ns}$ |
| $C_b$ | Maximum Allowed Capacitive Load per Line| $\le 400$ | $\le 400$ | $\le 550$ | $\text{pF}$ |
| $I_{OL}$ | Output Fall Sink Current ($V_{OL}=0.4\,\text{V}$)| $\ge 3.0$ | $\ge 3.0$ | $\ge 20.0$ | $\text{mA}$ |

---

## 2. Mathematical Pull-Up Resistor ($R_p$) Sizing

Selecting the correct pull-up resistor is the single most critical hardware design step for an I2C bus. The value of $R_p$ is strictly bounded by two physical constraints:
1. **$R_{p(max)}$**: Set by the **maximum allowable rise time ($t_r$)** and **bus capacitance ($C_b$)**.
2. **$R_{p(min)}$**: Set by the **maximum sink current ($I_{OL}$)** of the internal NMOS drivers and the supply voltage ($V_{DD}$).

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

### 2.1 Derivation of Maximum Pull-Up Resistance ($R_{p(max)}$)

When an I2C device releases SDA or SCL, the line charges through $R_p$ according to the classic first-order RC charging equation:
$$V(t) = V_{DD} \left(1 - e^{-\frac{t}{R_p C_b}}\right)$$

The I2C specification defines the **rise time ($t_r$)** as the time required for the voltage to transition from $V_{IL} = 0.3 \times V_{DD}$ to $V_{IH} = 0.7 \times V_{DD}$.

#### Step-by-Step Derivation:
1. Find time $t_1$ when $V(t_1) = 0.3 \times V_{DD}$:
   $$0.3 \times V_{DD} = V_{DD} \left(1 - e^{-\frac{t_1}{R_p C_b}}\right)$$
   $$e^{-\frac{t_1}{R_p C_b}} = 1 - 0.3 = 0.7 \implies -\frac{t_1}{R_p C_b} = \ln(0.7) \implies t_1 = -R_p C_b \ln(0.7) \approx 0.3567 \times R_p C_b$$

2. Find time $t_2$ when $V(t_2) = 0.7 \times V_{DD}$:
   $$0.7 \times V_{DD} = V_{DD} \left(1 - e^{-\frac{t_2}{R_p C_b}}\right)$$
   $$e^{-\frac{t_2}{R_p C_b}} = 1 - 0.7 = 0.3 \implies -\frac{t_2}{R_p C_b} = \ln(0.3) \implies t_2 = -R_p C_b \ln(0.3) \approx 1.2040 \times R_p C_b$$

3. The total rise time $t_r$ is $t_2 - t_1$:
   $$t_r = t_2 - t_1 = R_p C_b \left[\ln(0.7) - \ln(0.3)\right] = R_p C_b \ln\left(\frac{0.7}{0.3}\right) = R_p C_b \ln\left(\frac{7}{3}\right)$$
   $$\ln\left(\frac{7}{3}\right) \approx 0.84729786 \approx 0.8473$$
   $$t_r = 0.8473 \times R_p \times C_b$$

4. Rearranging for $R_{p(max)}$:
   $$\mathbf{R_{p(max)} = \frac{t_{r(max)}}{0.8473 \times C_b}}$$

---

### 2.2 Derivation of Minimum Pull-Up Resistance ($R_{p(min)}$)

When any device asserts a logic LOW, its internal NMOS sinks current from $V_{DD}$ through $R_p$:
$$I_{sink} = \frac{V_{DD} - V_{OL}}{R_p}$$

To guarantee that the LOW-level voltage remains below the maximum allowable threshold ($V_{OL(max)} = 0.4\,\text{V}$) while staying within the driver's rated sink capacity ($I_{OL}$, typically $3.0\,\text{mA}$ for Standard/Fast mode):

$$\mathbf{R_{p(min)} = \frac{V_{DD} - V_{OL(max)}}{I_{OL}}}$$

---

### 2.3 Worked Numerical Design Examples

#### Case 1: 3.3V Fast-mode (400 kHz) System with $C_b = 180\,\text{pF}$
- **Given Parameters**:
  - $V_{DD} = 3.3\,\text{V}$
  - Speed: Fast-mode ($400\,\text{kHz}$) $\implies t_{r(max)} = 300\,\text{ns}$, $I_{OL} = 3.0\,\text{mA}$, $V_{OL} = 0.4\,\text{V}$
  - Total estimated bus capacitance: $C_b = 180\,\text{pF}$

1. **Calculate $R_{p(min)}$**:
   $$R_{p(min)} = \frac{3.3\,\text{V} - 0.4\,\text{V}}{3.0 \times 10^{-3}\,\text{A}} = \frac{2.9\,\text{V}}{0.003\,\text{A}} \approx \mathbf{966.7\,\Omega}$$

2. **Calculate $R_{p(max)}$**:
   $$R_{p(max)} = \frac{300 \times 10^{-9}\,\text{s}}{0.8473 \times (180 \times 10^{-12}\,\text{F})} = \frac{300 \times 10^{-9}}{1.5251 \times 10^{-10}} \approx \mathbf{1967\,\Omega} \ (1.97\,\text{k}\Omega)$$

3. **Engineering Selection**:
   - The valid resistor window is **$967\,\Omega \le R_p \le 1967\,\Omega$**.
   - Standard E24 Resistors in this window: $1.0\,\text{k}\Omega$, $1.1\,\text{k}\Omega$, $1.2\,\text{k}\Omega$, $1.3\,\text{k}\Omega$, $1.5\,\text{k}\Omega$, $1.6\,\text{k}\Omega$, $1.8\,\text{k}\Omega$.
   - **Recommended Choice: $1.5\,\text{k}\Omega$ or $1.8\,\text{k}\Omega$**.
   - With $R_p = 1.5\,\text{k}\Omega$:
     $$t_r = 0.8473 \times 1500 \times (180 \times 10^{-12}) = 228.8\,\text{ns} \quad (< 300\,\text{ns spec, PASS})$$
     $$I_{sink} = \frac{3.3 - 0.4}{1500} = 1.93\,\text{mA} \quad (< 3.0\,\text{mA spec, PASS})$$

---

#### Case 2: 5.0V Standard-mode (100 kHz) High-Capacitance Bus ($C_b = 350\,\text{pF}$)
- **Given Parameters**:
  - $V_{DD} = 5.0\,\text{V}$, $t_{r(max)} = 1000\,\text{ns}$, $I_{OL} = 3.0\,\text{mA}$, $V_{OL} = 0.4\,\text{V}$, $C_b = 350\,\text{pF}$

1. **Calculate $R_{p(min)}$**:
   $$R_{p(min)} = \frac{5.0\,\text{V} - 0.4\,\text{V}}{0.003\,\text{A}} = \frac{4.6\,\text{V}}{0.003\,\text{A}} \approx \mathbf{1533\,\Omega} \ (1.53\,\text{k}\Omega)$$

2. **Calculate $R_{p(max)}$**:
   $$R_{p(max)} = \frac{1000 \times 10^{-9}\,\text{s}}{0.8473 \times (350 \times 10^{-12}\,\text{F})} = \frac{1000 \times 10^{-9}}{2.9656 \times 10^{-10}} \approx \mathbf{3372\,\Omega} \ (3.37\,\text{k}\Omega)$$

3. **Engineering Selection**:
   - Valid window: **$1.53\,\text{k}\Omega \le R_p \le 3.37\,\text{k}\Omega$**.
   - **Recommended Standard Choice: $2.2\,\text{k}\Omega$ or $2.7\,\text{k}\Omega$**.

---

## 3. Bus Capacitance ($C_b$) Budgeting

Bus capacitance $C_b$ is the sum of three physical contributors:
$$C_b = C_{trace} + \sum C_{pin} + C_{cable}$$

```text
                                         Bus Line (SDA / SCL)
    ───────────────────────────────────────────┬───────────────────────────┬─────────────
                                               │                           │
                                            [Cpin 1]                    [Cpin 2]
                                               │                           │
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒┴▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒┴▒▒▒▒▒▒▒▒▒▒▒▒▒
    ▲ [Ctrace] Distributed Microstrip Capacitance across FR4 Dielectric to GND Plane
```

1. **PCB Trace Capacitance ($C_{trace}$)**:
   - For standard 4-layer FR4 boards ($H = 0.1\text{--}0.2\,\text{mm}$ prepreg, $\varepsilon_r \approx 4.2\text{--}4.5$):
     $$\text{Trace Capacitance} \approx 1.5\text{ to }2.5\,\text{pF per inch} \ (0.6\text{ to }1.0\,\text{pF per cm})$$
   - A $15\,\text{cm}$ ($6\,\text{inch}$) PCB routing run contributes $\approx 10\text{--}15\,\text{pF}$.
2. **Device Pin Capacitance ($C_{pin}$)**:
   - Every IC input pin (controller + all target ICs) contributes internal pad and bond-wire capacitance.
   - Typically **$5\text{ to }10\,\text{pF}$ per device**.
   - Connecting 8 sensors contributes $8 \times 10\,\text{pF} = 80\,\text{pF}$.
3. **Cables & Connectors ($C_{cable}$)**:
   - Off-board wiring, ribbon cables, or harness connections:
     $$\text{Ribbon Cable / Twisted Pair} \approx 30\text{ to }60\,\text{pF per meter}$$
   - A 1-meter external cable alone can add $50\,\text{pF}$.

---

## 4. Extending I2C Distance & High-Capacitance Networks

When bus capacitance exceeds the standard $400\,\text{pF}$ limit or bus length exceeds $1\text{--}2\,\text{meters}$, passive pull-up resistors become ineffective. Use the following hardware solutions:

### 4.1 Active Rise-Time Accelerators (e.g., LTC4311)
- Connects in parallel with the bus lines.
- Detects the start of a rising edge ($dV/dt$).
- When the bus passes a threshold, it activates a high-current slew-rate boost circuit that injects current directly into the line for $\sim 30\,\text{ns}$, snapping the rising edge to $V_{DD}$ in $< 50\,\text{ns}$ regardless of large $C_b$ (up to $4000\,\text{pF}$).

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
- Capacitance on Segment A ($C_{b1}$) does not load Segment B ($C_{b2}$).
- Allows multi-board backplanes and long cable runs.

### 4.3 Differential I2C (e.g., PCA9615)
- Translates single-ended SDA and SCL into **two twisted pairs of differential signals** ($DSDA+ / DSDA-$ and $DSCL+ / DSCL-$).
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
   - Maintain a minimum separation of **$3 \times \text{Trace Width}$ ($3W$ rule)**, or route a grounded guard trace between them.
2. **Series Damping Resistors ($R_s$)**:
   - Insert series resistors ($R_s = 22\,\Omega\text{ to }100\,\Omega$) on SDA and SCL located immediately adjacent to the microcontroller pins.
   - $R_s$ dampens ringing, absorbs reflections caused by fast active falling edges, and provides basic ESD / overcurrent protection for IO pins.
3. **Solid Ground Reference**:
   - Always route I2C traces over an unbroken Ground Plane (Layer 2) to maintain controlled impedance and minimize return path inductance.
   - Never route I2C traces across split ground planes or power plane voids.

---

## 6. Bench RCA Troubleshooting Matrix

The table below diagnoses the root causes of the most common I2C hardware and firmware anomalies encountered during board bring-up:

| Oscilloscope / Analyzer Symptom | Root Cause | Underlying Physics | Corrective Engineering Action |
| :--- | :--- | :--- | :--- |
| **Address NACK (No ACK from peripheral)** | Wrong Address, Device Unpowered, or in Reset | Receiver does not assert ACK (SDA remains HIGH on 9th clock). | 1. Verify 7-bit vs 8-bit shifted address format.<br>2. Check $V_{DD}$ pin on sensor with DMM.<br>3. Verify RESET pin is pulled HIGH (not held in reset). |
| **Rounded, sluggish rising edges ($t_r > 300\,\text{ns}$)** | Pull-Up Resistor ($R_p$) Too High or Excessive $C_b$ | RC time constant $\tau = R_p C_b$ is too large; signal fails to reach $V_{IH}$ in time. | Lower $R_p$ value (e.g. swap $10\,\text{k}\Omega$ to $2.2\,\text{k}\Omega$ or $1.5\,\text{k}\Omega$). |
| **Logic LOW voltage ($V_{OL}$) is too high ($> 0.5\,\text{V}$)** | Pull-Up Resistor ($R_p$) Too Low | $R_p$ pulls too hard; NMOS cannot sink current without significant $I_{OL} \times R_{DS(on)}$ voltage drop. | Increase $R_p$ value towards $R_{p(min)}$ or use driver with higher sink capacity. |
| **Bus Stuck: SDA permanently held LOW ($0\,\text{V}$)** | Slave interrupted during read cycle | Target device waiting for clock pulse to shift out bit `0`; MCU reboots into IDLE. | Implement the 9-clock bus recovery sequence in microcontroller `I2C_Init()`. |
| **Bus Stuck: SCL permanently held LOW ($0\,\text{V}$)** | Target executing infinite Clock Stretch | Peripheral internal firmware hung or awaiting ADC conversion that never completes. | 1. Check peripheral supply voltage.<br>2. Implement hardware reset line toggle or power cycle via P-MOSFET high-side switch. |
| **Spurious START / STOP glitches mid-byte** | Crosstalk between SCL and SDA | Fast SCL edge injects capacitive spike on SDA that crosses logic threshold while SCL is HIGH. | 1. Separate traces on PCB.<br>2. Add $22\,\Omega\text{--}47\,\Omega$ series resistors.<br>3. Verify 50 ns spike filter is enabled in MCU registers. |
| **Severe ringing and overshoot on falling edges** | Long unterminated stub traces | Fast NMOS turn-on induces high $dI/dt$ across trace inductance. | Add $33\,\Omega\text{ to }100\,\Omega$ series damping resistors ($R_s$) close to driver pins. |
