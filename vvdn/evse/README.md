# EVSE Architecture & IoT Low Voltage Controller Knowledge Base

Welcome to the **VVDN EVSE (Electric Vehicle Supply Equipment) Knowledge Base**. This repository provides an end-to-end engineering guide to the architecture, electrical design, firmware state machines, safety interlocks, and IoT connectivity of **Low Voltage (LV) Controller Boards** used in modern AC Smart Chargers and DC Fast Charging systems.

---

## 1. Executive Summary & System Division

In modern Electric Vehicle Supply Equipment (EVSE), the hardware is divided into two distinct electrical domains:
1. **High Voltage (HV) / Power Distribution Stage**: Manages the grid AC input (Single-Phase $230\,\text{V}$ or Three-Phase $400\,\text{V}$), main contactors, heavy-gauge busbars, residual current sensors, and high-power relays.
2. **Low Voltage (LV) Controller Board (The "Brain" & IoT Gateway)**: Operates strictly within the Safety Extra Low Voltage (SELV / PELV) domain (typically $+12\,\text{V}$, $+5\,\text{V}$, and $+3.3\,\text{V}$). It executes vehicle pilot signaling, contactor actuation, safety monitoring, precision energy metering, user authentication, and cloud communication over OCPP.

```text
       HIGH VOLTAGE DOMAIN (230V / 400V AC)                 LOW VOLTAGE CONTROLLER DOMAIN (SELV)
   ┌───────────────────────────────────────────────┐     ┌─────────────────────────────────────────────────┐
   │                                               │     │                                                 │
   │  AC Grid In ──────► Main Contactor ─────► EV  │     │  Microcontroller (Real-Time Safety & Pilot)     │
   │  (L1, L2, L3, N)         ▲                    │     │   • IEC 61851-1 Control Pilot (±12V PWM)        │
   │                          │ (12V Coil Drive)   │     │   • Proximity Pilot (Cable Rating Sensing)      │
   │                          │                    │     │   • Contactor Coil Driver & Auxiliary Feedback  │
   │  Current Transformers ───┼────────────────────┼────►│   • 6mA DC / 30mA AC Residual Current Monitor   │
   │  (Energy Metering)       │ (Opto-Isolated)    │     │   • Energy Metering AFE (CS5463 / ADE7953)      │
   │                          │                    │     │   • Motorized Connector Lock H-Bridge           │
   │  Auxiliary SMPS          │                    │     ├─────────────────────────────────────────────────┤
   │  (85-264V AC to 12V DC)──┼────────────────────┼────►│  IoT Gateway & Communications Processor         │
   │                          │                    │     │   • Wi-Fi (802.11 b/g/n) & BLE 5.0              │
   │  Protective Earth (PE) ──┴────────────────────┼────►│   • 4G LTE Cat-1 / NB-IoT Cellular Modem        │
   │                                               │     │   • Ethernet (10/100 Mbps RJ45)                 │
   │                                               │     │   • RS-485 Modbus (Dynamic Load Balancing)      │
   │                                               │     │   • RFID / NFC Tap (ISO 14443 Type A/B)         │
   │                                               │     │   • OCPP 1.6-J / OCPP 2.0.1 Cloud Stack         │
   └───────────────────────────────────────────────┘     └─────────────────────────────────────────────────┘
```

---

## 2. Core Functional Blocks of the LV Controller Board

The IoT-based Low Voltage Controller Board integrates nine critical electronic subsystems:

1. **Power Management Unit (PMU)**: Converts the auxiliary $+12\,\text{V}/+24\,\text{V}$ input from the main power board into stable $+5\,\text{V}$, $+3.3\,\text{V}$, and generating a precision $\pm 12\,\text{V}$ dual-rail supply for the Control Pilot. Includes a supercapacitor "Last-Gasp" backup circuit to dispatch power-failure alerts to the cloud before shutting down.
2. **Control Pilot (CP) Circuit**: Implements the $\pm 12\,\text{V}$, $1.0\,\text{kHz}$ bipolar PWM signaling specified by **IEC 61851-1** and **SAE J1772**. Modulates duty cycle to communicate available current ($6\,\text{A}\text{ to }80\,\text{A}$) and samples pilot voltage via precision op-amps to detect vehicle state changes (States A, B, C, D, E, F).
3. **Proximity Pilot (PP) & Cable Detect**: Senses the resistor-encoded value of the connected Type 2 charging cable ($13\,\text{A}, 20\,\text{A}, 32\,\text{A}, 63\,\text{A}$) and controls a motorized solenoid H-bridge to physically lock the plug into the socket during an active session.
4. **Safety & Protective Interlocks**:
   - **Residual Current Monitoring (RCM)**: Interfaced to an active fluxgate sensor detecting $6\,\text{mA}$ DC and $30\,\text{mA}$ AC leakage currents (IEC 62955 compliance).
   - **Welded Contactor Detection**: Optocoupled or auxiliary contact sensing ensuring main contacts open cleanly before the plug lock releases.
   - **Open Protective Earth (PE) Monitoring**: Continuously monitors the chassis ground bond and neutral-to-earth potential.
   - **Over-Temperature Monitoring**: Analog NTC thermistors placed on high-current terminals, contactor body, and the PCB ambient.
   - **Hardware Emergency Stop (E-Stop)**: Fail-safe hardware trip cutting off contactor gate drive instantly.
