# UART Protocol: Architecture, Hardware, and Debugging Guide

## 1. What is UART?

**UART** stands for **Universal Asynchronous Receiver-Transmitter**.
- **Universal**: Configurable parameters (baud rate, data length, parity, stop bits).
- **Asynchronous**: No shared clock line is transmitted between devices (unlike SPI or I2C). Both devices must agree on transmission speed (**baud rate**) in advance.
- **Receiver-Transmitter**: Dual independent channels allow simultaneous transmit and receive (**Full Duplex**).

---

## 2. UART Frame Anatomy

In UART, data is transmitted one bit at a time over a single wire. When no data is transmitted, the line is in an **Idle** state (**Logic High / Mark**).

```text
Idle (High) ──────┐          ┌───┬───┬───┬───┬───┬───┬───┬───┐       ┌────── Idle (High)
                  │ Start(0) │D0 │D1 │D2 │D3 │D4 │D5 │D6 │D7 │ Parity│Stop(1)
                  └──────────┴───┴───┴───┴───┴───┴───┴───┴───┴───────┘
                              (Data bits: LSB first to MSB)
```

### Components of a Frame:
1. **Start Bit (1 bit, always Logic 0 / Low)**:
   - Transitions the line from High to Low.
   - Signals the receiver's internal counter to start clocking and sample incoming bits.
2. **Data Bits (typically 8 bits, can be 5 to 9)**:
   - Sent **LSB (Least Significant Bit) first**, ending with **MSB**.
3. **Parity Bit (Optional, 1 bit)**:
   - Used for simple error detection.
   - **None (N)**: No parity bit sent.
   - **Even (E)**: Set to 1 or 0 so the total count of 1s (including parity) is even.
   - **Odd (O)**: Set to 1 or 0 so the total count of 1s (including parity) is odd.
4. **Stop Bit (1, 1.5, or 2 bits, always Logic 1 / High)**:
   - Brings the line back to the Idle (High) state.
   - Gives the receiver time to process the received byte before the next Start bit.

> **Industry Default**: `8-N-1` (8 Data bits, No Parity, 1 Stop bit) = **10 physical bits per transmitted byte**.

---

## 3. Baud Rate: Significance, Hardware Generation & Calculations

> [!NOTE]
> A dedicated deep-dive document with worked examples and error analysis is available at [baud-rate-calculations.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/baud-rate-calculations.md).

### 3.1 What Does Baud Rate Signify?

**Baud Rate** is named after French engineer Émile Baudot. It measures the **number of signal changes (symbol changes or modulations) occurring per second** on the communication line.

#### A. Baud Rate vs. Bit Rate
- **Bit Rate (bps)**: The actual number of information bits transmitted per second.
- **Baud Rate (Bd)**: The number of physical line-state transitions per second.
- **In binary UART**: Each state change represents exactly one bit ($0\text{V} = 0$, $3.3\text{V} = 1$). Therefore:
  $$\text{Baud Rate (symbols/sec)} = \text{Bit Rate (bits/sec)}$$
  *(In multi-level modulations like QAM or PAM4, one baud can carry 2, 4, or more bits. In UART, 1 Baud = 1 bps).*

#### B. Physical Significance: Bit Period ($T_{bit}$)
The baud rate strictly determines the physical duration in time that every single bit occupies on the wire:
$$T_{bit} = \frac{1}{\text{Baud Rate}}$$

At **115,200 Baud**:
$$T_{bit} = \frac{1}{115200} \approx 8.68 \times 10^{-6}\,\text{s} = 8.68\,\mu\text{s}$$

Every bit (Start, Data 0-7, Parity, Stop) must be held on the wire for exactly $8.68\,\mu\text{s}$. Because UART is asynchronous (no clock wire), both sender and receiver rely on internal timers calibrated to this exact interval.

#### C. Gross Baud Rate vs. Actual Useful Payload Throughput
In an `8-N-1` configuration, transmitting **1 byte (8 bits)** of real payload requires:
$$\text{Total Bits on Wire} = 1\,\text{Start} + 8\,\text{Data} + 0\,\text{Parity} + 1\,\text{Stop} = 10\,\text{bits}$$

