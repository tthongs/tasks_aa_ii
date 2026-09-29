# System Schematics, Safety Compliance & PCB Design: Smart Programmable Power Supply

Welcome to the **VVDN Engineering Hub Technical Dossier on System Schematics, Safety Compliance, PCB Layout, and Hardware Bring-Up** for the Smart Programmable Power Supply. This document provides the complete end-to-end interconnection schematic, IEC 62368-1 safety isolation rules, 4-layer PCB layout guidelines, Bill of Materials (BOM), bring-up checklist, and bench troubleshooting matrix.

---

## 1. Complete End-to-End System Interconnect Schematic

Below is the master system interconnection schematic uniting the universal AC frontend, QR Flyback converter, $+24.0\,\text{V}$ intermediate DC bus, 4-switch synchronous Buck-Boost post-regulator, dual-domain power metering, central MCU, and user interface:

```text
====================================================================================================================================================
                        COMPLETE SYSTEM INTERCONNECT SCHEMATIC: SMART PROGRAMMABLE POWER SUPPLY (85-265V AC -> 5-20V / 3A DC)
====================================================================================================================================================

  [ MAINS INPUT ]
  85-265V AC ──[ FUSE 2A ]──[ NTC 10Ω ]──┬──[ 2-STAGE EMI FILTER ]──[ BRIDGE RECTIFIER ]──┬──> +V_BULK (120-375V DC)
                                         │  (C_X, L_CM1, L_CM2)     (GBU606: 600V/6A)     │
                                        ┌┴┐                                             ┌─┴─┐ C_BULK (100uF/450V)
                                        │ │ MOV1 (14D471K)                              └─┬─┘
                                        └┬┘                                               │
                                         │                                             GND_PRI
  EARTH (PE) ────────────────────────────┴────────────────────────────────────────────────┴─── EARTH (PE)

  [ STAGE 1: ISOLATED QR FLYBACK CONVERTER ]
  +V_BULK ───[ Primary Winding (PQ26/20: 220uH) ]───┬─── Drain (IPB80R290P7: 800V Superjunction)
                                                    │    │
                                            [ RCD Snubber ]
                                            (50kΩ / 2.2nF)
                                                    │
                                                   Gate ─── Driven by UCC28740 Controller
                                                    │
                                                 Source ───[ R_sense: 0.2Ω ]─── GND_PRI

  ==================================================================================================================================================
                              REINFORCED SAFETY ISOLATION BARRIER (>= 6.4mm Creepage / 3000V RMS Hipot / Y1 Safety Cap)
  ==================================================================================================================================================

  Secondary Winding (12T) ───[ MP6908 + BSC052N06NS Synchronous Rectifier ]───┬───> +24V Intermediate DC Bus (72W)
                                                                              │
                                                                           ┌──┴──┐
                                                                           │TL431│ ───> [ PC817 Optocoupler ] ───> (Feedback to UCC28740)
                                                                           └──┬──┘
                                                                              │
                                                                           GND_SEC

  [ STAGE 2: 4-SWITCH SYNCHRONOUS BUCK-BOOST POST-REGULATOR ]
  +24V Intermediate Bus ───[ Q_A: Buck HS ]───┬───[ Inductor: 10uH / 8.5A ]───┬───[ Q_D: Boost HS ]───┬───[ R_shunt: 10mΩ ]───> +V_OUT (5-20V/3A)
                                              │                               │                       │
                                       [ Q_B: Buck LS ]                [ Q_C: Boost LS ]            ┌─┴─┐ C_OUT (4x 22uF MLCC + 100uF Poly)
                                              │                               │                     └─┬─┘
                                           GND_SEC                         GND_SEC                    │
                                                                                                   GND_SEC
  [ STAGE 3: DIGITAL CONTROL & DUAL-DOMAIN POWER METERING ]
  AC Input ──[ AMC1311 Isolated Modulator ]──┐
                                             ▼
  +V_OUT   ──[ INA226 16-Bit I2C Monitor  ]──┼───> [ STM32G474 / ESP32-S3 Central MCU ]
                                             │     - Dynamic Real-Time η = P_DC / P_AC (10Hz)
  DAC1 Out ──[ 11kΩ Summing Resistor ]───────┼───> - Controls V_OUT (5.0V - 20.0V in 10mV steps)
  DAC2 Out ──[ CC Analog Clamp Comparator ]──┘     - Controls I_LIMIT (0.1A - 3.0A in 10mA steps)
                                                   │
                                                   ├─── [ 1.3" OLED Display: V, I, P, η, Temp ]
                                                   ├─── [ MicroSD Logger: CSV Timestamped Log ]
                                                   └─── [ USB-C Interface: SCPI Protocol & CLI]
====================================================================================================================================================
```

