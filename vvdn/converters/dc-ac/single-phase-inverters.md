# Single-Phase DC-AC Inverters: Topologies, Unipolar/Bipolar SPWM & Filter Design

Welcome to the **VVDN Engineering Hub Technical Dossier on Single-Phase DC-AC Inverters**. Single-phase inverters convert a DC source into a sinusoidal AC output voltage and form the core of residential solar micro-inverters, Uninterruptible Power Supplies (UPS), battery power backup systems, and mobile power inverters.

This guide provides a comprehensive hardware analysis covering Half-Bridge and Full-Bridge (H-Bridge) topologies, square-wave vs. quasi-square modulation, mathematical derivations of Bipolar and Unipolar Sinusoidal PWM (SPWM), carrier frequency harmonic cancellation, and LC output low-pass filter design.

---

## 1. Operating Principle & Inverter Architectures

### 1.1 Half-Bridge Inverter:
The Half-Bridge inverter employs two switches and a split DC bus capacitor divider:

```text
                        Half-Bridge Inverter Power Stage
   +Vdc ────┬─────────────────────────────┬─────────────────────────────────┐
            │                             │                                 │
        Drain (D)                         │                                 │
        ┌───┴───┐ S1                      │                                ┌┴┐
        │  Q1   │ High-Side Switch      ┌─┴─┐ C1                           │ │ C_bulk
        └───┬───┘                       │   │                              └┬┘
            │ Source (S)                └─┬─┘                               │
            ├─── Switching Leg A ─────────┼───[ Filter Lf ]───┬───> +VAC    │
            │                             ├─── Split Neutral ─┼─────> -VAC  │
        Drain (D)                         │    Point (0V)    ┌┴┐            │
        ┌───┴───┐ S2                    ┌─┴─┐ C2             │ │ Cf         │
        │  Q2   │ Low-Side Switch       │   │                └┬┘            │
        └───┬───┘                       └─┬─┘                 │             │
            │ Source (S)                  │                   │             │
   GND ─────┴─────────────────────────────┴───────────────────┴─────────────┴─── GND
```
- **Output Swing**: Node A swings between +V_dc/2 and -V_dc/2 relative to the neutral point.
- **Limitation**: The maximum peak fundamental AC voltage is V_pk_ac = V_dc / 2. To generate 230 V_rms (325 V_peak), a DC bus of at least 650 V ... 700 V is required.

---

