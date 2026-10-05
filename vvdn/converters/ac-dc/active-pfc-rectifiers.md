# Active Power Factor Correction (PFC) Rectifiers: Boost, Totem-Pole GaN & Vienna

Welcome to the **VVDN Engineering Hub Technical Dossier on Active Power Factor Correction (PFC) Rectifiers**. To comply with international grid harmonic regulations (**IEC 61000-3-2 Class D** and **IEEE 519**), every offline power supply exceeding 75 W—from server power supplies and laptop adapters to EV on-board chargers and telecom rectifiers—must incorporate Active PFC.

This guide provides an exhaustive hardware engineering analysis of the classic **Active Boost PFC Pre-regulator**, the ultra-high-efficiency **Bridgeless Totem-Pole GaN PFC**, and the multi-megawatt **Three-Phase Three-Level Vienna Rectifier**.

---

## 1. Why Active PFC? Regulatory Mandates & Power Quality

A passive diode rectifier draws narrow current spikes, resulting in poor power factor (PF ≈ 0.60) and massive harmonic injection (THD_i > 80\%). 

```text
               Passive Diode Current vs. Active PFC Current Waveforms
   PASSIVE RECTIFIER:                           ACTIVE PFC RECTIFIER:
   v_in, i_in ^                                 v_in, i_in ^
              │     Pulsed Current Spikes                  │    Input Current i_in is pure SINUSOID
              │        |             |                     │    in PERFECT PHASE with Voltage v_in!
              │       / \           / \                    │        /\            /\
              │  .---'   '---. .---'   '---.               │  .---./  \.-.   .---./  \.-.
              │ /  Voltage    \           /                │ /    /    \  \ /    /    \  \
           0V ┼/───────────────\─────────/──> Time      0V ┼/────/──────\──\────/──────\──\──> Time
              │ PF = 0.60, THDi = 110%                     │ PF = 0.998, THDi = 2.5%
              │ (FAILS IEC 61000-3-2)                      │ (COMPLIES WITH IEC 61000-3-2 CLASS D)
```

### True Power Factor Decomposition:
```
PF = (Real Power (P)) / (Apparent Power (S)) = 1 / (sqrt(1 + THD_i^2)) * cos φ_1
```
To achieve PF ≈ 1.0, the power supply must concurrently:
1. Drive phase displacement angle to zero (cos φ_1 -> 1.0).
2. Force harmonic distortion to near zero (THD_i -> 0 => 1 / (sqrt(1 + THD_i^2)) -> 1.0).

---

## 2. Classic Active Boost PFC Topology & Dual-Loop Control

