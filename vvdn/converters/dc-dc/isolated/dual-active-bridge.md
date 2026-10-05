# Dual Active Bridge (DAB) DC-DC Converter: Bidirectional Physics, Modulation & ZVS

Welcome to the **VVDN Engineering Hub Technical Dossier on the Dual Active Bridge (DAB) Converter**. This guide provides an advanced mathematical and hardware analysis of the DAB topology—the premier isolated bidirectional DC-DC architecture for Electric Vehicle (EV) onboard chargers, Vehicle-to-Grid (V2G) systems, battery energy storage systems (BESS), and solid-state transformers (SST).

---

## 1. Operating Principle & Bidirectional Architecture

The **Dual Active Bridge (DAB)** converter comprises two active full-bridge (H-bridge) switching stages coupled across a high-frequency isolation transformer with an energy-transfer power inductance (L):

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: BIDIRECTIONAL DUAL ACTIVE BRIDGE (DAB) CONVERTER (400V <-> 48V, 3.3kW EV/ESS)
========================================================================================================================

  +================ PORT 1: HIGH-VOLTAGE DC BUS (+400V) ================+   +================ PORT 2: LOW-VOLTAGE DC BUS (+48V) =================+
  +V1 (+400V DC) ─────────┬───────────────────────┬─────────────────────┐     +V2 (+48V DC) ──────────┬───────────────────────┬─────────────────────┐
      │                   │                       │                     │         │                   │                       │                     │
     ┌┴─────────────────┐ │                       │                    ┌┴┐       ┌┴─────────────────┐ │                       │                    ┌┴┐
     │ C1_BULK          │ │                       │                    │ │ C1_CER│ C2_BULK          │ │                       │                    │ │ C2_CER
     │ 470µF / 450V     │ │                       │                    └┬┘ 4x 1µF│ 1200µF / 63V     │ │                       │                    └┬┘ 6x 10µF
     │ Poly Film        │ │                       │                     │  630V  │ Low-ESR Poly     │ │                       │                     │  100V
     └┬─────────────────┘ │                       │                     │        └┬─────────────────┘ │                       │                     │
      │               Drain(D)                Drain(D)                  │         │               Drain(D)                Drain(D)                  │
      │              ┌────┴──────────┐       ┌────┴──────────┐          │         │              ┌────┴──────────┐       ┌────┴──────────┐          │
      │              │ S1: HS SiC-FET│       │ S3: HS SiC-FET│          │         │              │ S5: HS N-MOS  │       │ S7: HS N-MOS  │          │
      │       +----->│ C3M0065090D   │+----->│ C3M0065090D   │          │         │       +----->│ IPT012N08N5   │+----->│ IPT012N08N5   │          │
      │       | Gate │ (900V, 65mΩ)  || Gate │ (900V, 65mΩ)  │          │         │       | Gate │ (80V, 1.2mΩ)  || Gate │ (80V, 1.2mΩ)  │          │
      │       |      └────┬──────────┘|      └────┬──────────┘          │         │       |      └────┬──────────┘|      └────┬──────────┘          │
      │       |     Source│           |     Source│                     │         │       |     Source│           |     Source│                     │
      │       |           │           |           │                     │         │       |           │           |           │                     │
      │       |           +=== NODE A |           +=== NODE B           │         │       |           +=== NODE C |           +=== NODE D           │
      │       |           |   (Leg A) |           |   (Leg B)           │         │       |           |   (Leg C) |           |   (Leg D)           │
      │       |           |           |           |                     │         │       |           |           |           |                     │
      │       |       Drain(D)        |       Drain(D)                  │         │       |       Drain(D)        |       Drain(D)                  │
      │       |      ┌────┴──────────┐|      ┌────┴──────────┐          │         │       |      ┌────┴──────────┐|      ┌────┴──────────┐          │
      │       |      │ S2: LS SiC-FET│|      │ S4: LS SiC-FET│          │         │       |      │ S6: LS N-MOS  │|      │ S8: LS N-MOS  │          │
      │   +---+----->│ C3M0065090D   │+----->│ C3M0065090D   │          │         │   +---+----->│ IPT012N08N5   │+----->│ IPT012N08N5   │          │
      │   |   | Gate └────┬──────────┘| Gate └────┬──────────┘          │         │   |   | Gate └────┬──────────┘| Gate └────┬──────────┘          │
      │   |   |     Source│           |     Source│                     │         │   |   |     Source│           |     Source│                     │
  GND_1 ──┴───┼───────────┴───────────┼───────────┴─────────────────────┴── GND_1│GND_2 ──┴───┼───────────┴───────────┼───────────┴─────────────────────┴── GND_2
          │   │                       │                                           │   │                       │
          │   +---[ ISOLATED GATE DRIVERS: UCC21520 ]<---+                        │   +---[ ISOLATED GATE DRIVERS: UCC21520 ]<---+
          │       (Reinforced 5.7kV Isolation)           │                        │       (High-Current 4A Source / 6A Sink)     │
          │                                              │                        │                                              │
          │   +=== ENERGY TRANSFER INDUCTOR & TRANSFORMER========+                │   +=== DIGITAL CONTROL SYSTEM (TMS320F28379D) ========================+
          │   |                                                  |                │   | - Phase-Shift Modulator: Generates 8 PWM outputs with resolution  |
          └───+---[ L_ext: 18µH / 20A ]───[ Primary N1: 16T ]────+                    |   of 150 picoseconds (High-Resolution PWM: HRPWM)                  |
                  Wurth 7443641800        * (Dot at Node A)      |                    | - Closed-loop digital phase angle shift: -90° <= φ <= +90°        |
                                                                 |                    | - Seamless bidirectional power flow reversal in < 1 millisecond   |
   ==============================================================│====================+====================================================================
                                                                 |                    |
                                          [ Secondary N2: 2T ]───┴────────────────────┘
                                          * (Dot at Node C)
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+V1 (Port 1 Rail)** | High-Voltage Battery / DC Bus | C_1 bank (+), S_1 Drain, S_3 Drain | Stiff 400V DC input/output rail | Polypropylene film capacitors handle high continuous RMS switching current (I_rms ≈ 10 A). |
| **NODE_A / NODE_B** | Primary Half-Bridge Legs A & B | Series Inductor L_ext, Transformer Primary N_1 | High-frequency AC excitation port (v_ac1) | 50% square wave at switching frequency f_s = 100 kHz; amplitude is ± 400 V. |
| **TANK_AC_LOOP** | Node A -> Inductor L_ext Pin 1 | Transformer N_1 Pin 1 -> Node B | High-frequency inductive power transfer branch | Power is transferred by driving current through L_ext; current is quasi-trapezoidal/sinusoidal. |
| **NODE_C / NODE_D** | Secondary Half-Bridge Legs C & D | Transformer Secondary N_2 | Low-voltage AC excitation port (v_ac2) | 50% square wave phase-shifted by angle φ relative to Port 1; amplitude is ± 48 V. |
| **+V2 (Port 2 Rail)** | Low-Voltage Battery / DC Bus | C_2 bank (+), S_5 Drain, S_7 Drain | Stiff 48V DC input/output rail | Very low ESR polymer capacitor bank absorbs high circulating RMS currents (I_rms ≈ 70 A). |
| **GND_1 / GND_2** | Port 1 Ground / Port 2 Ground | Galvanic isolation barrier | Fully isolated system grounds | Galvanic isolation barrier rated for > 3000 V_RMS withstand; creepage >= 8.0 mm. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **S_1 ... S_4** | Primary SiC Power MOSFETs | Wolfspeed C3M0065090D | V_DS = 900 V, I_D = 36 A, R_DS(on) = 65 mΩ, Q_g = 30 nC | Silicon carbide (SiC) provides zero reverse-recovery and ultra-low switching loss at 100 kHz. |
| **S_5 ... S_8** | Secondary LV N-MOSFETs | Infineon IPT012N08N5 | V_DS = 80 V, I_D = 300 A, R_DS(on) = 1.2 mΩ, Q_g = 178 nC | OptiMOS 5 in 8-pin PowerBlock package handles high secondary RMS current (I_rms ≈ 55 A). |
| **L_ext** | Energy Transfer Inductor | Würth Elektronik 7443641800 | L = 18 µH, I_sat = 28 A, I_rms = 22 A, DCR = 4.8 mΩ | Determines maximum bidirectional power transfer: P_max = (n V_1 V_2) / (8 f_s L_ext). |
| **T_1** | Planar Isolation Transformer | Custom E64 Planar Core (3C95) | Turns: 16:2 (8:1), L_m = 1.2 mH, L_lk < 0.8 µH | Multi-layer heavy copper PCB planar windings achieve > 99\% transformer efficiency and low leakage. |
| **C_1 Bank** | Port 1 DC Link Film Caps | KEMET C4AEGBW5300A3FJ | 470 µF, 450 V_DC, Metallized Polypropylene Film | Handles continuous high-frequency triangular ripple current without dielectric breakdown. |
| **C_2 Bank** | Port 2 DC Link Polymer Caps | Panasonic 63SVPF220M | 6 * 220 µF, 63 V, OS-CON Polymer, ESR = 12 mΩ | Paralleled array yields < 2 mΩ net ESR to prevent low-voltage bus voltage ripple. |
| **U_drv1-4** | Isolated Dual Gate Drivers | TI UCC21520DW | 5.7 kV_RMS reinforced isolation, 4 A / 6 A sink/source | High CMTI (> 100 V/ns) prevents false gate triggering during fast SiC switching edges. |
| **U_ctrl** | Central Digital Controller | TI TMS320F28379D | Dual-Core 200MHz C28x DSP, 150ps HRPWM resolution | Controls phase-shift angle φ in real-time based on bus current and voltage demand. |