### 1.2 Full-Bridge (H-Bridge) Inverter:
The Full-Bridge topology utilizes four switches in two bridge legs (Leg A and Leg B):

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: SINGLE-PHASE FULL-BRIDGE (H-BRIDGE) INVERTER (400V DC -> 230V AC RMS, 3kVA)
========================================================================================================================

    +VDC BUS (+400V DC Rail) ──────────────┬───────────────────────────────┬─────────────────────────────┐
        │                                  │                               │                             │
       ┌┴─────────────────┐            Drain (D)                       Drain (D)                        ┌┴┐
       │ C_BUS_BULK       │           ┌────┴──────────┐               ┌────┴──────────┐                 │ │ C_HF_FILM
       │ 680µF / 450V     │           │ Q1: HS LEG A  │               │ Q3: HS LEG B  │                 └┬┘ 4x 1µF / 630V
       │ Aluminum Elec.   │    +----->│ IPW65R041CFD7 │        +----->│ IPW65R041CFD7 │                  │  Poly Film
       └┬─────────────────┘    | Gate │ (650V, 41mΩ)  │        | Gate │ (650V, 41mΩ)  │                  │
        │                      |      └────┬──────────┘        |      └────┬──────────┘                  │
        │                      |     Source│                   |     Source│                             │
        │   HIGH-SIDE DRIVER   |           │                   |           │                             │
        │   HO_A --------------+           +=== NODE SW_A      |           +=== NODE SW_B                │
        │   (UCC27282: Leg A)              |    (0V to +400V)  |           |    (0V to +400V)            │
        │                                  |                   |           |                             │
        │                              Drain (D)   +-----------+       Drain (D)                         │
        │                             ┌────┴───────┴──┐               ┌────┴──────────┐                  │
        │                             │ Q2: LS LEG A  │               │ Q4: LS LEG B  │                  │
        │                      +----->│ IPW65R041CFD7 │        +----->│ IPW65R041CFD7 │                  │
        │                      | Gate └────┬──────────┘        | Gate └────┬──────────┘                  │
        │   LO_A --------------+     Source│             LO_B -+     Source│                             │
        │   (Low-Side Leg A)               │             HO_B ─────────────+ (UCC27282: Leg B)           │
        │                                  │                               │                             │
    GND_DC ────────────────────────────────┴───────────────────────────────┴─────────────────────────────┴─── GND_DC
                                           │                               │
                                           │  SYMMETRICAL LC SINE FILTER   │
                                           ├──[ Lf1: 1.5mH / 20A Choke ]───┼────────────────────────+=== AC LINE (L)
                                           │  Sendust Toroid (DCR=12mΩ)    │                        │    (230V RMS, 50Hz)
                                           │                               │                       ┌┴┐
                                           │                               │                       │ │ Cf: 4.7µF / 310VAC
                                           │                               │                       └┬┘ Metallized Poly
                                           │                               │                        │  (Across L-N)
                                           │                               ├──[ Lf2: 1.5mH / 20A ]──+=== AC NEUTRAL (N)
                                           │                               │  Sendust Toroid        │
                                           │                               │                        │
                                           │                               │   [ HALL CURRENT SENSOR ]
                                           │                               │   LEM CASR 15-NP       │
                                           │                               │   (Output -> DSP ADC)  │
                                           │                               │                        │
    EARTH (PE) ────────────────────────────┴───────────────────────────────┴────────────────────────┴─── EARTH (PE)
