# SPI Modes, Timing Budgets & Propagation Delay Calculations

This document details the exact state transitions of SPI clock modes (CPOL & CPHA), shift register physics, AC timing parameters, round-trip delay calculations for high-speed operation, and lab measurement techniques.

---

## 1. Clock Polarity (CPOL) & Clock Phase (CPHA) Deep Dive

In SPI, the Serial Clock (**SCLK**) synchronizes all data transmission. Because SPI lacks a formal IEEE specification, device manufacturers utilize combinations of two fundamental parameters: **Clock Polarity (CPOL)** and **Clock Phase (CPHA)**.

### 1.1 Parameter Definitions

#### A. Clock Polarity (CPOL)
CPOL specifies the idle logic level of the SCLK line when no data is being transferred ($\overline{\text{CS}} = \text{HIGH}$):
- **$\text{CPOL} = 0$**: SCLK idles at **Logic LOW (0V)**.
  - The leading (first) edge is a **Rising Edge (0 -> 1)**.
  - The trailing (second) edge is a **Falling Edge (1 -> 0)**.
- **$\text{CPOL} = 1$**: SCLK idles at **Logic HIGH ($V_{DD}$)**.
  - The leading (first) edge is a **Falling Edge (1 -> 0)**.
  - The trailing (second) edge is a **Rising Edge (0 -> 1)**.

#### B. Clock Phase (CPHA)
CPHA specifies the alignment between data bit transitions (toggling/shifting) and data bit sampling (latching/capturing):
- **$\text{CPHA} = 0$**: Data is sampled on the **Leading (first) clock edge**.
  - The first data bit must be driven onto the bus **before** the first clock edge (immediately upon $\overline{\text{CS}}$ assertion).
  - Subsequent data bits are shifted onto the line on the **Trailing (second) clock edge**.
- **$\text{CPHA} = 1$**: Data is sampled on the **Trailing (second) clock edge**.
  - The first data bit is shifted onto the line on the **Leading (first) clock edge**.
  - Data bits are captured on the **Trailing (second) clock edge**.

---

### 1.2 Comprehensive Waveform Comparison Across All 4 Modes

The following ASCII diagram illustrates the transmission of one byte (`0b10100101` / `0xA5`) under each of the four standard modes:

```text
CS#           ──────┐                                                                             ┌──────
                    └─────────────────────────────────────────────────────────────────────────────┘

--- MODE 0: CPOL=0, CPHA=0 (Idle Low, Sample on Rising Edge, Shift on Falling Edge) ---
SCLK                ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐
      ──────────────┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └────────────────────────
                    ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼
DATA  ──────────────< 1 >─< 0 >─< 1 >─< 0 >─< 0 >─< 1 >─< 0 >─< 1 >──────────────────────────────────────
      CS asserts -> ▲       ▲       ▲       ▲       ▲       ▲       ▲       ▲
      D7 Driven     Sample1 Sample2 Sample3 Sample4 Sample5 Sample6 Sample7 Sample8

--- MODE 1: CPOL=0, CPHA=1 (Idle Low, Shift on Rising Edge, Sample on Falling Edge) ---
SCLK                ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐
      ──────────────┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └────────────────────────
                    ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲
DATA  ──────────────────< 1 >─< 0 >─< 1 >─< 0 >─< 0 >─< 1 >─< 0 >─< 1 >──────────────────────────────────
                    Shift1  ▲
                            Sample1

--- MODE 2: CPOL=1, CPHA=0 (Idle High, Sample on Falling Edge, Shift on Rising Edge) ---
SCLK  ──────────────┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌────────────────────────
                    └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘
                    ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼
DATA  ──────────────< 1 >─< 0 >─< 1 >─< 0 >─< 0 >─< 1 >─< 0 >─< 1 >──────────────────────────────────────
      CS asserts -> ▲       ▲
      D7 Driven     Sample1 Sample2

--- MODE 3: CPOL=1, CPHA=1 (Idle High, Shift on Falling Edge, Sample on Rising Edge) ---
SCLK  ──────────────┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌────────────────────────
                    └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘
                    ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲
DATA  ──────────────────< 1 >─< 0 >─< 1 >─< 0 >─< 0 >─< 1 >─< 0 >─< 1 >──────────────────────────────────
                    Shift1  ▲
                            Sample1
```

---

