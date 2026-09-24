# SPI Protocol: Architecture, Hardware, and Debugging Guide

## 1. What is SPI?

**SPI** stands for **Serial Peripheral Interface**. Developed by Motorola in the mid-1980s, SPI has become the de facto synchronous serial communication standard for short-distance, board-level embedded systems.

Unlike UART (asynchronous) or I2C (synchronous, half-duplex, multi-master bus with addressing overhead), SPI is designed for **high-speed, low-complexity, full-duplex data exchange** between a central controller and peripheral devices.

### Core Architectural Attributes:
- **Synchronous**: Uses an explicit shared clock line (**SCLK**). Sender and receiver never need to negotiate or guess baud rates, eliminating the clock drift and framing error issues common to UART.
- **Full-Duplex**: Dedicated transmission (**MOSI**) and reception (**MISO**) lines operate concurrently, allowing simultaneous two-way data streaming.
- **Controller-Target Architecture** (formerly Master-Slave): A single Controller initiates all transactions, generates the clock, and drives Chip Select lines to address individual peripherals.
- **High Throughput**: Commonly operates from **1 MHz up to 50 MHz, 80 MHz, or 100+ MHz**, limited primarily by PCB trace length, load capacitance, and slave propagation delay.
- **Zero Protocol Addressing Overhead**: Slaves are selected using physical hardware lines (**CS / SS**) rather than in-band 7-bit/10-bit address bytes as in I2C.

### Interface Comparison Matrix:

| Feature | UART | I2C | SPI |
| :--- | :--- | :--- | :--- |
| **Clocking** | Asynchronous (No clock wire) | Synchronous (Shared SCL) | Synchronous (Shared SCLK) |
| **Duplex** | Full Duplex | Half Duplex | Full Duplex |
| **Physical Lines** | 2 (TX, RX) + GND | 2 (SDA, SCL) + GND | 4 (SCLK, MOSI, MISO, CS) + GND |
| **Typical Speeds** | 9.6 kbps – 1.5 Mbps | 100 kbps, 400 kbps, 1–3.4 Mbps | 1 Mbps – 50+ Mbps |
| **Addressing** | Point-to-point (None) | In-band 7-bit / 10-bit address | Dedicated hardware Chip Select ($\overline{\text{CS}}$) |
| **Bus Arbitration** | None | Multi-master arbitration | Single Controller (Multi-CS or Daisy-chain) |
| **Flow Control** | Optional RTS/CTS or XON/XOFF | Hardware clock stretching (Wait states) | None inherent (Controller controls clock pacing) |
| **Overhead** | Start/Stop/Parity bits (~20%) | ACK/NACK, Start/Stop bits, Address | Near zero (data shifts directly into registers) |
| **Typical Use Cases** | Debug console, modems, GPS | Low-speed sensors, RTCs, EEPROMs | Flash memory, displays, high-speed ADCs, DACs |

---

## 2. SPI Physical Signals & Bus Topologies

### 2.1 The Four Classic Signal Lines

```text
  +------------------+                    +------------------+
  |                  |------ SCLK ------->|                  |
  |    Controller    |------ MOSI ------->|    Peripheral    |
  |     (Master)     |<----- MISO --------|     (Slave)      |
  |                  |------ CS0# ------->|                  |
  +------------------+                    +------------------+
```

1. **SCLK / SCK (Serial Clock)**:
   - Generated exclusively by the Controller.
   - Synchronizes the shifting and sampling of data bits on MOSI and MISO.
2. **MOSI / SDO / COPI (Controller Out Peripheral In)**:
   - Carries serial data from the Controller to the Peripheral.
   - Driven actively by the Controller's push-pull output.
3. **MISO / SDI / CIPO (Controller In Peripheral Out)**:
   - Carries serial data from the Peripheral to the Controller.
   - Driven by the Peripheral only when its Chip Select is asserted (active LOW). When deselected, the Peripheral's MISO pin enters a **High-Impedance (High-Z / tri-state)** condition.
