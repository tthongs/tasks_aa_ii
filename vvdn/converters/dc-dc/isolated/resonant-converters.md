# Isolated Resonant DC-DC Converters: SRC, PRC & LLC Half-Bridge Masterclass

Welcome to the **VVDN Engineering Hub Technical Dossier on Isolated Resonant DC-DC Converters**. Resonant power conversion is the gold standard for high-density, ultra-high-efficiency power systems—including 80 PLUS Titanium server power supplies, telecom rectifiers, electric vehicle (EV) DC-DC converters, and renewable energy interfaces. 

This document explores the mathematical principles of resonant tanks, compares **Series Resonant Converters (SRC)** and **Parallel Resonant Converters (PRC)**, and conducts a deep dive into the industry-dominant **LLC Resonant Half-Bridge Converter**, including First Harmonic Approximation (FHA), gain curves M(f_n, Q, L_n), ZVS/ZCS boundary conditions, and a complete hardware design methodology.

---

## 1. Why Resonant Conversion? Hard vs. Soft Switching

Conventional PWM converters (Forward, Flyback, Full-Bridge) suffer from hard switching: switches turn on and turn off while carrying full voltage and current simultaneously.

```text
                  Hard Switching vs. Soft Switching (ZVS)
   HARD SWITCHING (Turn-On):                 SOFT SWITCHING / ZVS (Turn-On):
      V_DS   I_D                                 V_DS   I_D
       ^      ^                                   ^      ^
       │\    /│                                   │\     │
       │ \  / │  Overlapping Area                 │ \    │   V_DS reaches 0V
       │  \/  │  = Turn-On Energy                 │  \   │   BEFORE I_D rises!
       │  /\  │    Loss (E_on)                    │   \  │   E_on = 0 Joules!
       │ /  \ │                                   │    \_│______
       0───────┴─────────> Time                   0──────┴─────────────> Time
```

### Limitations of Hard-Switched PWM:
1. **Switching Losses**: P_sw = ( E_on + E_off ) * f_s. As switching frequency increases above 100 kHz, switching losses dominate, severely limiting power density.
2. **Capacitive Turn-On Loss**: Energy stored in MOSFET parasitic drain-source capacitance (1 / 2 C_oss V_DS^2) is dissipated internally as heat every turn-on cycle.
3. **Diode Reverse Recovery**: Secondary diodes snapped off at high di/dt suffer reverse-recovery current spikes, inducing ringing and electromagnetic interference (EMI).

### The Resonant Solution:
Resonant converters introduce an LC tank network that shapes the switch voltage or current into smooth sinusoids:
- **Zero-Voltage Switching (ZVS)**: Voltage across the switch drops to zero before gate drive turn-on, eliminating E_on and C_oss losses.
- **Zero-Current Switching (ZCS)**: Current through the switch or rectifier diode drops to zero before turn-off, eliminating turn-off losses and reverse-recovery phenomena.

---

## 2. Resonant Converter Taxonomy: SRC vs. PRC vs. LLC

```text
                               Resonant Converter Topologies
         Series Resonant (SRC)       Parallel Resonant (PRC)         LLC Resonant (LLC)
               Cr     Lr                   Cr     Lr                     Cr     Lr
     +Vin ────[  ]───^^^^──┐     +Vin ────[  ]───^^^^──┬───     +Vin ────[  ]───^^^^──┬───
                           │                           │                              │
                          ( ) Xfmr                    ┌┴┐                            ┌┴┐
                          ( ) Primary                 │ │ Cp                         │ │ Lm (Magnetizing)
                           │                          └┬┘                            └┬┘
                           │                           │                              │
                           │                          ( ) Xfmr                       ( ) Xfmr
                           │                          ( ) Primary                    ( ) Primary
     GND  ─────────────────┴───  GND  ─────────────────┴───     GND  ─────────────────┴───
```

### Comprehensive Comparison:

| Feature / Metric | Series Resonant Converter (SRC) | Parallel Resonant Converter (PRC) | LLC Resonant Converter |
| :--- | :--- | :--- | :--- |
| **Resonant Tank Elements** | L_r, C_r (2 elements) | L_r, C_p (2 elements) | L_r, C_r, L_m (3 elements) |
| **No-Load / Light-Load Regulation** | **Fails**: At no load (R_L -> inf), gain is fixed at 1; frequency must go to inf. | **Good**: Can regulate down to zero load with finite frequency change. | **Excellent**: Regulates seamlessly from full load down to zero load. |
| **Circulating Energy at Light Load** | Minimal (current drops with load). | Extremely high (tank current flows through C_p regardless of load). | Minimal (magnetizing current circulates only enough to guarantee ZVS). |
| **Output Filter** | Capacitive (C_o only). | Inductive (L_o + C_o). | Capacitive (C_o only, no inductor). |
| **Efficiency at Wide Range** | Poor across wide V_IN variations. | Poor at light load. | **Peak Industry Standard** (> 97\%). |

---

## 3. The LLC Resonant Half-Bridge Converter: Architecture & Physics

The **LLC Resonant Converter** utilizes three reactive elements: a series resonant capacitor C_r, a series resonant inductor L_r (often integrated as transformer primary leakage inductance), and the transformer primary magnetizing inductance L_m:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: LLC RESONANT HALF-BRIDGE CONVERTER (400V -> 12V/40A, 500W SERVER PSU)
========================================================================================================================

                  +-----------------[ D_boot: DFLS1100 ]<------+ +VCC_DRV (+12V)
                  |                 [ 100V / 1A Schottky]      |
                  |                                           [R_boot: 2.2Ω]
                  |                                            |
                  |     +-----------[ C_boot: 0.1µF/50V X7R ]--+
                  |     |                                      |
                  |     |   +---[ RESONANT LLC CONTROLLER IC (e.g. UCC256403 / L6599A) ]---+
                  |     |   |                                                              |
                  +-------->| BOOT      [HO] Pin 16 ---[ R_g1: 4.7Ω ]----+                 |
                        |   |                                            |                 |
                        +-->| PHASE/HB  [LO] Pin 11 ---[ R_g2: 4.7Ω ]--+ |                 |
                            |                                          | |                 |
         OPTO_FB ---------->| FB (VCO)  [VCC] Pin 12 <-- +12V          | |                 |
         ISEN_IN ---------->| ISEN      [GND] Pin 10 --> GND_PRI       | |                 |
                            +------------------------------------------|-|-----------------+
                                                                       | |
    +V_BUS (+400V DC Rail) ───────────────┬────────────────────────────|─|───────────────────────┐
        │                                 │                            │ │                       │
       ┌┴─────────────────┐           Drain (D)                        │ │                      ┌┴┐
       │ C_BUS_BULK       │          ┌────┴──────────┐                 │ │                      │ │ C_CER
       │ 330µF / 450V     │          │ Q1: HS N-MOS  │<----------------+ │                      └┬┘ 2x 1µF/630V
       │ Aluminum Elec.   │          │ IPW60R099CP   │                   │                       │   Poly Film
       └┬─────────────────┘          │ (650V, 99mΩ)  │                   │                       │
        │                            └────┬──────────┘                   │                       │
        │                           Source│                              │                       │
        │                                 │                              │                       │
        │                                 +=== HALF-BRIDGE MID (HB)      │                       │
        │                                 |    (0V to +400V Square Wave) │                       │
        │                                 |                              │                       │
        │       +-------------------------+--[ Cr: 24nF / 630V MKP ]     │                       │
        │       |                         |  SERIES RESONANT CAP         │                       │
        │       |                         |  (Low-Loss Polypropylene)    │                       │
        │       |                         |                              │                       │
        │       |                         +--[ Lr: 22µH Resonant Choke ]-+                       │
        │       |                         |  (Integrated Leakage / Ext)  |                       │
        │       |                         |                              |                       │
        │       |                     Drain (D)                          |                       │
        │       |                    ┌────┴──────────┐                   |                       │
        │       |                    │ Q2: LS N-MOS  │<------------------+                       │
        │       |                    │ IPW60R099CP   │                                           │
        │       |                    │ (650V, 99mΩ)  │                                           │
        │       |                    └────┬──────────┘                                           │
        │       |                   Source│                                                      │
        │       |                         +---[ CT1: Resonant Current ]                          │
        │       |                         │   Sense Transformer -> ISEN                          │
        │       |                         │                                                      │
    GND_PRI ────┴─────────────────────────┴──────────────────────────────────────────────────────┴─── GND_PRI
                                          │
                                          +=== TANK EXCITATION NODE
                                          |
                                          ├──[ Lm: 110µH Magnetizing Inductance ]──┐
                                          │  (Integrated Transformer Core Gap)     │
                                          │                                        │
                                          +---[ Transformer Primary Winding Np ]───┤ (Np: 18T)
                                          |   * (Dot at Tank Node)                 |
                                          |                                        |
                                          +----------------------------------------+
                                          |
   =======================================│===================================== ISOLATION BARRIER =================
                                          |
    GND_SEC ──────────────────────────────┼───+─────────────────────────────────────────────────────────┬─── GND_SEC
                                          │   │                                                         │
                                          │   │                        SECONDARY CENTER-TAP             │
                                          │   │                        (Ns1: 1T, Ns2: 1T Cu-Foil)       │
                                          │   │                                   │                     │
                                          │   │                     +-------------+-------------+       │
                                          │   │                     |                           |       │
                                          │   │               SECONDARY WINDING 1         SECONDARY WINDING 2
                                          │   │               (Ns1: 1T Foil)              (Ns2: 1T Foil)│
                                          │   │               * (Dot at SR1 Drain)        |             │
                                          │   │                     |                     * (Dot at Center-Tap)
                                          │   │                 Drain (D)                 |             │
                                          │   │               ┌─────┴──────────┐      Drain (D)         │
                                          │   │               │ Q_SR1: SYNC FET│     ┌────┴──────────┐  │
                                          │   │               │ BSC014N04LS    │     │ Q_SR2: SYNC   │  │
                                          │   │        +----->│ (40V, 1.4mΩ)   │ +-->│ BSC014N04LS   │  │
                                          │   │        | Gate └─────┬──────────┘ |   └────┬──────────┘  │
                                          │   │        |      Source│            |  Source│             │
                                          │   │        |            │            |        │             │
                                          │   │   +----+------------|------------+--------+             │
                                          │   │   | DUAL SYNCHRONOUS RECTIFIER CONTROLLER               │
                                          │   │   | (e.g. MP6922 / TEA1995: Zero-Current Sensing)       │
                                          │   │   +-----------------+-----------------------------------+
                                          │   │                     │
                                          │   │                  GND_SEC
                                          │   │
                                          │   +===================================+=== +VOUT (+12V/40A, 500W)
                                          │                                       │    (Pure Capacitive Filter!)
                                          │                                      ┌┴──────────────────┐
                                          │                                      │ COUT_BULK         │
                                          │                                     ┌┴┐ 6x 470µF/16V    ┌┴┐ COUT_CER
                                          │                                     │ │ Poly (ESR=4mΩ)  │ │ 8x 47µF/16V
                                          │                                     └┬┘                 └┬┘ X7R 1210
                                          │                                      │                   │
                                          │            +VOUT                     │      +VOUT        │
                                          │              │                       │        │          │
                                          │           [ 1kΩ ]                    │     [ R_fb1: 38.3kΩ ]
                                          │              │                       │        │
                                          │     [ Anode: Pin 1 ]                 │        +---> TL431 REF
                                          │     PC817 OPTOCOUPLER                │        │     (V_ref=2.50V)
                                          │     [ Cathode: Pin 2 ]               │     [ R_fb2: 10.0kΩ ]
                                          │              │                       │        │
                                          │              +----[ CATHODE: TL431 ]─+       GND_SEC
                                          │              |    (Precision Shunt)  |        │
                                          │              +----[ ANODE: GND_SEC ]─+        │
                                          │                                               │
    GND_SEC ──────────────────────────────┴───────────────────────────────────────────────┴─── GND_SEC (Return)
