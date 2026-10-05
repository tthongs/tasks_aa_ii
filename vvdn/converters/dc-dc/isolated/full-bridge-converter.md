# Isolated Full-Bridge DC-DC Converter: Hard-Switched vs Phase-Shifted ZVS Mechanics

Welcome to the **VVDN Engineering Hub Technical Dossier on the Isolated Full-Bridge DC-DC Converter**. This document delivers an in-depth hardware engineering analysis of the Full-Bridge topology, focusing on the industrial workhorse: the **Phase-Shifted Full-Bridge (PSFB) Zero-Voltage-Switching (ZVS)** converter. It covers bipolar transformer utilization, leading-leg vs. lagging-leg commutation physics, duty-cycle loss (Δ D), secondary diode voltage ringing suppression, and practical design equations for kilowatts-scale power supplies.

---

## 1. Operating Principle & Full-Bridge Architecture

The **Full-Bridge DC-DC Converter** employs four primary semiconductor switches configured in an H-bridge configuration across a center-tapped or full-wave secondary stage:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: PHASE-SHIFTED FULL-BRIDGE (PSFB) ZVS CONVERTER (400V -> 48V/20A, 1kW)
========================================================================================================================

    +V_BUS (+400V DC Rail) ───────────────┬───────────────────────────────┬─────────────────────────────┐
        │                                 │                               │                             │
       ┌┴─────────────────┐           Drain (D)                       Drain (D)                        ┌┴┐
       │ C_BUS_BULK       │          ┌────┴──────────┐               ┌────┴──────────┐                 │ │ C_CER
       │ 470µF / 450V     │          │ Q1: HS LEADING│               │ Q3: HS LAGGING│                 └┬┘ 4x 1µF/630V
       │ Aluminum Elec.   │   +----->│ IPW60R045CP   │        +----->│ IPW60R045CP   │                  │   Poly Film
       └┬─────────────────┘   | Gate │ (650V, 45mΩ)  │        | Gate │ (650V, 45mΩ)  │                  │
        │                     |      └────┬──────────┘        |      └────┬──────────┘                  │
        │                     |     Source│                   |     Source│                             │
        │   DUAL-LEG DRIVER   |           │                   |           │                             │
        │   HO_A -------------+           +=== NODE MID_A     |           +=== NODE MID_B               │
        │   (Leading Leg)                 |    (Leading Leg)  |           |    (Lagging Leg)            │
        │                                 |                   |           |                             │
        │                             Drain (D)   +-----------+       Drain (D)                         │
        │                            ┌────┴───────┴──┐               ┌────┴──────────┐                  │
        │                            │ Q2: LS LEADING│               │ Q4: LS LAGGING│                  │
        │                     +----->│ IPW60R045CP   │        +----->│ IPW60R045CP   │                  │
        │                     | Gate └────┬──────────┘        | Gate └────┬──────────┘                  │
        │   LO_A -------------+     Source│             LO_B -+     Source│                             │
        │   HO_B ---------------------------------------------+           │                             │
        │                                 │                               │                             │
    GND_PRI ──────────────────────────────┴───────────────────────────────┴─────────────────────────────┴─── GND_PRI
                                          │                               │
                                          │  RESONANT SHIM INDUCTOR       │
                                          ├──[ L_shim: 8.5µH / 15A ]──────┼────────────────────────┐
                                          │  Wurth 7443640850             │                        │
                                          │                               │                        │
                                          │  DC BLOCKING CAPACITOR        │                        │
                                          ├──[ C_b: 0.22µF / 630V Film ]──┼──[ CT1: Prim Current ]─┤
                                          │                               │   Sense Transformer    │
                                          │                               │   (1:100 Ratio)        │
                                          │                               │                        │
                                          │                               │   TRANSFORMER PRIMARY  │
                                          │                               │   +---[ Np: 16T ]------+
                                          │                               │   |   * (Dot at Mid_A)
                                          │                               └───+--------------------+
                                          │
   =======================================│===================================== ISOLATION BARRIER =================
                                          │
    GND_SEC ──────────────────────────────┼───+─────────────────────────────────────────────────────────┬─── GND_SEC
                                          │   │                                                         │
                                          │   │                        SECONDARY CENTER-TAP             │
                                          │   │                        (Ns1: 3T, Ns2: 3T)               │
                                          │   │                                   │                     │
                                          │   │                     +-------------+-------------+       │
                                          │   │                     |                           |       │
                                          │   │               SECONDARY WINDING 1         SECONDARY WINDING 2
                                          │   │               (Ns1: 3T)                   (Ns2: 3T)     │
                                          │   │               * (Dot at Anode D1)         |             │
                                          │   │                     |                     * (Dot at Center-Tap)
                                          │   │                     +---[>|] D1           |             │
                                          │   │                         IDH12G65C6        +---[>|] D2 (SiC Schottky)
                                          │   │                         [Cathode]             [Cathode] │
                                          │   │                             │                     │     │
                                          │   │                             +==========+==========+     │
                                          │   │                                        |                │
                                          │   │                                        +=== NODE SEC_RECT
                                          │   │                                        |    (Rectified +75V)
                                          │   │                                        |                │
                                          │   │                                        ├──[ R_snub_sec: 4.7Ω / 3W ]
                                          │   │                                        │         │      │
                                          │   │                                        │   [ C_snub: 1.5nF/200V ]
                                          │   │                                        │         │      │
                                          │   │                                        │      GND_SEC   │
                                          │   │                                        │                │
                                          │   │                                        +---[ Lo: 22µH / 25A Choke ]---+
                                          │   │                                            Coilcraft AGP4233-223      │
                                          │   │                                            (DCR = 3.6mΩ, Isat = 28A)  │
                                          │   │                                                                       │
                                          │   │                                                                       +=== +VOUT (+48V/20A)
                                          │   │                                                                       │
                                          │   │                                                                      ┌┴──────────────────┐
                                          │   │                                                                      │ COUT_BULK         │
                                          │   │                                                                     ┌┴┐ 4x 220µF/63V    ┌┴┐ COUT_CER
                                          │   │                                                                     │ │ Poly (ESR=12mΩ) │ │ 6x 10µF/100V
                                          │   │                                                                     └┬┘                 └┬┘ X7R 1210
                                          │   │                                                                      │                   │
    GND_SEC ──────────────────────────────┴───┴──────────────────────────────────────────────────────────────────────┴───────────────────┴─── GND_SEC
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+V_BUS** | PFC Pre-Regulator Bus | C_bus (+), Q_1 Drain, Q_3 Drain | High-voltage 400V DC input rail | Symmetrical high-frequency decoupling film capacitors placed adjacent to each half-bridge leg. |
| **MID_A (Leading Leg)**| Q_1 Source, Q_2 Drain | Shim Inductor L_shim Pin 1 | High-speed ZVS leading leg switching node | Driven by 50\% complementary PWM with fixed dead-time (t_dead ≈ 200 ns). |
| **MID_B (Lagging Leg)**| Q_3 Source, Q_4 Drain | Transformer Primary N_p Pin 2 | Phase-shifted lagging leg switching node | Phase-shifted by angle φ relative to Leg A; achieves ZVS using energy stored in L_shim. |
| **PRIM_RESONANT** | Shim Inductor L_shim Pin 2 | Series DC Blocking Cap C_b, Current Transformer CT1 | Primary resonant energy transfer loop | L_shim supplements transformer leakage inductance to ensure ZVS down to 20\% light load. |
| **SEC_RECT** | SiC Diodes D_1, D_2 Common Cathodes | Output Filter Choke L_o Pin 1, Snubber | High-frequency rectified DC pulse train | Operating frequency is 2 f_s = 200 kHz; SiC diodes eliminate reverse-recovery voltage overshoot. |
| **+VOUT** | Output Choke L_o Pin 2 | C_out bank (+), Feedback network, Load (+) | High-power regulated +48V DC bus | Power copper plane designed for 20A continuous load current. |
| **GND_SEC** | Transformer Secondary Center-Tap | C_out bank (-), Secondary Return | Secondary isolated power ground | Carries total load return current (20 A). |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1 ... Q_4** | Primary High-Voltage N-FETs | Infineon IPW60R045CP | V_DS = 650 V, I_D = 60 A, R_DS(on) = 45 mΩ, C_oss = 160 pF | Low R_DS(on) and well-defined output capacitance C_oss enable complete ZVS discharge during dead-time. |
| **L_shim** | External Resonant Inductor | Würth Elektronik 7443640850 | L = 8.5 µH, I_sat = 22 A, I_rms = 16 A, DCR = 3.2 mΩ | High-frequency gapped core handles circulating primary reactive energy without thermal runaway. |
| **C_b** | DC Blocking Film Cap | Vishay MKP1848520704K2 | 0.22 µF, 700 V_DC, Metallized Polypropylene | Prevents net DC volt-second imbalance from walking the transformer core into saturation. |
| **T_1** | Main PSFB Transformer | Custom ETD49 Core (3C95) | Turns: 16:(3+3), L_m = 2.4 mH, L_lk = 1.5 µH | Triple-insulated wire, interleaved secondary copper foil for low proximity loss and leakage control. |
| **D_1, D_2** | Secondary SiC Diodes | Infineon IDH12G65C6 | V_RRM = 650 V, I_F = 12 A, Q_c = 17 nC, V_F = 1.35 V | SiC Schottky eliminates diode reverse recovery snap-off, allowing smaller snubbers and higher efficiency. |
| **L_o** | Output Filter Inductor | Coilcraft AGP4233-223ME | L = 22 µH, I_sat = 28 A, I_rms = 22 A, DCR = 3.6 mΩ | Heavy edge-wound copper ribbon choke maintains CCM across entire active load spectrum. |
| **C_out,bulk** | Output Bulk Capacitor | Panasonic 63SVPF220M | 4 * 220 µF, 63 V, OS-CON Polymer, ESR = 12 mΩ | Low equivalent impedance (3 mΩ) absorbs inductor current ripple with < 25 mV ripple. |
| **U_1 (Controller)** | Phase-Shifted PWM IC | TI UCC28951-Q1 | Advanced ZVS controller with adaptive delay, sync rect drive | Independent programmable dead-time control for leading and lagging legs. |