4. **$\overline{\text{CS}}$ / $\overline{\text{SS}}$ / NSS (Chip Select / Slave Select)**:
   - Dedicated active-LOW control line driven by the Controller.
   - Asserting CS (driving it LOW) wakes the target Peripheral, enables its MISO output buffer, and synchronizes the transaction frame.
   - Deasserting CS (returning it HIGH) terminates the transaction, resets the peripheral's internal bit counter, and tri-states its MISO pin.

> [!NOTE]
> **Modern Signal Nomenclature**: The open-source and standards community (including OSHWA and the Linux Kernel) adopted modern descriptive naming:
> - **SCLK**: Serial Clock
> - **COPI**: Controller Out, Peripheral In (formerly MOSI)
> - **CIPO**: Controller In, Peripheral Out (formerly MISO)
> - **CS**: Chip Select (formerly SS)

---

### 2.2 Multi-Peripheral Bus Topologies

Unlike I2C where all devices sit on two shared wires, SPI handles multiple peripherals using one of two physical wiring schemes:

#### Topology A: Independent / Parallel Chip Select (Star Topology)
This is the **most common and robust industrial configuration**. SCLK, MOSI, and MISO are shared across all devices in parallel. The Controller allocates one dedicated GPIO pin for each target's $\overline{\text{CS}}$.

```text
                   +------------------------ SCLK
                   |         +-------------- MOSI
                   |         |        +----- MISO
                   |         |        |
  +------------+   |         |        |
  |            |---+---------|--------|--------+
  | Controller |---|---------+--------|--------|--------+
  |            |---|---------|--------+        |        |
  |            |   |         |        |        |        |
  |        CS1#|---|---------|--------|----+   |        |
  |        CS2#|---|---------|--------|----|---|----+   |
  +------------+   |         |        |    |   |    |   |
                   v         v        v    v   v    v   v
                +-----------------------+ +-----------------------+
                | SCLK  MOSI  MISO  CS# | | SCLK  MOSI  MISO  CS# |
                |      Target 1         | |      Target 2         |
                +-----------------------+ +-----------------------+
```

- **Advantages**:
  - Independent addressing: Peripherals can operate at different clock speeds and different SPI modes (e.g. Target 1 at 10 MHz Mode 0; Target 2 at 2 MHz Mode 3).
  - High fault isolation: Failure of one peripheral does not block communication with others.
- **Disadvantages**:
  - Pin count scales linearly with the number of peripherals ($N$ devices require $3 + N$ pins).

#### Topology B: Cascaded / Daisy-Chain Topology
Certain devices (e.g., multi-channel ADCs, LED matrix drivers like MAX7219, shift registers like 74HC595) support cascading. All devices share a single $\overline{\text{CS}}$ and a single SCLK. Data ripples from one device to the next:

```text
  +------------+       +----------+       +----------+
  | Controller | SCLK  | Target 1 | SCLK  | Target 2 |
  |            |---+-->| SCLK     |---+-->| SCLK     |
  |            |   |   |          |   |   |          |
  |        MOSI|---|-->| SDI  SDO |--->-->| SDI  SDO |---> (to CIPO/MISO)
  |            |   |   |          |       |          |
  |         CS#|---+-->| CS#      |------>| CS#      |
  +------------+       +----------+       +----------+
```

- **Operation**: The Controller outputs $N \times 8$ clock cycles. Data pushed into Target 1 overflows through its SDO pin into Target 2's SDI pin. When $\overline{\text{CS}}$ rises HIGH, both chips latch their internal shift registers simultaneously.
- **Trade-off**: Reduces GPIO pin count to exactly 4 pins regardless of device count, but all devices must support daisy-chain mode, share identical SPI modes, and tolerate latency.

---

## 3. SPI Clock Modes: CPOL and CPHA

Because SPI was never standardized by an international treaty organization, early manufacturers introduced differences in how the clock line behaves during idle periods and on which clock edge data is captured.