```

### 1.2 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VDC_BUS** | DC Source / PFC Pre-Regulator | C_bus (+), Q_1 Drain, Q_3 Drain | High-voltage stiff DC link | Symmetrical high-frequency film bypass capacitors placed directly across each phase leg. |
| **SW_A (Leg A Mid)** | Q_1 Source, Q_2 Drain | Sine Filter Inductor L_f1 Pin 1 | High-speed PWM leg A switching node | Swings between 0 V and +400 V at carrier frequency f_c = 20 kHz; high dv/dt node. |
| **SW_B (Leg B Mid)** | Q_3 Source, Q_4 Drain | Sine Filter Inductor L_f2 Pin 1 | High-speed PWM leg B switching node | Swings between 0 V and +400 V; differential voltage v_AB = v_SW_A - v_SW_B. |
| **AC_LINE (L)** | Filter Inductor L_f1 Pin 2 | AC Output Terminal 1, Filter Cap C_f Terminal 1 | Pure sinusoidal AC line rail | Fundamental 230 V_RMS, 50 Hz sine wave; carrier ripple attenuated by > 40 dB. |
| **AC_NEUT (N)** | Filter Inductor L_f2 Pin 2 | AC Output Terminal 2, Filter Cap C_f Terminal 2 | Pure sinusoidal AC neutral rail | Symmetrical inductor L_f2 ensures balanced common-mode emission attenuation to Earth. |
| **GND_DC** | Q_2 Source, Q_4 Source, C_bus (-) | DC link return plane | High-current circulating DC ground | Heavy ground copper plane on internal PCB Layer 2. |

### 1.3 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1 ... Q_4** | High-Voltage N-MOSFETs | Infineon IPW65R041CFD7 | V_DS = 650 V, I_D = 50 A, R_DS(on) = 41 mΩ, Q_rr = 570 nC | Integrated fast body diode prevents destructive latchup during inductive freewheeling dead-time. |
| **L_f1, L_f2** | AC Sine Filter Inductors | Custom Sendust Core (CS468125) | 2 * 1.5 mH, I_rated = 20 A, DCR = 12 mΩ | Low-loss powder core prevents thermal saturation under full 3 kVA rated load current (I_rms = 13 A). |
| **C_f** | Differential AC Filter Cap | KEMET R46KR447000M2M | 4.7 µF, 310 V_AC, Metallized Polypropylene Film | Handles continuous 50 Hz AC reactive currents with negligible dissipation factor (tan δ < 0.001). |
| **C_bus,bulk** | DC Link Bulk Capacitor | Nichicon LGN2W681MELC | 680 µF, 450 V_DC, 105°C, ESR = 0.12 Ω | Absorbs double grid-frequency (100 Hz) pulsating power delivered to single-phase AC loads (P(t) = P_o [1 - cos 2ω t]). |
| **U_drv1, U_drv2**| High-Voltage Half-Bridge Drivers| TI UCC27282DR | 120 V / 650 V, 3 A sink / source, robust -5 V negative swing | Built-in shoot-through protection and 150 ns dead-time prevents rail-to-rail shoot-through. |
| **U_sense** | Closed-Loop Current Sensor | LEM CASR 15-NP | Nominal 15 A_RMS, bandwidth DC to 300 kHz, isolated | Provides fast current feedback to DSP for instantaneous current limiting and overcurrent trip. |

- **Output Swing**: Differential voltage v_AB = v_A - v_B swings across three discrete levels: +V_dc, 0 V, and -V_dc.
- **Advantage**: Peak AC output voltage equals full V_dc (V_pk_ac = V_dc), requiring only half the DC bus voltage of a half bridge (V_dc ≈ 350 V ... 400 V for 230 V_rms).

---

## 2. Modulation Techniques: Bipolar vs. Unipolar SPWM

In **Sinusoidal Pulse-Width Modulation (SPWM)**, a high-frequency triangular carrier wave v_tri(t) at switching frequency f_c is compared against a low-frequency reference sine wave v_ref(t) at grid frequency f_m (50 Hz):
- Amplitude Modulation Index: m_a = V_pk_ref / V_pk_tri (0 <= m_a <= 1)
- Frequency Modulation Ratio: m_f = f_c / f_m

```text
                  Bipolar SPWM vs. Unipolar SPWM Output Waveforms
   BIPOLAR SPWM (2-Level Differential Output):
   v_AB  ^
   +Vdc  ┼──┐  ┌┐ ┌──┐ ┌───┐ ┌──┐ ┌┐  ┌──
         │  │  ││ │  │ │   │ │  │ ││  │
   -Vdc  ┼──┴──┴┴─┴──┴─┴───┴─┴──┴─┴┴──┴──> Time (Switches between +Vdc and -Vdc)
         │ First harmonic cluster appears at CARRIER FREQUENCY: f_c
   
   UNIPOLAR SPWM (3-Level Differential Output):
   v_AB  ^
   +Vdc  ┼──┐  ┌┐ ┌──┐ ┌───┐ ┌──┐ ┌┐  ┌──
         │  │  ││ │  │ │   │ │  │ ││  │
     0V  ┼──┴──┴┴─┴──┴─┴───┴─┴──┴─┴┴──┴───────────────
         │                                  ┌┐ ┌──┐ ┌───┐
   -Vdc  ┼──────────────────────────────────┴┴─┴──┴─┴───┴──> Time
         │ First harmonic cluster appears at DOUBLE CARRIER: 2 * f_c !
