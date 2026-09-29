# CAN Hardware Connection & Circuit Schematic Guide

This engineering guide provides detailed, practical hardware schematics and connection blueprints for the **CAN** (**Controller Area Network**, ISO 11898) and **CAN FD** differential automotive bus across high-speed transceivers, split termination networks, common-mode chokes, ESD protection arrays, and galvanically isolated nodes for high-voltage EV/industrial systems.

---

## 1. High-Speed CAN / CAN FD Transceiver Circuit (TJA1051 / TCAN1042)

Connecting a microcontroller's integrated CAN controller (e.g., STM32 `bxCAN` / `FDCAN`, NXP S32K) to a physical differential bus:

```text
       +5.0V (VCC)         +3.3V (VIO)
            │                   │
        ┌───┴───┐           ┌───┴───┐
        │ 0.1µF │ Decoupling│ 0.1µF │ Decoupling
        └───┬───┘           └───┬───┘
            │                   │
       ┌────┴───────────────────┴──────────────────────────────────────────┐
       │   VCC (Pin 3)         VIO (Pin 5)                                 │
       │                                                                   │
   MCU │   TXD (Pin 1)                         CANH (Pin 7)                ├─────> CAN_H (To Bus)
   ────┤   (3.3V Logic)                                                    │
       │   RXD (Pin 4)                         CANL (Pin 6)                ├─────> CAN_L (To Bus)
   ◄───┤   (3.3V Logic)                                                    │
       │   S / STB (Pin 8) ──── GND (Normal)   GND (Pin 2)                 │
       │                        or MCU GPIO    (Chassis Return)            │
       └───────────────────────────────────────────┬───────────────────────┘
                                                   │
                                                  GND
```

### Critical Circuit Highlights:
1. **The $V_{IO}$ Logic Translation Pin**:
   - The differential bus drivers require a $+5.0\,\text{V}$ supply ($V_{CC}$) to generate the standard $+2.5\,\text{V} \dots +3.5\,\text{V}$ dominant differential voltages.
   - However, modern microcontrollers operate on $+3.3\,\text{V}$ logic.
   - Connecting $+3.3\,\text{V}$ to the **$V_{IO}$ pin** (available on TJA1051T/3, TCAN1042V) shifts the TXD and RXD logic thresholds directly to $+3.3\,\text{V}$, eliminating the need for external level shifters!
2. **Silent Mode / Standby Pin (`S` / `STB`)**:
   - Tied to Ground for normal active transmission and reception.
   - Pulling `S` HIGH disables the transmitter (Silent Mode), preventing the node from sending frames or error flags while keeping the receiver listening (ideal for software diagnostics, babbling-node containment, or listen-only listen modes).

---

## 2. Split Termination Network ($60\Omega + 60\Omega$ with Center Capacitor)

While a single $120\,\Omega$ resistor across CANH and CANL provides basic differential impedance matching, automotive OEMs mandate **Split Termination** to suppress common-mode electromagnetic radiation:

```text
                                         CAN_H Line
       ──────────────────────────────────────┬─────────────────────────────────
                                             │
                                           [R1] 60.4Ω 1% Metal Film
                                             │
                                             ├───[ C_split: 4.7nF ]─── GND (Chassis Ground)
                                             │
                                           [R2] 60.4Ω 1% Metal Film
                                             │
       ──────────────────────────────────────┴─────────────────────────────────
                                         CAN_L Line
```

### Why Split Termination is Superior to Single $120\,\Omega$:
- **Differential Resistance**: $R_{diff} = R_1 + R_2 = 60.4\,\Omega + 60.4\,\Omega \approx 120.8\,\Omega$ (perfect differential impedance matching).
- **Common-Mode Low-Pass Filter**: Common-mode noise appearing equally on CAN_H and CAN_L sees the center node as a virtual AC ground:
  $$f_{cutoff} = \frac{1}{2 \pi \cdot (R/2) \cdot C_{split}} = \frac{1}{2 \pi \cdot (30\,\Omega) \cdot (4.7\,\text{nF})} \approx 1.13\,\text{MHz}$$
  High-frequency common-mode noise and ground bounce are shunted directly to Ground before radiating through the wiring harness.

---

## 3. High-Reliability EMC & Surge Clamping Network (CMC + TVS Diode)

For automotive powertrain, chassis, and industrial robotics exposed to severe electromagnetic fields and ESD discharges:

```text
       CAN Transceiver                                                Wiring Harness Connector
       ┌─────────────┐            Common Mode Choke                   ┌──────────────────────┐
       │ CANH (Pin 7)├────────────[ Coil 1 (51µH) ]──────────────────►│ Pin 1 (CAN_H)        │
       │             │                                     │          │                      │
       │ CANL (Pin 6)├────────────[ Coil 2 (51µH) ]────────┼─────────►│ Pin 2 (CAN_L)        │
       └─────────────┘                                     │          │                      │
                                                          ┌┴────┴┐    │ Pin 3 (GND / Shield) │
                                                          │NUP2105    └──────────┬───────────┘
                                                          │PESD2CAN              │
                                                          │Dual TVS              │
                                                          └───┬──┘               │
                                                              │                  │
                                                         Chassis Earth ──────────┘
```