The standard **Active Boost PFC** cascades a full-wave diode bridge with a high-frequency step-up boost converter:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: CONTINUOUS CONDUCTION MODE (CCM) ACTIVE BOOST PFC (85V-265V AC -> 400V DC, 600W)
========================================================================================================================

    AC LINE (85-265V) ──[ F1: 8A Time-Lag ]──[ NTC: 5Ω/8A ]──┬──[ EMI FILTER ]──[ BRIDGE RECTIFIER ]──┬─────────────────┐
                                              (Relay K1 Bypass)│  (CX1, CMC1, CY1) (GBU808: 800V/8A)   │                 │
    AC NEUTRAL ────────────────────────────────────────────────┴──────────────────────────────────────┼─┐               │
                                                                                                      │ │               │
                                    +-----------------[ D_inrush: 10A / 600V Standard ]---------------+ │               │
                                    |                 (Direct Startup Inrush Bypass Path)               │               │
                                    |                                                                   │               │
                                    |                                                                   │               │
                                    |                                     PFC BOOST INDUCTOR            │               │
                                    |                                 +---[ L_pfc: 450µH / 8A ]---------+               │
                                    |                                 |   Sendust CS33125 Toroid        │               │
                                    |                                 |   (DCR = 45mΩ, Isat = 11A)     ┌┴┐ C_in_HF      │
                                    |                                 +----------------+               │ │ 1.0µF / 450V │
                                    |                                                  │               └┬┘ Poly Film    │
                                    |                                                  +=== NODE SW     │ (Absorbs HF)  │
                                    |                                                  |    (0V to 400V)│               │
                                    |                                                  |                │               │
                                    |                               Drain (D)          ├──[ R_snub ]    │               │
                                    |                              ┌────┴──────────┐   │    2.2Ω / 2W   │               │
                                    |                              │ Q1: N-MOSFET  │   │   [ C_snub ]   │               │
                                    |                              │ IPW60R045CP   │   │    470pF/630V  │               │
                                    |                       +----->│ (650V, 45mΩ)  │   │     GND_PWR    │               │
                                    |                       | Gate └────┬──────────┘   │                │               │
                                    |                       |      Source│             │                │               │
                                    |   GATE DRIVER IC      |           │              │                │               │
                                    |   UCC27517 (Low-Side) |           +--------------+                │               │
                                    |   OUT ----[ R_g: 4.7Ω ]+          │                               │               │
                                    |                                  ┌┴┐ R_shunt: 20mΩ / 3W 1%        │               │
                                    |                                  │ │ (Low-Side Inductor Sense)    │               │
                                    |                                  └┬┘                              │               │
                                    |                                   │                               │               │
                                    |                                GND_PWR ───────────────────────────┴───────────────┘
                                    |                                   │
                                    |      BOOST PFC RECTIFIER DIODE    │
                                    |      +---[ D_pfc: SiC Schottky ]--+
                                    |      |   Wolfspeed C3D06060A
                                    |      |   (600V, 6A, Qrr = 0)
                                    |      +---[ Anode  ->|  Cath ]-----+
                                    |                                   │
                                    +───────────────────────────────────+=== +VDC BUS (+400V DC Regulated)
                                                                        │
                                                                       ┌┴──────────────────┐
                                                                       │ C_BULK BANK       │
                                                                      ┌┴┐ 2x 330µF / 450V ┌┴┐ C_HF_CER
                                                                      │ │ Nichicon LGN    │ │ 2x 0.47µF / 630V
                                                                      └┬┘ (Hold-Up Cap)   └┬┘ Film Capacitor
                                                                       │                   │
                                                                       │      +VDC         │
                                                                       │        │          │
                                                                       │     [ R_fb1: 1.0MΩ / 0.5W ]
                                                                       │     [ R_fb2: 1.0MΩ / 0.5W ]
                                                                       │        │
                                                                       │        +---> V_FB (To PFC Controller)
                                                                       │        │     (V_ref = 2.500V)
                                                                       │     [ R_fb3: 12.7kΩ / 0.1% ]
                                                                       │        │
                                                                       │       AGND (Quiet Ground)
                                                                       │        │
                                                                       │     (Single Star Tie Point)
    GND_PWR (Power Ground Return) ─────────────────────────────────────┴────────+──────────┴───> -VDC (GND)
