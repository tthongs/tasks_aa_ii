# CAN Protocol: Architecture, Standards & Engineering Guide

Welcome to the **VVDN Engineering Hub CAN Protocol Knowledge Base**. This documentation suite provides an exhaustive, industry-grade reference covering the physical layer, differential signaling, non-destructive bitwise arbitration, fault confinement, error detection, CAN 2.0A/B, CAN FD, CAN XL, timing budgets, split termination, higher-layer protocols (J1939, CANopen, UDS), and bench troubleshooting for automotive and industrial embedded bring-up.

---

## 1. Executive Summary & Bus Overview

**CAN** (**Controller Area Network**) is a robust, balanced differential serial communication bus standard originally developed by Robert Bosch GmbH in 1986 and internationally standardized under **ISO 11898**. Designed specifically to replace complex, heavy, and fault-prone point-to-point wiring harnesses in automotive vehicles, CAN has become the foundational backbone across automotive electronic control units (ECUs), industrial automation, medical robotics, and avionics.

Unlike point-to-point protocols (UART) or master-directed peripheral buses (SPI, I2C), CAN is a **multi-master, broadcast-oriented, event-driven, packet-switched bus**:
- **Multi-Master**: Any electronic control unit on the bus can initiate data transmission whenever the bus is idle.
- **Message-Based Addressing**: Nodes do not have physical hardware destination addresses. Instead, every message contains an **Identifier** (11-bit in Standard CAN, 29-bit in Extended CAN) indicating the message content, type, and system-wide priority.
- **Non-Destructive Bitwise Arbitration**: If two or more nodes attempt transmission simultaneously, an electrical Wired-AND arbitration resolves contention bit-by-bit without delaying or corrupting the highest-priority frame.
- **Robust Fault Confinement**: Built-in self-diagnostics allow failing or babbling nodes to detect their own internal faults and automatically disconnect themselves (**Bus-Off**) to safeguard the remaining network.

```text
                  120Ω Terminator                                         120Ω Terminator
                  ┌────────────┐                                         ┌────────────┐
       CAN_H ─────┤   [120Ω]   ├──────┬─────────────────┬────────────────┤   [120Ω]   ├─────
                  └────────────┘      │                 │                └────────────┘
       CAN_L ─────────────────────────┼─────────────────┼───────────────────────────────────
                                      │                 │
                               ┌──────┴──────┐   ┌──────┴──────┐
                               │ Transceiver │   │ Transceiver │
                               │  (ISO11898) │   │  (ISO11898) │
                               └──────┬──────┘   └──────┬──────┘
                                  TXD │ RXD         TXD │ RXD
                               ┌──────┴──────┐   ┌──────┴──────┐
                               │ Controller  │   │ Controller  │
                               │   (MCU #1)  │   │   (MCU #2)  │
                               └─────────────┘   └─────────────┘
```

---

## 2. CAN Standards & Generational Evolution

The CAN protocol has continuously evolved to meet soaring automotive data bandwidth demands, progressing from Classical CAN to CAN FD and CAN XL:

| Parameter / Feature | Classical CAN 2.0A | Classical CAN 2.0B | CAN FD (ISO 11898-1:2015) | CAN XL (CiA 610-1 / ISO) |
| :--- | :--- | :--- | :--- | :--- |
| **Year Standardized** | 1991 (Bosch 2.0A) | 1991 (Bosch 2.0B) | 2012 (Bosch) / 2015 (ISO) | 2020 (CiA) / 2024 (ISO) |
| **Identifier Length** | **11-bit** (Base ID) | **29-bit** (Extended ID) | 11-bit or 29-bit | 11-bit (Priority) + 32-bit (Addr) |
| **Max Payload Size** | **8 Bytes** | **8 Bytes** | **Up to 64 Bytes** | **Up to 2048 Bytes** |
| **Arbitration Bitrate** | Up to 1.0 Mbps | Up to 1.0 Mbps | Up to 1.0 Mbps | Up to 1.0 Mbps |
| **Data Phase Bitrate** | Identical (Up to 1 Mbps) | Identical (Up to 1 Mbps) | **2.0 to 5.0+ Mbps** | **10.0 to 20.0+ Mbps** |
| **CRC Security** | CRC-15 | CRC-15 | CRC-17 (<= 16B) / CRC-21 (>16B) | CRC-32C + CRC-13 |
| **Bit Stuffing Method** | Dynamic (1 bit / 5 bits) | Dynamic (1 bit / 5 bits) | Dynamic + Fixed in CRC field | Dynamic + Fixed stuffing |
| **Primary Industry** | Industrial, Body ECUs | Heavy Duty (J1939), Fleet | Powertrain, ADAS, Gateway | Software-Defined Vehicle, Ethernet bridge |