### 1.1 Core Energy Transfer Mechanism:
1. Both primary and secondary bridges generate high-frequency AC square-wave voltages (v_ac1 and v_ac2) with 50\% duty cycle at frequency f_s (50 kHz ... 200 kHz).
2. Power transfer is **not** controlled by varying duty cycle or frequency; instead, it is governed by the **Phase-Shift Angle (φ)** between the primary AC square wave and the secondary AC square wave across the energy-transfer inductor (L):
   - **Forward Power Flow (P_1 -> 2)**: Primary leads Secondary (φ > 0).
   - **Reverse Power Flow (P_2 -> 1)**: Secondary leads Primary (φ < 0).
   - **Zero Power Flow (P = 0)**: Bridges are in exact phase synchronization (φ = 0).

---

## 2. Mathematical Formulations & Phase-Shift Modulation

```text
                  Single Phase Shift (SPS) Key Waveforms
  v_ac1 ^        +V1
        │   ┌──────────────┐              ┌──────────────┐
        └───┘              └──────────────┘              └───────> Time
                           -V1
  v_ac2 ^               +V2' (Reflected)
        │         ┌──────────────┐              ┌──────────────┐
        └─────────┘              └──────────────┘              ──> Time
            │◄─φ─►│
            Phase Shift Angle
  i_L   ^           I_pk
        │          / \                           / \
        │         /   \                         /   \
     0A ┼────────/─────\───────────────────────/─────\───────────> Time
        │       /       \                     /       \
        │      /         \-I_pk              /         \-I_pk
```

