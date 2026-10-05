# SPI Hardware Connection & Circuit Schematic Guide

This engineering guide provides detailed, practical hardware schematics and connection blueprints for the **SPI** (**Serial Peripheral Interface**) across single-slave interfaces, multi-slave star and daisy-chain networks, high-speed Quad-SPI (QSPI) Flash, galvanically isolated bridges, and high-frequency level shifting.

---

## 1. Single-Target Standard 4-Wire SPI Circuit (MCU to Sensor / ADC)

The fundamental interface connecting a microcontroller to a peripheral sensor (e.g., Bosch BMI088 IMU, TI ADS1118 ADC):

```text
       Controller (Master MCU)                                 Target Peripheral (IMU / ADC / Flash)
       ┌─────────────────────────┐                             ┌─────────────────────────┐
       │                    SCLK ├───[ 22Ω ]──────────────────►│ SCLK                    │
       │                         │                             │                         │
       │             MOSI / COPI ├───[ 22Ω ]──────────────────►│ MOSI / SDI              │
       │                         │                             │                         │
       │             MISO / CIPO │◄───────────────────[ 22Ω ]──┤ MISO / SDO              │
       │                         │                             │                         │
       │                   CS0#  ├───[ 22Ω ]──┬───────────────►│ CS# / NSS               │
       │                         │            │                │                         │
       │                     GND ├────────────┼────────────────┤ GND                     │
       └─────────────────────────┘            │                └─────────────────────────┘
                                             [10k] Pull-Up
                                              │
                                             +3.3V (VDD)
```