```

### 3.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+V_BUS** | PFC 400V Bulk Bus | C_bus (+), Q_1 Drain, Controller V_IN | Stiff DC high-voltage rail | Symmetrical high-frequency MLCC bypass directly at half-bridge drain. |
| **HB (Switch Node)** | Q_1 Source, Q_2 Drain | Resonant Cap C_r Pin 1, Driver PHASE | High-speed ZVS switching midpoint | Swings between 0 V and +400 V at variable frequency (80 kHz ... 200 kHz). |
| **RESONANT_TANK** | Resonant Cap C_r Pin 2 | Series Resonant Choke L_r Pin 1 | High-current AC resonant loop | C_r sees high peak AC voltage (± 600 V_pk); must use low-loss MKP dielectric. |
| **TANK_XFMR** | Resonant Choke L_r Pin 2 | Transformer Primary N_p Pin 1, L_m | Transformer excitation node | Sinusoidal current excitation produces zero EMI harmonics compared to hard-switched PWM. |
| **SR1_GATE / SR2_GATE**| SR Controller OUTA / OUTB | Synchronous Rectifier Q_SR1, Q_SR2 Gates | Ultra-fast sync rect gate signals | Senses V_DS across FET to turn ON when channel conducts and turn OFF at exact zero-crossing (ZCS). |
| **+VOUT** | Transformer Secondary Center-Tap | C_out bank (+), Feedback network, Load (+) | High-efficiency regulated +12V DC rail | **No Output Inductor Needed**: LLC functions as a smooth current source, feeding C_o directly. |
| **GND_SEC** | Sync FETs Q_SR1, Q_SR2 Sources | C_out bank (-), Secondary Return | Secondary high-current power return | Continuous plane pour handling 40A return current. |

### 3.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1, Q_2** | Resonant Half-Bridge FETs | Infineon IPW60R099CP | V_DS = 650 V, I_D = 31 A, R_DS(on) = 99 mΩ, C_oss = 95 pF | Low C_oss allows fast zero-voltage switching transitions with modest magnetizing current I_m. |
| **C_r** | Series Resonant Capacitor | KEMET R76IR4240SE30K | 24 nF, 630 V_DC, Double Metallized Polypropylene | Ultra-low dissipation factor (tan δ < 0.0005); handles continuous 4 A_rms resonant tank current. |
| **L_r** | Series Resonant Inductor | Custom PQ26/20 (3C95) | L_r = 22 µH, I_pk = 4.8 A, DCR = 14 mΩ | High-frequency litz-wire winding minimizes AC resistance from skin and proximity effects. |
| **T_1 (LLC)** | LLC Power Transformer | Custom ETD44 Core (3C95) | Turns: 18:(1+1), L_m = 110 µH, L_k ≈ 4 µH | Precisely gapped center leg controls magnetizing inductance ratio k = L_m / L_r = 5.0. |
| **Q_SR1, Q_SR2** | Synchronous Rectifier FETs | Infineon BSC014N04LS | V_DS = 40 V, I_D = 125 A, R_DS(on) = 1.4 mΩ, Q_g = 35 nC | Superjunction sync FETs in PowerPAK eliminate > 15 W of diode forward conduction loss. |
| **C_out,bulk** | Output Bulk Capacitor | Panasonic 16SEPC470M | 6 * 470 µF, 16 V, Conductive Polymer, ESR = 4 mΩ | Net bank ESR < 0.7 mΩ; absorbs secondary resonant AC ripple current (I_rms ≈ 20 A). |
| **U_1 (Controller)** | LLC Resonant Controller | TI UCC256403DDBR | Variable frequency control (35 kHz ... 1 MHz), soft start, burst mode | Built-in high-voltage startup and hybrid hysteretic control for lightning-fast transient response. |
| **U_2 (SR Driver)** | Dual Smart SR Controller | MPS MP6922GS | V_DS sensing down to -30 mV, t_prop < 20 ns | Prevents shoot-through by ensuring synchronous switches turn OFF cleanly before current reverses. |


### 3.1 Two Characteristic Resonant Frequencies:
1. **Series Resonant Frequency (f_r or f_0)**:
   Determined by the resonant tank L_r and C_r:
   ```
