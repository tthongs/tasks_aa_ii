# Uncontrolled Diode Rectifiers: 1-Phase & 3-Phase Bridge Physics & Filter Sizing

Welcome to the **VVDN Engineering Hub Technical Dossier on Uncontrolled Diode Rectifiers**. Uncontrolled rectifiers utilize passive semiconductor PN-junction or Schottky diodes to achieve AC-to-DC conversion without active gating signals. They are ubiquitous as input rectification stages in legacy linear power supplies, low-cost offline switched-mode power supplies (SMPS under 75 W), and industrial motor drive front-ends.

This guide explores single-phase and three-phase rectifier topologies, capacitor filtering physics, diode conduction angle contraction, crest factor, Peak Inverse Voltage (PIV) ratings, and inrush surge protection.

---

## 1. Operating Principle & Rectifier Architectures

### 1.1 Single-Phase Full-Wave Diode Bridge (Graetz Bridge):

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: SINGLE-PHASE AC-DC BRIDGE RECTIFIER WITH FRONTEND EMI & INRUSH PROTECTION
========================================================================================================================

    AC LINE (230V RMS) ──[ F1: 6.3A Time-Lag ]──[ NTC: 10Ω/5A Inrush ]──┬──────────────────┐
                                                 (Relay K1 Bypass)      │                  │
                                                                       ┌┴┐ MOV1           ┌┴┐ CX1: X2 Cap
                                                                       │ │ 14D471K        │ │ 0.47µF / 310VAC
                                                                       └┬┘ (Surge 4.5kA)  └┬┘ (Differential EMI)
                                                                        │                  │
    AC NEUT (0V RMS) ───────────────────────────────────────────────────┼──────────────────┴───+
                                                                        │                      │
                                                                        │  COMMON-MODE CHOKE   │
                                                                        ├──[ CMC1: 2x 15mH ]───┼──────────┐
                                                                        │  Wurth 744825315     │          │
                                                                        │                      │          │
                                                                       ┌┴┐ CY1                ┌┴┐ CY2     │
                                                                       │ │ 2.2nF/400V Y2      │ │ 2.2nF   │
                                                                       └┬┘                    └┬┘         │
    EARTH (PE) ─────────────────────────────────────────────────────────┴──────────────────────┴───+      │
                                                                                                   │      │
                                            +---[ FULL-WAVE BRIDGE RECTIFIER (e.g. GBU808: 800V/8A) ]------+
                                            |                                                              |
                                            |     [ AC1: Pin 2 ] ------------------------------------------+
                                            |     [ AC2: Pin 3 ] <-----------------------------------------+
                                            |                                                              |
                                            |     [ +DC: Pin 1 ] ──────────────┬───────────────────────────+
                                            |     [ -DC: Pin 4 ] ──┐           │
                                            +----------------------|-----------|---------------------------+
                                                                   │           │
                                                                   │           +=== +VDC BUS (+325V Peak DC)
                                                                   │           │
                                                                   │          ┌┴──────────────────┐
                                                                   │          │ C_BULK BANK       │
                                                                   │         ┌┴┐ 2x 470µF/450V   ┌┴┐ C_HF_CER
                                                                   │         │ │ Aluminum Elec.  │ │ 2x 0.47µF/630V
                                                                   │         └┬┘ (Low ESR)       └┬┘ Film / X7R
                                                                   │          │                   │
                                                                   │          │      +VDC         │
                                                                   │          │        │          │
                                                                   │          │     [ R_bleed1: 150kΩ / 1W ]
                                                                   │          │     [ R_bleed2: 150kΩ / 1W ]
                                                                   │          │        │          │
                                                                   │          │     (Safety Discharge)
                                                                   │          │        │          │
                                                                   +──────────┴────────+──────────┴───> -VDC (DC Return GND)
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **AC_LINE_RAW** | AC Input IEC C14 Receptacle (L) | Fuse F_1 Input | 230V AC Live utility mains | Sized for 6.3A time-lag rating to survive startup capacitive charging surges. |
| **AC_LINE_PROT** | Fuse F_1 Output | NTC Thermistor Pin 1, MOV1 Pin 1, C_X1 Pin 1 | Protected Live rail | MOV1 clamps line voltage spikes exceeding 385 V_RMS / 505 V_DC. |
| **AC1 (Bridge)** | Common Mode Choke Pin 2 | GBU808 Bridge Rectifier Pin 2 (AC1) | Filtered AC Line input | Input to leg formed by top diode D_1 and bottom diode D_4. |
| **AC2 (Bridge)** | Common Mode Choke Pin 4 | GBU808 Bridge Rectifier Pin 3 (AC2) | Filtered AC Neutral input | Input to leg formed by top diode D_3 and bottom diode D_2. |
| **+VDC (DC Bus)** | GBU808 Bridge Rectifier Pin 1 (+) | C_bulk (+), Bleeder Resistors, Load (+) | Full-wave rectified pulsating DC bus | Peak voltage V_pk = sqrt(2) * 230 V ≈ 325 V; double line frequency ripple (100 Hz). |
| **-VDC (GND)** | GBU808 Bridge Rectifier Pin 4 (-) | C_bulk (-), Bleeder Return, Load Return | Rectifier zero-volt DC return | Common cathode-referenced return for downstream converters. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **BR_1** | Glass Passivated Bridge | Diodes Inc. GBU808 | V_RRM = 800 V, I_F(AV) = 8.0 A, I_FSM = 200 A, V_F = 1.0 V | 800 V rating survives 2.5 kV ring-wave surges; heatsink mounted for loads > 3 A. |
| **C_bulk** | Bulk Filter Capacitors | Nichicon LGU2W471MELY | 2 * 470 µF, 450 V_DC, 105°C, ESR = 0.22 Ω | Sized to ensure DC bus hold-up time t_hold >= 20 ms during AC utility cycle dropouts. |
| **NTC_1** | Inrush Current Limiter | TDK / EPCOS B57237S0100M000 | R_25 = 10.0 Ω, I_max = 5.0 A, Energy = 55 J | Limits cold-turn-on inrush current to I_inrush = 325 V / 10 Ω = 32.5 A. |
| **MOV_1** | Metal Oxide Varistor | Littelfuse V275LA20CP | V_RMS = 275 V, V_DC = 369 V, I_peak = 6500 A, W_max = 120 J | Clamps lightning and grid switching transients per IEC 61000-4-5 Class 3. |
| **CMC_1** | Common-Mode Choke | Würth Elektronik 744825315 | 2 * 15.0 mH, I_rated = 3.5 A, DCR = 82 mΩ | High common-mode impedance (> 5 kΩ at 1 MHz) attenuates conducted EMI. |
| **C_X1, C_Y1/2**| Safety EMI Filter Caps | Vishay F1772 (X2) / Murata (Y2) | C_X = 0.47 µF / 310 V_AC, C_Y = 2.2 nF / 400 V_AC | Certified to UL/ENEC 60384-14 for direct across-the-line and line-to-earth suppression. |

