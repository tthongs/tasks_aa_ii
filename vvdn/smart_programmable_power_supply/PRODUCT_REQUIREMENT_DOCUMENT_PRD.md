# Product Requirement Document (PRD)

---

### Project Information
* **Project Code**: `VVDN_SPPS_2026`
* **Project Name**: Smart Programmable Voltage Supply Module (85–265 V AC Input, 5–20 V / 3 A DC Programmable Output)
* **Revision**: `Rev 1.0`
* **Date**: `08 Oct 2026`

---

### Revision History

| Date | Revision No. | Description | Prepared/Revised By | Reviewed By | Approved By |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 08 Oct 2026 | Rev 1.0 | Initial release of PRD for Smart Programmable Voltage Supply Module | Hardware Team Lead (SPPS) | BU SME (Power Electronics) | BU Head (Embedded Hardware) |

---

### Customer Sign Off
**CUSTOMER SIGN-OFF FORM**

* **Customer**: Commercial Test & Measurement / Industrial OEM Client
* **Technical In-Charge**:
  * Name: `<Customer Technical Lead>`
  * Designation: Director of Hardware Engineering
  * Email ID: `customer.tech@client.com`
  * Address: `<Client Technology Park, San Jose, CA>`
  * Comments: Requirements reviewed and aligned with next-generation automated test equipment (ATE) specifications.
  * Signature & Date: `____________________`
* **Program In-Charge**:
  * Name: `<Customer Program Manager>`
  * Designation: Program Director
  * Email ID: `customer.pm@client.com`
  * Address: `<Client Technology Park, San Jose, CA>`
  * Comments: Approved for Phase 1 Architecture and Schematic Bring-Up.
  * Signature & Date: `____________________`

---

### Internal Sign Off
**INTERNAL SIGN-OFF**

* **VVDN Technical In-Charge**:
  * Name: Vignesh Anandhan / Karpagamoorthy R
  * Designation: Principal Hardware Architect
  * Email ID: `vignesh.a@vvdntech.com`
  * Address: VVDN Technologies, B-22, Infocity Sector-34, Gurgaon-122001, Haryana, India
  * Comments: Multi-mode 4-switch Buck-Boost architecture with dual-domain metering meets all technical boundaries.
  * Signature & Date: `____________________`
* **VVDN Program In-Charge**:
  * Name: Gaurav Gupta / Shivam Saxena
  * Designation: Engineering Delivery Manager
  * Email ID: `gaurav.gupta@vvdntech.com`
  * Address: VVDN Technologies, B-22, Infocity Sector-34, Gurgaon-122001, Haryana, India
  * Comments: Project schedule, deliverable releases, and BOM targets approved.
  * Signature & Date: `____________________`
* **Internal Sign Off (Level 1 - BU SME)**:
  * Name: BU SME (Power & Industrial BU)
  * Comments: Architecture validated against IEC 62368-1 reinforced isolation and CISPR 32 Class B standards.
  * Signature & Date: `____________________`

---

## Table of Contents
* **1. Introduction**
  * 1.1 Purpose
  * 1.2 Document Conventions
  * 1.3 Intended Audience and Reading Suggestions
  * 1.4 Abbreviation
  * 1.5 References
* **2. Product Overview**
  * 2.1 Product - Business Perspective
  * 2.2 Product - Technical Perspective
  * 2.3 Use Cases
  * 2.4 Product Interfaces
    * 2.4.1 Hardware Interfaces
    * 2.4.2 Software Interfaces
* **3. Systems & Domains Involved**
* **4. Product Requirements**
  * 4.1 System 1 Requirements (Hardware Power Supply Module)
    * 4.1.1 Specific Requirements
  * 4.2 System 2 Requirements (Embedded Control & Telemetry Software)
    * 4.2.1 Specific Requirements
* **5. Assumptions**
* **6. Dependencies**
* **7. Standard Deliverables & Release Order**
  * 7.1 Product Development Plan
  * 7.2 System 1 Development Plan
  * 7.3 System 2 Development Plan
* **8. Architecture <optional>**
  * 8.1 System 1: Domain 1 Architecture (Hardware Power Stage)
  * 8.2 System 1: Domain 2 Architecture (Firmware & Control Loop)
* **9. Bill Of Material <optional>**
  * 9.1 System 1: Product BOM
* **10. Out of Scope**
* **11. Open Items**

---

## 1. Introduction

### 1.1 Purpose
The purpose of this Product Requirement Document (PRD) is to capture all engineering, electrical, mechanical, safety, firmware, and telemetry requirements for the development of the **Smart Programmable Voltage Supply Module (85–265 V AC In, 5–20 V / 3 A DC Out)**. This document serves as the definitive contractual and technical reference for the entire hardware design, embedded firmware implementation, verification testing, and manufacturing lifecycle of the product.

> [!IMPORTANT]
> The requirements captured in this document supersede any previous documents, customer RFQs, preliminary proposals, and meeting discussions. This PRD shall be taken as the sole authoritative reference baseline for design acceptance and sign-off.

### 1.2 Document Conventions
* **Typographical Conventions**:
  * Requirements marked with **[MUST]** represent mandatory non-negotiable specifications essential for compliance, safety, and functionality.
  * Requirements marked with **[SHOULD]** represent highly desired performance metrics where reasonable engineering trade-offs may be considered upon SME approval.
  * Requirements marked with **[COULD]** represent future optional enhancements.