f_r = 1 / (2π sqrt(L_r * C_r))
```
2. **Lower Resonant Frequency (f_m or f_p)**:
   Determined when L_m is liberated from secondary clamping (magnetizing current resonates with C_r):
   ```
f_m = 1 / (2π sqrt((L_r + L_m) * C_r)) = f_r / (sqrt(1 + L_n))
```
   Where L_n = L_m / L_r is the inductance ratio.

---

## 4. First Harmonic Approximation (FHA) & Voltage Gain Formulation

Under **First Harmonic Approximation (FHA)**, the square-wave voltages and currents are modeled by their fundamental sinusoidal Fourier components:

```text
                       LLC Resonant Equivalent AC Circuit (FHA Model)
                     Cr           Lr
          ───o─────[   ]────────^^^^^^───────┬────────────────o───
             +                               │                +
                                            ┌┴┐
            v_ac,in                         │ │ Lm           v_ac,out  (R_ac)
                                            └┬┘
             -                               │                -
          ───o───────────────────────────────┴────────────────o───
```

### 4.1 Equivalent AC Resistance (R_ac):
Reflecting the DC load resistance R_L = V_o / I_o across the secondary rectifier and transformer turns ratio n = N_p / N_s:
```
R_ac = (8 * n^2) / π^2 * R_L
```

### 4.2 Normalized Parameters:
- Normalized switching frequency: f_n = f_s / f_r
- Inductance ratio: L_n = L_m / L_r (typically between 3 ... 8)
- Quality factor: Q = (sqrt(L_r / C_r)) / R_ac = Z_o / R_ac

### 4.3 DC Voltage Gain Formula:
The transfer function of the LLC resonant tank is:
```
M(f_n, Q, L_n) = | v_ac,out / v_ac,in | = 1 / (sqrt([ 1 + 1 / L_n ( 1 - 1 / f_n^2 ) ]^2 + Q^2 ( f_n - 1 / f_n )^2))
```

---

## 5. LLC Operating Regions & Gain Curve Analysis

```text
                        LLC Resonant Converter Gain Curves
         Gain M ^
                │                   Q = 0.2 (Light Load)
            1.6 ┼                 .-'""'-.
                │               .'        '.  Q = 0.5 (Nominal)
            1.4 ┼              /    /\      \
                │             /    /  \      \    Q = 1.0 (Full Load)
            1.2 ┼            /    /    \      '.
                │           /    /      \       \
       Unity 1.0┼──────────/────/────────\───────\──────── Resonance (fn = 1.0)
                │         /    /          \       \
            0.8 ┼        /    /            \       \
                │       /    /              \       \
            0.6 ┼──────'────'────────────────'───────'────
                │     │                  │
                0    f_m                f_r (fn=1.0)        ───> Normalized Frequency (fn)
                │◄── Capacitive ──►│◄─── Inductive ZVS Zone ────►│
                   (FORBIDDEN ZONE)