---

### 1.3 Three-Phase Six-Pulse Diode Bridge Rectifier:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: THREE-PHASE 6-PULSE DIODE BRIDGE RECTIFIER (400V LINE-LINE RMS -> 540V DC)
========================================================================================================================

    LINE L1 (R-Phase) ──[ F1: 20A ]──┬─────────────────────────────────────────────────────────────┐
    LINE L2 (S-Phase) ──[ F2: 20A ]──┼───────────────┬─────────────────────────────────────────────┼──────────────┐
    LINE L3 (T-Phase) ──[ F3: 20A ]──┼───────────────┼───────────────┬─────────────────────────────┼──────────────┼──────────────┐
                                     │               │               │                             │              │              │
                                    ┌┴┐ D1          ┌┴┐ D3          ┌┴┐ D5                         │              │              │
                                    │>│ Diodes Inc. │>│ Diodes Inc. │>│ Diodes Inc.                │              │              │
                                    │ │ 40TPS12     │ │ 40TPS12     │ │ 40TPS12                    │              │              │
                                    └┬┘ (1200V/35A) └┬┘ (1200V/35A) └┬┘ (1200V/35A)                │              │              │
                                     │               │               │                             │              │              │
                                     +---------------+---------------+=== COMMON CATHODE BUS       │              │              │
                                                                     |    (Positive DC Output)     │              │              │
                                                                     |                             │              │              │
                                                                     ├──[ L_dc: 2.5mH / 30A Choke ]┼──────────────┼──────────────┼───> +VDC (+540V)
                                                                     |  (Damps 300Hz Ripple)       │              │              │     │
                                                                    ┌┴┐ D4                        ┌┴┐ D6         ┌┴┐ D2          │    ┌┴────────────────┐
                                                                    │>│ 40TPS12                   │>│ 40TPS12    │>│ 40TPS12     │    │ C_DC BANK       │
                                                                    └┬┘ (Anode to DC-)            └┬┘            └┬┘             │   ┌┴┐ 2x 1000µF/450V │
                                                                     │                             │              │              │   │ │ Series Paired  │
                                                                     +─────────────────────────────+──────────────+──────────────┴───└┬┘ (ESR = 45mΩ)  │
                                                                     |                                                                 │ (Bleeders 100k)│
                                                                     +=================================================================+───> -VDC (GND)
```

- Top diodes (D_1, D_3, D_5) conduct whichever phase has the **highest positive potential**.
- Bottom diodes (D_4, D_6, D_2) conduct whichever phase has the **most negative potential**.
- Commutation occurs naturally every 60° (π / 3 radians).
- **Fundamental DC Output Ripple Frequency**:
  ```