* **Inheritance**: High-level system requirements cascade down into subsystem specifications unless explicitly stated otherwise.
* **Standards Reference**: All engineering units conform to the International System of Units (SI).

### 1.3 Intended Audience and Reading Suggestions
This document is intended for:
1. **Client Engineering & Management Teams**: For functional scope sign-off and milestone tracking (Sections 1, 2, 7, 10).
2. **Hardware Architecture & Schematic Teams**: For power stage sizing, magnetics, safety creepage, and BOM selection (Sections 2.4.1, 4.1, 8.1, 9.1).
3. **Embedded Firmware & Software Teams**: For control state machines, DAC summing calibration, SCPI parser, and data logging tasks (Sections 2.4.2, 4.2, 8.2).
4. **Layout & Mechanical Engineering Teams**: For 4-layer stackup, creepage slots, thermal copper spreading, and connector placements (Sections 4.1.1, 8.1).
5. **Quality Assurance & Certification Teams**: For bench bring-up, Hipot dielectric testing, CISPR 32 Class B EMC, and IEC 62368-1 compliance verification (Sections 4.1.1, 7.2).

Suggested reading sequence: Section 1 $\rightarrow$ Section 2 $\rightarrow$ Section 4 $\rightarrow$ Section 8 $\rightarrow$ Section 9.

### 1.4 Abbreviation

#### Table 1: Abbreviation
| Acronym | Definition |
| :--- | :--- |
| **AC** | Alternating Current |
| **ADC** | Analog-to-Digital Converter |
| **AGND** | Analog Ground (Quiet Reference) |
| **ATE** | Automated Test Equipment |
| **BOM** | Bill of Materials |
| **CC** | Constant Current Mode |
| **CCM** | Continuous Conduction Mode |
| **CISPR** | International Special Committee on Radio Interference |
| **CMC** | Common Mode Choke |
| **CSV** | Comma-Separated Values |
| **CV** | Constant Voltage Mode |
| **DAC** | Digital-to-Analog Converter |
| **DC** | Direct Current |
| **DUT** | Device Under Test |
| **EMA** | Exponential Moving Average |
| **EMC** | Electromagnetic Compatibility |
| **EMI** | Electromagnetic Interference |
| **ESR** | Equivalent Series Resistance |
| **FAT32** | File Allocation Table 32-bit Filesystem |
| **Hipot** | High Potential (Dielectric Withstand Test) |
| **I2C** | Inter-Integrated Circuit Serial Bus |
| **IEC** | International Electrotechnical Commission |
| **LDO** | Low-Dropout Linear Regulator |
| **LSB** | Least Significant Bit |
| **MCU** | Microcontroller Unit |
| **MLCC** | Multi-Layer Ceramic Capacitor |
| **MOV** | Metal Oxide Varistor |
| **NTC** | Negative Temperature Coefficient Thermistor |
| **OLED** | Organic Light-Emitting Diode Display |
| **PF** | Power Factor |
| **PGND** | Power Ground (Switched Currents) |
| **PRD** | Product Requirement Document |
| **PWM** | Pulse Width Modulation |
| **QR** | Quasi-Resonant Valley Switching |
| **RMS** | Root Mean Square |
| **SCPI** | Standard Commands for Programmable Instruments |
| **SELV** | Safety Extra-Low Voltage |
| **SR** | Synchronous Rectification |
| **THD** | Total Harmonic Distortion |
| **TIW** | Triple Insulated Wire |
| **USB-CDC**| Universal Serial Bus - Communications Device Class |
| **UVLO** | Under-Voltage Lockout |
| **ZCD** | Zero-Crossing Detection |

### 1.5 References

#### Table 2: Reference
| SL No | Description | Version & Document Link |
| :--- | :--- | :--- |
| 1 | Statement of Work (SOW): Smart Programmable Voltage Supply | Ver 1.0 (Signed 2026-09-15) |
| 2 | IEC 62368-1: Audio/video, information & communication technology safety | Ed. 3.0 (2020) |
| 3 | EN 55032 / CISPR 32: Electromagnetic compatibility of multimedia equipment | Class B Limits (2015+A11:2020) |
| 4 | IEC 61000-4-5: Surge Immunity Testing (Lightning & Line Transients) | Level 3 (2kV Line-to-Earth) |
| 5 | Texas Instruments LM5176 4-Switch Synchronous Buck-Boost Datasheet | Rev C, SNVSAU6C |
| 6 | Texas Instruments UCC28740 Quasi-Resonant Flyback Controller Datasheet | Rev B, SLUSBN5B |
| 7 | IEEE 488.2 Standard Digital Interface for Programmable Instrumentation (SCPI)| Standard Commands Syntax |

---

## 2. Product Overview

### 2.1 Product - Business Perspective
Modern electronics manufacturing facilities, engineering test benches, and automated test fixtures require versatile, high-density programmable DC power modules capable of operating universally from worldwide AC mains ($85\,\text{V} \dots 265\,\text{V}$ AC) while delivering dynamically adjustable voltages ($5.0\,\text{V} \dots 20.0\,\text{V}$) at currents up to $3.0\,\text{A}$ ($60\,\text{W}$). 