These variations are governed by two 1-bit configuration parameters:
- **CPOL (Clock Polarity)**: Defines the logic level of SCLK when the bus is idle.
- **CPHA (Clock Phase)**: Defines which clock edge is used to capture (sample) data versus shift (toggle) data.

Together, these form the **Four Universal SPI Modes (0, 1, 2, 3)**.

> [!NOTE]
> A dedicated deep-dive document with worked timing diagrams, edge-trigger state transitions, and round-trip delay analysis is available at [spi-timing-and-modes.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/VVDN/protocols/spi/spi-timing-and-modes.md).

### 3.1 The SPI Mode Matrix

| Mode | CPOL (Polarity) | CPHA (Phase) | Clock Idle Level | Data Sampled On (Capture) | Data Shifted On (Toggle) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | `0` (Logic Low) | `0` (Leading Edge) | **Low (0)** | **Leading / Rising Edge** | **Trailing / Falling Edge** |
| **1** | `0` (Logic Low) | `1` (Trailing Edge) | **Low (0)** | **Trailing / Falling Edge** | **Leading / Rising Edge** |
| **2** | `1` (Logic High) | `0` (Leading Edge) | **High (1)** | **Leading / Falling Edge** | **Trailing / Rising Edge** |
| **3** | `1` (Logic High) | `1` (Trailing Edge) | **High (1)** | **Trailing / Rising Edge** | **Leading / Falling Edge** |

---

### 3.2 Visual Timing Waveforms

#### Mode 0 (CPOL=0, CPHA=0) — *The Global Standard for Flash & Sensors*
- SCLK sits at **0** when idle.
- When $\overline{\text{CS}}$ drops LOW, the first data bit is driven onto MOSI immediately.
- The receiver samples on the **Rising edge** (first edge).
- The transmitter transitions the next bit on the **Falling edge** (second edge).

```text
CS#    ────────┐                                                             ┌────────
               └─────────────────────────────────────────────────────────────┘
SCLK (Idle Low)       ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐
       ───────────────┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───────────
                      ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼
                      |   |   |   |   |   |   |   |   |   |   |   |   |   |
DATA (MOSI/MISO)  ───< D7  >─< D6  >─< D5  >─< D4  >─< D3  >─< D2  >─< D1  >─< D0  >───
                      ▲       ▲       ▲       ▲       ▲       ▲       ▲       ▲
                      |       |       |       |       |       |       |       |
              Sample (Rising) |       |       |       |       |       |       |
                          Shift (Falling)     |       |       |       |       |
```

#### Mode 3 (CPOL=1, CPHA=1) — *The Alternative Flash Standard*
- SCLK sits at **1** when idle.
- When $\overline{\text{CS}}$ drops LOW, SCLK remains High.
- The first clock transition is a **Falling edge**, which causes both sides to shift/setup the first bit.
- The receiver samples on the **Rising edge** (trailing edge).

```text
CS#    ────────┐                                                             ┌────────
               └─────────────────────────────────────────────────────────────┘
SCLK (Idle High)──────┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───────────
                      └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘
                      ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲   ▼   ▲
                      |   |   |   |   |   |   |   |   |   |   |   |   |   |
DATA (MOSI/MISO)  ───────< D7  >─< D6  >─< D5  >─< D4  >─< D3  >─< D2  >─< D1  >─< D0 >
                          ▲       ▲       ▲       ▲       ▲       ▲       ▲       ▲
                          |       |       |       |       |       |       |       |
                  Shift (Falling) |       |       |       |       |       |       |
                               Sample (Rising)    |       |       |       |       |
```

> [!TIP]
> **Why do SPI Flash chips support both Mode 0 and Mode 3?**
> In both Mode 0 and Mode 3, **data is sampled on the Rising edge** of SCLK and **shifted on the Falling edge**. The only physical difference is the idle state of the clock between byte transfers. Because SPI Flash chips sample on the rising edge, internal state machines seamlessly handle both modes without configuration registers.

---

## 4. Shift Register Mechanics & Frame Transfer

### 4.1 The Dual Circular Shift Register Model
Under the hood, an SPI transfer is fundamentally a **circular byte exchange** between two shift registers connected in a ring:

```text
            +----------------- CONTROLLER -----------------+
            |  [ b7 ] [ b6 ] [ b5 ] [ b4 ] [ b3 ] [ b2 ] [ b1 ] [ b0 ]  |
            +---|----------------------------------------------^----+
                | (MOSI)                                       | (MISO)
                v                                              |
            +---|----------------------------------------------^----+
            |  [ b7 ] [ b6 ] [ b5 ] [ b4 ] [ b3 ] [ b2 ] [ b1 ] [ b0 ]  |
            +------------------- PERIPHERAL ----------------+
                                   ▲
                                   | SCLK (Generated by Controller)
```

1. Before the transfer starts, the Controller loads its byte (e.g. command `0x9F`) into its shift register, and the Peripheral loads its byte (e.g. status `0x00`) into its shift register.
2. The Controller asserts $\overline{\text{CS}}$ LOW and starts toggling SCLK.
3. On every clock cycle:
   - The Controller pushes 1 bit out of MOSI into the Peripheral's register.
   - The Peripheral pushes 1 bit out of MISO into the Controller's register.
4. After 8 clock cycles, the two 8-bit values have completely swapped places.

### 4.2 The "To Read, You Must Write" Principle (Dummy Bytes)
Because the Controller generates the clock, **the Peripheral cannot transmit data on its own initiative**.
- If the Controller wants to read an 8-bit register from a sensor or flash chip, it **must transmit 8 clock pulses**.
- To generate 8 clock pulses, the Controller's hardware transmitter must push a byte onto the wire.
- This transmitted byte is known as a **Dummy Byte** (typically `0x00` or `0xFF`).
- In software APIs (such as Linux `ioctl(SPI_IOC_MESSAGE)` or Python `spi.xfer2()`), read operations always require providing a TX buffer of equal length.

### 4.3 Bit Order & Word Size
- **Bit Order**: The vast majority of SPI devices transmit **MSB-first (Most Significant Bit first: D7 -> D0)**. Certain specialized legacy peripherals (e.g., some display controllers or ADC interfaces) use **LSB-first**.
- **Word Size**: Standard SPI uses **8-bit** words. Many precision instrumentation ADCs and DACs (e.g., Analog Devices, Texas Instruments) use **16-bit, 24-bit, or 32-bit** frames.

---

## 5. Electrical Signatures, High-Speed Constraints & Signal Integrity

### 5.1 Voltage Levels & Logic Domains
SPI lines use standard single-ended CMOS push-pull logic:
- **3.3V CMOS**: Common in microcontrollers, industrial sensors, and legacy Flash memories.
- **1.8V CMOS**: Standard for modern high-density processors (Qualcomm, NXP i.MX8, Rockchip, Apple Silicon) and high-speed QSPI/OSPI Flash.
- **1.2V / 0.8V**: Ultra-low-power wearables and modern FinFET SoC interfaces.

> [!CAUTION]
> **Direct Interconnection Warning**: Connecting a 3.3V MCU directly to a 1.8V SPI sensor will destroy the sensor's input electrostatic discharge (ESD) protection diodes. Always use unidirectional or dedicated high-speed level translators (e.g., TI TXU0304 or NXP 74LVC4245).
> **Avoid passive bidirectional level translators** (such as TXS0108E with internal pull-ups) for SPI frequencies $> 10\,\text{MHz}$ due to edge distortion caused by internal one-shot rise-time accelerators.

---

### 5.2 Signal Integrity & High-Speed Edge Termination

At frequencies above 10 MHz, SPI signals (especially SCLK) exhibit high-frequency transmission line behaviors. Fast edge rates ($t_r < 1.5\,\text{ns}$) cause **ringing, voltage overshoot, and ground bounce**:

```text
Severe Clock Ringing (Unterminated)       Clean Terminated Clock (Series Resistor)
        ┌───┐                                      ┌───┐
   /\  /     \  /\                            ┌────┘   └────┐
──/  \/       \/  \──                       ──┘             └──
   ▲ Double-clocking glitch!
```