### 1.3 Mode Matrix Summary & Industry Prevalence

| Mode | CPOL | CPHA | Idle SCLK | Data Driven / Shifted | Data Sampled / Latched | Typical Applications |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | `0` | `0` | **Low** | Falling edge (and on $\overline{\text{CS}}$ assert) | **Rising edge** | **Industry Standard**: NOR Flash, SD Cards, EEPROMs, IMUs |
| **1** | `0` | `1` | **Low** | Rising edge | **Falling edge** | Specialized ADCs, display controllers |
| **2** | `1` | `0` | **High** | Rising edge (and on $\overline{\text{CS}}$ assert) | **Falling edge** | Legacy DSP peripherals, industrial converters |
| **3** | `1` | `1` | **High** | Falling edge | **Rising edge** | **Flash Standard**: Winbond, Macronix, Microchip memory |

> [!NOTE]
> **Why Mode 0 and Mode 3 Dominate Memory**:
> Notice that in both **Mode 0** and **Mode 3**, data is sampled on the **Rising edge** and shifted on the **Falling edge**. The only physical difference is the idle state of the clock between frames. Consequently, almost all serial NOR Flash memories (e.g. Winbond W25Q series, Macronix MX25 series) specify support for **both Mode 0 and Mode 3**.

---

## 2. Shift Register Operation: Bit-by-Bit Cycle Budget

An SPI interface is physically implemented as a pair of coupled shift registers clocked simultaneously by SCLK:

```text
              +------------- CONTROLLER REGISTER (TX: 0x9F) -------------+
              |   [1]     [0]     [0]     [1]     [1]     [1]     [1]    [1]   |
              +---|-------------------------------------------------------^----+
                  | MOSI                                                  | MISO
                  v                                                       |
              +---|-------------------------------------------------------^----+
              |   [0]     [1]     [0]     [1]     [0]     [0]     [1]    [1]   |
              +-------------- PERIPHERAL REGISTER (TX: 0x53) ------------+
```

### Trace Table for Mode 0 (8 Clock Cycles):

| Clock Pulse | Controller Shifts Out (MOSI) | Peripheral Shifts Out (MISO) | Controller Shift Reg (After Edge) | Peripheral Shift Reg (After Edge) |
| :---: | :---: | :---: | :---: | :---: |
| **CS LOW** | Driven: `1` (Bit 7) | Driven: `0` (Bit 7) | `10011111` | `01010011` |
| **Clock 1** | Latched by target (`1`) | Latched by host (`0`) | `00111110` | `10100111` |
| **Clock 2** | Latched by target (`0`) | Latched by host (`1`) | `01111101` | `01001110` |
| **Clock 3** | Latched by target (`0`) | Latched by host (`0`) | `11111010` | `10011100` |
| **Clock 4** | Latched by target (`1`) | Latched by host (`1`) | `11110101` | `00111001` |
| **Clock 5** | Latched by target (`1`) | Latched by host (`0`) | `11101010` | `01110011` |
| **Clock 6** | Latched by target (`1`) | Latched by host (`0`) | `11010100` | `11100111` |
| **Clock 7** | Latched by target (`1`) | Latched by host (`1`) | `10101001` | `11001111` |
| **Clock 8** | Latched by target (`1`) | Latched by host (`1`) | `01010011` (`0x53`) | `10011111` (`0x9F`) |

At the completion of cycle 8:
- Controller holds `0x53` (received from Peripheral).
- Peripheral holds `0x9F` (received from Controller).
- Exact swap achieved in 8 clock cycles with zero protocol overhead.

---

## 3. AC Timing Parameters & Bus Timing Budget

At high clock frequencies ($\ge 20\,\text{MHz}$), physical propagation delays through PCB traces, digital isolators, and internal semiconductor silicon consume a major fraction of the clock period.

### 3.1 Key AC Timing Parameters Defined

```text
                  tCSS                                                tCSH
CS#   ────────┐                                                            ┌──────
              └────────────────────────────────────────────────────────────┘
                         |<--- tHIGH --->|<- tLOW ->|
SCLK  ───────────────────┌───────────────┐          ┌───────────────┐
                         │               └──────────┘               └───
                         |<------------ TSCLK ------------->|
                         ▲                          ▼
                         |<-- tSU -->|<- tH ->|     |<- tV ->|
DATA (MOSI/MISO)  ───────X───────────X────────X─────X────────X──────────
                         |   Valid Input Data |     | New Output Valid
```

