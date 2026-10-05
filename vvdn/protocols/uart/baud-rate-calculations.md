# UART Baud Rate: Significance, Hardware Generation & Error Calculations

This document details the definition of baud rate, how microcontrollers and SoCs generate it from internal clocks, how to calculate baud divisors and errors, and how to measure unknown baud rates in the lab.

---

## 1. What Does Baud Rate Signify?

**Baud Rate** is named after the French telecommunications pioneer Émile Baudot. It measures the **number of symbol changes (signal transitions or modulations) occurring per second** across the physical transmission medium.

### 1.1 Baud Rate vs. Bit Rate
- **Bit Rate (bits per second / bps)**: Quantifies the volume of raw binary digits (0s and 1s) transmitted per second.
- **Baud Rate (symbols per second / Bd)**: Quantifies the frequency of physical state changes on the line per second.
- **In Binary UART**:
  - Each physical symbol represents a binary logic level (0V = 0, 3.3V / 5V = 1).
  - Therefore, **1 Baud = 1 bit per second (bps)**.
  *(In advanced RF or ethernet modulations such as PAM4 or QAM, one baud carries multiple bits. For UART, the two terms are numerically equivalent).*

---

### 1.2 Physical Meaning on the Wire: Bit Period (T_bit)
The baud rate determines the exact length of time each bit is held on the transmission line:

```
T_bit = 1 / (Baud Rate)
```

For common baud rates:
- **9,600 Baud**:
  ```
T_bit = 1 / 9600 ≈ 104.17 µs
```
- **115,200 Baud**:
  ```
T_bit = 1 / 115200 ≈ 8.68 µs
```
- **1,500,000 Baud (1.5M)**:
  ```
T_bit = 1 / 1500000 ≈ 0.667 µs = 666.7 ns
```

Because UART is **asynchronous** (there is no shared clock line), both sender and receiver must calibrate their local timers to this exact T_bit duration. If the receiver's timer drifts, it will sample during transitions or read the wrong bit.

---

### 1.3 Gross Baud Rate vs. Useful Payload Throughput
In standard `8-N-1` configuration, transmitting **1 byte (8 bits) of useful data** requires transmitting **10 physical bits on the wire**:
- 1 Start bit
- 8 Data bits
- 0 Parity bits
- 1 Stop bit

**Framing Efficiency**:
```
Efficiency = (8 Data Bits) / (10 Total Bits) = 80\%
```

**Payload Throughput Formula**:
```
Payload Throughput (Bytes/s) = (Baud Rate) / (Total Bits per Frame) = (Baud Rate) / 10
```

| Baud Rate | T_bit | Frame Duration (10 bits) | Max Payload Throughput |
| :--- | :--- | :--- | :--- |
| **9,600** | 104.17 µs | 1.042 ms | 960 Bytes/s (0.94 KB/s) |
| **19,200** | 52.08 µs | 520.8 µs | 1,920 Bytes/s (1.88 KB/s) |
| **38,400** | 26.04 µs | 260.4 µs | 3,840 Bytes/s (3.75 KB/s) |
| **57,600** | 17.36 µs | 173.6 µs | 5,760 Bytes/s (5.63 KB/s) |
| **115,200** | 8.68 µs | 86.8 µs | 11,520 Bytes/s (11.25 KB/s) |
| **921,600** | 1.085 µs | 10.85 µs | 92,160 Bytes/s (90.0 KB/s) |
| **1,500,000** | 0.667 µs | 6.67 µs | 150,000 Bytes/s (146.5 KB/s) |

---

## 2. Hardware Generation: Baud Rate Generator (BRG)

Microcontrollers and SoCs (STM32, ESP32, NXP, Qualcomm, Microchip, 16550 UART) generate baud rates by dividing down an internal system/peripheral clock (f_clk).

### 2.1 The 16* Oversampling Mechanism
Because the receiver cannot rely on external clock edges, it clocks an internal counter at **16* the target baud rate** (OS = 16):
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
The peripheral clock f_clk is divided by the Baud Rate Generator (BRG) register:

```
Baud Rate = f_clk / (OS * Divisor)
```

Where:
- f_clk = UART peripheral clock frequency (Hz)
- OS = Oversampling factor (typically 16, or 8 in high-speed mode)
- Divisor = Prescaler register value (e.g., `UBRR` in AVR, `USART_BRR` in STM32, `DLL/DLM` in 16550)

Solving for the **Divisor** to write to the register:
```
Divisor = f_clk / (OS * Baud_target)
```

---

## 3. Baud Rate Error & Tolerance Calculation