#### Mitigations:
1. **Series Source Termination**: Place a **$22\,\Omega\text{ to }47\,\Omega$ resistor** in series on the SCLK and MOSI lines immediately adjacent to the Controller's output pins. This absorbs signal reflections from high-impedance receiver inputs.
2. **$\overline{\text{CS}}$ Pull-Up Resistor**: Install a **$10\,\text{k}\Omega$ pull-up resistor** to $V_{DD}$ on every $\overline{\text{CS}}$ line. When the Controller is in reset or booting, its GPIO pins float in High-Z mode; the pull-up keeps all peripherals safely deselected, preventing bus corruption.
3. **MISO Pull-Up/Pull-Down**: A high-impedance $100\,\text{k}\Omega$ pull-up or pull-down prevents MISO from floating when all slaves are deselected, eliminating stray capacitive switching currents in the Controller's input buffer.

---

### 5.3 Maximum Frequency & Bus Timing Constraints
The maximum theoretical clock speed is dictated by the **round-trip propagation delay**:
$$T_{SCLK, min} > 2 \times t_{propagation\_trace} + t_{CO\_slave} + t_{SU\_master}$$

Where:
- $t_{CO\_slave}$ = Slave clock-to-output valid delay (typically $6 - 15\,\text{ns}$).
- $t_{SU\_master}$ = Controller input setup time (typically $2 - 5\,\text{ns}$).
- $t_{propagation\_trace}$ = PCB trace delay ($\approx 6\,\text{ps/mm}$ on standard FR4).

If $T_{SCLK}$ is too short, the Peripheral's MISO data bit will arrive at the Controller **after** the sampling clock edge has already passed, resulting in bit errors.

---

## 6. Advanced SPI Architectures: Dual, Quad (QSPI) & Octal (OSPI)

Classic SPI utilizes 1 bit per clock on MOSI and MISO. For high-speed boot flash memories (NOR Flash) where multi-megabyte firmware images must load in milliseconds, single-bit SPI becomes a bandwidth bottleneck.

```text
Standard SPI (1-bit):  [SCLK]  [CS#]  [MOSI]  [MISO]
Dual SPI     (2-bit):  [SCLK]  [CS#]  [IO0]   [IO1]
Quad SPI     (4-bit):  [SCLK]  [CS#]  [IO0]   [IO1]   [IO2]   [IO3]
Octal SPI    (8-bit):  [SCLK]  [CS#]  [IO0]   [IO1]   [IO2]   [IO3]   [IO4]   [IO5]   [IO6]   [IO7]  [DQS]
```

### Protocol Comparison:

| Protocol | Data Lines | Bits / Cycle | Max Clock | Peak Bandwidth | Common Use Case |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Standard SPI** | 2 (MOSI, MISO) | 1 | 25–50 MHz | 3–6 MB/s | Sensors, EEPROM, ADCs, SD card (SPI mode) |
| **Dual SPI** | 2 (IO0, IO1) | 2 | 80–104 MHz | 20–26 MB/s | Mid-speed serial NOR flash |
| **Quad SPI (QSPI)** | 4 (IO0–IO3) | 4 | 104–133 MHz | 52–66 MB/s | Linux SoC boot flash, MCU XIP (Execute-in-Place) |
| **Octal SPI (OSPI)** | 8 (IO0–IO7) | 8 (SDR) / 16 (DTR) | 133–200 MHz | 200–400 MB/s | High-density automotive flash, IoT PSRAM |

#### QSPI Phase Architecture (1-1-4 vs 1-4-4 vs 4-4-4):
- **1-1-4**: Command byte sent on 1 line (IO0), 24/32-bit Address sent on 1 line, Data read on 4 lines (IO0–IO3).
- **1-4-4**: Command sent on 1 line; Address and Data sent across all 4 lines.
- **4-4-4 (QPI Mode)**: Command, Address, and Data all transmit across 4 lines concurrently for maximum throughput.

---

## 7. Linux SPI Subsystem & Debugging Tools