- **$T_{SCLK}$ (Clock Period)**: Total duration of one SCLK cycle ($1 / f_{SCLK}$).
- **$t_{HIGH} / t_{LOW}$ (Clock Pulse Widths)**: SCLK High and Low durations (typically $45\% - 55\%$ of $T_{SCLK}$).
- **$t_{SU}$ (Setup Time)**: Minimum duration data must remain stable **before** the active sampling clock edge.
- **$t_H$ (Hold Time)**: Minimum duration data must remain stable **after** the active sampling clock edge.
- **$t_V$ or $t_{CO}$ (Clock-to-Output Valid Delay)**: Propagation time from the active clock edge until the transmitting device drives valid data onto the wire.
- **$t_{DIS}$ (Output Disable Time)**: Time for the peripheral's MISO buffer to return to High-Z after $\overline{\text{CS}}$ goes HIGH.
- **$t_{CSS}$ (CS Setup Time)**: Time between $\overline{\text{CS}}$ active (LOW) and the first SCLK edge.
- **$t_{CSH}$ (CS Hold Time)**: Time between the last SCLK edge and $\overline{\text{CS}}$ deasserting (HIGH).
- **$t_{CS\_HIGH}$ (CS Deselect / Recovery Time)**: Minimum inactive HIGH duration required between consecutive transactions.

---

### 3.2 Maximum Operating Frequency & Round-Trip Delay Formula

In an SPI transaction, the Controller generates SCLK. 
- For **Write operations (MOSI)**: SCLK and MOSI travel in the same direction from Controller to Peripheral. Timing margin is relatively generous.
- For **Read operations (MISO)**: SCLK travels from Controller to Peripheral, triggers the Peripheral's output buffer, and MISO must travel **all the way back** to the Controller before the Controller's sampling edge.

This creates a **Round-Trip Propagation Constraint**:

$$T_{SCLK, min} > 2 \times (t_{prop\_out} + t_{prop\_in}) + t_{CO\_peripheral} + t_{SU\_controller} + t_{skew}$$

For symmetrical forward and return paths:
$$T_{SCLK, min} > 2 \times t_{prop\_path} + t_{CO\_peripheral} + t_{SU\_controller} + t_{margin}$$

Where:
- $t_{prop\_path} = t_{trace} + t_{cable} + t_{isolator}$ (one-way propagation delay).
- $t_{CO\_peripheral}$ = Peripheral clock-to-output delay (from peripheral datasheet).
- $t_{SU\_controller}$ = Controller input data setup time (from SoC / MCU datasheet).
- $t_{margin}$ = Recommended engineering safety margin ($\approx 2 - 3\,\text{ns}$).

The maximum safe read frequency is:
$$f_{SCLK, max} = \frac{1}{T_{SCLK, min}}$$

---

### 3.3 Worked Real-World Engineering Scenarios

#### Scenario 1: High-Speed On-Board NOR Flash (Winbond W25Q128FV)
- **Physical Layout**: On-board Flash memory located 50 mm (2 inches) from an STM32H7 MCU.
- **Propagation Parameters**:
  - FR4 PCB Trace Delay: $\approx 6.5\,\text{ps/mm} \implies t_{trace} = 50\,\text{mm} \times 6.5\,\text{ps/mm} = 0.325\,\text{ns}$.
  - Isolators / Buffers: None ($t_{isolator} = 0$).
  - One-way path delay: $t_{prop\_path} \approx 0.33\,\text{ns}$.
- **Silicon Parameters** (from Datasheets):
  - Flash $t_{CO}$ (Clock to output valid): $7.0\,\text{ns}$.
  - STM32H7 SPI Controller Setup Time $t_{SU}$: $3.0\,\text{ns}$.
  - Safety Margin $t_{margin}$: $2.0\,\text{ns}$.
- **Calculation**:
  $$T_{SCLK, min} = (2 \times 0.33\,\text{ns}) + 7.0\,\text{ns} + 3.0\,\text{ns} + 2.0\,\text{ns} = 12.66\,\text{ns}$$
  $$f_{SCLK, max} = \frac{1}{12.66 \times 10^{-9}\,\text{s}} \approx \mathbf{78.9\,\text{MHz}}$$
