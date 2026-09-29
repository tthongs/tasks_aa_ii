# LIN Protocol: Architecture, Standards & Engineering Guide

Welcome to the **VVDN Engineering Hub LIN Protocol Knowledge Base**. This documentation suite provides an exhaustive, industry-grade reference covering the single-wire physical layer, battery-level signaling, deterministic schedule tables, auto-baud clock synchronization, Protected Identifier (PID) parity, Classic vs. Enhanced checksum algorithms, LIN 2.1 / ISO 17987 specifications, and bench bring-up troubleshooting for automotive mechatronics and body electronics.

---

## 1. Executive Summary & Bus Overview

**LIN** (**Local Interconnect Network**) is a standardized, single-wire, low-cost serial communications sub-bus developed by the LIN Consortium (Motorola, Audi, BMW, DaimlerChrysler, Volvo, Volkswagen, and Volcano Automotive) in 1999 and internationally codified under **ISO 17987**.

Designed specifically as a cost-effective complementary sub-network beneath high-speed CAN networks, LIN eliminates unnecessary silicon and wiring costs for simple mechatronic actuators and sensors where CAN transceivers and quartz crystals are economically prohibitive.

Unlike multi-master arbitration buses (CAN) or multi-line point-to-point buses (SPI), LIN operates on a strictly deterministic **Single-Master / Multi-Slave** architecture:
- **Single-Wire Simplicity**: Uses a single physical copper wire referenced to the vehicle chassis Ground (GND), drastically reducing automotive harness weight and connector pin counts.
- **Battery-Level Signaling**: Operates directly at vehicle battery potential ($V_{BAT} = 12\,\text{V}$ nominal, $9\,\text{V} \dots 18\,\text{V}$ dynamic operating range), eliminating the need for step-down voltage regulators on basic sensor modules.
- **Deterministic Scheduling**: The Master Node commands 100% of bus communication via fixed **Schedule Tables**. Bus collisions cannot occur during normal operation, ensuring guaranteed message latency and zero jitter.
- **Ultra-Low Cost Slaves (No Quartz Crystal Required)**: LIN slaves can run on inexpensive internal RC oscillators ($\pm 14\%$ drift). Every frame header begins with a known calibration byte (`0x55`), allowing slaves to dynamically calibrate their bit clocks to the Master's high-precision crystal clock on every single frame!

```text
               +12V Battery (VBAT)
                 │         │
               [1kΩ]     [30kΩ]
                 │─|<─     │─|<─ (Diode)
                 │         │
   LIN Bus ──────┼─────────┼───────────────────────────────
                 │         │
          ┌──────┴──────┐ ┌┴────────────┐
          │ Master Node │ │ Slave Node  │ (Up to 15 Slaves)
          │  (ECU/BCM)  │ │ (Door/Seat) │
          └─────────────┘ └─────────────┘
```

---

## 2. LIN Standards & Generational Evolution

| Standard Version | Release Year | Governing Body | Key Enhancements & Milestones |
| :--- | :--- | :--- | :--- |
| **LIN 1.3** | 2002 | LIN Consortium | Initial mature specification. 8-N-1 UART framing, **Classic Checksum** (data bytes only), fixed baud rates up to 19.2 kbps. |
| **LIN 2.0** | 2003 | LIN Consortium | Major architectural upgrade: Introduced **Enhanced Checksum** (includes PID), diagnostic frames (`0x3C`, `0x3D`), node capability files (NCF), and schedule table switching. |
| **LIN 2.1** | 2006 | LIN Consortium | Node configuration services (Assign NAD, Conditional Change NAD), standardized Transport Layer (LIN TP), and event-triggered collision resolving schedule tables. |
| **LIN 2.2A** | 2010 | LIN Consortium | Clarifications on physical layer conformance, wake-up timeout handling, and node configuration responses. |
| **ISO 17987 (1 to 7)** | 2016 | ISO International | Transitioned LIN into formal ISO standard. Added 12V and 24V commercial vehicle electrical conformance, LIN TP testing, and formal physical layer test procedures. |

---

## 3. Protocol Comparison Matrix: LIN vs. Vehicle & Serial Buses

| Metric / Parameter | LIN (ISO 17987) | CAN 2.0 (ISO 11898) | UART (RS-232 / TTL) | I2C | K-Line (ISO 9141) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Signal Wires** | **1 wire** + GND | **2 wires** (CAN_H, CAN_L) | 2 wires (TX, RX) + GND | 2 wires (SDA, SCL) + GND | 1 wire + GND (Bidirectional) |
| **Operating Voltage** | **12V nominal** ($9-18\text{V}$) | $2.5\text{V} \dots 3.5\text{V}$ diff | $3.3\text{V} / 5\text{V}$ or $\pm 12\text{V}$ | $1.8\text{V} \dots 5.0\text{V}$ | 12V nominal |
| **Max Bitrate** | **19.2 kbps** (Max 20 kbps) | 1.0 Mbps (FD: 5 Mbps) | 115.2 kbps – 1.5 Mbps | 100k, 400k, 1 Mbps | 10.4 kbps |
| **Bus Topology** | Single-Master / Multi-Drop | Multi-Master / Multi-Drop | Point-to-Point | Multi-Master / Multi-Drop | Point-to-Point diagnostic |
| **Max Node Count** | **16 nodes** (1 M + 15 S) | 30 to 100+ nodes | 2 nodes | Up to 128 (7-bit addr) | 1 ECU + 1 Tester |
| **Max Bus Length** | **40 meters** | 40m @ 1M, 1km @ 50k | < 15 meters | < 2 to 3 meters | < 10 meters |
| **Clock Requirements**| Master: Quartz ($\pm 0.5\%$),<br>Slave: **RC osc ($\pm 14\%$)** | Crystal required<br>($\pm 0.1\%$ to $\pm 50\text{ppm}$)| Quartz / Resonator<br>($\pm 2\%$) | Synchronous clock line<br>(Master driven) | Quartz required ($\pm 1\%$) |
| **Arbitration** | **None** (Deterministic Slot) | Non-destructive CSMA/CR | None | Open-drain Wired-AND | None |
| **Typical Cost Ratio**| **0.3x – 0.5x of CAN** | **1.0x (Baseline)** | 0.2x of CAN | 0.1x of CAN | 0.3x of CAN |
| **Primary Domain** | Door mirrors, seats, wipers | Powertrain, ADAS, BCM | Debug consoles, GPS | On-board sensors, PMIC | Legacy OBD-II diagnostics |