### 7.1 Linux Kernel Architecture
The Linux SPI subsystem is divided into three functional layers:

1. **SPI Master / Controller Drivers** (`drivers/spi/spi-<controller>.c`, e.g., `spi-imx.c`, `spi-bcm2835.c`, `spi-cadence-quadspi.c`): Hardware-specific driver managing the peripheral's DMA, FIFO, and clock prescalers.
2. **SPI Core** (`drivers/spi/spi.c`): Manages message queues, bus locking, and transaction dispatching.
3. **SPI Device Drivers**:
   - Kernel drivers for dedicated hardware (e.g. `drivers/mtd/spi-nor/` for flash, `drivers/net/can/mcp251x.c` for CAN controllers).
   - **`spidev` (`drivers/spi/spidev.c`)**: Generic user-space driver exposing raw read/write/ioctl primitives via `/dev/spidev<bus>.<cs>`.

---

### 7.2 Device Tree Configuration (`.dts`)
To expose a generic SPI interface to user-space using `spidev`:

```dts
&spi1 {
    status = "okay";
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_spi1>;
    cs-gpios = <&gpio1 12 GPIO_ACTIVE_LOW>,
               <&gpio1 13 GPIO_ACTIVE_LOW>;

    /* Target 0: Generic user-space spidev */
    spidev@0 {
        compatible = "rohm,dh2228fv"; /* standard accepted fallback for spidev */
        reg = <0>;                    /* Chip Select 0 */
        spi-max-frequency = <20000000>; /* 20 MHz */
    };

    /* Target 1: Industrial SPI sensor */
    sensor@1 {
        compatible = "adi,adxl345";
        reg = <1>;                    /* Chip Select 1 */
        spi-max-frequency = <5000000>;  /* 5 MHz */
        spi-cpol;                     /* Mode 3 (CPOL=1, CPHA=1) */
        spi-cpha;
    };
};
```

---

### 7.3 Checking Interfaces & Hardware Loopback Test

#### Step 1: Verify Dev Nodes
```bash
# Check if spidev nodes are created in user space
ls -l /dev/spidev*
# Output: /dev/spidev0.0  /dev/spidev0.1  /dev/spidev1.0
```

#### Step 2: Perform Hardware Loopback Test
A loopback test validates the SPI controller, clock generator, and kernel driver stack without requiring external hardware.
1. Electrically connect **MOSI to MISO** with a jumper wire.
2. Compile and run the official Linux kernel `spidev_test` utility:

```bash
# Download and build spidev_test (or install from your distro)
gcc -O2 /usr/src/linux/tools/spi/spidev_test.c -o spidev_test

# Execute loopback test at 10 MHz in Mode 0
./spidev_test -D /dev/spidev0.0 -s 10000000 -m 0 -v
```

Expected Output on Success:
```text
spi mode: 0x0
bits per word: 8
max speed: 10000000 Hz (10000 KHz)
TX | FF 40 00 00 00 00 95 FF FF FF FF FF 40 00 00 00 00 95 ...
RX | FF 40 00 00 00 00 95 FF FF FF FF FF 40 00 00 00 00 95 ...
```
If RX matches TX bit-for-bit, your SPI master controller and software stack are 100% operational.

---

## 8. Production Code Examples

### 8.1 Python Example (`spidev`)
Reading the 3-byte JEDEC ID (`0x9F` command) from an external Winbond or Macronix SPI Flash memory:

```python
#!/usr/bin/env python3
"""
SPI NOR Flash JEDEC ID Reader using Linux spidev
Reads Manufacturer ID, Memory Type, and Capacity
"""

import spidev
import time

def read_flash_jedec_id(bus: int = 0, device: int = 0):
    # Initialize SPI
    spi = spidev.SpiDev()
    spi.open(bus, device)
    
    try:
        # Configure bus parameters
        spi.max_speed_hz = 10_000_000  # 10 MHz
        spi.mode = 0b00                 # Mode 0 (CPOL=0, CPHA=0)
        spi.bits_per_word = 8
        spi.lsbfirst = False            # MSB First
        
        # JEDEC Read ID Command: 0x9F followed by 3 dummy bytes
        tx_buf = [0x9F, 0x00, 0x00, 0x00]
        
        # xfer2 maintains CS asserted throughout the full 4-byte transfer
        rx_buf = spi.xfer2(tx_buf)
        
        # Extract received bytes
        cmd_echo = rx_buf[0]  # Stale data shifted out during command byte
        mfg_id   = rx_buf[1]  # Manufacturer ID (e.g. 0xEF for Winbond)
        mem_type = rx_buf[2]  # Memory Type
        capacity = rx_buf[3]  # Capacity code (e.g. 0x17 = 64Mbit, 0x18 = 128Mbit)
        
        print("=" * 45)
        print(" SPI NOR FLASH IDENTIFICATION REPORT")
        print("=" * 45)
        print(f"Raw RX Bytes      : {[hex(b) for b in rx_buf]}")
        print(f"Manufacturer ID   : 0x{mfg_id:02X}")
        print(f"Memory Type       : 0x{mem_type:02X}")
        print(f"Capacity Code     : 0x{capacity:02X}")
        
        # Known manufacturer decoding
        manufacturers = {0xEF: "Winbond", 0xC2: "Macronix", 0x20: "Micron", 0x1F: "Adesto"}
        name = manufacturers.get(mfg_id, "Unknown Manufacturer")
        print(f"Identified Device : {name} Serial Flash")
        print("=" * 45)
        
    finally:
        spi.close()

if __name__ == "__main__":
    read_flash_jedec_id(bus=0, device=0)
```

---

### 8.2 POSIX C Example (`spidev` ioctl)
High-performance C application using the Linux `SPI_IOC_MESSAGE(N)` atomic transfer ioctl:

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>