### Critical Hardware Design Rules:
1. **Series Damping Resistors (R_series = 22 Ω ... 33 Ω)**:
   - High-speed SPI edges have fast slew rates (t_rise < 1.5 ns). At frequencies >= 10 MHz, PCB traces longer than a few centimeters behave as transmission lines.
   - Placing series damping resistors adjacent to each driver pin (SCLK, MOSI, CS# at the Controller; MISO at the Peripheral) absorbs reflections, eliminates ringing, and prevents double-clocking artifacts.
2. **Chip Select Pull-Up Resistor (10 kΩ to V_DD)**:
   - When the microcontroller powers on or is held in reset, its GPIO pins float in high-impedance (High-Z) mode.
   - An external pull-up resistor guarantees that NOT(CS) remains firmly at Logic HIGH during system boot, keeping the peripheral disabled and preventing spurious commands on the SPI bus.
3. **Decoupling Capacitors**:
   - Place a 0.1 µF X7R ceramic capacitor directly adjacent to the peripheral's V_DD pin, with a low-inductance via directly to the ground plane.

---

## 2. Multi-Target Dedicated Chip-Select Topology (Star Routing)

When connecting multiple distinct SPI peripherals (e.g., NOR Flash, IMU, and TFT Display) to a single SPI peripheral:

```text
       Controller (Master MCU)
       ┌─────────────────────┐
       │                SCLK ├───┬──────────────────────┬──────────────────────┐
       │                     │   │                      │                      │
       │                MOSI ├───┼──────────┬───────────┼──────────┬───────────┤
       │                     │   │          │           │          │           │
       │                MISO │◄──┼──────┐   │           │          │           │
       │                     │   │      │   │           │          │           │
       │                CS0# ├───┼──────┼───┼───────────┼──────────┼─────┐     │
       │                CS1# ├───┼──────┼───┼─────┐     │          │     │     │
       │                CS2# ├───┼──────┼───┼─────┼─────┼────┐     │     │     │
       └─────────────────────┘   │      │   │     │     │    │     │     │     │
                                 ▼      │   ▼     ▼     ▼    │     ▼     ▼     ▼
                            ┌───────────┴───────┐ ┌──────────┴─────┐ ┌─────────────┴─────┐
                            │ SCLK MISO MOSI CS#│ │ SCLK MISO MOSI │ │ SCLK MISO MOSI CS#│
                            │                   │ │           CS#  │ │                   │
                            │   Target #1       │ │   Target #2    │ │   Target #3       │
                            │  (NOR Flash)      │ │   (IMU Sensor) │ │  (TFT Display)    │
                            └───────────────────┘ └────────────────┘ └───────────────────┘
```

### Essential Hardware Considerations:
1. **MISO High-Impedance (Tri-State) Verification**:
   - Peripherals must float their MISO pin in high-impedance mode whenever their NOT(CS) is HIGH.
   - *Trap*: Some cheap display controllers or sensors fail to tri-state MISO when deselected, permanently corrupting the shared MISO line for all other targets. Test with an oscilloscope: verify MISO floats freely when all CS lines are HIGH.
2. **Shared Bus Capacitive Loading**:
   - Each added device adds 5 pF ... 10 pF of pin input capacitance plus trace capacitance (C_L ≈ 1 pF/cm).
   - Total bus capacitance slows clock rise times: t_r ≈ 2.2 * R_driver * C_total. Reduce clock frequency if more than 3 to 4 targets share the bus.

---

## 3. Multi-Target Daisy-Chain Topology (Shift-Register Architecture)

Used extensively in LED matrix drivers (MAX7219, TLC5940), digital potentiometers, and relay drivers (74HC595) to drive dozens of devices using only 3 MCU pins:

```text
       Controller (MCU)
       ┌─────────────────────┐
       │                SCLK ├───┬──────────────────────┬──────────────────────┐
       │                     │   │                      │                      │
       │                CS#  ├───┼──────────┬───────────┼──────────┬───────────┤
       │                     │   │          │           │          │           │
       │                MOSI ├───┼──────────┼─────┐     │          │           │
       │                     │   │          │     │     │          │           │
       │                MISO │◄──┼──────────┼─────┼─────┼──────────┼─────┐     │
       └─────────────────────┘   │          │     │     │          │     │     │
                                 ▼          ▼     ▼     ▼          ▼     │     ▼
                            ┌───────────────────┐ ┌───────────────────┐ ┌────┴──────────────┐
                            │ SCLK      CS#     │ │ SCLK      CS#     │ │ SCLK      CS#     │
                            │                   │ │                   │ │                   │
                            │  DIN         DOUT ├─►  DIN         DOUT ├─►  DIN         DOUT ├──┘
                            │                   │ │                   │ │                   │
                            │     Device #1     │ │     Device #2     │ │     Device #3     │
                            │    (74HC595 #1)   │ │    (74HC595 #2)   │ │    (74HC595 #3)   │
                            └───────────────────┘ └───────────────────┘ └───────────────────┘
```

### Working Principle:
- Data is clocked in serially as a continuous multi-byte stream.
- As new bits enter Device #1 via `DIN`, overflow bits from Device #1's shift register emerge on `DOUT` and feed directly into Device #2's `DIN`.
- When the entire payload (e.g., 24 bits for three 8-bit devices) has been shifted, the Controller pulses the shared **NOT(CS)** line to latch the data into all devices simultaneously.

---

## 4. High-Speed Quad-SPI (QSPI) NOR Flash Circuit (Winbond W25Q128JV)

For high-speed firmware execution (Execute-in-Place / XiP) and graphic assets streaming:

```text
       Host Microcontroller (STM32 / NXP i.MX)                 Quad-SPI NOR Flash (W25Q128JV, 133MHz)
       ┌─────────────────────────────────────┐                 ┌────────────────────────────────────┐
       │                          QSPI_CLK   ├───[ 22Ω ]──────►│ CLK (Pin 6)                        │
       │                                     │                 │                                    │
       │                          QSPI_NSS   ├───[ 22Ω ]──┬───►│ CS# (Pin 1)                        │
       │                                     │            │    │                                    │
       │                          QSPI_IO0   ├───[ 22Ω ]──┼───►│ DI / IO0 (Pin 5)                   │
       │                          QSPI_IO1   ◄───[ 22Ω ]──┼───┤ DO / IO1 (Pin 2)                   │
       │                          QSPI_IO2   ◄───[ 22Ω ]──┼───┤ WP# / IO2 (Pin 3)                  │
       │                          QSPI_IO3   ◄───[ 22Ω ]──┼───┤ HOLD# / RESET# / IO3 (Pin 7)       │
       │                                     │            │    │                                    │
       │                          VDD (+3.3V)├────────────┼───►│ VCC (Pin 8)                        │
       │                                     │           [10k] │                                    │
       │                          GND        ├────┬───────┼───►│ GND (Pin 4)   [ 0.1µF ] [ 4.7µF ]  │
       └─────────────────────────────────────┘    │       │    └──────────────────┬─────────┬───────┘
                                                 GND     +3.3V                   GND       GND
```

### PCB Layout Guidelines for QSPI:
1. **Length Matching**: Match trace lengths between `CLK` and all 4 data lines (`IO0` through `IO3`) within ± 1.0 mm (≈ 6 ps skew) to prevent data phase misalignment at 104 MHz - 133 MHz.
2. **Continuous Ground Return Plane**: Route all 6 QSPI lines directly above an uninterrupted, solid ground plane layer. Never cross split plane boundaries.
3. **Controlled Characteristic Impedance**: Design traces with 50 Ω ± 10\% single-ended characteristic impedance.

---

## 5. Galvanically Isolated High-Speed SPI (ADI ADuM3401 / TI ISO7741)

Used in high-voltage automotive EV Battery Management Systems (BMS), motor drives, and solar inverters to cross hazardous voltage barriers (> 1500 V_rms):

```text
       Low-Voltage Safe Domain (MCU)                             High-Voltage Domain (Isolated ADC / BMS)
       +3.3V_MCU                                                 +3.3V_ISO (From Isolated DC-DC)
           │                                                         │
       ┌───┴───┐                                                 ┌───┴───┐
       │ 0.1µF │ Decoupling                                      │ 0.1µF │ Decoupling
       └───┬───┘                                                 └───┬───┘
           │                                                         │
       ┌───┴───────────────────────┐ Galvanic Isolation  ┌───────────┴───────────────────────┐
       │ VDD1 (Pin 1)              │     Barrier         │                      VDD2 (Pin 16)│
       │                           │     ======          │                                   │
   MCU │ VIA (Pin 3)   SCLK        ├──────►||──────►─────┤ VOA (Pin 14)   SCLK               │ Isolated
   ────┤                           │       ||            │                                   ├─── BMS
       │ VIB (Pin 4)   MOSI        ├──────►||──────►─────┤ VOB (Pin 13)   MOSI               │    IC /
   ────┤                           │       ||            │                                   ├─── ADC
       │ VIC (Pin 5)   CS#         ├──────►||──────►─────┤ VOC (Pin 12)   CS#                │
   ────┤                           │       ||            │                                   │
       │ VOD (Pin 6)   MISO        │◄──────||◄─────┼─────┤ VID (Pin 11)   MISO               │
   ◄───┤                           │       ||      │     │                                   │
       │ GND1 (Pins 2, 8)          │               │     │ GND2 (Pins 9, 15)                 │
       └───────────┬───────────────┘               │     └───────────┬───────────────────────┘
                   │                               │                 │
              GND_MCU (Chassis Ground)             │             GND_ISO (Isolated Battery -)
                                                   ▼
                                         Reverse Channel for MISO
```

### Critical Isolator Engineering Constraints:
- **Propagation Delay Limit**: Digital isolators introduce 8 ns ... 15 ns propagation delay in *each* direction. Total round-trip delay is doubled (2 * t_prop ≈ 20 ns - 30 ns).
- **Maximum Safe Clock Rate**: With a 12 ns isolator and 10 ns peripheral clock-to-output time (t_CO), the maximum safe read frequency is capped at:
  ```
f_max <= 1 / (2 * (t_prop + t_CO + t_SU)) ≈ 1 / (2 * (12ns + 10ns + 4ns)) ≈ 19.2 MHz
```
