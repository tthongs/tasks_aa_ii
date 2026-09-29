# LIN Hardware Connection & Circuit Schematic Guide

This engineering guide provides detailed, practical hardware schematics and connection blueprints for the **LIN** (**Local Interconnect Network**, ISO 17987) single-wire automotive bus across Master and Slave nodes, automotive surge protection networks (ISO 7637-2), and vehicle body harness topologies.

---

## 1. Automotive Master Node Circuit Architecture (TJA1021 / TLIN1029-Q1)

In a LIN cluster, the **Master Node** coordinates all scheduling and transmits frame headers. It requires an explicit external **$1\,\text{k}\Omega$ master pull-up termination** path:

```text
       +12V Battery Power (VBAT / KL30)
             │
             ├───[ Diode: BAS21 / 1N4148 ] (Prevents reverse current if VBAT drops)
             │
            [R_master] 1.0kΩ 1% (Master Pull-Up)
             │
             ├───┬─────────────────────────────────────────────────────────────> Single-Wire LIN Bus
             │   │                                                               (To All Slaves)
             │  [C_master] 1.0nF Ceramic (EMC Slew-Rate Filter)
             │   │
             │  GND
             │
             │   LIN (Pin 6)
       ┌─────┴───────────────────────────────────┐
       │                                         │
       │         NXP TJA1021 / TI TLIN1029       │
       │         Automotive LIN Transceiver      │
       │                                         │
   MCU │ TXD (Pin 1)                 VBAT (Pin 7)├───[ Reverse Protection Diode ]─── +12V VBAT
   ────┤ (From UART TX)                          │
       │ RXD (Pin 4)                 WAKE (Pin 8)├─── Open / Tie to Ground
   ◄───┤ (To UART RX)                            │
       │ NSLP (Pin 2)                GND (Pin 3) ├─── GND (Chassis Return)
   ────┤ (Sleep Control GPIO)                    │
       └─────────────────────────────────────────┘
```

### Critical Component Roles:
1. **$1.0\,\text{k}\Omega$ Master Termination Resistor**:
   - The master pull-up drops the total bus impedance to $\approx 1\,\text{k}\Omega \parallel (30\,\text{k}\Omega / N_{slaves}) \approx 800\,\Omega \dots 950\,\Omega$.
   - This low impedance guarantees fast bus rise times ($t_r < 5\,\mu\text{s}$) even with $10\,\text{nF}$ total harness wiring capacitance.
2. **Reverse Blocking Diode (BAS21 / 1N4148)**:
   - Placed in series with the $1\,\text{k}\Omega$ pull-up resistor.
   - If the vehicle battery voltage ($V_{BAT}$) fluctuates or drops during engine crank ($6\,\text{V}$ cold crank), this diode prevents current from back-feeding from the bus capacitance into the battery rail.
3. **Master EMC Filter Capacitor ($C_{master} = 1.0\,\text{nF}$)**:
   - Placed directly between the LIN bus pin and Ground on the master board to shape transition edges and suppress RF radiated emissions.

---

## 2. Automotive Slave Node Circuit Architecture

Slave nodes (door lock motors, seat heaters, rain/light sensors) contain an **integrated internal $30\,\text{k}\Omega$ pull-up** and require only minimal external passive components:

```text
                               +12V Local VBAT
                                     │
                             ┌───────┴───────┐
                             │  [ 0.1µF MLCC]│ Decoupling
                             └───────┬───────┘
                                     │
                             ┌───────┴─────────────────────────────────────────┐
                             │ VBAT (Pin 7)                                    │
                             │            Microchip MCP2003A / TI TLIN1029     │
                             │            Automotive Slave Transceiver         │
                             │                                                 │
   MCU UART TX ─────────────►│ TXD (Pin 1)                 LIN (Pin 6)         ├──────► Single-Wire LIN Bus
                             │                                                 │        (From Master)
   MCU UART RX ◄─────────────┤ RXD (Pin 4)                     │               │
                             │                                 │ (Integrated   │
   MCU Sleep GPIO ──────────►│ CS / NSLP (Pin 2)               │  30kΩ + Diode)│
                             │                                 │               │
                             │ GND (Pin 3)                     │               │
                             └───────┬─────────────────────────┼───────────────┘
                                     │                         │
                                    GND                       [220pF] Slave EMC Filter Cap
                                                               │
                                                              GND
```

### Slave Design Guidelines:
- **No External $1\,\text{k}\Omega$ Resistor**: Adding an external $1\,\text{k}\Omega$ pull-up to a slave node will violate LIN specification pull-up requirements and overload transceiver output transistors.
- **Slave Capacitance ($C_{slave} \approx 220\,\text{pF}$)**: The LIN specification restricts each slave node to $\le 250\,\text{pF}$ of total pin and filter capacitance to ensure a cluster of 16 slave nodes does not exceed the total maximum network capacitance limit ($10\,\text{nF}$).

---

## 3. Automotive Transient Surge Protection Network (ISO 7637-2 / ISO 16750)

In automotive wiring harnesses, load dump transients, inductive relay kicks, and electrostatic discharge (ESD) will destroy unshielded transceivers. A dedicated automotive surge suppression network is mandatory:

```text
       LIN Transceiver Pin                                        External Wiring Harness Connector
       ──────────────────┬─────────────────[ Ferrite Bead ]──────────────┬───────────────> LIN Wire to Harness
                         │                  (600Ω @ 100MHz)              │
                        [C] 220pF                                      ┌─┴─┐
                         │                                             │   │ Automotive TVS Diode
                        GND                                            │   │ (PESD1LIN / SMAJ24CA)
                                                                       │   │ Clamps -27V to +40V pulses
                                                                       └─┬─┘
                                                                         │
                                                                    Chassis Earth
```

### Automotive Transient Standards Met:
- **ISO 7637-2 Pulse 1 (Inductive Disconnect)**: $-100\,\text{V}$ negative inductive spike clamped safely by the TVS forward diode drop.
- **ISO 7637-2 Pulse 2a / 3a / 3b (Switching & Coupling)**: $+75\,\text{V} / \pm 150\,\text{V}$ high-frequency transients absorbed by the ferrite bead and TVS.
- **ESD Ruggedness (IEC 61000-4-2)**: $\pm 15\,\text{kV}$ air discharge and $\pm 8\,\text{kV}$ contact discharge.

---

## 4. Complete Vehicle Body Cluster Wiring Topology

```text
   Master Electronic Control Unit (BCM / Gateway)
   ┌──────────────────────────────────────────────┐
   │ Master Transceiver                           │
   │ [1kΩ Pull-Up + BAS21 Diode + 1nF Filter]     │
   └──────────────────────┬───────────────────────┘
                          │
                          │ Single-Wire Automotive Harness (0.35 mm² to 0.5 mm² wire)
                          │ (Total Length: Up to 40 meters, Max 16 Nodes)
                          ├───┬───────────────────────────────┬───────────────────────────────┐
                          │   │                               │                               │
                          ▼   ▼                               ▼                               ▼
                     ┌────────┴──────────────┐       ┌────────┴──────────────┐       ┌────────┴──────────────┐
                     │ Slave Node #1         │       │ Slave Node #2         │       │ Slave Node #3         │
                     │ (Driver Door Lock)    │       │ (Window Lifter Motor) │       │ (Side Mirror Fold)    │
                     │ [Internal 30kΩ, 220pF]│       │ [Internal 30kΩ, 220pF]│       │ [Internal 30kΩ, 220pF]│
                     └───────────────────────┘       └───────────────────────┘       └───────────────────────┘
```