### 2.1 Transferred Power Equation (Single Phase Shift - SPS):
Defining the normalized phase-shift ratio d = φ / π (where -1 <= d <= 1):

```
P = (V_1 * V_2') / (2π f_s L) * φ (1 - |φ| / π) = (V_1 * (n V_2)) / (2 f_s L) * d (1 - |d|)
```
where:
- V_1: DC voltage of Port 1
- V_2' = n * V_2: DC voltage of Port 2 reflected to primary (n = N_1 / N_2)
- L = L_ext + L_leakage: Total series energy-transfer inductance
- f_s: Switching frequency (Hz)

### 2.2 Maximum Transferred Power:
The power parabolic curve peaks at a phase shift of **90° (φ = π/2, or d = 0.5)**:
```
P_max = (V_1 * V_2') / (8 f_s L)
```
*Engineering Design Guideline*: Normal operating power is sized at d_nom ≈ 0.2 ... 0.35 (φ ≈ 36° ... 63°) to reserve dynamic margin and maintain high efficiency.

---

## 3. Zero-Voltage Switching (ZVS) Soft-Switching Boundaries

The DAB topology achieves ultra-high efficiency (> 97.5\%) by operating with **Zero-Voltage Switching (ZVS)** on all 8 switches:
- Before each MOSFET turns on, the circulating inductive current i_L(t) discharges the output capacitance (C_oss) of the incoming switch and charges C_oss of the outgoing switch.
- When V_DS drops to zero, the anti-parallel body diode clamps the switch to zero volts, allowing lossless turn-on (P_sw(on) = 0).