int spi_read_jedec(const char *device_node, uint32_t speed_hz) {
    int fd = open(device_node, O_RDWR);
    if (fd < 0) {
        perror("Failed to open SPI device");
        return -1;
    }

    uint8_t mode = SPI_MODE_0;
    uint8_t bits = 8;

    // Set SPI Mode
    if (ioctl(fd, SPI_IOC_WR_MODE, &mode) < 0) {
        perror("Failed to set SPI mode");
        close(fd);
        return -1;
    }

    // Set Bits Per Word
    if (ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bits) < 0) {
        perror("Failed to set bits per word");
        close(fd);
        return -1;
    }

    // Set Max Speed
    if (ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed_hz) < 0) {
        perror("Failed to set max speed hz");
        close(fd);
        return -1;
    }

    // Prepare Buffers: 1 byte Command (0x9F) + 3 Dummy Bytes
    uint8_t tx[4] = {0x9F, 0x00, 0x00, 0x00};
    uint8_t rx[4] = {0x00, 0x00, 0x00, 0x00};

    struct spi_ioc_transfer tr = {
        .tx_buf = (unsigned long)tx,
        .rx_buf = (unsigned long)rx,
        .len = 4,
        .speed_hz = speed_hz,
        .delay_usecs = 0,
        .bits_per_word = bits,
        .cs_change = 0, // Keep CS asserted throughout the 4 bytes
    };

    // Perform atomic SPI transfer
    if (ioctl(fd, SPI_IOC_MESSAGE(1), &tr) < 0) {
        perror("Failed to execute SPI transfer");
        close(fd);
        return -1;
    }

    printf("SPI Transfer Successful:\n");
    printf("  TX Sent : %02X %02X %02X %02X\n", tx[0], tx[1], tx[2], tx[3]);
    printf("  RX Recv : %02X %02X %02X %02X\n", rx[0], rx[1], rx[2], rx[3]);
    printf("  Manufacturer ID : 0x%02X\n", rx[1]);
    printf("  Memory Type     : 0x%02X\n", rx[2]);
    printf("  Capacity Code   : 0x%02X\n", rx[3]);

    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    const char *node = (argc > 1) ? argv[1] : "/dev/spidev0.0";
    return spi_read_jedec(node, 10000000); // 10 MHz
}
```

---

## 9. Common Errors & Troubleshooting Checklist

### 9.1 Root Cause Failure Matrix

| Symptom | Probable Root Cause | Verification & Diagnostic Action |
| :--- | :--- | :--- |
| **All Bytes Read as `0xFF` or `0x00`** | 1. MISO line floating.<br>2. Peripheral not powered.<br>3. Wrong Chip Select pin driven.<br>4. MOSI/MISO swapped. | Probe $\overline{\text{CS}}$ on scope: Does it transition to $0\,\text{V}$ during transfer? If $\overline{\text{CS}}$ is HIGH, slave MISO buffer remains tri-stated. |
| **Data Shifted by Exactly 1 Bit**<br>(e.g. Expected `0x9F`, read `0x3E` or `0x4F`) | **Clock Phase (CPHA) Mismatch**: Controller sampling on wrong edge before data has stabilized. | Switch between **Mode 0** and **Mode 1** (or Mode 2 and Mode 3). Check peripheral datasheet for exact CPOL/CPHA timing. |
| **First Byte Always Corrupted** | $\overline{\text{CS}}$ asserted too late relative to SCLK ($t_{CSS}$ violated), or line capacitance delaying edge. | Ensure Controller firmware inserts a minimum setup delay ($t_{CSS} \ge 20\,\text{ns}$) between driving $\overline{\text{CS}}$ LOW and first SCLK edge. |
| **Communication Works at 1 MHz, Fails at 20 MHz** | 1. Excessive capacitive loading ($C_L > 50\,\text{pF}$).<br>2. SCLK signal reflections / ringing.<br>3. Round-trip propagation delay exceeding $T_{SCLK}/2$. | Inspect SCLK with 500 MHz scope probe. Check for double-clocking ringing. Add $33\,\Omega$ series resistors at Controller output. |
| **Corrupted Data During Multi-Slave Access** | Multiple slaves driving MISO simultaneously due to slow tri-state disable time ($t_{DIS}$) or overlapping $\overline{\text{CS}}$. | Add a short delay ($t_{CS\_HIGH} \ge 50\,\text{ns}$) between deasserting Slave 1 and asserting Slave 2. |
| **Read Operations Return Stale or Blank Data** | **Dummy Byte Omission**: Software called read API without providing clocking TX bytes. | Remember: "To read, you must write". In C/Python, verify TX buffer length equals total transaction length (Command + Address + Read Bytes). |

---

### 9.2 Step-by-Step Lab Oscilloscope / Logic Analyzer Checklist

When bringing up a new SPI peripheral on the bench:
1. **Verify Power & Logic Levels**: Measure $V_{DD}$ on the target IC pin. Confirm Controller and Target share the same $V_{IO}$ voltage (1.8V or 3.3V).
2. **Confirm Ground Reference**: Connect oscilloscope ground clip directly to the nearest target ground pad.
3. **Trigger on Chip Select ($\overline{\text{CS}}$)**:
   - Configure oscilloscope / logic analyzer Channel 1 to $\overline{\text{CS}}$, set trigger to **Falling Edge**.
   - Verify that $\overline{\text{CS}}$ goes solidly LOW ($< 0.4\,\text{V}$) and returns to HIGH ($> 0.8 \times V_{DD}$) when finished.
4. **Inspect SCLK Quality**:
   - Check SCLK idle voltage: If CPOL=0, SCLK must be $0\,\text{V}$ before $\overline{\text{CS}}$ drops. If CPOL=1, SCLK must be $V_{DD}$.
   - Inspect edge sharpness: Rise time ($t_r$) should be clean and monotonic without stair-stepping or resonant ringing.
5. **Decode MOSI & MISO**:
   - Align cursors with the active sampling edge (Rising for Mode 0/3; Falling for Mode 1/2).
   - Read the 8 bit values manually under the cursors.
   - If manual decoding matches expected data but software reads incorrect values, your Controller's SPI driver mode setting is inverted.