- **Verdict**: **PASS for 50 MHz operation** ($T_{SCLK} = 20\,\text{ns} > 12.66\,\text{ns}$). The interface runs reliably at 50 MHz.

---

#### Scenario 2: Off-Board Industrial Sensor with Cable & Galvanic Isolator
- **Physical Layout**: Precision SPI ADC connected via a **30 cm ribbon cable** and an optocoupler / digital isolator (e.g. ADuM1401).
- **Propagation Parameters**:
  - 30 cm Ribbon Cable Delay ($\approx 5.0\,\text{ns/m}$): $t_{cable} = 0.3\,\text{m} \times 5.0\,\text{ns} = 1.5\,\text{ns}$.
  - Digital Isolator Propagation Delay: $t_{isolator} = 25.0\,\text{ns}$ per direction!
  - Total One-Way Path Delay: $t_{prop\_path} = 1.5\,\text{ns} + 25.0\,\text{ns} = 26.5\,\text{ns}$.
- **Silicon Parameters**:
  - ADC $t_{CO}$: $18.0\,\text{ns}$.
  - Controller $t_{SU}$: $5.0\,\text{ns}$.
  - Safety Margin: $3.0\,\text{ns}$.
- **Calculation**:
  $$T_{SCLK, min} = (2 \times 26.5\,\text{ns}) + 18.0\,\text{ns} + 5.0\,\text{ns} + 3.0\,\text{ns} = 53.0\,\text{ns} + 26.0\,\text{ns} = \mathbf{79.0\,\text{ns}}$$
  $$f_{SCLK, max} = \frac{1}{79.0 \times 10^{-9}\,\text{s}} \approx \mathbf{12.6\,\text{MHz}}$$
- **Verdict**:
  - Attempting to run this sensor at standard $20\,\text{MHz}$ ($T_{SCLK} = 50\,\text{ns}$) **will fail completely**, resulting in corrupted MISO reads.
  - The maximum safe operating clock is **10 MHz or lower** (e.g. 5–8 MHz).

---

## 4. Gross Clock Rate vs. Effective Payload Throughput

While SPI has zero frame-addressing overhead, actual payload throughput is affected by:
1. **$\overline{\text{CS}}$ Assertion and Deselect Overhead**: Controller must lower CS before clocking and raise it between transactions.
2. **Command & Address Overhead**: In Flash and sensors, 1 to 5 bytes of command and address precede payload data.
3. **Dummy Wait Cycles**: High-speed Flash reads require 4 to 8 dummy clock cycles for internal array access.
4. **Inter-Byte Latency**: CPU interrupt-driven transfers introduce microsecond delays between bytes compared to hardware DMA streams.

### 4.1 Throughput Comparison Across Bus Configurations

Assumes a continuous 1 KB (1024-byte) burst read:

| Clock Rate ($f_{SCLK}$) | Raw Bitrate | Standard SPI (1-bit) Effective Throughput | Dual SPI (2-bit) Effective Throughput | Quad SPI (QSPI 4-bit) Effective Throughput |
| :---: | :---: | :---: | :---: | :---: |
| **1 MHz** | 1.0 Mbps | $120\,\text{KB/s}$ ($0.96\,\text{Mbps}$) | $235\,\text{KB/s}$ | $450\,\text{KB/s}$ |
| **10 MHz** | 10.0 Mbps | $1.20\,\text{MB/s}$ ($9.6\,\text{Mbps}$) | $2.35\,\text{MB/s}$ | $4.55\,\text{MB/s}$ |
| **25 MHz** | 25.0 Mbps | $3.05\,\text{MB/s}$ ($24.4\,\text{Mbps}$) | $5.95\,\text{MB/s}$ | $11.6\,\text{MB/s}$ |
| **50 MHz** | 50.0 Mbps | $6.10\,\text{MB/s}$ ($48.8\,\text{Mbps}$) | $11.9\,\text{MB/s}$ | $23.3\,\text{MB/s}$ |
| **80 MHz** | 80.0 Mbps | $9.75\,\text{MB/s}$ ($78.0\,\text{Mbps}$) | $19.1\,\text{MB/s}$ | $37.5\,\text{MB/s}$ |
| **104 MHz** (QSPI) | 104.0 Mbps | — | $24.8\,\text{MB/s}$ | $48.9\,\text{MB/s}$ |