### Component Functions:
1. **Common Mode Choke (CMC, $51\,\mu\text{H} \dots 100\,\mu\text{H}$)**:
   - Windings are bifilar wound on a common ferrite core.
   - Differential signals pass unhindered with near-zero insertion loss.
   - Unwanted common-mode noise currents induce opposing flux that chokes out the disturbance, providing up to $30\,\text{dB}$ attenuation between $10\,\text{MHz}$ and $100\,\text{MHz}$.
2. **Automotive Dual TVS Diode (NXP PESD2CAN / onsemi NUP2105L)**:
   - SOT-23 package integrating two bidirectional clamping diodes connected to Ground.
   - Ultra-low capacitance ($C_d < 15\,\text{pF}$) to prevent distorting $2\,\text{Mbps} - 5\,\text{Mbps}$ CAN FD bit edges.
   - Withstands $\pm 30\,\text{kV}$ ESD contact discharges (IEC 61000-4-2) and ISO 7637-2 electrical transients.

---

## 4. Galvanically Isolated CAN Transceiver (TI ISO1042 / ADI ADM3053)

Essential in Electric Vehicles (EV main traction inverters, 400V/800V Battery Management Systems, and EVSE DC Fast Chargers) to bridge between high-voltage battery domains and low-voltage vehicle networks:

```text
       Low-Voltage Safe Domain (Microcontroller)                 High-Voltage Hazardous Domain (400V Inverter / Bus)
       +3.3V_MCU                                                 +5.0V_ISO (From Isolated DC-DC Supply)
           │                                                         │
       ┌───┴───┐                                                 ┌───┴───┐
       │ 0.1µF │ Decoupling                                      │ 0.1µF │ Decoupling
       └───┬───┘                                                 └───┬───┘
           │                                                         │
       ┌───┴───────────────────────┐ Galvanic Isolation  ┌───────────┴────────────────────────────────┐
       │ VCC1 (Pin 1)              │     Barrier         │                               VCC2 (Pin 16)│
       │                           │     ======          │                                            │
   MCU │ TXD (Pin 2)               ├──────►||──────►─────┤ Differential Driver           CANH (Pin 14)├───> CAN_H
   ────┤                           │       ||            │                                            │
       │ RXD (Pin 3)               │◄──────||◄─────┼─────┤ Differential Receiver         CANL (Pin 13)├───> CAN_L
   ◄───┤                           │       ||      │     │                                            │
       │ GND1 (Pin 4)              │               │     │ GND2 (Pin 9)                               │
       └───────────┬───────────────┘               │     └───────────┬────────────────────────────────┘
                   │                               │                 │
              GND_MCU (Chassis Ground)             │             GND_ISO (Isolated High-Voltage Return)
                                                   ▼
                                     Capacitive Isolation Barrier
                                     (Reinforced Insulation: 5000 Vrms)
```

---

## 5. Multi-Node Linear Bus Wiring Topology

```text
       Node #1 (Extreme End)          Node #2 (Stub Node)            Node #3 (Extreme End)
       ┌───────────────────┐          ┌───────────────────┐          ┌───────────────────┐
       │ Transceiver       │          │ Transceiver       │          │ Transceiver       │
       │ [Split Term 120Ω] │          │ [No Termination!] │          │ [Split Term 120Ω] │
       └─────────┬─────────┘          └─────────┬─────────┘          └─────────┬─────────┘
                 │                              │ (Stub < 0.3m)                │
   CAN_H ────────o──────────────────────────────o──────────────────────────────o────────
   CAN_L ────────o──────────────────────────────o──────────────────────────────o────────
                 │                                                             │
           [120Ω Split]                                                  [120Ω Split]
```

### Fundamental Physical Topology Rules:
1. **Strict Linear Daisy-Chain (No Star / Tree Routing)**:
   - CAN is strictly a transmission line bus. Star topologies create impedance discontinuities and severe signal reflections that destroy bit decoding.
2. **Termination Exclusively at Extreme Ends**:
   - Exactly two $120\,\Omega$ termination networks must exist across the entire network—one at each physical extreme.
   - Total bus DC resistance measured with an ohmmeter between CAN_H and CAN_L with power OFF must read:
     $$R_{bus,total} = 120\,\Omega \parallel 120\,\Omega \approx 60\,\Omega$$
3. **Keep Stubs Shorter than $0.3\,\text{m}$**:
   - Connections from the linear backbone trunk to an individual ECU must be kept as short as physically possible ($< 0.3\,\text{meters}$) to prevent transmission line stub reflections.