- Protocol efficiency is $\frac{8}{10} = 80\%$.
- **Effective Data Throughput (Bytes per second)**:
  $$\text{Payload Rate (Bytes/s)} = \frac{\text{Baud Rate}}{\text{Total Bits per Frame}} = \frac{\text{Baud Rate}}{10}$$

| Baud Rate | $T_{bit}$ | Frame Time (10 bits) | Theoretical Payload Throughput |
| :--- | :--- | :--- | :--- |
| **9600** | $104.17\,\mu\text{s}$ | $1.042\,\text{ms}$ | $960\,\text{Bytes/s}$ ($0.94\,\text{KB/s}$) |
| **19200** | $52.08\,\mu\text{s}$ | $520.8\,\mu\text{s}$ | $1,920\,\text{Bytes/s}$ ($1.88\,\text{KB/s}$) |
| **38400** | $26.04\,\mu\text{s}$ | $260.4\,\mu\text{s}$ | $3,840\,\text{Bytes/s}$ ($3.75\,\text{KB/s}$) |
| **57600** | $17.36\,\mu\text{s}$ | $173.6\,\mu\text{s}$ | $5,760\,\text{Bytes/s}$ ($5.63\,\text{KB/s}$) |
| **115200** | $8.68\,\mu\text{s}$ | $86.8\,\mu\text{s}$ | $11,520\,\text{Bytes/s}$ ($11.25\,\text{KB/s}$) |
| **921600** | $1.085\,\mu\text{s}$ | $10.85\,\mu\text{s}$ | $92,160\,\text{Bytes/s}$ ($90.0\,\text{KB/s}$) |
| **1500000** | $0.667\,\mu\text{s}$ | $6.67\,\mu\text{s}$ | $150,000\,\text{Bytes/s}$ ($146.5\,\text{KB/s}$) |

---

### 3.2 How Hardware Calculates & Generates the Baud Rate (Baud Rate Generator / BRG)

Microcontrollers and SoCs (e.g., STM32, ESP32, NXP, Qualcomm, 16550 UART) generate baud rates from an internal system/peripheral clock ($f_{clk}$).

#### A. The Oversampling Mechanism
To reliably sample asynchronous data without a shared clock:
1. The receiver runs an oversampling clock, standardly at **$16\times$ the target baud rate** (some controllers allow $8\times$).
2. When the line drops from High to Low (Start bit falling edge), the UART counter starts.
3. At tick **7 or 8** (midpoint of the start bit), the receiver samples again to verify it is a valid start bit (not a noise glitch).
4. Each subsequent bit is sampled **16 ticks later**, guaranteeing sampling at the exact middle of each bit period where the signal is cleanest.

```text
Clock Ticks (16x):  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 ... 23 24
Line Level:        HIGH ────────┐                                  ┌─────────────
                                └──────── START BIT (Low) ─────────┘   DATA D0...
Sample Point:                                  ▲ (Tick 7-8: Midpoint)          ▲ (+16 Ticks)
```

#### B. The Hardware Divisor Formula
The peripheral clock $f_{clk}$ is divided down using a register called the **Divisor** (e.g., `UBRR` in AVR, `USART_BRR` in STM32, `DLL/DLM` in 16550):

$$\text{Baud Rate} = \frac{f_{clk}}{OS \times \text{Divisor}}$$

Where:
- $f_{clk}$ = Clock frequency supplied to the UART peripheral (in Hz).
- $OS$ = Oversampling factor (typically $16$).
- $\text{Divisor}$ = Value loaded into the Baud Rate Generator register.

#### C. Calculating the Required Divisor:
$$\text{Divisor} = \frac{f_{clk}}{OS \times \text{Baud}_{target}}$$

---

### 3.3 Baud Rate Error & Tolerance Calculation

In hardware, the divisor is often an integer register. When $f_{clk} / (OS \times \text{Baud})$ does not yield a whole number, rounding creates a **baud rate error**.