```

### 2.1 Bipolar SPWM:
- Diagonal switch pairs are driven simultaneously: (S_1, S_4) ON together, or (S_2, S_3) ON together.
- Output voltage v_AB switches violently between +V_dc and -V_dc.
- The dominant harmonic cluster appears around **carrier frequency f_c**.
- High dv/dt stress and requires a large output filter inductor.

### 2.2 Unipolar SPWM (The Modern Standard):
- Bridge legs are modulated with two 180° phase-opposed reference waves:
  - Leg A compares v_ref(t) with v_tri(t).
  - Leg B compares -v_ref(t) with v_tri(t).
- During the positive AC half-cycle, v_AB alternates smoothly between **+V_dc and 0 V**.
- During the negative AC half-cycle, v_AB alternates smoothly between **0 V and -V_dc**.
- **Harmonic Doubling Feature**: The switching frequency ripple in Leg A and Leg B cancels differentially. The first major harmonic band appears at **2 * f_c**!
  - For a 20 kHz MOSFET switching frequency, the output filter only needs to attenuate ripple starting at **40 kHz**, dramatically reducing inductor size and core losses.

---

## 3. Mathematical Formulations & Harmonic Spectrum

### 3.1 Fundamental Output Voltage:
In the linear modulation range (m_a <= 1.0):
```
V_pk_fund = m_a * V_dc => V_rms,fund = (m_a * V_dc) / sqrt(2) ≈ 0.707 * m_a * V_dc
```

### 3.2 Total Harmonic Distortion (THD) Standards:
```
THD_v = (sqrt(Sum(h=2 to inf) V_h^2)) / V_1 * 100\%
```
- Grid-tied standards (**IEEE 519 / IEC 61000-3-2**) mandate:
  - Individual voltage harmonics: <= 3\%
  - Total Voltage THD: <= 5\%

---

## 4. LC Output Low-Pass Filter Design

To transform the high-frequency pulsed PWM waveform into a clean 50 Hz sine wave with THD < 2\%, a second-order LC low-pass filter is required:

```text
                             LC Low-Pass Filter Topology
                  Lf (Filter Inductor)
   Node A ────────────^^^^^^^^──────────┬──────────────────> Grid / Load L
                                        │
                                       ┌┴┐
                                       │ │ Cf (Film Capacitor)
                                       └┬┘
                                        │
   Node B ──────────────────────────────┴──────────────────> Grid / Load N
```

### 4.1 Filter Cutoff Frequency Selection:
The corner frequency f_cut must be positioned comfortably between the fundamental line frequency (f_m) and the effective switching frequency (f_sw,eff = 2 f_c for unipolar):
```
10 * f_m <= f_cut <= 1 / 5 * f_sw,eff
```
```
f_cut = 1 / (2π sqrt(L_f * C_f))
```

### 4.2 Inductor Sizing (L_f):
The filter inductor limits the high-frequency ripple current. To restrict peak-to-peak ripple Δ I_L to 20\% ... 30\% of rated peak load current I_pk:
```
L_f >= V_dc / (8 * f_sw,eff * Δ I_L)
```

### 4.3 Capacitor Sizing (C_f):
The capacitor must attenuate switching frequency harmonics without drawing excessive reactive VAR current at the fundamental frequency (Q_cap <= 5\% * S_rated):
```
C_f <= (0.05 * P_rated) / (2π * f_m * V_ac,rms^2)
```
And satisfies the corner frequency requirement:
```
C_f = 1 / ((2π f_cut)^2 * L_f)
```
*Component Rule*: Always specify low-dissipation-factor Metalized Polypropylene (MKP) film capacitors rated for continuous AC voltage (X2 / Snubber grade).

---

## 5. Practical Design Example: 3 kW 230V/50Hz Solar Inverter

- **DC Bus Voltage**: V_dc = 400 V
- **Output Rating**: V_o = 230 V_rms, 50 Hz, P_o = 3000 W (I_rms = 13.04 A, I_pk = 18.44 A)
- **Switching Frequency**: f_c = 25 kHz (Unipolar SPWM => f_sw,eff = 50 kHz)
- **Modulation Index**:
  ```
m_a = (sqrt(2) * 230 V) / 400 V = 325.3 V / 400 V ≈ 0.813
```
- **Inductor Sizing (Δ I_L = 20\% * I_pk = 3.69 A)**:
  ```
L_f = 400 V / (8 * 50 000 Hz * 3.69 A) ≈ 0.271 mH => Select 0.33 mH
```
- **Corner Frequency Selection**:
  ```
f_cut = 2.5 kHz (10 * 50 Hz << 2.5 kHz << 50 kHz)
```
- **Capacitor Sizing**:
  ```
C_f = 1 / ((2π * 2500)^2 * 0.33 * 10^-3) ≈ 12.3 µF => Select 10 µF / 300VAC MKP
```
- **Reactive VAR Verification**:
  ```
Q_c = 2π * 50 * 10 µF * (230 V)^2 ≈ 166 VAR (166 / 3000 ≈ 5.5\% of rated power - fully compliant)
```