---

## 3. Protocol Comparison Matrix

To assist hardware system architects in selecting the optimal vehicle and board bus, the following table compares CAN against other mainstream embedded protocols:

| Feature / Metric | CAN (ISO 11898) | LIN (ISO 17987) | FlexRay (ISO 17458) | Automotive Ethernet | I2C | SPI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Physical Lines** | **2** (CAN_H, CAN_L) | **1** (LIN Single-wire) | **2 or 4** (Ch A, Ch B diff) | **2** (100BASE-T1 twisted pair)| **2** (SDA, SCL) | **4+** (SCLK, MOSI, MISO, CS) |
| **Signaling Type** | Differential voltage | Single-ended (12V VBAT) | Balanced differential | Full-duplex PAM3 differential | Open-drain wired-AND | Push-pull CMOS |
| **Duplex Mode** | **Half-Duplex** | **Half-Duplex** | Half-Duplex (Dual-channel) | **Full-Duplex** | Half-Duplex | Full-Duplex |
| **Bus Topology** | Linear bus (Multi-drop) | Linear bus (Master-Slave)| Star, Bus, Hybrid | Point-to-point (Switched) | Multi-drop open-drain | Multi-drop (CS per node) |
| **Max Bitrate** | 1 Mbps (FD: 5 Mbps) | 20 kbps | 10 Mbps | 100 Mbps – 10 Gbps | 100 kbps – 1.0 Mbps | 1 Mbps – 50+ Mbps |
| **Max Distance** | 40m @ 1M, 1km @ 50k | 40m | 24m | 15m (Unshielded Twisted Pair)| < 2 meters | < 30 cm |
| **Arbitration** | **Non-destructive CSMA/CR** | **None (Master Schedule)** | Time-triggered TDMA | CSMA/CD or Full-duplex switch | Wired-AND bit-by-bit | Dedicated chip selects |
| **Error Handling** | CRC, Stuff, Form, Bit, ACK | Checksum, Parity | 24-bit CRC, Slot monitor | Ethernet FCS (32-bit CRC) | ACK / NACK bit | None inherent |
| **Fault Confinement**| **Automatic (TEC/REC Bus-Off)**| None (Slave ignores frame)| Node isolation via Guardian | Link drops / PHY auto-neg | Software bus-clear (9 clocks) | Software timeout |
| **Relative Cost** | Medium | Very Low (<0.5x CAN) | High (2x-3x CAN) | Very High (4x-8x CAN) | Lowest (Silicon native) | Lowest (Silicon native) |
| **Primary Domain** | Powertrain, Chassis, BCM | Seats, Mirrors, Wipers, HVAC | Steer-by-wire, Brake-by-wire | Autonomous driving, Radar, Infotainment | Board-level sensors, PMIC | Board-level Flash, IMU, ADC |

---

## 4. Documentation Suite Roadmap

The CAN documentation suite is partitioned into four deep-dive engineering modules:

```text
protocols/can/
├── README.md (.docx)                              # Master Hub, standard comparison, roadmap & quick links
├── can-working-and-architecture.md (.docx)        # Physical layer, differential voltages, arbitration, fault confinement
├── can-frame-and-protocol-analysis.md (.docx)     # Frame formats (2.0A/B, FD), bit stuffing, J1939, CANopen, UDS
├── can-circuit-and-hardware-connections.md (.docx)# Schematics: Transceiver VIO, split termination, CMC, TVS, ISO1042
└── can-timing-bitrates-and-hardware.md (.docx)    # Bit timing budgets, Time Quanta, SJW, TDC, termination & RCA matrix
```

### [1. Working Mechanism & Electrical Architecture](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-working-and-architecture.md)
- Differential signaling physics: V_CAN_H, V_CAN_L, Recessive (2.5V diff 0V) vs Dominant (3.5V/1.5V diff 2.0V).
- Physical transceiver architecture (TJA1042, TCAN1042, isolated ISO1050), TXD dominant clamp, loopback delay (t_loop).
- Split termination (60 Ω + 60 Ω with 4.7 nF filter) vs standard 120 Ω parallel termination.
- Non-destructive bitwise arbitration mechanics and preemption latency.
- The 5 CAN error detection mechanisms (Bit, Stuff, CRC, Form, ACK).
- Fault confinement state machine: Error Active, Error Passive, and Bus-Off transitions via Transmit and Receive Error Counters (TEC, REC).
- CAN controller architecture: Mailbox systems, Acceptance Filters & Masks, and FIFO overrun management.