#### A. Actual Baud Rate & Percentage Error Formulas
$$\text{Baud}_{actual} = \frac{f_{clk}}{OS \times \text{Divisor}_{rounded}}$$

$$\text{Error (\%)} = \left( \frac{\text{Baud}_{actual} - \text{Baud}_{target}}{\text{Baud}_{target}} \right) \times 100\%$$

#### B. Why Does Error Cause Framing Errors? (Cumulative Phase Drift)
- The receiver resynchronizes its clock **only at the falling edge of the Start bit**.
- For all 8 data bits, parity, and the stop bit (up to 10 bit periods), the receiver runs purely open-loop.
- With each passing bit, any timing mismatch accumulates:
  $$\Delta t_{accumulated} = N \times (T_{bit, actual} - T_{bit, target})$$
- By bit 9 or 10 (the Stop bit), if the sampling point drifts by more than **$\pm 0.5 \times T_{bit}$**, the receiver will sample during a logic transition or adjacent bit.
- **Rule of Thumb**: Total clock difference between sender and receiver **must remain within $\pm 2.5\%$ to $\pm 3\%$**. Exceeding $3\%$ results in corrupted bytes and `Framing Errors (FE)`.

---

### 3.4 Practical Real-World Examples

#### Example 1: 16 MHz Clock with Integer Divisor (The "Bad Clock" Problem)
- Given: $f_{clk} = 16\,\text{MHz} = 16,000,000\,\text{Hz}$, Target Baud = $115200$, $OS = 16$.
- Compute Divisor:
  $$\text{Divisor} = \frac{16,000,000}{16 \times 115200} = \frac{16,000,000}{1,843,200} \approx 8.68055$$
- An integer-only register must round to **$9$** (or $8$):
  - With $\text{Divisor} = 9$:
    $$\text{Baud}_{actual} = \frac{16,000,000}{16 \times 9} = 111,111.1\,\text{bps}$$
    $$\text{Error} = \left( \frac{111111.1 - 115200}{115200} \right) \times 100\% = \mathbf{-3.55\%}$$
  - **Verdict**: **Fails!** $-3.55\%$ exceeds the $3\%$ limit. Communication will suffer frequent framing errors and corrupted packets.

#### Example 2: Fractional Baud Rate Generator (Modern MCUs / SoCs)
Modern microcontrollers (like STM32) provide fractional dividers (e.g. 12-bit Mantissa + 4-bit Fraction):
- Ideal Divisor = $8.68055$
- Mantissa = $8$
- Fraction = $\text{round}(0.68055 \times 16) = \text{round}(10.88) = 11$
- Effective Divisor = $8 + \frac{11}{16} = 8.6875$
- Recalculate Actual Baud:
  $$\text{Baud}_{actual} = \frac{16,000,000}{16 \times 8.6875} = 115,107.9\,\text{bps}$$
  $$\text{Error} = \left( \frac{115107.9 - 115200}{115200} \right) \times 100\% = \mathbf{-0.08\%}$$
- **Verdict**: **Passes with flying colors!** ($< 0.1\%$ error).

#### Example 3: Why "Baud Rate Friendly" Crystals Exist (11.0592 MHz, 18.432 MHz)
In older hardware (8051, AVR, legacy industrial controllers), you will see unusual crystal frequencies like **$11.0592\,\text{MHz}$**:
- Divisor for 115,200 baud:
  $$\text{Divisor} = \frac{11,059,200}{16 \times 115200} = \frac{11,059,200}{1,843,200} = \mathbf{6.0000}$$
- Divisor for 9600 baud:
  $$\text{Divisor} = \frac{11,059,200}{16 \times 9600} = \mathbf{72.0000}$$
- Because $11.0592\,\text{MHz}$ is an exact multiple of all standard baud rates, integer divisors yield **$0.00\%$ baud rate error**.

---

### 3.5 How to Measure Unknown Baud Rate in the Lab (Oscilloscope / Logic Analyzer)