Existing commercial bench supplies are bulky, costly, lack built-in isolated AC input power metering, and require external PCs for efficiency characterization. The **Smart Programmable Voltage Supply Module** solves these pain points by integrating:
1. A universal mains Quasi-Resonant Flyback frontend with reinforced isolation.
2. An ultra-efficient 4-switch synchronous Buck-Boost post-regulator with sub-$25\,\text{mV}$ ripple.
3. Dual-domain real-time efficiency monitoring ($\eta = P_{DC} / P_{AC}$) updating at $10\,\text{Hz}$.
4. Autonomous MicroSD data logging and USB-C SCPI automation in a compact embedded form factor.

This product enables original equipment manufacturers (OEMs), automated test equipment (ATE) integrators, and laboratories to dramatically cut bench footprint, lower equipment cost by $> 40\%$, and automate real-time energy efficiency audits.

### 2.2 Product – Technical Perspective
The module is designed as an intelligent two-stage power conversion subsystem with galvanically isolated primary and secondary domains:
* **Stage 1 (Isolated AC-DC Converter)**: Universal mains ($85\,\text{V} \dots 265\,\text{V}$ AC) input with 2-stage EMI filter, surge clamp, quasi-resonant valley-switched Flyback power stage (PQ26/20 transformer), and secondary synchronous rectification delivering a rock-solid $+24.0\,\text{V}$ intermediate DC bus ($72\,\text{W}$ max throughput).
* **Stage 2 (MCU-Controlled DC-DC Post-Regulator)**: 4-switch non-inverting synchronous Buck-Boost converter (LM5176) stepping the $+24\,\text{V}$ bus up or down into a regulated $5.0\,\text{V} \dots 20.0\,\text{V}$ DC output at up to $3.0\,\text{A}$.
* **Stage 3 (Digital Control, Metering & Telemetry)**:
  * Primary AC metering via isolated $\Delta\Sigma$ modulator (AMC1311) and current transformer measuring true RMS active power ($P_{AC}$).
  * Secondary DC metering via 16-bit I2C power monitor (INA226) measuring true load power ($P_{DC}$).
  * Embedded Cortex-M4F MCU computing conversion efficiency ($\eta = P_{DC} / P_{AC} \times 100\%$) at $10\,\text{Hz}$, writing timestamped CSV records to MicroSD, updating an onboard 1.3" OLED GUI, and communicating with external automated test software via USB-C SCPI protocol.

```text
===================================================================================================================
                                         FIGURE 1: BOUNDARY DIAGRAM
===================================================================================================================

                +─────────────────────────────────────────────────────────────────────────────+
                │                 SMART PROGRAMMABLE VOLTAGE SUPPLY MODULE                    │
                │                                                                             │
  Mains AC In   │  ┌───────────────┐     Reinforced Barrier     ┌───────────────────────────┐ │  Programmable DC
  85–265V AC ───┼─>│ Stage 1:      │─── (3kV RMS / >=6.4mm) ───>│ Stage 2: Synchronous      │─┼─> Output Rail
  (47–63 Hz)    │  │ QR Flyback    │      Transformer / Opto    │ 4-Switch Buck-Boost Stage │ │  5.0V–20.0V @ 3.0A
                │  │ (+24V Bus)    │                            │ (LM5176 + 4x 3.4mΩ FETs)  │ │  (Sub-25mV ripple)
                │  └───────┬───────┘                            └─────────────┬─────────────┘ │
                │          │                                                  │               │
                │          │ Isolated AC Power                                │ DC Power Sense│
                │          ▼ (AMC1311 + CT)                                   ▼ (INA226 I2C)  │
                │  ┌────────────────────────────────────────────────────────────────────────┐ │
                │  │ Stage 3: Central Microcontroller (STM32G474RET6, 32-bit Cortex-M4F)    │ │
                │  │ - Dynamic 12-Bit DAC Voltage Steering (3.65mV / LSB resolution)        │ │
                │  │ - Autonomous Hardware CC Overload Clamping (Sub-5µs response)          │ │
                │  │ - Real-Time Efficiency Engine (η = P_DC / P_AC @ 10Hz with EMA Filter) │ │
                │  └───────┬────────────────────────────┬───────────────────────────┬───────┘ │
                +──────────┼────────────────────────────┼───────────────────────────┼─────────+
                           │                            │                           │
                           ▼                            ▼                           ▼
                 ┌──────────────────┐         ┌──────────────────┐        ┌──────────────────┐
                 │ 1.3" OLED GUI    │         │ MicroSD Logger   │        │ USB-C / SCPI     │
                 │ Display Module   │         │ (FAT32 CSV Log)  │        │ Virtual COM Port │
                 └──────────────────┘         └──────────────────┘        └──────────────────┘
                    [LOCAL USER]               [ANALYTICS FILE]            [HOST AUTOMATION]
```

### 2.3 Use Cases