---

## 2. Safety Compliance & Reinforced Isolation Design (IEC 62368-1)

Because this equipment operates directly from hazardous mains AC ($85\,\text{V} \dots 265\,\text{V}$ AC) and delivers a touchable, user-accessible low-voltage DC bench output ($5\,\text{V} \dots 20\,\text{V}$), strict adherence to **IEC 62368-1 (Audio/video, information and communication technology equipment safety)** is mandatory:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                    Safety Isolation Spacing Rules (IEC 62368-1)                   │
├────────────────────────────┬─────────────────────────────┬────────────────────────┤
│ Parameter / Barrier        │ Minimum Requirement         │ SPPS Design Value      │
├────────────────────────────┼─────────────────────────────┼────────────────────────┤
│ **Clearance (Air Spacing)**│ $\ge 4.0\,\text{mm}$        │ **$\ge 5.2\,\text{mm}$**│
│ **Creepage (Surface Track)│ $\ge 5.0\,\text{mm}$ (IIb)  │ **$\ge 6.8\,\text{mm}$**│
│ **Isolation Slot in PCB**  │ Recommended under barrier   │ **$2.0\,\text{mm}$ Air Gap Slot**│
│ **Dielectric Withstand**   │ $3000\,\text{V}_{\text{RMS}}$ (1 minute)│ Tested to $3750\,\text{V}_{\text{RMS}}$│
│ **Y-Capacitor Class**      │ Class Y1 or Dual Y2         │ **Class Y1 (2.2nF/400VAC)**│
│ **Optocoupler Rating**     │ V_IOTV $\ge 5000\,\text{V}_{\text{RMS}}$│ **PC817 / EL817 (5kV RMS)**│
│ **Transformer Wire**       │ Triple Insulated Wire (TIW) │ **Furukawa TEX-E (Reinforced)**│
└────────────────────────────┴─────────────────────────────┴────────────────────────┘
```

```text
               PCB Isolation Slot Milling Across Primary-Secondary Boundary
  PRIMARY AC DOMAIN (HOT!)                  SECONDARY DC DOMAIN (SELV SAFE!)
  +V_BULK, Q1, Primary Winding              +24V, Buck-Boost, MCU, User Terminals
  ┌───────────────────────────┐             ┌───────────────────────────┐
  │                           │             │                           │
  │     High Voltage Track    │  2.0mm Milled│     Low Voltage Track     │
  │     ───────────────────   │  Air Gap Slot│    ───────────────────    │
  │                           │  (Air: infinite│                        │
  │     Optocoupler Primary   │   creepage!)│     Optocoupler Secondary │
  │        ┌─────────┐        │   ========= │        ┌─────────┐        │
  │        │  PC817  │ ───────┼── │  SLOT │ ┼─────── │  PC817  │        │
  │        └─────────┘        │   ========= │        └─────────┘        │
  │                           │             │                           │
  │     Transformer Primary   │             │     Transformer Secondary │
  │        ┌─────────┐        │   ========= │        ┌─────────┐        │
  │        │ PQ26/20 │ ───────┼── │  SLOT │ ┼─────── │ PQ26/20 │        │
  │        └─────────┘        │   ========= │        └─────────┘        │
  │                           │             │                           │
  └───────────────────────────┘             └───────────────────────────┘
  ◄────── Creepage Distance >= 8.0mm across milled slot ────────────────►