When connecting to an unknown board or unlabelled test point:
1. Connect oscilloscope / logic analyzer probe to the board's **TX** pin and **GND**.
2. Trigger the scope on a falling edge while the board boots or transmits data.
3. Zoom in and find the **narrowest single pulse** (shortest high or low pulse). In random data, the narrowest pulse corresponds to a single bit ($1 \times T_{bit}$).
4. Measure the pulse width with cursor $\Delta t$.
5. Compute the baud rate:
   $$\text{Baud Rate} = \frac{1}{\Delta t}$$

*Measurement Cheatsheet:*
- If $\Delta t \approx 104\,\mu\text{s} \longrightarrow \mathbf{9600}$ Baud
- If $\Delta t \approx 26.0\,\mu\text{s} \longrightarrow \mathbf{38400}$ Baud
- If $\Delta t \approx 8.68\,\mu\text{s} \longrightarrow \mathbf{115200}$ Baud
- If $\Delta t \approx 1.08\,\mu\text{s} \longrightarrow \mathbf{921600}$ Baud
- If $\Delta t \approx 0.67\,\mu\text{s} \longrightarrow \mathbf{1500000}$ (1.5M) Baud

---

## 4. Electrical Signatures & Standards

UART is the **logical protocol** (controller/state machine). The physical voltage on the wire depends on the standard:

| Standard | Logic 0 | Logic 1 | Typical Distance | Topology |
| :--- | :--- | :--- | :--- | :--- |
| **TTL / CMOS (3.3V)** | $0\,\text{V}$ | $3.3\,\text{V}$ | $< 1\,\text{meter}$ (board-level) | Point-to-point |
| **TTL / CMOS (1.8V)** | $0\,\text{V}$ | $1.8\,\text{V}$ | $< 0.5\,\text{meter}$ (modern SoCs) | Point-to-point |
| **RS-232** | $+3\,\text{V}\dots +15\,\text{V}$ | $-3\,\text{V}\dots -15\,\text{V}$ | Up to $15\,\text{meters}$ | Point-to-point (Inverted logic!) |
| **RS-485** | Differential: $V_A - V_B < -200\,\text{mV}$ | Differential: $V_A - V_B > +200\,\text{mV}$ | Up to $1200\,\text{meters}$ | Multi-drop bus (up to 32+ devices) |

> [!CAUTION]
> **Never connect an RS-232 cable directly to a TTL UART header (e.g. Raspberry Pi, Qualcomm/NXP/Rockchip SoC header).** RS-232 voltages ($\pm 12\text{V}$) will permanently fry the SoC pins. Always use a level converter/transceiver (e.g., MAX3232).

---

## 5. Flow Control

When the receiver's hardware FIFO or software buffer fills up, it must tell the sender to pause.

1. **None**:
   - Assumes the receiver can always keep up. If receiver drops bytes, data is lost (Buffer Overrun).
2. **Hardware Flow Control (RTS/CTS)**:
   - Uses dedicated lines:
     - **RTS (Request to Send)**: Driven by receiver to indicate readiness to accept data.
     - **CTS (Clear to Send)**: Read by sender before pushing bytes onto TX.
   - Extremely reliable and has zero protocol overhead.
3. **Software Flow Control (XON / XOFF)**:
   - Uses in-band control characters over the data line:
     - `XOFF` (`0x13`, DC3 / Ctrl+S): "Pause transmission"
     - `XON` (`0x11`, DC1 / Ctrl+Q): "Resume transmission"
   - Not suitable for binary data transfer unless escaped.

---

## 6. Linux Serial Subsystem & Debugging Tools

### Identifying Ports:
```bash
# Check kernel detection of USB serial converters (FTDI, CP210x, CH340, PL2303)
dmesg | grep -E "tty|usb"

# List available tty devices
ls -l /dev/ttyUSB* /dev/ttyACM* /dev/ttyS*
```

### Checking & Modifying Port Parameters (`stty`):
```bash
# View current configuration
stty -F /dev/ttyUSB0 -a

# Set baud rate to 115200 with raw mode (no echo, no carriage return translation)
stty -F /dev/ttyUSB0 115200 cs8 -cstopb -parenb raw -echo
```

