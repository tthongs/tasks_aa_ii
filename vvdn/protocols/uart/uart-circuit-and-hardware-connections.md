# UART Hardware Connection & Circuit Schematic Guide

This engineering guide provides detailed, practical hardware schematics and connection blueprints for **UART** (**Universal Asynchronous Receiver-Transmitter**) across logic-level MCU connections, USB bridges, RS-232, RS-485 differential buses, and bidirectional voltage level translators.

---

## 1. Logic-Level (3.3V / 5V) MCU-to-MCU Cross-Over Connection

When directly interconnecting two microcontrollers on the same PCB or short board-to-board header:

```text
       Controller #1 (STM32 / ESP32)                               Controller #2 (MCU / Sensor)
       ┌───────────────────────────┐                               ┌───────────────────────────┐
       │                       TXD ├───[ 22Ω ]────────────────────►│ RXD                       │
       │                           │                               │                           │
       │                       RXD │◄────────────────────[ 22Ω ]───┤ TXD                       │
       │                           │                               │                           │
       │                       RTS ├───[ 22Ω ]────────────────────►│ CTS                       │
       │                           │                               │                           │
       │                       CTS │◄────────────────────[ 22Ω ]───┤ RTS                       │
       │                           │                               │                           │
       │                       GND ├───────────────────────────────┤ GND                       │
       └───────────────────────────┘         Common Ground         └───────────────────────────┘
```

### Critical Hardware Design Rules:
1. **The TX/RX Cross-Over Rule**:
   - Controller #1 **TXD** (Transmit Data, Output) must connect to Controller #2 **RXD** (Receive Data, Input).
   - Controller #1 **RXD** (Receive Data, Input) must connect to Controller #2 **TXD** (Transmit Data, Output).
   - *Trap*: Connecting TX to TX and RX to RX will cause bus contention and complete failure.
2. **Common Ground Connection (Mandatory)**:
   - Asynchronous signaling requires a common voltage reference. Without a shared Ground wire, ground potential shifts will shift the logic threshold (V_IL / V_IH), causing severe framing errors and corrupted data.
3. **Series Damping Resistors (R_series = 22 Ω ... 47 Ω)**:
   - Placed in series on high-speed lines adjacent to the transmitting pin.
   - Absorbs high-frequency transmission line reflections, damps ringing caused by PCB trace parasitic inductance, and protects against ESD/current spikes.
4. **Hardware Flow Control (RTS/CTS)**:
   - **RTS** (Request to Send / Ready to Receive) is driven by the receiving MCU and connects to the sending MCU's **CTS** (Clear to Send).

---

## 2. USB-to-UART Bridge Circuit (FTDI FT232RL / CP2102N / CH340N)

To interface microcontrollers with a host PC via USB Type-C:

```text
       USB-C Receptacle                                               Host Microcontroller
       ┌──────────────┐          ┌───────────────────────┐            ┌──────────────────┐
       │ VBUS (+5V)   ├─────────►│ VBUS (Pin 19)         │            │                  │
       │              │          │                       │            │                  │
       │ D-           ├─────────►│ USBDM (Pin 15)   TXD  ├─[ 1kΩ ]───►│ RXD              │
       │ D+           ├─────────►│ USBDP (Pin 16)   RXD  │◄─[ 1kΩ ]───┤ TXD              │
       │              │          │                  RTS# ├───────────►│ CTS              │
       │ CC1 ──[5.1k]─┤          │                  CTS# │◄───────────┤ RTS              │
       │ CC2 ──[5.1k]─┤          │  FT232RL / CP2102N    │            │                  │
       │ GND          ├────┬────►│ GND (Pins 7, 18, 21,25│     ┌──────┤ DTR# / NRST      │
       └──────────────┘    │     └───────────┬───────────┘     │      └──────────────────┘
                           │                 │ 3V3OUT          │
                          GND                ├───[ 0.1µF ]─┐  [0.1µF] Cap (Auto-Reset)
                                             │             │   │
                                             ▼ To VDDIO   GND  ▼ To MCU Reset Pin (NRST)
```