---

## 4. Documentation Suite Roadmap

The LIN documentation suite is partitioned into four deep-dive engineering modules:

```text
protocols/lin/
├── README.md (.docx)                              # Master Hub, standard comparison, roadmap & quick links
├── lin-working-and-architecture.md (.docx)        # Single-wire physical layer, 12V signaling, master-slave scheduling
├── lin-frame-and-protocol-analysis.md (.docx)     # Frame format (Break, Sync, PID, Data, Checksum), Classic vs Enhanced
└── lin-timing-synchronization-and-hardware.md (.docx) # Auto-baud math, RC sync, slot sizing, circuitry & RCA matrix
```

### [1. Working Mechanism & Electrical Architecture](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-working-and-architecture.md)
- Single-wire physical layer (ISO 17987-4): Recessive ($\ge 0.8 \times V_{BAT}$) vs Dominant ($\le 0.2 \times V_{BAT}$) voltage thresholds.
- Termination asymmetry: Master pull-up ($1\,\text{k}\Omega$ + diode) vs Slave pull-up ($30\,\text{k}\Omega$ + diode).
- Transceiver architectures (TJA1021, MCP2003, TLIN1029): open-drain NMOS, TXD dominant clamp timeout, and EMC slew-rate control.
- Deterministic schedule table execution, cycle times, and collision-resolving tables for event-triggered frames.
- Low-power Sleep Mode ($<10\,\mu\text{A}$) and dominant Wake-Up pulse mechanics.
- LIN 2.1 Node Configuration and Identification services (NAD, Supplier ID, Function ID).

### [2. Frame Data & Protocol Analysis](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-frame-and-protocol-analysis.md)
- Master Header anatomy: Synch Break Field ($\ge 13$ bits low), Break Delimiter ($\ge 1$ bit high), Synch Byte (`0x55`), and Protected Identifier (PID).
- PID parity equations ($P0, P1$) and the 64-frame ID allocation map.
- Slave Response anatomy: 1 to 8 payload bytes in 8-N-1 UART format and 8-bit checksum.
- Classic Checksum (LIN 1.3 / Diagnostic) vs Enhanced Checksum (LIN 2.x) algorithms with carry handling.
- LIN Frame Types: Unconditional, Event-Triggered, Sporadic, and Diagnostic (`0x3C`, `0x3D`).
- LIN Transport Layer (LIN TP / ISO 17987-2): Single Frame (SF) and Multi-Frame (FF, CF) message flows.
- Logic analyzer and oscilloscope decoded trace walk-through.

### [3. Timing Calculations, Synchronization & Hardware Engineering](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-timing-synchronization-and-hardware.md)
- Bit timing theory ($T_{bit}$) across standard baud rates ($19200$, $9600$, $2400\,\text{bps}$).
- Nominal frame duration and maximum slot sizing formula ($T_{frame\_max} = 1.4 \times T_{frame\_nom}$).
- Slave auto-baud clock synchronization mathematics: 5 falling edges of `0x55` spanning 8 bit times ($8 \times T_{bit}$).
- Microcontroller timer input capture implementation and RC oscillator frequency drift compensation ($\pm 14\%$ down to $\pm 1.5\%$).
- Total bus line capacitance budget ($C_{bus} \le 10\,\text{nF}$) and passive rise time ($t_r$).
- Automotive protection circuitry: Load dump (ISO 7637-2), reverse polarity diode, and TVS clamp layout.
- Root Cause Analysis (RCA) troubleshooting matrix for bench and assembly bring-up.

---

## 5. Engineering CLI Utility: `tools/lin_calc.py`

An automated hardware calculator is provided in the repository to calculate frame slot timing, generate/verify PID parity bits, calculate Classic and Enhanced checksums, and evaluate auto-baud timer capture parameters:

```bash
# 1. Calculate frame duration, max slot time, and bus RC parameters for 19.2 kbps with 8 bytes payload
python3 tools/lin_calc.py --baud 19200 --data-bytes 8 --slaves 8

# 2. Compute PID and parity bits (P0, P1) for LIN ID 0x23
python3 tools/lin_calc.py --pid 0x23

# 3. Calculate Enhanced Checksum for PID 0x23 with 4 payload bytes
python3 tools/lin_calc.py --checksum --pid 0x23 --data 0x01 0x02 0x03 0x04

# 4. Calculate auto-baud timer ticks and clock resolution for 48 MHz timer clock at 19.2 kbps
python3 tools/lin_calc.py --autobaud --timer-clk 48MHz --baud 19200
```

---

## 6. Document Synchronization

All Markdown guides in this directory are synchronized with Microsoft Word (`.docx`) companion files for mentor and customer deliverables using the repository generator:

```bash
python3 tools/md_to_docx.py protocols/lin/README.md
python3 tools/md_to_docx.py protocols/lin/lin-working-and-architecture.md
python3 tools/lin/lin-frame-and-protocol-analysis.md
python3 tools/lin/lin-timing-synchronization-and-hardware.md
```