```

### 2.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **RECT_OUT (+)** | Full-Wave Bridge (+) | Inrush Diode D_inrush Anode, Boost Choke L_pfc Pin 1, C_in,HF | 100Hz/120Hz rectified haversine input | High-frequency film cap C_in,HF prevents 100kHz ripple from feeding back into bridge diodes. |
| **SW (PFC Node)** | Boost Choke L_pfc Pin 2, Q_1 Drain | SiC Diode D_pfc Anode, Snubber | High-voltage 100kHz boost switching node | Heavy trace routing; minimize loop area between Q_1 drain, D_pfc anode, and C_bulk return. |
| **+VDC (400V Bus)** | Diode D_pfc Cathode, D_inrush Cathode | C_bulk bank (+), Feedback Divider, Downstream PSU | Regulated +400V DC intermediate bus | Inrush diode D_inrush bypasses boost choke during plug-in to prevent core saturation. |
| **ISENSE_P / N** | Current Shunt R_shunt Kelvin Pads | PFC Controller Current Loop Amplifier | Average inductor current sensing | Route as shielded differential pair; carries rectified sinusoidal current wave. |
| **V_FB** | Resistor Divider R_fb1-3 Junction | PFC Controller Voltage Loop Amp (Pin 1) | Output voltage regulation feedback | Total divider resistance ≈ 2 MΩ to minimize quiescent bleeder power dissipation. |
| **GND_PWR** | Bridge (-), R_shunt (-), C_bulk (-) | High-current power return plane | Circulating power stage ground | Solid ground plane; isolated from quiet analog signal ground AGND. |

### 2.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1** | PFC Boost N-MOSFET | Infineon IPW60R045CP | V_DS = 650 V, I_D = 60 A, R_DS(on) = 45 mΩ, Q_g = 150 nC | Superjunction CoolMOS provides ultra-low conduction losses at high RMS current (I_rms ≈ 6.5 A at 90 V_ac). |
| **D_pfc** | SiC Boost Rectifier Diode | Wolfspeed C3D06060A | V_RRM = 600 V, I_F = 6 A, Q_c = 14 nC, V_F = 1.5 V | **Zero Reverse Recovery (Q_rr ≈ 0)**: Essential for continuous conduction mode (CCM) to avoid turn-on shoot-through. |
| **D_inrush** | Startup Inrush Bypass Diode | Diodes Inc. S10MC | V_RRM = 1000 V, I_F = 10 A, I_FSM = 300 A | Conducts initial 80 A surge at AC plug-in; prevents L_pfc saturation and protects D_pfc. |
| **L_pfc** | Boost PFC Inductor | Custom Sendust Core (CS33125) | L = 450 µH, I_sat = 11 A, I_rms = 7.5 A, DCR = 45 mΩ | Low-permeability Sendust material (µ_r = 60) maintains soft saturation characteristics without overheating. |
| **C_bulk** | DC Bus Bulk Capacitors | Nichicon LGN2W331MELY | 2 * 330 µF, 450 V_DC, 105°C, ESR = 0.18 Ω | Accommodates 100Hz double-frequency ripple current (I_ripple ≈ 2.8 A_rms) and 20ms hold-up. |
| **R_shunt** | Inductor Current Sense Shunt | Isabellenhütte ISA-WELD | 20 mΩ, 3.0 W, 1\%, TCR < 20 ppm/°C | Non-inductive electron-beam welded manganin construction ensures clean current measurement. |
| **U_1 (PFC IC)** | CCM PFC Controller | TI UCC28019A / UCC28180 | Continuous average current mode, internal ramp sync | Eliminates external AC voltage sensing; requires only current and output voltage sense. |


### 2.1 The Boost Requirement (V_dc = 400 V):
Because a Boost converter can only step *up* voltage (V_out > V_in), the regulated DC bus must exceed the peak of the highest AC input line voltage:
- Universal AC Mains: 85 V ... 265 V_rms
- Maximum Peak AC Line: V_pk,max = sqrt(2) * 265 V ≈ 375 V
- Standard Industry DC Bus: **V_dc = 390 V ... 400 V DC**.

---

### 2.2 Dual-Loop Average Current-Mode Control:

```text
                     Dual-Loop Average Current-Mode Controller
                                      400V DC Bus
                                           │
                                     [ Voltage Divider ]
                                           │
                                           v  V_fb
      V_ref (2.5V) ──────>( - )            │
                           [ Error Amp 1 ]<┘
                           (Voltage Loop)
                                 │
                                 v  V_comp (Slow Outer Loop: ~10 Hz Bandwidth)
   |v_in(t)|                     │
   (Rectified Sine) ────────────( X ) MULTIPLIER
                                 │
                                 v  i_ref(t) = k * V_comp * |v_in(t)| (Reference Current)
                                 │
                                 v
                          ┌─────( - )
                          │ [ Error Amp 2 ] (Inner Fast Current Loop: ~15 kHz)
                          │      │
                          │      v
                          │   [ PWM Modulator ] ───> Gate Q1 (100 kHz)
                          │      ^
                          │      │
   Inductor Current i_L ──┴──────┘
```

1. **Slow Outer Voltage Loop (sim 10 ... 20 Hz)**:
   - Compares the 400 V DC bus with a reference to maintain voltage regulation.
   - **Crucial Engineering Rule**: The loop bandwidth must be strictly below 20 Hz to avoid tracking the 100 Hz / 120 Hz rectified AC line ripple. If the voltage loop were fast, it would distort the input current reference!
2. **Fast Inner Current Loop (sim 10 ... 20 kHz)**:
   - Multiplies the voltage error signal V_comp by the instantaneous rectified AC line waveform |v_in(t)| to construct an instantaneous reference current i_ref(t).
   - Modulates the switch duty cycle cycle-by-cycle to force the inductor current i_L(t) to perfectly match i_ref(t).

---

## 3. Advanced Bridgeless Totem-Pole GaN PFC

Conventional Boost PFC suffers conduction losses from the diode bridge (2 * V_F ≈ 2 * 0.8 V = 1.6 V drop => 16 W lost at 10 A). The **Bridgeless Totem-Pole PFC** eliminates the diode bridge entirely:

```text
                     Bridgeless Totem-Pole PFC Power Stage
                      L_pfc
   AC Line ───────────^^^^^^──────┬───────────────────────────────┐
                                  │                               │
                              Drain (D)                       Drain (D)
                              ┌───┴───┐ Q1 (GaN HEMT)         ┌───┴───┐ S1 (Si Superjunction)
                              │  HS   │ High-Frequency        │  LS   │ Low-Frequency
                              └───┬───┘ (100kHz - 1MHz)       └───┬───┘ Line Synchronous
                                  │ Source                        │ Source (50Hz)
                                  ├── Midpoint HF ──┐             ├── Midpoint LF ──┐
                                  │                 │             │                 │
                              Drain (D)             │         Drain (D)             │
                              ┌───┴───┐ Q2 (GaN HEMT)│         ┌───┴───┐ S2 (Si Superjunction)
                              │  LS   │ High-Frequency│        │  LS   │ Low-Frequency
                              └───┬───┘ (100kHz - 1MHz)│       └───┬───┘ Line Synchronous
                                  │ Source          │             │ Source (50Hz)   │
   GND_DC ────────────────────────┴─────────────────┼─────────────┴─────────────────┼─── GND_DC
                                                    │                               │
   AC Neutral ──────────────────────────────────────┼───────────────────────────────┘
                                                    │
                                                   ┌┴┐ C_bulk (400V DC)
                                                   │ │
                                                   └┬┘