```

---

## 3. High-Voltage 4-Layer PCB Stackup & Layout Guidelines

The PCB is architected as a high-density **4-layer board ($1.6\,\text{mm}$ FR-4, $2\,\text{oz}$ copper on outer layers, $1\,\text{oz}$ copper on inner layers)**:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                             4-Layer PCB Layer Stackup                             │
├───────┬──────────────────────────┬────────┬───────────────────────────────────────┤
│ Layer │ Name                     │ Copper │ Primary Signal Allocation             │
├───────┼──────────────────────────┼────────┼───────────────────────────────────────┤
│ **L1**│ Top Layer (High Power)   │ 2.0 oz │ Power switches, inductors, AC traces  │
│ **L2**│ Inner Layer 1 (Ground)   │ 1.0 oz │ Partitioned GND_PRI and GND_SEC       │
│ **L3**│ Inner Layer 2 (Power)    │ 1.0 oz │ +16V Aux, +3.3V Logic, +5V Aux planes │
│ **L4**│ Bottom Layer (Signals)   │ 2.0 oz │ Feedback, I2C/SPI buses, Kelvin traces│
└───────┴──────────────────────────┴────────┴───────────────────────────────────────┘
```

### Essential PCB Layout Guidelines:
1. **High $di/dt$ Primary Loop Area Minimization**:
   - The loop formed by $C_{bulk} \rightarrow \text{Transformer Primary} \rightarrow Q_1 \rightarrow R_{sense} \rightarrow C_{bulk}$ ground return carries pulsed currents of $3.5\,\text{A}$ at $70\,\text{kHz}$. This loop must be routed with minimum physical enclosure area to suppress magnetic dipole radiation.
2. **Switch Node (SW1, SW2) Copper Island Sizing**:
   - The switch nodes experience extreme $dV/dt$ transitions ($> 20\,\text{V/ns}$). The copper polygon must be sized adequately to carry $3.5\,\text{A}$ continuous without overheating, but kept physically compact to avoid forming an RF radiating patch antenna.
3. **Kelvin-Sense Routing for Shunt Resistors**:
   - Both the primary current sense resistor ($R_{sense} = 0.2\,\Omega$) and the secondary output shunt ($R_{shunt} = 10\,\text{m}\Omega$) must use true 4-wire differential Kelvin connections routed directly from the inner component pads to the sensing ICs, running parallel on Layer 4 shielded by the Layer 2 ground plane.
4. **Separation of Grounds**:
   - **GND_PRI**: Primary rectified ground (never connect to Earth or Secondary!).
   - **GND_SEC_PWR**: Secondary high-current power ground carrying Buck-Boost switched currents.
   - **GND_SEC_ANA**: Sensitive analog ground for MCU ADC references and TL431. Connected to `GND_SEC_PWR` at exactly **one single star point** directly beneath the output capacitor bank.

---