```

### The Three Operating Modes:

1. **Resonance Operation (f_s = f_r => f_n = 1.0)**:
   - The tank impedance is purely resistive (Z_r = 0).
   - Gain is identically **unity (M = 1.0)** independent of load Q.
   - Primary switches achieve perfect **ZVS turn-on**.
   - Secondary rectifier diodes turn off at zero current (**ZCS**), completely eliminating diode reverse recovery losses!
   - This is the highest efficiency operating point (typically designed for nominal input voltage).

2. **Below Resonance (f_m < f_s < f_r => f_n < 1.0) [Boost Mode]**:
   - Gain M > 1.0. The converter boosts output voltage to compensate for low V_IN (e.g., during line sag or battery discharge).
   - Tank current resonates and falls to the magnetizing current I_m before the half-cycle ends.
   - Secondary diode current terminates naturally to zero during the cycle: **perfect secondary ZCS**.
   - Primary MOSFETs maintain **ZVS turn-on**.

3. **Above Resonance (f_s > f_r => f_n > 1.0) [Buck Mode]**:
   - Gain M < 1.0. The converter steps down output voltage for high V_IN.
   - Primary MOSFETs maintain **ZVS turn-on**.
   - Secondary diode current is continuous and snapped off at switch turn-off: **ZCS is lost on secondary** (reverse-recovery occurs, requiring ultra-fast diodes or Schottky diodes).

4. **Capacitive Region (f_s < f_m) — THE FORBIDDEN ZONE**:
   - Tank current leads switch voltage. Primary switches lose ZVS and suffer **hard turn-on**.
   - Body diodes of the MOSFETs conduct reverse recovery current directly into the incoming switch, causing catastrophic switch shoot-through failure.
   - Modern LLC controller ICs (e.g., UCC25640x, HR1001) integrate **Capacitive Mode Prevention (CMP)** logic to clamp minimum switching frequency above the capacitive threshold.

---

## 6. Step-by-Step LLC Resonant Hardware Design Procedure

### Step 1: Establish Converter Specifications
- Input Voltage: V_IN,nom = 390 V, V_IN,min = 320 V, V_IN,max = 420 V (PFC Rail)
- Output: V_o = 12 V, I_o = 25 A (P_o = 300 W)
- Resonant frequency target: f_r = 100 kHz

### Step 2: Transformer Turns Ratio (n)
Design for unity gain M_nom = 1.0 at nominal input V_IN,nom:
```
n = N_p / N_s = V_IN,nom / (2 * (V_o + V_F)) = 390 V / (2 * (12 V + 0.4 V)) ≈ 15.7 => Select n = 16
```

### Step 3: Calculate Required Minimum and Maximum Gain
```
M_max = (n * (V_o + V_F)) / (V_IN,min / 2) = (16 * 12.4 V) / (320 V / 2) = 198.4 / 160 = 1.24
```
```
M_min = (n * (V_o + V_F)) / (V_IN,max / 2) = (16 * 12.4 V) / (420 V / 2) = 198.4 / 210 = 0.94
```
Add 10\% design margin: M_peak,req = 1.1 * M_max = 1.36.

### Step 4: Select Inductance Ratio (L_n) and Quality Factor (Q)
- An inductance ratio L_n = L_m / L_r = 5 provides an excellent balance between wide voltage regulation and low circulating current.
- From FHA gain curves for L_n = 5 and M_peak = 1.36, choose maximum full-load quality factor:
  ```