5. **Precision Energy Metering**: An integrated Analog Front-End (AFE) measuring True RMS Voltage, True RMS Current, Active Power, Reactive Power, and Total Active Energy (kWh) compliant with MID (European Measuring Instruments Directive).
6. **Contactor Actuation Driver**: Low-side N-channel MOSFET or smart high-side driver with inductive flyback suppression diode to switch the $12\,\text{V}$ or $24\,\text{V}$ DC coils of 4-pole power contactors.
7. **Human-Machine Interface (HMI)**: High-luminance RGB LED halo/ring (displaying Ready, Authorizing, Charging, and Fault modes), piezo audio buzzer, and high-frequency RFID/NFC reader (13.56 MHz) for user tap-to-charge authentication.
8. **IoT Network Gateway**: Dual-processor (Cortex-M4 safety MCU + Linux/FreeRTOS IoT SoC) or integrated wireless SoC (e.g., ESP32-S3 / NXP i.MX) supporting multi-bearer connectivity (Wi-Fi, Bluetooth, 4G LTE, Ethernet).
9. **Cloud Protocol Engine (OCPP 1.6-J & 2.0.1)**: Runs secure WebSockets (`wss://`) with TLS 1.3 to communicate with the Central System / Charging Station Management System (CSMS).

---

## 3. Applicable Industry & Safety Standards

| Standard | Governing Body | Scope & Application in EVSE |
| :--- | :--- | :--- |
| **IEC 61851-1** | International Electrotechnical Commission | General requirements for conductive EV charging systems, pilot functions, sequencing, and tolerances. |
| **SAE J1772** | SAE International | North American EV conductive charge coupler standard (Type 1 connector, PWM pilot electrical definitions). |
| **IEC 62196-2** | IEC | Plugs, socket-outlets, vehicle connectors, and vehicle inlets (Type 2 Mennekes & Type 1 physical interfaces). |
| **IEC 62955** | IEC | Residual Direct Current Detecting Device (RDC-DD) to be used for Mode 3 charging of electric vehicles ($6\,\text{mA}$ DC trip). |
| **ISO 15118** | ISO / IEC | Road vehicles — Vehicle to grid communication interface (High-Level Communication, Plug & Charge via GreenPHY PLC). |
| **OCPP 1.6-J / 2.0.1** | Open Charge Alliance (OCA) | Application protocol for communication between EV charging stations and central management backends. |
| **IEC 60664-1** | IEC | Insulation coordination for equipment within low-voltage systems (Creepage and clearance rules). |

---

## 4. Documentation Suite Roadmap

The EVSE documentation suite is organized into focused, modular technical guides:

```text
vvdn/evse/
├── README.md (.docx)                              # Master architecture, domain overview & standards index
├── evse-low-voltage-controller-working.md (.docx) # Detailed working of the LV controller board, pilot, safety & metering
├── evse-iot-and-communication-subsystem.md (.docx)# IoT gateway, 4G/Wi-Fi/Ethernet, OCPP 1.6J/2.0.1 & DLM
└── evse-hardware-schematic-and-interfacing.md (.docx) # Schematics, BOM selection, galvanic isolation & bring-up checklist
```

### [1. Low Voltage Controller Board Working & Architecture](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-low-voltage-controller-working.md)
- Complete internal working of the LV controller board.
- Dual-rail power supply generation ($\pm 12\,\text{V}$ bipolar charge pumps).
- Control Pilot (CP) op-amp circuit, state transitions (A through F), and diode check mechanics.
- Proximity Pilot (PP) resistor decoding and motorized plug lock H-bridge.
- RCM $6\,\text{mA}$ DC / $30\,\text{mA}$ AC leakage trip mechanics.
- Welded contactor detection and fail-safe interlocks.
- Energy metering AFE interfacing with Current Transformers.

### [2. IoT & Communication Subsystem](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-iot-and-communication-subsystem.md)
- Dual-core / Dual-processor architecture (Real-time safety MCU + Linux/FreeRTOS IoT SoC).
- Multi-bearer connectivity: 4G LTE Cat-1 modem (AT commands / PPP), Wi-Fi $802.11\text{b/g/n}$, BLE commissioning, and 10/100 Ethernet.
- Complete OCPP 1.6-J and OCPP 2.0.1 message flows (`BootNotification`, `Authorize`, `StartTransaction`, `MeterValues`, `StopTransaction`).
- Dynamic Load Management (DLM) and solar diversion over RS-485 Modbus RTU.
- Dual-bank Over-the-Air (OTA) firmware update architecture.

### [3. Hardware Schematic Design & Electrical Interfacing](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-hardware-schematic-and-interfacing.md)
- Schematic sub-circuits: CP driver, PP divider, contactor gate driver, motorized lock H-bridge, RCM trigger.
- Galvanic isolation barriers: Reinforced insulation, creepage ($\ge 6\text{--}8\,\text{mm}$), optocouplers, and digital isolators.
- EMC / Surge suppression: MOV, TVS diode, and common-mode filter selections.
- Board bring-up checklist, oscilloscope test points, and root-cause troubleshooting matrix.

---

## 5. Engineering CLI Utility: `tools/evse_calc.py`

An automated hardware calculator is provided to compute charging parameters, duty cycles, and safety metrics:

```bash
# Calculate allowable AC current and charging power from CP PWM duty cycle:
python3 tools/evse_calc.py --mode pwm --duty 53.3 --phase 3

# Sizing required PWM duty cycle for a specific grid current allocation:
python3 tools/evse_calc.py --mode current --current 32 --phase 3 --voltage-grid 400

# Decode Control Pilot voltage state:
python3 tools/evse_calc.py --mode cp --voltage 6.0

# Decode Proximity Pilot cable assembly resistor:
python3 tools/evse_calc.py --mode pp --resistance 220

# Run complete charging session evaluation:
python3 tools/evse_calc.py --mode full --current 32 --phase 3 --voltage-grid 400
```