### 1.1 Hard-Switched Full-Bridge vs. Phase-Shifted Full-Bridge (PSFB)
- **Hard-Switched Full-Bridge**: Diagonal switch pairs (Q1-Q4 and Q2-Q3) are driven simultaneously via conventional pulse-width modulation (PWM). Turn-on and turn-off occur at high V_DS and high I_D, leading to severe switching losses (E_sw proportional to f_s * V_in^2 * I), preventing operation above 50 kHz.
- **Phase-Shifted Full-Bridge (PSFB)**: Each bridge leg operates at a fixed ≈ 50\% duty cycle with a small dead-time. Voltage regulation is achieved by **shifting the phase** of Leg B (Lagging Leg: Q3/Q4) relative to Leg A (Leading Leg: Q1/Q2). The primary leakage inductance (L_lk) and MOSFET parasitic output capacitances (C_oss) are utilized to achieve **Zero-Voltage Switching (ZVS)** at all switch transitions.

---

## 2. PSFB Switching Intervals & Detailed Waveforms

```text
                          PSFB Key Operating Waveforms
   Gate Q1  ───┐                ┌───────────────────┐                ┌────────
               └────────────────┘                   └────────────────┘
   Gate Q2  ────────────┐                ┌───────────────────┐
            ────────────┘                └───────────────────┘
   Gate Q3  ───────┐                ┌───────────────────┐                ┌────
            ───────┘                └───────────────────┘
   Gate Q4  ────────────────┐                ┌───────────────────┐
            ────────────────┘                └───────────────────┘
               │◄-φ-►│ Phase Shift Angle
   V_AB     ───┐     ┌──────────┐                   ┌──────────┐
               │     │          │                   │          │
            ───┴─────┘          └───────────────────┘          └──────────────
                                │◄────── -Vin ─────►│
   I_primary         /──────────\                   /──────────\
            ────────/            \─────────────────/            \─────────────
                   /              \               /              \
   V_rect      ┌───┐            ┌───┐           ┌───┐            ┌───┐
            ───┘   └────────────┘   └───────────┘   └────────────┘   └────────
               │◄ΔD►│ Duty Cycle Loss
```