f_ripple = 6 * f_line = 6 * 50 Hz = 300 Hz
```
- **Average DC Voltage (without filter cap)**:
  ```
V_dc,avg = (3 sqrt(3)) / π * V_pk_phase = 3 / π * V_pk_line-line ≈ 1.35 * V_LL,rms
```
  *(For 400 V_rms three-phase grid, V_dc,avg ≈ 540 V DC).*

---

## 2. Capacitive Filter Physics & Diode Conduction Angle

When a bulk capacitor C_bulk is connected across the rectifier output to smooth the DC rail, the diodes do not conduct for the full half-cycle (180°):

```text
               Diode Conduction Interval & Pulsed Current Spikes
   Voltage ^
       Vpk ┼───────.             .───────.             .───────
           │      / \           / \     / \           / \
           │     /   '-._______.-' \   /   '-._______.-' \
           │    /   Capacitor Ripple\ /                   \
        0V ┼───/─────────────────────v─────────────────────\───────────> Time
   Current ^
           │      |               |     |               |
      I_pk ┼──────|───────────────|─────|───────────────|──────────────
           │     / \             / \   / \             / \
        0A ┼────'───'───────────'───'─'───'───────────'───'────────────> Time
           │◄-θc-►│ Conduction Angle (Narrow Pulsed Spike!)
```

### 2.1 The Physics of Narrow Conduction Angles (θ_c):
- The diodes can only conduct when the input AC voltage exceeds the capacitor voltage: v_ac(t) > v_cap(t).
- As the capacitor discharges slowly into the load, the diode stays reverse-biased during most of the cycle.
- Near the voltage crest, the diode turns ON for a brief interval θ_c ≈ 30° ... 60°.
- **Consequence**: The entire charge needed to supply the load for a full half-cycle (10 ms) must be delivered in just 1.5 ... 3 ms!
- The diode peak current I_pk spikes to **5 ... 10 * the average load current**, producing:
  - Severe crest factor: CF = I_pk / I_rms >= 3.0
  - High total harmonic distortion: THD_i >= 80\% ... 120\%
  - Poor power factor: PF ≈ 0.55 ... 0.65 lagging.

---

## 3. Mathematical Formulations & Component Sizing

### 3.1 Bulk Capacitor Sizing for Specified Ripple (Δ V_ripple):
Assuming the capacitor discharges into load P_o during the discharge time t_dis ≈ 1 / (2 f_line):
```
C_bulk >= P_o / (2 * f_line * V_dc,pk * Δ V_ripple) = I_dc,load / (2 * f_line * Δ V_ripple)
```
Where:
- f_line = 50 Hz or 60 Hz
- V_dc,pk = sqrt(2) * V_ac,rms
- Δ V_ripple is the allowable peak-to-peak DC ripple voltage (typically 5\% ... 10\% * V_dc,pk).

### 3.2 Diode Peak & RMS Current Stresses:
```
I_diode,pk ≈ I_dc * π / θ_c
```
```
I_diode,rms ≈ I_dc * sqrt(π / (2 θ_c))
```
*Component Selection Rule*: Specify diodes whose non-repetitive peak forward surge current rating (I_FSM) is at least 10 ... 20 * rated DC load current.

---

## 4. Inrush Current & Thermal Protection

```text
               Inrush Current Limiting: NTC vs. Relay Pre-Charge
   SCHEME A (Low Cost, < 100W):                  SCHEME B (High Reliability, > 100W):
   AC ───[ Fuse ]───[ NTC Thermistor ]─── Bridge  AC ───[ Fuse ]───┬───[ Power Resistor R_pre ]───┬─── Bridge
                                                                   │                              │
                                                                   └───[ Bypass Relay Contact ]───┘
```

1. **Cold Inrush Surge**: When first plugged into AC mains at peak voltage (v_ac = 325 V), the uncharged bulk capacitor looks like an absolute short circuit (Z_cap ≈ 0 Ω). Inrush current is limited only by line impedance, easily exceeding 100 A ... 200 A, which can weld switch contacts and trip circuit breakers.
2. **NTC Thermistor (Scheme A)**: A Negative Temperature Coefficient thermistor has high resistance when cold (5 ... 10 Ω), limiting inrush to I_inrush = 325 V / 10 Ω = 32.5 A. Once running, load current heats the NTC, dropping its resistance to < 0.5 Ω.
   - *Failure Mode*: If power drops out for 1 second and immediately returns, the NTC is still hot and provides **zero protection**!
3. **Relay-Bypassed Power Resistor (Scheme B)**: Mandatory for industrial power electronics. A ceramic wirewound resistor (20 ... 50 Ω) limits initial charging. Once C_bulk reaches 80\% ... 90\% of peak voltage, a microcontroller or analog timer closes an electromechanical relay across the resistor, eliminating continuous resistor power dissipation.