### Common Terminal Emulators:
- **picocom** (Lightweight, recommended for embedded bringup):
  ```bash
  picocom -b 115200 /dev/ttyUSB0
  # Exit: Ctrl+A then Ctrl+X
  ```
- **minicom**:
  ```bash
  minicom -D /dev/ttyUSB0 -b 115200
  # Configure: Ctrl+A then Z
  ```
- **screen**:
  ```bash
  screen /dev/ttyUSB0 115200
  # Exit: Ctrl+A then k, then y
  ```

---

## 7. Code Examples

### A. Python (`pyserial`)
```python
import serial
import time

def run_uart():
    # Initialize port
    ser = serial.Serial(
        port="/dev/ttyUSB0",
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1.0  # Read timeout in seconds
    )

    try:
        # Send data
        message = b"hello target\n"
        ser.write(message)
        print(f"Sent: {message}")

        # Read response
        response = ser.readline()
        print(f"Received: {response.decode(errors='replace')}")
    finally:
        ser.close()

if __name__ == "__main__":
    run_uart()
```

### B. POSIX C (`termios`)
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <string.h>

int open_uart(const char *portname, speed_t baud) {
    int fd = open(portname, O_RDWR | O_NOCTTY | O_SYNC);
    if (fd < 0) {
        perror("Error opening serial port");
        return -1;
    }

    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        perror("Error from tcgetattr");
        close(fd);
        return -1;
    }

    // Set baud rates
    cfsetospeed(&tty, baud);
    cfsetispeed(&tty, baud);

    // 8-N-1 configuration
    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8; // 8-bit chars
    tty.c_cflag &= ~PARENB;                    // No parity
    tty.c_cflag &= ~CSTOPB;                    // 1 stop bit
    tty.c_cflag &= ~CRTSCTS;                   // No hardware flow control
    tty.c_cflag |= (CLOCAL | CREAD);           // Enable read & ignore ctrl lines

    // Raw input mode
    tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    tty.c_iflag &= ~(IXON | IXOFF | IXANY);    // Turn off s/w flow control
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);

    // Raw output mode
    tty.c_oflag &= ~OPOST;

    // Read timeout: 0.5s (VTIME in deciseconds), minimum 0 bytes
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 5;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        perror("Error from tcsetattr");
        close(fd);
        return -1;
    }

    return fd;
}

int main() {
    int fd = open_uart("/dev/ttyUSB0", B115200);
    if (fd < 0) return 1;

    char buf[128];
    int n = read(fd, buf, sizeof(buf) - 1);
    if (n > 0) {
        buf[n] = '\0';
        printf("Received %d bytes: %s\n", n, buf);
    }

    close(fd);
    return 0;
}
```

---

## 8. Common Errors & Troubleshooting Checklist

1. **Framing Error (FE)**:
   - **Symptom**: Receiver detected invalid Stop bit (sampled 0 instead of 1).
   - **Cause**: Baud rate mismatch, noisy signal lines, or clock drift exceeding ~3%.
2. **Parity Error (PE)**:
   - **Symptom**: Bit count does not match expected parity bit.
   - **Cause**: Corrupted bit over long wire or mismatched parity setting (e.g. Even vs None).
3. **Overrun Error (OE)**:
   - **Symptom**: New character arrived in UART buffer before CPU/driver read previous character.
   - **Cause**: High interrupt latency, baud rate too fast for CPU, or lack of hardware flow control.
4. **Break Condition**:
   - **Symptom**: Continuous logic Low (0) for longer than one full frame.
   - **Cause**: Cable disconnected, RX floating, or target board held in reset.
5. **Garbage Characters**:
   - **Cause**: Mismatched baud rate (e.g., target sending at 115200, host listening at 9600 or 1500000).
6. **No Output At All**:
   - **Check**:
     1. Are TX and RX swapped? (Target TX must go to Host RX).
     2. Is GND connected? (Without common reference, voltages cannot be measured).
     3. Is the device actually booted / receiving power?