In hardware, divisor registers store finite numerical values (integers or fixed-point fractions). When f_clk / (OS * Baud) is not a whole number, rounding results in a **frequency mismatch**.

### 3.1 Formulas
```
Baud_actual = f_clk / (OS * Divisor_rounded)
```

```
Error (\%) = ( (Baud_actual - Baud_target) / Baud_target ) * 100\%
```

---

### 3.2 Why Timing Error Causes Framing Errors (Cumulative Phase Drift)
- The receiver resynchronizes its timing clock **only once per byte** (at the start bit's falling edge).
- For the remainder of the 10-bit frame (8 data bits, parity, stop bit), the receiver operates open-loop.
- With each passing bit N, timing error accumulates:
  ```
Δ t_accumulated = N * (T_bit, actual - T_bit, target)
```
- By bit 9 or 10 (the Stop bit), if Δ t_accumulated drifts by more than **± 0.5 * T_bit** (50% of a bit width), the receiver samples on the transition edge or into the adjacent bit.
- **Tolerance Threshold**:
  - Across a 10-bit transmission, total mismatch between sender and receiver **must be < ± 2.5\% to ± 3.0\%**.
  - Any error > 3\% results in frequent **Framing Errors (FE)** or corrupted characters.

---

## 4. Practical Real-World Scenarios

### Scenario A: 16 MHz Clock with Integer Divisor (Why 115200 Fails)
- Microcontroller running at f_clk = 16 MHz = 16,000,000 Hz, Target = 115,200, OS = 16.
- Compute Divisor:
  ```
Divisor = 16,000,000 / (16 * 115200) = 16,000,000 / 1,843,200 ≈ 8.68055
```
- With an integer-only register (rounded to 9):
  ```
Baud_actual = 16,000,000 / (16 * 9) = 111,111.1 bps
```
  ```
Error = ( (111111.1 - 115200) / 115200 ) * 100\% = -3.55\%
```
- **Result**: **FAIL**. -3.55\% exceeds the 3\% limit. Communication with a PC or host will be unstable and drop bytes.

---

### Scenario B: Fractional Baud Rate Generator (Modern MCUs / SoCs)
Modern microcontrollers (such as STM32) provide fractional baud rate registers (e.g. 12-bit mantissa + 4-bit fraction):
- Ideal Divisor = 8.68055
- Integer Mantissa = 8
- 4-bit Fraction = round(0.68055 * 16) = round(10.88) = 11
- Fractional Divisor = 8 + 11 / 16 = 8.6875
- Actual Baud Rate:
  ```
Baud_actual = 16,000,000 / (16 * 8.6875) = 115,107.9 bps
```
  ```
Error = ( (115107.9 - 115200) / 115200 ) * 100\% = -0.08\%
```
- **Result**: **PASS**. Extremely stable (< 0.1\% error).

---

### Scenario C: Why Crystals like 11.0592 MHz and 18.432 MHz Exist
On older boards or dedicated UART interfaces, you will frequently see crystal frequencies like **11.0592 MHz** or **18.432 MHz**:
- Divisor for 115,200 baud on 11.0592 MHz:
  ```
Divisor = 11,059,200 / (16 * 115200) = 11,059,200 / 1,843,200 = 6.0000
```
- Divisor for 9,600 baud:
  ```
Divisor = 11,059,200 / (16 * 9600) = 72.0000
```
- Because 11.0592 MHz is an exact multiple of 115,200 * 16, integer division produces **0.00\% baud rate error**.

---

## 5. Lab Measurement: Finding Unknown Baud Rates with an Oscilloscope

When probing an unidentified serial port or debugging mismatched communication:
1. Connect oscilloscope / logic analyzer channel 1 to the **TX pin** and reference probe to **GND**.
2. Set trigger to **Falling Edge**.
3. Cause the target board to transmit (reboot the board or trigger serial output).
4. Inspect the waveform and identify the **narrowest single pulse** (shortest HIGH or LOW pulse in the burst). In random data, this narrowest pulse corresponds to a single bit (1 * T_bit).
5. Measure its width (Δ t) with scope cursors:
   ```
Baud Rate = 1 / (Δ t)
```

### Quick Lookup Cheatsheet:
| Measured Pulse Width (Δ t) | Inferred Baud Rate |
| :--- | :--- |
| ≈ 104 µs | **9,600** Baud |
| ≈ 52.1 µs | **19,200** Baud |
| ≈ 26.0 µs | **38,400** Baud |
| ≈ 17.4 µs | **57,600** Baud |
| ≈ 8.68 µs | **115,200** Baud |
| ≈ 1.08 µs | **921,600** Baud |
| ≈ 0.67 µs | **1,500,000** (1.5M) Baud |

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