#### Table 3: Use Case
| Sl. No. | Use Case ID | Actor | Description | Pre-Condition | Normal Flow | Post-Condition |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **UC-01** | Test Engineer | Precision Bench Supply Output Tuning | Module powered from AC mains; Output OFF. | User adjusts rotary encoder or sends SCPI `:VOLT 12.0`. MCU updates DAC1; Buck-Boost steps output to $12.00\,\text{V}$ in $< 100\,\mu\text{s}$. | Output regulates at $12.00\,\text{V} \pm 10\,\text{mV}$. |
| 2 | **UC-02** | DUT Load | Dynamic Load Step Transients | Module delivering $12.0\,\text{V}$ at $1.5\,\text{A}$. | DUT surges current from $1.5\,\text{A} \rightarrow 3.0\,\text{A}$. Type-II loop restores voltage within $120\,\mu\text{s}$ with $< 250\,\text{mV}$ sag. | Output voltage recovers to within $1\%$ of setpoint. |
| 3 | **UC-03** | Fault / Short | Hardware Constant Current (CC) Clamping | Module operating in CV mode at $20.0\,\text{V}$, current limit set to $2.0\,\text{A}$. | DUT encounters short circuit ($I > 2.0\,\text{A}$). Analog comparator pulls `COMP` pin down in $< 5\,\mu\text{s}$. Voltage folds back. | Current is strictly clamped at $2.0\,\text{A}$; no MOSFET stress. |
| 4 | **UC-04** | QA Engineer | Autonomous Efficiency Audit & Logging | MicroSD card inserted; Module powered. | User sends `:LOG:START` or presses Log button. 10Hz task records $V_{AC}, I_{AC}, P_{AC}, V_{DC}, I_{DC}, P_{DC}, \eta$ to CSV file. | Full session CSV log stored safely on MicroSD card. |
| 5 | **UC-05** | Host PC / ATE | Automated SCPI Production Test | USB-C connected to automated test rack. | ATE sends `:VOLT 5.0`, queries `:MEAS:EFF?`. Module executes command and returns `86.5`. | Automated compliance logging completed. |

```text
===================================================================================================================
                                   FIGURE 2 & 3: MAJOR USE CASE WORKFLOWS
===================================================================================================================

  [ USE CASE 1: VOLTAGE SETPOINT PROGRAMMING ]
  User / Host PC ──[ SCPI :VOLT 12.0 ]──> MCU Parser ──> Updates 12-Bit DAC1 (1.76V) ──> Injects into FB Node
                                                                                                  │
  V_OUT Regulates to 12.00V (<10mV error) <── LM5176 Adjusts Buck Duty Cycle (D = 50%) <──────────┘

  [ USE CASE 3: HARDWARE CONSTANT CURRENT CLAMPING DURING OVERLOAD ]
  Load Current Surges > 3.0A ──> Kelvin Shunt (10mΩ) ──> INA240A2 (50 V/V) ──> V_ISENSE > V_ISET
                                                                                       │
  Output Current Clamped at 3.0A <── Duty Cycle Throttled in < 5µs <── BAT54 Pulls Down COMP Pin
```

### 2.4 Product Interfaces

#### 2.4.1 Hardware Interfaces

#### Table 4: Hardware Interfaces
| Sl. No | Entity 1 | Entity 2 | Interface | Usage Description |
| :--- | :--- | :--- | :--- | :--- |
| 1 | AC Mains Grid | SPPS Module | IEC 320-C14 Receptacle | $85\,\text{V} \dots 265\,\text{V}$ AC RMS, 3-prong grounded input with integrated fuse holder. |
| 2 | SPPS Module | User / DUT | 4mm Gold-Plated Binding Posts | Heavy-duty $15\,\text{A}$ Red (+) and Black (-) terminals accepting banana plugs, spade lugs, or bare wire. |
| 3 | SPPS Module | Host PC | USB Type-C Receptacle | USB 2.0 Full-Speed Virtual COM Port for SCPI commands and remote firmware flash. |
| 4 | SPPS Module | Storage Card | Push-Push MicroSD Socket | SPI / 4-bit SDIO interface supporting FAT32 flash cards up to $32\,\text{GB}$. |
| 5 | SPPS Module | Local Operator | Dual Rotary Encoders | Incremental optical encoders with push-button for setting voltage ($10\,\text{mV}$) and current ($10\,\text{mA}$). |
| 6 | SPPS Module | Local Operator | 1.3" I2C Monochrome OLED | $128\times 64$ graphical display presenting real-time meters ($V, I, P, \eta, T$) and CC/CV status. |
| 7 | SPPS Module | Local Operator | Output Enable Push-Button | Momentary tactile switch with dual-color LED (Green: Output Active, Red: Tripped/Fault). |

#### 2.4.2 Software Interfaces

#### Table 5: Software Interfaces
| S. No | Entity 1 | Entity 2 | Interface | Protocol / Mode | Usage Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Host ATE Application | SPPS Module | USB-CDC Virtual COM Port | IEEE 488.2 SCPI | Accepts standard instrument commands (`:VOLT`, `:CURR`, `:OUTP`, `:MEAS:EFF?`) at $115200\,\text{baud}$, 8N1. |
| 2 | Telemetry Task | MicroSD Card | SPI / FatFs | FAT32 CSV File System | Non-blocking ring-buffered logging of timestamped records at $10\,\text{Hz}$ rate. |
| 3 | Metering Task | Primary AMC1311 | Hardware Sinc3 Filter | Differential Bitstream | Synchronous digital filtering converting isolated modulations into true RMS AC power. |
| 4 | Metering Task | Secondary INA226 | I2C Bus (400 kHz) | Register Protocol | Reads DC bus voltage ($1.25\,\text{mV/LSB}$) and shunt current ($100\,\mu\text{A/LSB}$) every $100\,\text{ms}$. |
| 5 | Display Task | OLED Controller | I2C Bus (400 kHz) | SSD1306 / SH1106 Driver | Updates real-time graphical dashboard and efficiency bar at $10\,\text{frames/sec}$. |

---

## 3. Systems & Domains Involved

The development of the Smart Programmable Voltage Supply Module spans five primary engineering domains:

#### Table 6: Domain Allocation
| Domain Name | Abbreviation | System 1 (Hardware Module) | System 2 (Firmware & GUI) | Responsibilities |
| :--- | :--- | :---: | :---: | :--- |
| **Hardware Engineering** | HW | **Yes** | No | AC frontend, magnetics, 4-switch Buck-Boost, sensing, schematics, PCB layout. |
| **Mechanical Engineering**| ME | **Yes** | No | Enclosure extrusion, 4mm post mounting, OLED bezel, thermal heatsinking, airflow. |
| **Embedded Firmware** | FW | No | **Yes** | FreeRTOS tasks, DAC control loops, INA226 driver, FAT32 logger, SCPI parser. |
| **Quality & Certification**| QA | **Yes** | **Yes** | Hipot dielectric testing, CISPR 32 EMC testing, load step verification, RCA matrix. |
| **Host Applications** | PC | No | **Yes** | Python SCPI automation library and graphical telemetry data dashboard. |

---

## 4. Product Requirements

### 4.1 System 1 Requirements: Hardware Power Supply Module

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             SYSTEM 1 HARDWARE SPECIFICATIONS SUMMARY                             │
├────────────────────────────┬─────────────────────────────┬───────────────────────────────────────┤
│ Parameter / Specification  │ Target Value                │ Verification Method                   │
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **AC Input Voltage Range** │ 85 V – 265 V AC RMS         │ Variac voltage sweep under full load  │
│ **AC Input Frequency**     │ 47 Hz – 63 Hz               │ AC power source frequency margin test │
│ **Inrush Current Limit**   │ < 30 A Peak @ 230V AC Cold  │ Current probe on oscilloscope         │
│ **Input Power Factor (PF)**│ > 0.60 @ 230V Full Load     │ Digital power analyzer measurement    │
│ **Dielectric Withstand**   │ 3000 V RMS (1 min, Pri-Sec) │ Hipot safety dielectric tester        │
│ **Creepage & Clearance**   │ Creepage >= 6.4mm, Clr >= 5mm│ Optical microscope PCB inspection     │
│ **Intermediate DC Bus**    │ +24.0 V DC +/- 1.0% (72W)   │ DMM measurement across full load      │
│ **Programmable DC Output** │ 5.0 V – 20.0 V DC           │ 6.5-digit DMM digital sweep           │
│ **Continuous DC Current**  │ 0.1 A – 3.0 A Continuous    │ Electronic load soak test             │
│ **Maximum Output Power**   │ 60.0 W Continuous           │ Continuous operation at 20V / 3A      │
│ **Output Voltage Ripple**  │ < 25 mV pk-pk @ 20V/3A      │ 20MHz BW tip-and-barrel scope probe   │
│ **Load Transient Recovery**│ < 120 µs to 1% of setpoint  │ 50% to 100% load step (1.5A -> 3.0A)  │
│ **Transient Sag / Peak**   │ < 250 mV Peak Deviation     │ Slew rate 1.5 A/µs                    │
│ **Overall Conversion Eff.**│ 84% – 89% End-to-End        │ P_dc / P_ac power analyzer ratio      │
│ **Post-Regulator Peak Eff**│ >= 96.5% @ 15V / 3A         │ DC input to DC output stage meter     │
└────────────────────────────┴─────────────────────────────┴───────────────────────────────────────┘
```

#### 4.1.1 Specific Requirements
1. **[MUST] AC Frontend & Protection**:
   * Fuse: Time-lag slow blow rated for $2.0\,\text{A} / 250\,\text{V}$ AC ($I^2t \ge 18\,\text{A}^2\text{s}$).
   * Inrush Limiter: $10\,\Omega$ NTC thermistor clamping cold-start peak current to $< 37.5\,\text{A}$.
   * Surge Protection: 14D471K MOV clamping line spikes up to $4.5\,\text{kA}$ ($8/20\,\mu\text{s}$).
   * EMI Filter: 2-stage common-mode choke ($15\,\text{mH} + 4.7\,\text{mH}$) with Class-X2 film capacitors ($220\,\text{nF}$) complying with **EN 55032 / CISPR 32 Class B** conducted emissions.
2. **[MUST] Primary Quasi-Resonant Flyback Stage**:
   * Controller: TI UCC28740 operating with zero-crossing valley switching.
   * Transformer: PQ26/20 ferrite core (3C95 material), primary inductance $L_p = 220\,\mu\text{H} \pm 10\%$, sandwich wound ($N_p = 48\,\text{T}, N_s = 12\,\text{T}, N_{aux} = 8\,\text{T}$).
   * Primary Switch: Infineon IPB80R290P7 ($800\,\text{V}$ Superjunction, $R_{DS(on)} = 0.29\,\Omega$).
   * Secondary Synchronous Rectification: MP6908 fast controller + Infineon BSC052N06NS ($60\,\text{V}, 5.2\,\text{m}\Omega$), holding secondary rectification losses $< 0.15\,\text{W}$.
3. **[MUST] Synchronous Buck-Boost Post-Regulator**:
   * Controller: TI LM5176 4-switch synchronous controller operating at $250\,\text{kHz} \pm 5\%$.
   * Switches: 4x Infineon BSC034N04LS ($40\,\text{V}, 3.4\,\text{m}\Omega$, SuperSO8).
   * Power Inductor: Wurth Elektronik 7443321000 flat-wire inductor ($10.0\,\mu\text{H}, 8.5\,\text{A}_{\text{RMS}}, I_{sat} = 11.5\,\text{A}, DCR = 11.8\,\text{m}\Omega$).
   * Capacitor Bank: $4\times 22\,\mu\text{F} / 25\,\text{V}$ 1210 X7R MLCCs in parallel with $1\times 100\,\mu\text{F} / 25\,\text{V}$ Panasonic OS-CON polymer capacitor ($\text{ESR} = 12\,\text{m}\Omega$).
4. **[MUST] Digital Voltage Control & Fast CC Clamp**:
   * 12-Bit DAC Summing Junction: Resistors $R_{top} = 49.9\,\text{k}\Omega, R_{DAC} = 11.0\,\text{k}\Omega, R_{bot} = 3.65\,\text{k}\Omega$ ($0.1\%$ precision), delivering $3.65\,\text{mV/LSB}$ step resolution from $5.0\,\text{V}$ to $20.0\,\text{V}$.
   * Hardware CC Clamp: $10\,\text{m}\Omega$ $0.1\%$ Kelvin shunt + TI INA240A2 ($50\,\text{V/V}$) + TI TLV3501 ($4.5\,\text{ns}$) comparator clamping the `COMP` pin in $< 5\,\mu\text{s}$ during overload.

---

### 4.2 System 2 Requirements: Embedded Control & Telemetry Software

1. **[MUST] Real-Time Dual-Domain Metering Engine**:
   * Sample primary AC RMS voltage, RMS current, real active power ($P_{AC}$), and power factor at $10\,\text{Hz}$ via AMC1311 bitstream.
   * Fetch secondary DC voltage ($V_{DC}$), current ($I_{DC}$), and load power ($P_{DC}$) via INA226 I2C bus every $100\,\text{ms}$.
   * Compute instantaneous and filtered conversion efficiency:
     $$\eta_{filt}[n] = 0.20 \cdot \left(\frac{P_{DC}}{P_{AC}} \times 100\right) + 0.80 \cdot \eta_{filt}[n-1]$$
   * Standby Clamp: If $P_{AC} < 0.50\,\text{W}$ or $P_{DC} < 0.05\,\text{W}$, force $\eta = 0.0\%$.
2. **[MUST] MicroSD FAT32 Data Logging Engine**:
   * FreeRTOS ring-buffered worker task writing CSV records every $100\,\text{ms} \dots 10\,\text{s}$ (user configurable).
   * Schema: `timestamp_ms,vac_rms,iac_rms,pac_w,pf,vdc_out,idc_out,pdc_w,eff_pct,temp_pri,temp_sec,mode`.
   * Flush to physical flash memory via `f_sync()` every $5.0\,\text{seconds}$.
3. **[MUST] SCPI Remote Automation Protocol**:
   * USB-CDC Virtual COM port supporting standard commands:
     * `*IDN?`, `*RST`, `:VOLT <v>`, `:VOLT?`, `:CURR <i>`, `:CURR?`, `:OUTP <1|0>`, `:OUTP?`.
     * `:MEAS:VOLT?`, `:MEAS:CURR?`, `:MEAS:POW?`, `:MEAS:EFF?`, `:LOG:START`, `:LOG:STOP`.
   * Response latency: $< 5.0\,\text{ms}$ per query.

---

## 5. Assumptions
1. **AC Mains Quality**: The AC mains supply is assumed to provide a nominal sinusoidal voltage within $85\,\text{V} \dots 265\,\text{V}$ AC RMS. Total harmonic distortion of the mains is assumed $\le 5\%$.
2. **Operating Environment**: The module operates in an indoor laboratory or industrial bench environment (ambient temperature $-20^\circ\text{C} \dots +50^\circ\text{C}$, non-condensing relative humidity $< 90\%$).
3. **Secondary Ground Grounding**: Secondary ground (`GND_SEC`) is galvanically isolated from Earth Ground (`PE`) by default, allowing floating operation, but may be strapped to Earth externally by the user if required.

---

## 6. Dependencies
1. **Silicon Component Availability**: Design relies on production availability of key active ICs: Texas Instruments LM5176, UCC28740, INA240A2, INA226, AMC1311, and STM32G474RET6.
2. **Third-Party Firmware Stacks**: Firmware implementation depends on STMicroelectronics STM32CubeG4 HAL drivers, FreeRTOS kernel, and ChaN's FatFs library.
3. **Custom Magnetics Fabrication**: Transformer fabrication depends on tooling and sample turnaround of Ferroxcube PQ26/20 ferrite cores with triple-insulated Furukawa TEX-E wire.

---

## 7. Standard Deliverables & Release Order

### 7.1 Product Development Plan
The project follows a standard 4-phase embedded hardware product engineering lifecycle:
* **Phase 1: Architecture, Modeling & PRD Sign-off** (Weeks 1–3).
* **Phase 2: Schematic Capture, Simulation & Layout** (Weeks 4–7).
* **Phase 3: Prototype Fabrication & Board Bring-Up (Rev A)** (Weeks 8–12).
* **Phase 4: Design Validation Testing (DVT), Compliance & Rev B** (Weeks 13–18).

### 7.2 System 1 Development Plan (Hardware Engineering)

#### Table 7: System 1 Development Plan
| Release ID | Hardware Deliverable [HW] | Mechanical Deliverable [ME] | Embedded Software Deliverable [FW] |
| :---: | :--- | :--- | :--- |
| **1** | Hardware Design Document (HDD) | Industrial Design (ID) Concept | Software Design Document (SDD) |
| **2** | Component Schematics (Altium) | Initial Mechanical Model (MDD) | Board Support Package (BSP) Drivers |
| **3** | 4-Layer PCB Layout & DRC | Final Enclosure CAD (STEP) | Control State Machine & DAC Loop |
| **4** | Gerber Package & Master BOM | Thermal & Heatsink Fab Package | FreeRTOS Telemetry Task & I2C |
| **5** | Assembled Rev A Prototype PCBA | 3D Printed Prototype Bezel | SCPI Command Parser v1.0 |
| **6** | Cold Checks & Variac Bring-Up | Enclosure Mechanical Fit Check | OLED Display GUI Driver |
| **7** | Dynamic Load Step Test Report | Thermal Soak Test (FLIR Camera) | MicroSD FAT32 Logger Engine |
| **8** | EMC & Safety Pre-Compliance Rep.| Drop & Vibration Test Report | Production Firmware Release 1.0 |
| **9** | Rev B Schematics & Layout Fixes| Extruded Aluminum Enclosure Tool| Production Calibration Firmware |
| **10**| Final Rev B Production PCBA | Mass Production Packaging | Final Golden Firmware Release v2.0 |

---

## 8. Architecture <optional>

> *Note: This is the proposed architecture and it might get changed during the design stage. Ensure license compliance for usage of open source tools.*

### 8.1 System 1: Hardware Architecture Diagram

```text
===================================================================================================================
                                      SYSTEM 1: HARDWARE POWER ARCHITECTURE