### [2. Frame Data & Protocol Analysis](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-frame-and-protocol-analysis.md)
- Standard CAN 2.0A (11-bit Identifier) and Extended CAN 2.0B (29-bit Identifier) bit-by-bit frame maps.
- CAN FD frame extension: EDL/FDF bit, BRS (Bit Rate Switch), ESI (Error State Indicator), and DLC expansion (up to 64 bytes).
- Bit stuffing rules, stuffed vs unstuffed fields, and worst-case transmission calculations.
- Higher-layer protocol frameworks:
  - **SAE J1939**: 29-bit CAN ID mapping, PGN, SPN, Transport Protocol (BAM, RTS/CTS).
  - **CANopen**: 11-bit COB-ID, Object Dictionary, NMT, SDO, PDO, and Heartbeat.
  - **ISO 14229 / ISO 15765-2 (UDS & CAN TP)**: Single Frame, First Frame, Consecutive Frame, Flow Control (BS, STmin).
- Logic analyzer and oscilloscope decoded trace walk-through with bit annotations.
- Linux SocketCAN ecosystem: `candump`, `cansend`, `cangen`, `vcan`, and C socket programming.

### [3. Hardware Connections & Circuit Schematics](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-circuit-and-hardware-connections.md)
- High-speed CAN / CAN FD transceiver (TJA1051/TCAN1042) with V_IO logic translation pin (3.3V MCU directly to 5V bus).
- Split termination network (60.4 Ω + 60.4 Ω + 4.7 nF center filter) for common-mode noise suppression.
- High-reliability automotive EMC & surge protection: Common Mode Choke (51 µH) and TVS diode array (PESD2CAN/NUP2105L).
- Galvanically isolated CAN node architecture (TI ISO1042 / ADI ADM3053) for 400V/800V EV traction and BMS.
- Linear multi-node bus wiring topology and stub length constraints (< 0.3 m).

### [4. Timing Calculations, Bitrates & Hardware Engineering](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-timing-bitrates-and-hardware.md)
- Bit timing theory: Nominal Bit Time (NBT), Time Quanta (t_q), Sync_Seg, Prop_Seg, Phase_Seg1, Phase_Seg2.
- Sample point optimization formulas (75\% - 87.5\% per CiA recommendations) and clock divisor integer math.
- Resynchronization Jump Width (SJW), hard synchronization, resynchronization rules, and oscillator tolerance (Δ f).
- Dual bitrate timing in CAN FD and Transmitter Delay Compensation (TDC) with Secondary Sample Point (SSP).
- Physical bus length vs bitrate limitations, propagation delay (τ ≈ 5 ns/m), and stub length rules.
- PCB routing: differential 120 Ω impedance, common-mode chokes, TVS diode layout, and isolation barriers.
- Root Cause Analysis (RCA) troubleshooting matrix for real-world bench and production failures.

---

## 5. Engineering CLI Utility: `tools/can_calc.py`

An automated hardware calculator is provided in the repository to synthesize CAN and CAN FD bit timing registers, calculate bus load, and simulate bitwise arbitration:

```bash
# 1. Calculate CAN 2.0 bit timing registers for 80 MHz clock at 500 kbps (87.5% sample point)
python3 tools/can_calc.py --clock 80MHz --baud 500000 --sp 87.5

# 2. Calculate CAN FD dual-bitrate timing (500 kbps Nominal, 2.0 Mbps Data phase)
python3 tools/can_calc.py --fd --clock 80MHz --baud 500000 --data-baud 2000000

# 3. Calculate frame duration, bit-stuffing overhead, and efficiency for 8-byte payload
python3 tools/can_calc.py --frame --id 0x123 --dlc 8 --baud 500000

# 4. Simulate bitwise arbitration between two competing CAN IDs
python3 tools/can_calc.py --arbitrate --id1 0x120 --id2 0x124
```

---

## 6. Document Synchronization

All Markdown guides in this directory are synchronized with Microsoft Word (`.docx`) companion files for mentor and customer deliverables using the repository generator:

```bash
python3 tools/md_to_docx.py protocols/can/README.md
python3 tools/md_to_docx.py protocols/can/can-working-and-architecture.md
python3 tools/md_to_docx.py protocols/can/can-frame-and-protocol-analysis.md
python3 tools/md_to_docx.py protocols/can/can-timing-bitrates-and-hardware.md
```
