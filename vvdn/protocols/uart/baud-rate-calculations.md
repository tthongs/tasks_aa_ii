# UART Baud Rate: Significance, Hardware Generation & Error Calculations

This document details the definition of baud rate, how microcontrollers and SoCs generate it from internal clocks, how to calculate baud divisors and errors, and how to measure unknown baud rates in the lab.

---

## 1. What Does Baud Rate Signify?

**Baud Rate** is named after the French telecommunications pioneer Émile Baudot. It measures the **number of symbol changes (signal transitions or modulations) occurring per second** across the physical transmission medium.

### 1.1 Baud Rate vs. Bit Rate
- **Bit Rate (bits per second / bps)**: Quantifies the volume of raw binary digits (0s and 1s) transmitted per second.
- **Baud Rate (symbols per second / Bd)**: Quantifies the frequency of physical state changes on the line per second.
- **In Binary UART**:
  - Each physical symbol represents a binary logic level ($0\text{V} = 0$, $3.3\text{V} / 5\text{V} = 1$).
  - Therefore, **1 Baud = 1 bit per second (bps)**.
  *(In advanced RF or ethernet modulations such as PAM4 or QAM, one baud carries multiple bits. For UART, the two terms are numerically equivalent).*

---

### 1.2 Physical Meaning on the Wire: Bit Period ($T_{bit}$)
The baud rate determines the exact length of time each bit is held on the transmission line:

$$T_{bit} = \frac{1}{\text{Baud Rate}}$$

For common baud rates:
- **9,600 Baud**:
  $$T_{bit} = \frac{1}{9600} \approx 104.17\,\mu\text{s}$$
- **115,200 Baud**:
  $$T_{bit} = \frac{1}{115200} \approx 8.68\,\mu\text{s}$$
- **1,500,000 Baud (1.5M)**:
  $$T_{bit} = \frac{1}{1500000} \approx 0.667\,\mu\text{s} = 666.7\,\text{ns}$$

Because UART is **asynchronous** (there is no shared clock line), both sender and receiver must calibrate their local timers to this exact $T_{bit}$ duration. If the receiver's timer drifts, it will sample during transitions or read the wrong bit.

---

### 1.3 Gross Baud Rate vs. Useful Payload Throughput
In standard `8-N-1` configuration, transmitting **1 byte (8 bits) of useful data** requires transmitting **10 physical bits on the wire**:
- 1 Start bit
- 8 Data bits
- 0 Parity bits
- 1 Stop bit

**Framing Efficiency**:
$$\text{Efficiency} = \frac{8\,\text{Data Bits}}{10\,\text{Total Bits}} = 80\%$$

**Payload Throughput Formula**:
$$\text{Payload Throughput (Bytes/s)} = \frac{\text{Baud Rate}}{\text{Total Bits per Frame}} = \frac{\text{Baud Rate}}{10}$$

| Baud Rate | $T_{bit}$ | Frame Duration (10 bits) | Max Payload Throughput |
| :--- | :--- | :--- | :--- |
| **9,600** | $104.17\,\mu\text{s}$ | $1.042\,\text{ms}$ | $960\,\text{Bytes/s}$ ($0.94\,\text{KB/s}$) |
| **19,200** | $52.08\,\mu\text{s}$ | $520.8\,\mu\text{s}$ | $1,920\,\text{Bytes/s}$ ($1.88\,\text{KB/s}$) |
| **38,400** | $26.04\,\mu\text{s}$ | $260.4\,\mu\text{s}$ | $3,840\,\text{Bytes/s}$ ($3.75\,\text{KB/s}$) |
| **57,600** | $17.36\,\mu\text{s}$ | $173.6\,\mu\text{s}$ | $5,760\,\text{Bytes/s}$ ($5.63\,\text{KB/s}$) |
| **115,200** | $8.68\,\mu\text{s}$ | $86.8\,\mu\text{s}$ | $11,520\,\text{Bytes/s}$ ($11.25\,\text{KB/s}$) |
| **921,600** | $1.085\,\mu\text{s}$ | $10.85\,\mu\text{s}$ | $92,160\,\text{Bytes/s}$ ($90.0\,\text{KB/s}$) |
| **1,500,000** | $0.667\,\mu\text{s}$ | $6.67\,\mu\text{s}$ | $150,000\,\text{Bytes/s}$ ($146.5\,\text{KB/s}$) |