```text
               ZVS Operating Range as a Function of Voltage Ratio (M)
   Phase Shift (d) ^
               0.5 ┼─────────────────────────────────────────────┐
                   │               FULL ZVS REGION               │
                   │           (All 8 switches achieve           │
                   │            Zero-Voltage Switching)          │
                   │                 .─────────.                 │
                   │             .──'           '──.             │
                   │         .──'                   '──.         │
                   │     .──'                           '──.     │
               0.0 ┴────'───────────────────────────────────'────┴───> Voltage Ratio M
                   0.0                 1.0                 2.0        (M = n*V2 / V1)
```

### ZVS Condition Formulations:
Defining the voltage conversion ratio M = (n V_2) / V_1:
1. **Primary Bridge ZVS Condition**:
   ```
d >= (M - 1) / (2 M) (For M > 1)
```
2. **Secondary Bridge ZVS Condition**:
   ```
d >= (1 - M) / 2 (For M < 1)
```
- When M = 1.0 (perfectly matched transformer ratio), **ZVS is maintained down to virtually zero load**!
- When M !=q 1.0 at light loads, inductive energy is insufficient to completely discharge C_oss, causing loss of ZVS and increased switching dissipation.

---

## 4. Advanced Modulation Strategies

To extend the soft-switching ZVS boundary and eliminate reactive circulating currents during light-load operation, advanced multi-variable modulation techniques are employed:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          DAB Modulation Strategies Comparison                     │
├─────────────────────┬───────────────────┬─────────────────────────────────────────┤
│ Modulation Strategy │ Control Degrees   │ Engineering Advantages                  │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Single Phase Shift│ 1 Degree of       │ Simplest control implementation;        │
│ (SPS)**             │ Freedom (φ)  │ high circulating current at light load. │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Extended Phase    │ 2 Degrees         │ Introduces inner duty cycle on primary  │
│ Shift (EPS)**       │ (φ, D_1)     │ bridge; expands ZVS down to 20% load.   │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Dual Phase Shift  │ 2 Degrees         │ Synchronized inner duty cycles          │
│ (DPS)**             │ (φ, D_1=D_2) │ (D_1 = D_2); slashes reactive power.  │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Triple Phase Shift│ 3 Degrees         │ Independent control of φ, D_1, D_2;│
│ (TPS)**             │ (φ, D_1, D_2)│ Global minimum RMS current optimization.│
└─────────────────────┴───────────────────┴─────────────────────────────────────────┘
```

---

## 5. Industrial Design Example: 10 kW EV Fast-Charging DAB Stage

- **Port 1 (DC Bus)**: V_1 = 400 V DC
- **Port 2 (EV Battery)**: V_2 = 300 V ... 450 V DC (Nominal 400 V)
- **Target Power**: P = 10.0 kW
- **Switching Frequency**: f_s = 100 kHz
- **Transformer Ratio**: n = N_1 / N_2 = 1.0
- **Nominal Phase Shift**: d = 0.25 (φ = 45°)

### Energy-Transfer Inductor Sizing (L):
```
L = (V_1 * (n V_2)) / (2 f_s * P) * d(1 - d) = (400 * 400) / (2 * 100000 * 10000) * 0.25(1 - 0.25) = 160000 / (2 * 10^9) * 0.1875 = 15.0 µH
```
*Inductor Realization*: High-frequency low-loss Sendust / Nanocrystalline distributed-gap toroidal inductor carrying 35 A_RMS AC current.