### 2.1 The Six Operating Modes of PSFB:
1. **Power Delivery Interval (Q_1, Q_4 ON)**: V_AB = +V_IN. Current flows through Q_1, L_lk, primary winding, and Q_4. Diode D_1 conducts, powering the output load and charging L_o.
2. **Leading-Leg Transition (Q_1 -> Q_2 Dead-Time)**: Q_1 turns OFF. The reflected output inductor current (n * I_Lo) quickly charges C_oss,Q1 to V_IN and discharges C_oss,Q2 to 0 V. The body diode of Q_2 clamps to ground, allowing Q_2 to turn ON under **ZVS**.
3. **Freewheeling Primary Interval (Q_2, Q_4 ON)**: V_AB = 0 V. Primary current circulates through Q_2 and Q_4. On the secondary, both rectifier diodes D_1 and D_2 conduct simultaneously, shorting the transformer secondary and freewheeling I_Lo.
4. **Lagging-Leg Transition (Q_4 -> Q_3 Dead-Time)**: Q_4 turns OFF. Because secondary diodes are shorted, **only the energy stored in the primary leakage inductance (L_lk)** is available to discharge C_oss,Q3 and charge C_oss,Q4.
5. **Duty Cycle Loss (Δ D) Interval**: Q_3 turns ON under ZVS (if energy was sufficient). V_AB = -V_IN, but secondary diodes remain shorted until the primary current reverses from +I_pk to -I_pk across L_lk. During this commutation interval, no energy transfers to the output.
6. **Reverse Power Delivery (Q_2, Q_3 ON)**: Primary current reaches -I_pk, diode D_1 reverse-biases, and D_2 supplies power to the load.