===================================================================================================================

  85-265V AC In ──[ Fuse 2A ]──[ NTC 10Ω ]──[ 2-Stage EMI Filter ]──[ GBU606 Bridge ]──┬──> +V_BULK (120-375V DC)
                                                                                       │
                                                                                    ┌──┴──┐ C_BULK (100uF/450V)
                                                                                    └──┬──┘
                                                                                       │
  ┌────────────────────────────────────────────────────────────────────────────────────┴──────────────────────────┐
  │ PRIMARY ISOLATED QUASI-RESONANT FLYBACK STAGE (UCC28740)                                                      │
  │ - PQ26/20 Ferrite Core Transformer (Lp = 220µH, Np = 48T, Ns = 12T, Naux = 8T)                               │
  │ - Primary Switch: Infineon IPB80R290P7 (800V Superjunction, 0.29Ω) + RCD Clamp (50kΩ / 2.2nF)                │
  │ - Secondary Synchronous Rectification: MP6908 + BSC052N06NS (60V, 5.2mΩ)                                     │
  │ - Optocoupled Feedback: PC817 + TL431 Shunt Reference                                                         │
  └───────────────────────────────────────────────────┬───────────────────────────────────────────────────────────┘
                                                      │
                                          +24.0V DC Intermediate Bus (72W)
                                                      │
  ┌───────────────────────────────────────────────────┴───────────────────────────────────────────────────────────┐
  │ SECONDARY SYNCHRONOUS 4-SWITCH BUCK-BOOST STAGE (LM5176)                                                      │
  │ - 4x Infineon BSC034N04LS (40V, 3.4mΩ) Power MOSFETs                                                          │
  │ - Inductor: Wurth Elektronik 7443321000 (10.0µH, 8.5A RMS, 11.5A Sat, 11.8mΩ DCR)                            │
  │ - Output Filter Bank: 4x 22µF 1210 MLCC + 1x 100µF/25V Panasonic OS-CON Polymer (ESR < 2.5mΩ)                 │
  └───────────────────────────────────────────────────┬───────────────────────────────────────────────────────────┘
                                                      │
                                        +V_OUT Programmable DC (5.0V–20.0V @ 3.0A)
                                                      │
                                                      ├───[ R_shunt: 10mΩ / 0.1% ]───> Output Binding Posts
                                                      │
  ┌───────────────────────────────────────────────────┴───────────────────────────────────────────────────────────┐
  │ SENSING, MCU CONTROL & USER TELEMETRY                                                                         │
  │ - AC Metering: AMC1311 Isolated Modulator + Talema AC1005 Current Transformer (True RMS P_ac, PF)            │
  │ - DC Metering: INA226 16-Bit I2C Power Monitor across 10mΩ Shunt                                              │
  │ - MCU 12-Bit DAC1: Summing injection network (49.9kΩ / 11.0kΩ / 3.65kΩ) for 3.65mV/LSB voltage tuning        │
  │ - Analog CC Clamp: INA240A2 (50 V/V) + TLV3501 (4.5ns) pulling down COMP pin in < 5µs                       │
  │ - Cortex-M4F MCU (STM32G474RET6): 10Hz Real-Time Efficiency Engine, MicroSD FAT32 Logger, OLED GUI, USB-SCPI│
  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Bill Of Material <optional>