```

### 3.1 Why Silicon MOSFETs Fail in Totem-Pole (The GaN Revolution):
- In the totem-pole configuration, the high-frequency switches operate in continuous conduction mode (CCM) half-bridge hard switching.
- Standard silicon MOSFETs possess massive body-diode reverse recovery charge (Q_rr ≈ 500 ... 2000 nC). When the opposite switch turns ON, this Q_rr causes destructive shoot-through spikes and extreme switching losses.
- **Gallium Nitride (GaN) HEMTs have ZERO reverse recovery (Q_rr = 0 nC)**.
- GaN enables the Totem-Pole topology to operate in CCM at > 100 kHz, achieving unprecedented **99.2\% conversion efficiency**!

---

## 4. Three-Phase Three-Level Vienna Rectifier

For high-power EV DC fast charging stations (50 kW ... 350 kW) and megawatt data centers, the **Vienna Rectifier** is the premier unidirectional active PFC topology:

```text
                     Three-Phase Three-Level Vienna Rectifier
                   L1
   Phase A ───────^^^^^──┬───[>|]─┬───[>|]─────────────────────────────┬───> +400V (Vdc/2)
                         │   D1   │   D2                               │
                         ├──[~]───┤                                   ┌┴┐
                         │   Q1   │ Bidirectional                     │ │ C1
                         │ (MOS)  │ Midpoint Switch                   └┬┘
                         │        │                                    ├─── Neutral (0V)
                         ├──[|<]──┴───[|<]─────────────────────────┐   │
                         │   D3       D4                           │  ┌┴┐
                         │                                         │  │ │ C2
                         └──────── Neutral Midpoint (0V) ──────────┼──└┬┘
                                                                   │   │
                                                                   └───┴───> -400V (-Vdc/2)
                                                                       Total Vdc = 800V
```

### Key Engineering Advantages:
1. **Three-Level Voltage Synthesis**: Node voltages switch between +V_dc / 2, 0 V, and -V_dc / 2.
2. **Halved Switch Voltage Stress**: Each MOSFET switch Q_1 experiences only half the total DC-link voltage (400 V stress on an 800 V EV bus!), allowing the use of low-cost, ultra-fast 650 V Superjunction or GaN FETs instead of expensive 1200 V SiC modules.
3. **Pristine Grid Quality**: Inherent 3-level PWM cuts inductor ripple in half, achieving THD_i < 2.0\% and PF > 0.998.

---

## 5. Component Sizing & Bulk Capacitor Hold-Up Time

### 5.1 Inductor Sizing (L_pfc):
Worst-case ripple occurs at the peak of the minimum AC line voltage:
```
L_pfc >= (V_in,pk,min * ( 1 - V_in,pk,min / V_dc )) / (f_s * Δ I_L)
```
Where V_in,pk,min = sqrt(2) * 85 V ≈ 120 V, V_dc = 400 V, and Δ I_L = 20\% * I_pk,max.

### 5.2 Bulk Capacitor Sizing for Hold-Up Time (t_hold):
Server and telecom specifications (e.g., Intel ATX / Open Compute) mandate that the DC bus must sustain full output power during a complete AC line dropout of 1 ... 2 missing AC cycles (t_hold = 16.67 ms ... 20 ms) without V_dc falling below the downstream DC-DC converter's minimum drop-out threshold (V_dc,min ≈ 300 V):

```
Δ E = P_out * t_hold = 1 / 2 C_bulk ( V_dc,nom^2 - V_dc,min^2 )
```
```
C_bulk >= (2 * P_out * t_hold) / (η * ( V_dc,nom^2 - V_dc,min^2 ))
```

#### Practical Sizing Example (1000 W Server PSU):
- P_out = 1000 W, η = 0.95
- V_dc,nom = 400 V, V_dc,min = 300 V
- t_hold = 20 ms (0.020 s)
```
C_bulk >= (2 * 1000 * 0.020) / (0.95 * (400^2 - 300^2)) = 40 / (0.95 * (160000 - 90000)) = 40 / 66500 ≈ 601 µF
```
*Design Recommendation*: Specify two 330 µF / 450 V (660 µF total) high-temperature 105°C aluminum electrolytic capacitors in parallel.