## 4. Comprehensive Bill of Materials (BOM)

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Bill of Materials (BOM): Key Active & Passive Parts                                 │
├──────┬─────┬───────────────────────────┬─────────────────────────┬──────────────┬────────────────────────────────────────┤
│ Item │ Qty │ Reference Designator      │ Description             │ Package      │ Manufacturer & Part Number             │
├──────┼─────┼───────────────────────────┼─────────────────────────┼──────────────┼────────────────────────────────────────┤
│ 1    │ 1   │ F1                        │ Fuse Time-Lag 2A / 250V │ 5x20mm Cart. │ Littelfuse 0218002.MXP                 │
│ 2    │ 1   │ NTC1                      │ Inrush Thermistor 10Ω   │ Disc 13mm    │ TDK/Epcos B57236S0100M000              │
│ 3    │ 1   │ MOV1                      │ Varistor 300V RMS 4.5kA │ Radial 14mm  │ Bourns MOV-14D471K                     │
│ 4    │ 2   │ L_CM1, L_CM2              │ Common Mode Choke 15mH  │ Toroidal     │ Wurth Elektronik 744823215             │
│ 5    │ 1   │ BR1                       │ Bridge Rectifier 600V 6A│ GBU-4        │ Diodes Inc. GBU606                     │
│ 6    │ 1   │ C_BULK1                   │ Electrolytic 100uF/450V │ Radial 18x25 │ Nichicon LGW2W101MELZ25                │
│ 7    │ 1   │ TX1                       │ Transformer PQ26/20 220uH│ PQ26/20      │ Custom VVDN / Ferroxcube 3C95          │
│ 8    │ 1   │ Q1                        │ Superjunction FET 800V  │ D2PAK / TO263│ Infineon IPB80R290P7                   │
│ 9    │ 1   │ U1 (Primary Controller)   │ QR Flyback Controller   │ SOIC-8       │ Texas Instruments UCC28740DR           │
│ 10   │ 1   │ U2 (Synchronous Rectifier)│ Smart SR Controller     │ SOIC-8       │ Monolithic Power MP6908GJ              │
│ 11   │ 1   │ Q_SR                      │ Secondary MOSFET 60V    │ SuperSO8     │ Infineon BSC052N06NS                   │
│ 12   │ 1   │ OPTO1                     │ Optocoupler 5000V RMS   │ DIP-4 / SMD  │ Everlight EL817(S)(TA)                 │
│ 13   │ 1   │ U3 (Buck-Boost Controller)│ 4-Switch Sync BB IC     │ HTSSOP-28    │ Texas Instruments LM5176PWPR           │
│ 14   │ 4   │ Q_A, Q_B, Q_C, Q_D        │ Power MOSFET 40V 3.4mΩ  │ SuperSO8     │ Infineon BSC034N04LS                   │
│ 15   │ 1   │ L1                        │ Flat-Wire Inductor 10uH │ 10x10mm SMD  │ Wurth Elektronik 7443321000            │
│ 16   │ 1   │ R_shunt                   │ Kelvin Shunt 10mΩ 0.1%  │ 2512 SMD     │ Bourns CSS2H-2512R-L010F               │
│ 17   │ 1   │ U4 (DC Power Monitor)     │ 16-Bit I2C Power IC     │ VSSOP-10     │ Texas Instruments INA226AIDGSR         │
│ 18   │ 1   │ U5 (Isolated AC Modulator)│ Isolated Delta-Sigma IC │ SOIC-8 Wide  │ Texas Instruments AMC1311DWVR          │
│ 19   │ 1   │ U6 (Microcontroller)      │ 32-Bit Cortex-M4F MCU   │ LQFP-64      │ STMicroelectronics STM32G474RET6       │
│ 20   │ 1   │ DISP1                     │ 1.3" OLED 128x64 I2C    │ Module       │ Waveshare 1.3inch OLED (SH1106)        │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Production Bring-Up Procedure & Testing Checklist