---

## 5. High-Speed Signal Integrity & PCB Routing Rules

At edge transition speeds under $2\,\text{ns}$, PCB traces behave as transmission lines regardless of the fundamental clock frequency.

### 5.1 Critical Trace Length Formula
A PCB trace must be treated as a transmission line when the trace length exceeds:
$$l_{crit} = \frac{t_{rise}}{2 \times t_{prop\_per\_cm}}$$

On standard FR4 PCB material:
$$t_{prop\_per\_cm} \approx 65\,\text{ps/cm} \quad (0.065\,\text{ns/cm})$$

If an MCU output has a rise time of $t_{rise} = 1.0\,\text{ns}$:
$$l_{crit} = \frac{1.0\,\text{ns}}{2 \times 0.065\,\text{ns/cm}} \approx \mathbf{7.69\,\text{cm}}\quad (\approx 3.0\,\text{inches})$$

Any trace longer than $7.5\,\text{cm}$ will experience severe reflections and edge ringing without proper termination.

### 5.2 Source Series Damping Resistor Calculation
To eliminate ringing and double-clocking on SCLK, match the driver's output impedance to the characteristic trace impedance:
$$R_{series} = Z_0 - R_{driver}$$

Where:
- $Z_0$ = Characteristic impedance of the PCB microstrip trace (standardly $50\,\Omega$).
- $R_{driver}$ = Internal output impedance of the Controller's CMOS push-pull pin (typically $15 - 25\,\Omega$).
- **Required Series Resistor**: $R_{series} \approx 50\,\Omega - 20\,\Omega = \mathbf{30\,\Omega}$ (Standard values: **$27\,\Omega\text{ to }33\,\Omega$**).

Place this resistor as close as physically possible to the Controller's SCLK and MOSI output pins.

---

## 6. Lab Measurement & Logic Analyzer Decoding Guide

### 6.1 Setting Up a Logic Analyzer (Saleae / Sigrok PulseView)
1. **Sampling Rate Rule of Thumb**: Set the logic analyzer sample rate to **at least $4\times$ (ideally $8\times - 10\times$) the SPI clock rate**.
   - For a 10 MHz SPI bus, set sample rate $\ge 80\,\text{MSa/s}$.
2. **Channel Connections**:
   - Channel 0: SCLK
   - Channel 1: MOSI (COPI)
   - Channel 2: MISO (CIPO)
   - Channel 3: $\overline{\text{CS}}$
   - Ground Lead: Connect directly to the DUT digital ground.
3. **Trigger Configuration**:
   - Set Trigger condition on Channel 3 ($\overline{\text{CS}}$) to **Falling Edge**.
4. **Configuring Protocol Decoder**:
   - Protocol: `SPI`
   - Select correct channels.
   - Set **Polarity** and **Phase** matching the device datasheet.
   - Set **Bit Order**: `MSB First`.
   - Set **Word Length**: `8 bits`.

### 6.2 Diagnostic Rules for Scope Screen Inspection
- **If data byte is shifted left by 1 bit**: The analyzer or MCU is sampling one edge too early (CPHA mismatch; switch CPHA from 0 to 1).
- **If data byte is shifted right by 1 bit**: The analyzer or MCU is sampling one edge too late (switch CPHA from 1 to 0).
- **If data reads all `0xFF` or `0x00`**: Check that $\overline{\text{CS}}$ is actually falling LOW during the clock burst; if $\overline{\text{CS}}$ remains HIGH, the target's MISO output is tri-stated.

---

## 7. Using the Workspace SPI Calculator Tool

You can calculate clock periods, round-trip timing budgets, maximum safe read frequencies, and payload throughput using the workspace tool:

```bash
# Example 1: Standard on-board Flash (5 cm trace, tCO = 7 ns, tSU = 3 ns)
python3 tools/spi_calc.py --clock 50MHz --trace-cm 5 --tco 7 --tsu 3

# Example 2: Off-board sensor with 30 cm ribbon cable and 25 ns digital isolator
python3 tools/spi_calc.py --clock 10MHz --trace-cm 5 --cable-cm 30 --isolator-ns 25 --tco 15 --tsu 5

# Example 3: Quad-SPI (QSPI) throughput analysis at 104 MHz
python3 tools/spi_calc.py --clock 104MHz --qspi
```