### Hardware Circuit Details:
- **USB-C CC Pull-Down Resistors**: Two separate 5.1 kΩ resistors from CC1 and CC2 to Ground identify the board as an upstream-facing device (UFP / Sink) to USB-C chargers.
- **Series Protection Resistors (1 kΩ)**: Placed on TXD and RXD lines between the bridge IC and MCU. If the MCU is unpowered while the USB bridge is connected, this prevents parasitic phantom-powering of the MCU through its internal I/O clamp diodes.
- **Auto-Reset Circuit for Firmware Upload**: Connecting the bridge **DTR#** pin through a 100 nF series ceramic capacitor to the microcontroller's active-LOW reset pin (`NRST`) automatically resets the MCU into the bootloader when flashing firmware.

---

## 3. High-Voltage RS-232 Transceiver Circuit (MAX3232 / SP3232)

For interfacing with legacy industrial machinery, PC serial ports, or avionics instruments using ± 12 V bipolar signaling:

```text
                                     +3.3V / +5.0V VCC
                                             │
                                     ┌───────┴───────┐
                                     │  [ 0.1µF MLCC]│ Decoupling
                                     └───────┬───────┘
                                             │
                                     ┌───────┴───────────────────────┐
                     ┌───[ 0.1µF ]──┤ C1+ (Pin 1)                   │
                     │               │ MAX3232 Transceiver           │
                     └───[ Cap ]─────┤ C1- (Pin 3)                   │
                                     │                               │
                     ┌───[ 0.1µF ]──┤ C2+ (Pin 4)                   │
                     │               │                               │
                     └───[ Cap ]─────┤ C2- (Pin 5)                   │
                                     │                               │
                                     │ V+ (Pin 2)  ───[ 0.1µF ]─── GND
                                     │ V- (Pin 6)  ───[ 0.1µF ]─── GND
                                     │                               │
   Microcontroller (3.3V Logic)      │                               │    DB9 Male Connector (DTE)
   ┌───────────────────────────┐     │                               │    ┌──────────────────────┐
   │                       TXD ├────►│ T1IN (Pin 11)   T1OUT (Pin 14)├───►│ Pin 2 (RXD on PC)    │
   │                           │     │ (3.3V Logic)    (±6V to ±12V) │    │                      │
   │                       RXD │◄────┤ R1OUT (Pin 12)  R1IN (Pin 13) │◄───┤ Pin 3 (TXD on PC)    │
   │                           │     │                 (±3V to ±25V) │    │                      │
   │                       GND ├─────┤ GND (Pin 15)                  │    │ Pin 5 (Signal GND)   │
   └───────────────────────────┘     └───────────────────────────────┘    └──────────────────────┘
```

### Critical Component Selection:
- **Charge Pump Flying Capacitors (C_1, C_2, C_V+, C_V-)**: Four 0.1 µF X7R ceramic capacitors generate internal +2* V_CC and -2* V_CC bipolar supplies.
- **Inversion Characteristic**: RS-232 inverts logic states physically:
  - Logic 0 (Space) = +5 V ... +12 V
  - Logic 1 (Mark / Idle) = -5 V ... -12 V

---

## 4. Half-Duplex RS-485 Differential Bus Transceiver Circuit (MAX485 / SN65HVD72)

For multi-drop industrial networks, factory automation (Modbus RTU), and long-distance communications up to 1200 meters:

```text
   +3.3V / +5.0V VCC
         │
     ┌───┴───┐
     │ 0.1µF │ Decoupling
     └───┬───┘
         │
   ┌─────┴─────────────────────────────────────────────────────────────────┐
   │     VCC (Pin 8)                                                       │
   │                                MAX485 / SN65HVD72                     │
   │                              ┌────────────────────┐                   │
   │  RO (Pin 1) ◄────────────────┤ Receiver Output    │                   │
   │                              │                    │     A (Pin 6)     │
   │  RE# (Pin 2) ──┐             │   Differential     ├─────────┬─────────┼──────> Non-Inverting Line (A / +)
   │                ├──┬──────────┤   Receiver         │         │         │
   │  DE (Pin 3) ───┘  │          │                    │     B (Pin 7)     │
   │                   │          │   Differential     ├────┬────┼─────────┼──────> Inverting Line (B / -)
   │  DI (Pin 4) ──────┼─────────►│   Driver           │    │    │         │
   │                   │          └────────────────────┘    │    │         │
   │     GND (Pin 5)   │                                    │    │         │
   └──────────┬────────┼────────────────────────────────────┼────┼─────────┘
              │        │                                    │    │
             GND       ▼ From MCU GPIO                     [120Ω] Termination (At extreme ends)
                       (DIR: 0=Receive, 1=Transmit)         │    │
                                                           ┌┴────┴┐
                                                           │ SM712│ Bidirectional TVS Diode
                                                           │ ESD  │ (Clamps -7V to +12V surges)
                                                           └──┬───┘
                                                              │
                                                         Chassis Earth
```

### Hardware Implementation Rules:
1. **Direction Control (DE and NOT(RE) Tied Together)**:
   - Driver Enable (**DE**, active HIGH) and Receiver Enable (NOT(RE), active LOW) are shorted together on the PCB and connected to a single MCU GPIO pin (`RS485_DIR`).
   - `DIR = LOW (0)`: Driver is disabled (High-Z), receiver is enabled. The node listens to the bus.
   - `DIR = HIGH (1)`: Driver is enabled, receiver is disabled. The node actively drives the differential pair.
2. **120 Ω Bus Termination**:
   - A single 120 Ω 1\% metal-film resistor must be placed across A and B at the **two extreme physical ends** of the transmission line cable. Intermediate nodes must never have termination enabled.
3. **Fail-Safe Biasing Network**:
   - To prevent receiver chatter when all drivers are tri-stated (idle bus where V_A - V_B = 0 V), install fail-safe biasing:
     - Pull-up resistor (560 Ω ... 1 kΩ) from line A to V_CC.
     - Pull-down resistor (560 Ω ... 1 kΩ) from line B to Ground.

---

## 5. Bidirectional 3.3V to 5V Voltage Level-Shifter (MOSFET BSS138)

To interface a 3.3V microcontroller (STM32, ESP32) with a 5V UART device (5V GPS, Arduino, SIM800L):

```text
       +3.3V (LV Rail)                                               +5.0V (HV Rail)
             │                                                             │
            [R1] 10k Pull-Up                                              [R2] 10k Pull-Up
             │                                                             │
             ├──────────────────┐                     ┌────────────────────┤
             │                  │                     │                    │
   3.3V MCU ─┴─ (LV Node)    Source                 Drain  (HV Node) ──────┴─ 5V Device
   (TXD or RXD)                 │     ┌─────────┐     │                        (RXD or TXD)
                             ┌──┴──┐  │  Body   │  ┌──┴──┐
                             │     ├──┤  Diode  ├──┤     │  N-Channel MOSFET (BSS138)
                             │     │  │  ─┤>├── │  │     │
                             └──┬──┘  └─────────┘  └──┬──┘
                                │                     │
                                └─── Gate ────────────┘
                                       │
                                    +3.3V (LV Power Rail)
```

### Circuit Operation:
1. **Idle State (Both lines HIGH)**:
   - The gate is at +3.3 V. Source is pulled to +3.3 V by R_1.
   - V_GS = 3.3 V - 3.3 V = 0 V < V_TH. The MOSFET is OFF.
   - The 5V side is held at +5.0 V by pull-up resistor R_2.
2. **3.3V Device Pulls Line LOW (TXD = 0V)**:
   - Source is driven to 0 V.
   - V_GS = 3.3 V - 0 V = 3.3 V > V_TH. The MOSFET turns fully ON.
   - The conducting channel shorts Drain to Source, pulling the 5V side down to Ground.
3. **5V Device Pulls Line LOW (TXD = 0V)**:
   - Drain is driven to 0 V.
   - Current flows through the MOSFET's intrinsic body diode from Source to Drain, pulling Source down to ≈ 0.6 V.
   - Once Source drops, V_GS rises above V_TH, fully turning on the channel and pulling the 3.3V node down to pure Ground.