Follow this rigorous multi-step procedure when assembling and verifying the first prototype board:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                            Hardware Bring-Up Checklist                            │
├──────┬──────────────────────┬─────────────────────────────────────────────────────┤
│ Step │ Verification Phase   │ Test Description & Expected Result                  │
├──────┼──────────────────────┼─────────────────────────────────────────────────────┤
│ **1**│ Cold Resistance & Hipot│ Verify impedance with DMM:                         │
│      │                      │ - Across L-N: $> 1\,\text{M}\Omega$ (Bleed resistor) │
│      │                      │ - Primary to Secondary: $> 100\,\text{M}\Omega$      │
│      │                      │ - Apply $3000\,\text{V}_{\text{RMS}}$ Hipot tester:  │
│      │                      │   Leakage current must be $< 1.0\,\text{mA}$.        │
├──────┼──────────────────────┼─────────────────────────────────────────────────────┤
│ **2**│ Low-Voltage Primary  │ Apply current-limited $+30\,\text{V}$ DC from bench  │
│      │ Functional Check     │ supply to $C_{bulk}$. Check UCC28740 startup pulses  │
│      │                      │ on gate using oscilloscope. Verify VCC charges.      │
├──────┼──────────────────────┼─────────────────────────────────────────────────────┤
│ **3**│ AC Mains Variac Ramp │ Connect through an Isolation Transformer + Variac.   │
│      │                      │ Slowly ramp AC voltage from $0\,\text{V} \rightarrow 85\,\text{V} \dots 230\,\text{V}$.│
│      │                      │ Verify $+24.0\,\text{V}$ intermediate bus stabilizes │
│      │                      │ with $< 50\,\text{mV}$ ripple. Check QR valley ring. │
├──────┼──────────────────────┼─────────────────────────────────────────────────────┤
│ **4**│ Buck-Boost & DAC Test│ Flash initial MCU firmware via ST-LINK. Command DAC  │
│      │                      │ to output voltages: $5.0\,\text{V}, 12.0\,\text{V}, 20.0\,\text{V}$.│
│      │                      │ Verify output with 6.5-digit DMM matches within 10mV.│
├──────┼──────────────────────┼─────────────────────────────────────────────────────┤
│ **5**│ CC Mode Clamping     │ Connect programmable electronic load in CC mode.     │
│      │                      │ Set current limit to $1.50\,\text{A}$. Increase load │
│      │                      │ to $2.0\,\text{A}$. Verify voltage folds back and    │
│      │                      │ current remains strictly clamped at $1.50\,\text{A}$.│
├──────┼──────────────────────┼─────────────────────────────────────────────────────┤
│ **6**│ Efficiency & Logger  │ Run $60\,\text{W}$ full-load test ($20\,\text{V} / 3\,\text{A}$) for│
│      │ Thermal Soak         │ 1 hour. Verify end-to-end efficiency $\ge 85\%$.     │
│      │                      │ Confirm MicroSD writes CSV records cleanly at 10Hz.  │
│      │                      │ FLIR thermal camera: Max heatsink $T \le 75^\circ\text{C}$.│
└──────┴──────────────────────┴─────────────────────────────────────────────────────┘
```

---

## 6. Root Cause Analysis (RCA) Troubleshooting Matrix

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           Bench Root Cause Analysis (RCA) Matrix                                          │
├────────────────────────────┬───────────────────────────────────────────┬──────────────────────────────────────────────────┤
│ Observed Symptom           │ Probable Root Cause                       │ Diagnostic & Corrective Action                   │
├────────────────────────────┼───────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ **Flyback does not start** │ 1. Auxiliary VCC not reaching UVLO turn-on│ 1. Check startup resistor from bulk rail; verify │
│ (0V on +24V bus)           │    threshold ($V_{CC(on)} \approx 14.5\text{V}$).│    $V_{CC}$ capacitor is not leaking.           │
│                            │ 2. Optocoupler phototransistor shorted.   │ 2. Measure FB pin voltage; if grounded, controller│
│                            │ 3. CS current sense resistor open/blown.  │    inhibits switching. Check TL431 reference pin.│
├────────────────────────────┼───────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ **Excessive primary switch │ 1. RCD snubber diode ($D_{snub}$) too slow│ 1. Ensure $D_{snub}$ is an ultrafast diode ($t_{rr}│
│ voltage spike (>650V)**    │    ($t_{rr} > 100\,\text{ns}$).           │    \le 50\,\text{ns}$ e.g. US1M, ES1J).          │
│                            │ 2. Transformer leakage inductance ($L_{lk}$)│ 2. Verify sandwich primary winding construction; │
│                            │    exceeds $3\%$ of $L_p$.                │    lower $R_{snub}$ from $50\,\text{k}\Omega$ to │
│                            │                                           │    $39\,\text{k}\Omega$ to dissipate more clamp. │
├────────────────────────────┼───────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ **Buck-Boost output hunts  │ 1. Inadequate phase margin in error amp   │ 1. Increase feedforward capacitor $C_{FF}$ across│
│ or oscillates at 5-10 kHz**│    compensation network.                  │    $R_{top}$ from $47\,\text{pF}$ to $100\,\text{pF}$.│
│                            │ 2. Excessive ESR on output capacitor bank.│ 2. Add ceramic MLCCs in parallel with polymer cap│
│                            │ 3. Digital DAC noise coupling into FB pin.│ 3. Add $100\,\text{pF}$ bypass directly at DAC pin│
├────────────────────────────┼───────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ **MicroSD card write error │ 1. Flash block erase latency ($>100\text{ms}$)│ 1. Use FreeRTOS queue ring buffer; never write │
│ or MCU watchdog reset**    │    blocking main execution thread.        │    to SD card directly inside the timer ISR!     │
│                            │ 2. 3.3V SD supply rail dips during write. │ 2. Place dedicated $47\,\mu\text{F}$ capacitor at│
│                            │                                           │    MicroSD socket VDD pin to buffer burst load.  │
├────────────────────────────┼───────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ **Efficiency displays 0.0% │ 1. Load current beneath minimum sensing   │ 1. Verify INA226 calibration register ($CAL=5120$)│
│ or fluctuates wildly**     │    threshold ($< 50\,\text{mA}$).         │    is loaded properly over I2C.                  │
│                            │ 2. Standby power clamp logic active.      │ 2. Verify current transformer burden resistor has│
│                            │ 3. Phase shift mismatch between V and I.  │    zero DC offset and scales correctly in C code.│
└────────────────────────────┴───────────────────────────────────────────┴──────────────────────────────────────────────────┘
```