---

## 3. Mathematical Formulations & Component Derivations

### 3.1 Effective Duty Cycle and Voltage Conversion:
Because of the duty cycle loss (Δ D) during primary current reversal:
```
D_eff = D - Δ D
```
```
Δ D = (4 * f_s * L_lk * I_o) / (n * V_IN)
```
Where n = N_p / N_s is the primary-to-secondary turns ratio.

The DC output voltage is:
```
V_out = 2 * N_s / N_p * V_IN * D_eff = 2 * N_s / N_p * V_IN * ( D - (4 * f_s * L_lk * I_o) / (n * V_IN) )
```

### 3.2 ZVS Energy Criterion (Leading vs. Lagging Leg):
- **Leading Leg Transition**:
  Assisted by both the leakage inductance and the reflected output filter inductance (L_o):
  ```
1 / 2 (L_lk + n^2 L_o) I_pk^2 > 4 / 3 C_oss V_IN^2
```
  *Result*: Leading leg achieves ZVS over virtually the entire load range (10\% ... 100\%).

- **Lagging Leg Transition**:
  During the freewheeling state, the secondary is shorted, isolating L_o. ZVS relies purely on primary leakage inductance L_lk:
  ```
1 / 2 L_lk I_pk^2 > 4 / 3 C_oss V_IN^2
```
  *Hardware Consequence*: At light load (I_pk low), the energy 1 / 2 L_lk I_pk^2 is insufficient to discharge C_oss, causing the lagging leg to **lose ZVS and suffer hard switching**.

### 3.3 Dead-Time Calculation:
```
t_dead,lead >= (2 * C_oss * V_IN) / I_pk,lead
```
```
t_dead,lag ≈ π / 2 sqrt(L_lk * (2 C_oss))
```

---

## 4. Hardware Engineering Challenges & Mitigation

| Engineering Challenge | Physical Mechanism | Hardware Mitigation Solution |
| :--- | :--- | :--- |
| **Lagging Leg ZVS Loss at Light Load** | L_lk energy drops with I_load^2; cannot overcome MOSFET C_oss. | Add an external shim inductor in series with primary, or introduce auxiliary commutating inductors / saturated inductors. |
| **Secondary Diode Voltage Ringing** | Resonance between secondary diode junction capacitance C_j and transformer leakage inductance L_lk. Ringing voltage can exceed 2 * V_sec. | Install primary auxiliary clamping diodes (clamping to V_IN rails), active secondary clamps, or RC snubbers across D_1, D_2. |
| **Transformer DC Flux Walking** | Unequal gate drive delays or asymmetric switch R_DS(on) create DC voltage offset, saturating the core. | Insert a low-loss polypropylene DC blocking capacitor in series with primary winding, or implement peak current-mode control. |
| **Loss of Effective Duty Cycle (Δ D)** | Increasing L_lk expands ZVS range but steals duty cycle, requiring a higher turns ratio and higher secondary voltage stress. | Optimize L_lk carefully; utilize planar transformers with controlled leakage and low C_oss GaN/SiC FETs. |

---

## 5. Comprehensive Design Example: 3.3 kW Telecom Power Supply

- **Input Voltage**: 380 V ... 420 V DC (PFC Output, Nominal 400 V)
- **Output Voltage**: 48 V ... 54 V DC (Nominal 50 V at 66 A)
- **Switching Frequency**: 100 kHz
- **Turns Ratio Selection (n = N_p / N_s)**:
  ```
D_max = 0.42, Δ D_est = 0.05 => D_eff = 0.37
```
  ```
n <= (2 * V_in,min * D_eff) / (V_o + V_drop) = (2 * 380 V * 0.37) / 50.5 V ≈ 5.56 => Select N_p = 16, N_s = 3 (n = 5.33)
```
- **Leakage Inductor Sizing**:
  ```
L_lk ≈ (Δ D * n * V_IN) / (4 * f_s * I_o) = (0.05 * 5.33 * 400) / (4 * 100 000 * 66) ≈ 4.0 µH
```
- **Primary Switch Selection**:
  650 V Superjunction MOSFETs with ultra-low C_oss (e.g., C_o(er) ≈ 120 pF) or 650 V GaN HEMTs.