> *Note: This is the expected BOM and it might get changed during the design stage. Pricing and cost information are excluded.*

#### Table 8: System 1 Product BOM
| Sl. No | Reference Designator | Description | Qty | Manufacturer | Mfg Part Number |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Subsystem 1 - AC Frontend & Flyback Converter** |
| 1 | F1 | Time-Lag Ceramic Fuse 2A / 250V | 1 | Littelfuse | 0218002.MXP |
| 2 | NTC1 | Inrush Current Thermistor 10Ω 3.2A | 1 | TDK / Epcos | B57236S0100M000 |
| 3 | MOV1 | Metal Oxide Varistor 300V RMS 4.5kA | 1 | Bourns | MOV-14D471K |
| 4 | L_CM1, L_CM2 | Common Mode Choke 15mH & 4.7mH | 2 | Wurth Elektronik | 744823215 / 744822472 |
| 5 | BR1 | Bridge Rectifier 600V 6A GBU | 1 | Diodes Inc. | GBU606 |
| 6 | C_BULK1 | Electrolytic Cap 100µF / 450V 105°C | 1 | Nichicon | LGW2W101MELZ25 |
| 7 | TX1 | Flyback Transformer PQ26/20 220µH | 1 | Custom VVDN | 3C95-PQ2620-72W |
| 8 | Q1 | Superjunction MOSFET 800V 0.29Ω D2PAK| 1 | Infineon | IPB80R290P7 |
| 9 | U1 | Quasi-Resonant Flyback Controller | 1 | Texas Instruments | UCC28740DR |
| 10 | U2 | Smart Synchronous Rectifier Driver | 1 | Monolithic Power | MP6908GJ |
| 11 | Q_SR | Synchronous N-MOSFET 60V 5.2mΩ | 1 | Infineon | BSC052N06NS |
| 12 | OPTO1 | Phototransistor Optocoupler 5kV RMS | 1 | Everlight | EL817(S)(TA) |
| **Subsystem 2 - Synchronous Buck-Boost Post-Regulator** |
| 13 | U3 | 4-Switch Synchronous Buck-Boost IC | 1 | Texas Instruments | LM5176PWPR |
| 14 | Q_A..Q_D | Power N-MOSFET 40V 3.4mΩ SuperSO8 | 4 | Infineon | BSC034N04LS |
| 15 | L1 | Flat-Wire Power Inductor 10µH 8.5A | 1 | Wurth Elektronik | 7443321000 |
| 16 | R_shunt | Metal Element Shunt 10mΩ 0.1% 3W 2512 | 1 | Bourns | CSS2H-2512R-L010F |
| 17 | C_OUT_CER | Ceramic Cap 22µF 25V X7R 1210 | 4 | Murata | GRM32ER71E226KE15L |
| 18 | C_OUT_POLY | Aluminum Polymer Cap 100µF 25V SMD | 1 | Panasonic | 25SVPF100M |
| 19 | R_top, R_DAC, R_bot | Precision Resistors 49.9k, 11k, 3.65k 0.1% | 3 | Vishay | TNPW0805 Series |
| **Subsystem 3 - Control, Metering & Telemetry** |
| 20 | U4 | 32-Bit ARM Cortex-M4F MCU 170MHz | 1 | STMicroelectronics | STM32G474RET6 |
| 21 | U5 | Isolated Delta-Sigma Modulator | 1 | Texas Instruments | AMC1311DWVR |
| 22 | T_CT1 | Toroidal Current Transformer 1000:1 | 1 | Talema | AC1005 |
| 23 | U6 | 16-Bit I2C Power Monitor IC | 1 | Texas Instruments | INA226AIDGSR |
| 24 | U7 | High-Speed Analog Comparator 4.5ns | 1 | Texas Instruments | TLV3501AIDBVR |
| 25 | DISP1 | 1.3" Monochrome OLED 128x64 I2C | 1 | Waveshare | 1.3inch OLED (SH1106) |
| 26 | CON_SD | Push-Push MicroSD Socket SMD | 1 | Amphenol | 114-00841-68 |
| 27 | CON_USB | USB Type-C Receptacle 16-Pin | 1 | GCT | USB4085-GF-A |