Q_max = 0.40
```

### Step 5: Calculate Equivalent Load and Resonant Tank Values
```
R_L = V_o / I_o = 12 V / 25 A = 0.48 Ω
```
```
R_ac = (8 * n^2) / π^2 * R_L = (8 * 16^2) / π^2 * 0.48 = (2048 * 0.48) / 9.8696 ≈ 99.6 Ω
```

1. **Resonant Capacitor (C_r)**:
   ```
C_r = 1 / (2π * f_r * Q * R_ac) = 1 / (2π * 100 000 * 0.40 * 99.6) ≈ 40 nF => Select 39 nF (Polypropylene Film)
```
2. **Resonant Inductor (L_r)**:
   ```
L_r = 1 / ((2π * f_r)^2 * C_r) = 1 / ((2π * 100 000)^2 * 39 * 10^-9) ≈ 65 µH
```
3. **Magnetizing Inductance (L_m)**:
   ```
L_m = L_n * L_r = 5 * 65 µH = 325 µH
```

### Step 6: Verify Primary ZVS Condition During Dead-Time
To guarantee ZVS at switch turn-on, the magnetizing current peak I_m,pk must discharge the two MOSFET output capacitances (2 C_oss) during dead-time t_d:
```
I_m,pk = (n * V_o) / (4 * L_m * f_r) = (16 * 12 V) / (4 * 325 µH * 100 000 Hz) = 192 / 130 ≈ 1.48 A
```
Required dead-time t_d,min:
```
t_d >= (2 * C_oss * V_IN) / I_m,pk = (2 * 150 pF * 400 V) / 1.48 A ≈ 81 ns
```
Setting dead-time t_d = 250 ns ... 350 ns guarantees complete, robust ZVS switching across all line and load variations.

---

## 7. Practical Engineering Summary

1. **Transformer Integration**: Rather than using a separate physical inductor for L_r, wind the transformer with intentional spatial separation or a magnetic shunt between primary and secondary sections to integrate L_r directly as transformer leakage inductance (L_lk = L_r).
2. **Resonant Capacitor Selection**: The resonant capacitor carries full resonant AC current (I_Cr,rms ≈ 2 ... 4 A). Never use ceramic MLCCs (due to DC bias capacitance drop and acoustic microphonics) or polyester film. **Always use High-Current Metalized Polypropylene (MKP) film capacitors**.
3. **Synchronous Rectification (SR)**: On the low-voltage high-current secondary (12 V, 25 A), replace Schottky diodes with low R_DS(on) MOSFETs (< 2 mΩ) driven by specialized resonant SR controllers (e.g., TEA1995, MP6924) sensing drain-source V_DS ringing.