---

## 2. Hardware Generation: Baud Rate Generator (BRG)

Microcontrollers and SoCs (STM32, ESP32, NXP, Qualcomm, Microchip, 16550 UART) generate baud rates by dividing down an internal system/peripheral clock ($f_{clk}$).

### 2.1 The $16\times$ Oversampling Mechanism
Because the receiver cannot rely on external clock edges, it clocks an internal counter at **$16\times$ the target baud rate** ($OS = 16$):
1. **Idle**: The line sits at Logic HIGH.
2. **Falling Edge Detection**: The line drops to Logic LOW, indicating a Start bit. The counter resets to 0.
3. **Midpoint Verification**: At tick **7 or 8** (midpoint of the start bit), the receiver samples again. If it is still LOW, the start bit is validated (rejecting high-frequency noise spikes).
4. **Data Sampling**: Subsequent bits are sampled **every 16 ticks thereafter**, ensuring each bit is sampled at its physical center where voltages are stable and reflections have settled.

```text
Clock Ticks (16x):  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 ... 23 24
Line Level:        HIGH ────────┐                                  ┌─────────────
                                └──────── START BIT (Low) ─────────┘   DATA D0...
Sample Point:                                  ▲ (Tick 7-8: Midpoint)          ▲ (+16 Ticks)
```

---

### 2.2 The Hardware Divisor Formula
The peripheral clock $f_{clk}$ is divided by the Baud Rate Generator (BRG) register:

$$\text{Baud Rate} = \frac{f_{clk}}{OS \times \text{Divisor}}$$

Where:
- $f_{clk}$ = UART peripheral clock frequency (Hz)
- $OS$ = Oversampling factor (typically $16$, or $8$ in high-speed mode)
- $\text{Divisor}$ = Prescaler register value (e.g., `UBRR` in AVR, `USART_BRR` in STM32, `DLL/DLM` in 16550)

Solving for the **Divisor** to write to the register:
$$\text{Divisor} = \frac{f_{clk}}{OS \times \text{Baud}_{target}}$$

---

## 3. Baud Rate Error & Tolerance Calculation

In hardware, divisor registers store finite numerical values (integers or fixed-point fractions). When $f_{clk} / (OS \times \text{Baud})$ is not a whole number, rounding results in a **frequency mismatch**.

### 3.1 Formulas
$$\text{Baud}_{actual} = \frac{f_{clk}}{OS \times \text{Divisor}_{rounded}}$$

$$\text{Error (\%)} = \left( \frac{\text{Baud}_{actual} - \text{Baud}_{target}}{\text{Baud}_{target}} \right) \times 100\%$$

---