---

## 10. Out of Scope
The following features and capabilities are explicitly excluded from the current project scope:
1. **Three-Phase AC Input**: Operation from 3-phase $400\,\text{V} / 480\,\text{V}$ AC industrial mains. (System is single-phase $85\,\text{V} \dots 265\,\text{V}$ AC only).
2. **Active Power Factor Correction (Active PFC)**: Active boost PFC stage for $\text{PF} > 0.98$ is excluded. (Passive line filtering with $\text{PF} \approx 0.62$ is provided; adequate for $< 75\,\text{W}$ class equipment).
3. **Negative Output Voltages**: Dual-rail bipolar outputs (e.g. $\pm 15\,\text{V}$) or negative rails. (System provides positive single-ended output $5.0\,\text{V} \dots 20.0\,\text{V}$ DC only).
4. **Wireless Connectivity**: Onboard Wi-Fi, Bluetooth, or cellular telemetry. (System uses USB-C SCPI and MicroSD card logging only).
5. **Bidirectional Power Flow**: Regenerative 4-quadrant electronic load sinking. (System is a forward source supply only).

---

## 11. Open Items
The following items are under active review and will be resolved in Revision 1.1:
1. **Enclosure Extrusion Width**: Finalizing extrusion profile dimensions ($120\,\text{mm} \times 80\,\text{mm} \times 45\,\text{mm}$ vs $140\,\text{mm} \times 90\,\text{mm} \times 50\,\text{mm}$) based on mechanical fit of binding posts and OLED bezel.
2. **Current Shunt Value Optimization**: Evaluating whether reducing $R_{shunt}$ from $10\,\text{m}\Omega$ to $5\,\text{m}\Omega$ yields higher full-load efficiency at $3.0\,\text{A}$ without compromising ADC low-current resolution ($< 50\,\text{mA}$).
3. **USB Power Delivery (USB-PD) Sink/Source Negotiation**: Deciding whether to incorporate a standalone USB-PD controller (STUSB4500) to allow the module to also be powered by an external USB-PD charger in field settings.