### 3.2 Why Timing Error Causes Framing Errors (Cumulative Phase Drift)
- The receiver resynchronizes its timing clock **only once per byte** (at the start bit's falling edge).
- For the remainder of the 10-bit frame (8 data bits, parity, stop bit), the receiver operates open-loop.
- With each passing bit $N$, timing error accumulates:
  $$\Delta t_{accumulated} = N \times (T_{bit, actual} - T_{bit, target})$$
- By bit 9 or 10 (the Stop bit), if $\Delta t_{accumulated}$ drifts by more than **$\pm 0.5 \times T_{bit}$** (50% of a bit width), the receiver samples on the transition edge or into the adjacent bit.
- **Tolerance Threshold**:
  - Across a 10-bit transmission, total mismatch between sender and receiver **must be $< \pm 2.5\%$ to $\pm 3.0\%$**.
  - Any error $> 3\%$ results in frequent **Framing Errors (FE)** or corrupted characters.

---

## 4. Practical Real-World Scenarios

### Scenario A: 16 MHz Clock with Integer Divisor (Why 115200 Fails)
- Microcontroller running at $f_{clk} = 16\,\text{MHz} = 16,000,000\,\text{Hz}$, Target = $115,200$, $OS = 16$.
- Compute Divisor:
  $$\text{Divisor} = \frac{16,000,000}{16 \times 115200} = \frac{16,000,000}{1,843,200} \approx 8.68055$$
- With an integer-only register (rounded to 9):
  $$\text{Baud}_{actual} = \frac{16,000,000}{16 \times 9} = 111,111.1\,\text{bps}$$
  $$\text{Error} = \left( \frac{111111.1 - 115200}{115200} \right) \times 100\% = \mathbf{-3.55\%}$$
- **Result**: **FAIL**. $-3.55\%$ exceeds the $3\%$ limit. Communication with a PC or host will be unstable and drop bytes.

---

### Scenario B: Fractional Baud Rate Generator (Modern MCUs / SoCs)
Modern microcontrollers (such as STM32) provide fractional baud rate registers (e.g. 12-bit mantissa + 4-bit fraction):
- Ideal Divisor = $8.68055$
- Integer Mantissa = $8$
- 4-bit Fraction = $\text{round}(0.68055 \times 16) = \text{round}(10.88) = 11$
- Fractional Divisor = $8 + \frac{11}{16} = 8.6875$
- Actual Baud Rate:
  $$\text{Baud}_{actual} = \frac{16,000,000}{16 \times 8.6875} = 115,107.9\,\text{bps}$$
  $$\text{Error} = \left( \frac{115107.9 - 115200}{115200} \right) \times 100\% = \mathbf{-0.08\%}$$
- **Result**: **PASS**. Extremely stable ($< 0.1\%$ error).

---

### Scenario C: Why Crystals like 11.0592 MHz and 18.432 MHz Exist
On older boards or dedicated UART interfaces, you will frequently see crystal frequencies like **$11.0592\,\text{MHz}$** or **$18.432\,\text{MHz}$**:
- Divisor for 115,200 baud on 11.0592 MHz:
  $$\text{Divisor} = \frac{11,059,200}{16 \times 115200} = \frac{11,059,200}{1,843,200} = \mathbf{6.0000}$$
- Divisor for 9,600 baud:
  $$\text{Divisor} = \frac{11,059,200}{16 \times 9600} = \mathbf{72.0000}$$
- Because $11.0592\,\text{MHz}$ is an exact multiple of $115,200 \times 16$, integer division produces **$0.00\%$ baud rate error**.

---

## 5. Lab Measurement: Finding Unknown Baud Rates with an Oscilloscope

When probing an unidentified serial port or debugging mismatched communication:
1. Connect oscilloscope / logic analyzer channel 1 to the **TX pin** and reference probe to **GND**.
2. Set trigger to **Falling Edge**.
3. Cause the target board to transmit (reboot the board or trigger serial output).
4. Inspect the waveform and identify the **narrowest single pulse** (shortest HIGH or LOW pulse in the burst). In random data, this narrowest pulse corresponds to a single bit ($1 \times T_{bit}$).
5. Measure its width ($\Delta t$) with scope cursors:
   $$\text{Baud Rate} = \frac{1}{\Delta t}$$

### Quick Lookup Cheatsheet:
| Measured Pulse Width ($\Delta t$) | Inferred Baud Rate |
| :--- | :--- |
| $\approx 104\,\mu\text{s}$ | **9,600** Baud |
| $\approx 52.1\,\mu\text{s}$ | **19,200** Baud |
| $\approx 26.0\,\mu\text{s}$ | **38,400** Baud |
| $\approx 17.4\,\mu\text{s}$ | **57,600** Baud |
| $\approx 8.68\,\mu\text{s}$ | **115,200** Baud |
| $\approx 1.08\,\mu\text{s}$ | **921,600** Baud |
| $\approx 0.67\,\mu\text{s}$ | **1,500,000** (1.5M) Baud |

---

## 6. Using the Workspace Calculator Tool

You can compute divisors, actual baud rates, bit periods, and error percentages for any peripheral clock using the workspace tool:

```bash
# Example 1: Check 16 MHz clock with 115200 baud
python3 tools/baud_calc.py --clock 16MHz --baud 115200

# Example 2: Check 48 MHz clock with 921600 baud and 8x oversampling
python3 tools/baud_calc.py --clock 48MHz --baud 921600 --oversample 8

# Example 3: Check 11.0592 MHz crystal
python3 tools/baud_calc.py --clock 11.0592MHz --baud 115200
```
