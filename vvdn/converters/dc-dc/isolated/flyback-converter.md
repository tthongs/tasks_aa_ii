# Isolated Flyback DC-DC Converter: Theory, CCM/DCM Modes & Snubber Design

Welcome to the **VVDN Engineering Hub Technical Dossier on the Flyback DC-DC Converter**. This document delivers an exhaustive hardware engineering, magnetic analysis, and mathematical breakdown of the isolated flyback topology, covering coupled-inductor energy storage, Continuous Conduction Mode (CCM) vs. Discontinuous Conduction Mode (DCM), Quasi-Resonant (QR) valley switching, RCD clamp snubber design, and multi-output cross-regulation.

---

## 1. Operating Principle & Working Mechanics

The **Flyback Converter** is an isolated, buck-boost-derived switched-mode power supply topology. The core magnetic element is **not** an ideal transformer, but a **coupled inductor** with a gapped magnetic core designed specifically to store energy during the switch ON time and release it during the OFF time:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: ISOLATED QUASI-RESONANT FLYBACK CONVERTER (100V-375V DC -> +12V/3A SELV OUT)
========================================================================================================================

    +VBULK (100V-375V DC) ─────────────────┬─────────────────────────────────────────────────────────────┐
        │                                  │                                                             │
       ┌┴─────────────────┐                │          PRIMARY RCD CLAMP SNUBBER                          │
       │ C_BULK           │                │    +-----[ D_snub: US1M (1000V / 1A) ]<-----+               │
       │ 100µF / 450V     │                │    |     (Ultra-Fast Recovery: trr < 75ns)  |               │
       │ Aluminum Elec.   │                │    |                                        |               │
       └┬─────────────────┘                │    +-----[ R_snub: 47kΩ / 3W ]--------------+               │
        │                                  │    |     [ C_snub: 2.2nF / 630V Poly ]------+               │
        │                                  │    |                                                        │
        │                                  +----+=== TRANSFORMER PRIMARY (Np: 48T)                       │
        │                                            |* (Dot at +VBULK)                                  │
        │                                            |                                                   │
        │                                            |                                                   │
        │                                            | (Dot inverted)                                    │
        │                                            +===================================+               │
        │                                                                                │               │
        │                                                                                │ Drain (D)     │
        │                                                                               ┌┴──────────────┐│
        │                                                                               │ Q1: N-MOSFET  ││
        │                                                                               │ IPB80R290P7   ││
        │                                                                        +----->│ (800V, 290mΩ) ││
        │                                                                        | Gate └┬──────────────┘│
        │                                                                        |       │ Source (S)    │
        │      +---[ PWM / QR CONTROLLER (e.g. UCC28740) ]---+                   |       │               │
        │      |                                             |                   |       +---[ CS Filter ]
        │      | GATE (Pin 6) -------[ R_gate: 10Ω ]---------+                   |       │    R_cs: 1kΩ  │
        │      |                                                                 |      ┌┴┐   C_cs: 220pF│
        │      | CS   (Pin 3) <--------------------------------------------------+      │ │ R_sense      │
        │      |                                                                        └┬┘ 0.25Ω / 2W 1%│
        │      | VCC  (Pin 5) <----+                                                     │               │
        │      |                   │                                                  GND_PRI            │
        │      | FB   (Pin 1) <--+ │                                                                     │
        │      |                 │ │                                                                     │
        │      | GND  (Pin 4)    │ │                                                                     │
        │      +--------+--------+-+---------------------------------------------------------------------+
        │               │        │ │
        │            GND_PRI     │ └──[ D_aux: 1N4148 ]<--+ AUXILIARY WINDING (Naux: 7T)
        │                        │                        │* (Provides controller bias VCC = +14V)
        │                        │                       ┌┴┐ C_aux: 10µF/25V
        │                        │                       └┬┘
        │                        │                        │
        │                        │                     GND_PRI
        │                        │
        │                        +---[ Collector (Pin 4) ] OPTOCOUPLER: PC817A
        │                             [ Emitter   (Pin 3) ] ---> GND_PRI
        │
    GND_PRI ─────────────────────────────────────────────────────────────────────────────────────────────
        │
       ┌┴┐ CY1: Safety Y-Capacitor (2.2nF / 400VAC Class Y1: Reinforced Isolation Across Barrier)
       └┬┘
        │
   ============================================= ISOLATION BARRIER (>= 6.4mm Creepage) ===================
        │
    GND_SEC ─────────────────────────────────────────────────────────────────────────────────────────────
        │                                                                                │
        │                                            +===================================+
        │                                            |
        │                                            | TRANSFORMER SECONDARY (Ns: 6T)
        │                                            | (Dot inverted relative to Np)
        │                                            |*
        │                                            +----[ D_sec: V30100P Schottky ]----+
        │                                            |    (100V / 30A Trench)            │
        │                                            |    [ Anode to Ns, Cathode to Out] │
        │                                            |                                   │
        │                                            +---[ R_snub_sec: 4.7Ω / 1W ]       │
        │                                            |         │                         │
        │                                            |   [ C_snub_sec: 1nF / 100V ]      │
        │                                            |         │                         │
        │                                            |      GND_SEC                      │
        │                                            |                                   │
        │                                            |                                   +=== +VOUT (+12V/3A)
        │                                            |                                   │
        │                                            |                                  ┌┴──────────────────┐
        │                                            |                                  │ COUT_BULK         │
        │                                            |                                 ┌┴┐ 2x 470µF/25V    ┌┴┐ COUT_CER
        │                                            |                                 │ │ Poly (ESR=10mΩ) │ │ 2x 22µF/25V
        │                                            |                                 └┬┘                 └┬┘ X7R 1210
        │                                            |                                  │                   │
        │                                            |            +VOUT                 │      +VOUT        │
        │                                            |              │                   │        │          │
        │                                            |           [ 1kΩ ]                │     [ R_fb1: 38.3kΩ ]
        │                                            |              │                   │        │
        │                                            |    [ Anode: Pin 1 ]              │        +---> REF (Pin 1)
        │                                            |    PC817 OPTOCOUPLER             │        │     (V_ref=2.50V)
        │                                            |    [ Cathode: Pin 2 ]            │     [ R_fb2: 10.0kΩ ]
        │                                            |              │                   │        │
        │                                            |              +----[ CATHODE ]----+       GND_SEC
        │                                            |              |    TL431 PRECISION|
        │                                            |              |    SHUNT REGULATOR|
        │                                            |              +----[ ANODE: GND ]─+
        │                                            │                                  │
    GND_SEC ─────────────────────────────────────────┴──────────────────────────────────┴─── GND_SEC (Return)
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VBULK** | Input Bridge Rectifier (+) | C_bulk (+), Transformer Primary Pin 1, RCD Snubber | High-voltage rectified DC input rail | Trace clearance must satisfy IEC 62368-1 high-voltage spacing (>= 2.5 mm). |
| **DRAIN_PRI** | Transformer Primary Pin 2 | Q_1 Drain, Diode D_snub Cathode | Primary switching node (0 V ... 650 V) | Keep copper loop from Primary Pin 2 through D_snub and C_snub extremely short to suppress leakage ringing. |
| **CS_PRI** | Q_1 Source | Sense Resistor R_sense Top Pad, R_cs Filter | Primary peak current sensing | Low-inductance resistor layout; Kelvin sense trace to controller CS comparator pin. |
| **VCC_AUX** | Aux Winding N_aux Pin 2 | Diode D_aux Anode -> C_aux (+), Controller VCC | Controller primary bootstrap bias rail | Delivers steady +14 V DC to controller after initial startup resistor charges C_aux. |
| **OPTO_COL** | PC817 Optocoupler Pin 4 | Controller FB Pin | Isolated closed-loop feedback signal | Modulates controller internal current setpoint; optocoupler emitter connects to GND_PRI. |
| **+VOUT (SELV)**| Diode D_sec Cathode | C_out bank (+), Opto Pullup, Feedback R_fb1 | Regulated +12V SELV isolated DC output rail | Complies with Safety Extra Low Voltage limits (< 60 V DC touchable). |
| **TL431_REF** | Divider R_fb1/R_fb2 Node | TL431 Shunt Regulator Reference (Pin 1) | Output voltage error sense | Precision reference node (2.500 V); TL431 sinks cathode current to drive Opto LED. |
| **GND_PRI / GND_SEC**| Primary GND / Secondary GND | Safety Capacitor C_Y1 bridging barrier | Galvanically isolated ground planes | Minimum 6.4 mm creepage slot milled through PCB laminate beneath optocoupler and transformer. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1** | Primary High-Voltage FET | Infineon IPB80R290P7 | V_DS = 800 V, I_D = 17 A, R_DS(on) = 290 mΩ, Q_g = 23 nC | 800 V rating absorbs V_bulk,max + V_reflect + V_spike = 375 V + 96 V + 150 V = 621 V. |
| **T_1** | Flyback Coupled Inductor | Custom PQ26/20 Core (3C95) | L_p = 220 µH, N_p:N_s:N_aux = 48:6:7, L_lk < 4.0 µH | Gapped core prevents magnetic saturation at I_pk = 2.4 A; triple-insulated wire (TIW) for secondary. |
| **D_snub** | RCD Snubber Diode | Diodes Inc. US1M | V_RRM = 1000 V, I_F = 1 A, t_rr < 75 ns, C_j = 15 pF | Fast recovery prevents reverse charge dumping into C_snub. |
| **R_snub, C_snub**| RCD Snubber Resistor/Cap | Vishay AC03 / Vishay MKP385 | R = 47 kΩ / 3 W, C = 2.2 nF / 630 V Film | Clamps leakage spike below 700 V; dissipates P_snub ≈ 1.8 W at full load. |
| **D_sec** | Secondary Output Rectifier | Vishay V30100P | V_RRM = 100 V, I_F = 30 A, V_F = 0.52 V | Trench MOS barrier Schottky handles peak inverse voltage V_PIV = V_o + V_bulk * (N_s/N_p) = 60 V. |
| **C_out,bulk** | Output Bulk Capacitor | Panasonic 25SVPF470M | 2 * 470 µF, 25 V, OS-CON Polymer, ESR = 10 mΩ | Absorbs large secondary discontinuous triangular current pulses (I_sec,rms ≈ 6.2 A). |
| **U_1 (Opto)** | Safety Optocoupler | Everlight EL817(B) | V_IOTV = 5000 V_RMS, CTR = 130\% ... 260\% | Connects isolated output error amplifier to primary PWM controller across safety barrier. |
| **U_2 (Ref)** | Precision Shunt Reference | TI TL431AQDBZR | V_ref = 2.495 V ± 0.5\%, I_k = 1 mA ... 100 mA | Closes voltage loop with high gain; includes Type-II compensation across Cathode and Ref. |
| **C_Y1** | Safety Y1 Barrier Cap | Murata DE1E3KX222MA4BP01F | 2.2 nF, 400 V_AC, Class Y1 (Reinforced) | Provides low-impedance return path for common-mode displacement currents; minimizes EMI emissions. |


### 1.1 Conduction Cycle Breakdown:
1. **Interval 1: Switch ON (0 < t <= D * T_s)**:
   - Primary switch Q1 turns ON. Input DC voltage V_IN is applied across primary winding N_p.
   - Due to the inverted dot polarity, secondary winding N_s generates a negative potential at the anode of D_sec.
   - Secondary diode D_sec is **reverse-biased**; no current flows to the secondary.
   - Energy is stored in the transformer's core air gap as magnetic flux:
     ```
E_stored = 0.5 * Lp * I_pk^2
```

Where:
- E_stored: Magnetic energy stored in coupled inductor core per switching cycle (J)
- Lp: Primary magnetizing inductance (H)
- I_pk: Peak primary drain current reached at end of switch on-time (A)
   - Primary current ramps up linearly: di_p / dt = V_IN / L_p.
   - The output load current is supplied entirely by the output capacitor bank C_out.
2. **Interval 2: Switch OFF (D * T_s < t <= T_s)**:
   - Q1 turns OFF. Primary current ceases.
   - By Faraday's and Lenz's laws, the collapsing magnetic field reverses the polarity of all windings.
   - Secondary winding potential jumps positive, forward-biasing D_sec.
   - The stored magnetic energy discharges into output capacitor C_out and the load:
     ```
di_s / dt = -(V_OUT + V_F) / L_s
```
   - Primary voltage rings up to V_IN + n(V_OUT + V_F) + V_spike, clamped by the RCD snubber.

---

## 2. Continuous (CCM) vs. Discontinuous (DCM) Conduction Modes

```text
               Flyback Magnetizing Current: CCM vs. DCM Waveforms
      CCM (Continuous Conduction)                     DCM (Discontinuous Conduction)
   Ip,Is ^                                         Ip,Is ^
         │       Secondary Current (Is/n)                │       Secondary Current (Is/n)
         │       ┌──.                                    │       ┌─.
         │      /    \                                   │      /   \
         │     /      \                                  │     /     \
         │    /        \                                 │    /       \
   I_ped ┼───.          '──. I_ped                       │   /         '──. 0A
         │  / Primary       \                            │  / Primary       │ Dead-time (Id = 0)
         │ /  Current (Ip)   \                           │ /  Current (Ip)  │ Resonant Ringing
      0A ┴'───────────────────'───────────> Time      0A ┴'─────────────────'───────.────.─> Time
         │◄── D*Ts ──►◄─(1-D)*Ts─►│                      │◄── D*Ts ──►◄─ D2*Ts ─►◄── D3*Ts ──►│
```

### 2.1 Comparative Analysis:
1. **Continuous Conduction Mode (CCM)**:
   - Magnetizing energy does not fall to zero before the next cycle (I_ped > 0).
   - **Advantages**: Lower peak current (I_pk), lower RMS conduction losses in MOSFET and capacitor, lower output voltage ripple.
   - **Drawbacks**: Slower dynamic response due to **Right-Half-Plane (RHP) Zero** in the control loop; secondary diode experiences hard-switching reverse recovery (Q_rr).
2. **Discontinuous Conduction Mode (DCM)**:
   - Stored energy completely discharges to zero during every cycle (I_ped = 0).
   - **Advantages**: Diode turns off at zero current (**Zero Reverse Recovery**); no RHP zero, enabling wide loop bandwidth and ultra-fast load step response.
   - **Drawbacks**: High peak currents (2* to 3* higher than CCM), higher I_rms resistive losses, larger bulk capacitors needed.
3. **Quasi-Resonant (QR) / Critical Conduction Mode (CrCM)**:
   - Detects the zero-current point and waits for the drain voltage to resonate down to its lowest valley before triggering turn-on, combining DCM advantages with low switching losses.

---

## 3. Mathematical Design Formulations

### 3.1 Voltage Conversion Ratio (CCM):
```
V_OUT = V_IN * (N_s / N_p) * (D / (1 - D))
```

### 3.2 Primary Inductance (L_p) Sizing:
For boundary conduction mode (BCM) between CCM and DCM at minimum input voltage:
```
L_p = (V_IN(min)^2 * D_max^2) / (2 * P_in * f_sw)
```
Primary peak current:
```
I_pk = (2 * P_in) / (V_IN(min) * D_max)
```

### 3.3 Semiconductor Voltage Stress Calculations:
1. **Primary Switch Maximum Voltage Stress (V_DS(max))**:
   ```
V_DS(max) = V_IN(max) + n(V_OUT + V_F) + V_spike
```
   where n = N_p / N_s is the primary-to-secondary turns ratio, and V_spike is the unabsorbed leakage spike (50 V ... 100 V).
2. **Secondary Diode Reverse Voltage Stress (V_rev(sec))**:
   ```
V_rev(sec) = V_OUT + V_IN(max) / n
```

---

## 4. Primary RCD Clamp Snubber Design

During primary switch turn-off, the energy trapped in the transformer's **primary leakage inductance (L_lk)** cannot couple to the secondary. It rings violently with the MOSFET output capacitance (C_oss), threatening overvoltage breakdown:

```text
                        RCD Snubber Clamping Action
             Leakage Inductance (L_lk)
           ───██████────────┬─────────────────────────────┐
                            │                             │
                            ├───[>|] D_snub (UF4007)      │
                            │        │                    │
                            │      ┌─┴─┐                Drain (D)
                            │      │   │ C_snub         ┌───┴───┐
                            │      └─┬─┘                │       │ Q1 MOSFET
                            │        ├───[ R_snub ]──┐  └───┬───┘
                            │        │               │      │ Source (S)
           +Vin DC ─────────┴────────┴───────────────┴──────┴─── GND_PRI
```

### 4.1 Step-by-Step Sizing Equations:
1. **Leakage Energy per Cycle**:
   ```
E_leak = 1 / 2 L_lk * I_pk^2
```
2. **Power Dissipated in Snubber Resistor**:
   ```
P_snub = E_leak * f_sw * (V_clamp / (V_clamp - n(V_OUT + V_F)))
```
3. **Snubber Resistor (R_snub)**:
   ```
R_snub = V_clamp^2 / P_snub
```
4. **Snubber Capacitor (C_snub)** (constraining ripple to Δ V_clamp <= 10\% V_clamp):
   ```
C_snub = V_clamp / (Δ V_clamp * R_snub * f_sw)
```
5. **Snubber Diode Selection**: Must be an **ultrafast recovery diode** (t_rr <= 50 ns, e.g., US1M, ES1J) rated for > 1.2 * V_DS(max).

---

## 5. Multi-Output Flyback Generation & Cross-Regulation

The Flyback topology is uniquely suited for multi-rail auxiliary supplies because adding an isolated DC rail requires merely **one secondary winding, one diode, and one capacitor**:

```text
                  Multi-Output Auxiliary Flyback Configuration
                                            Secondary 1
                                            ┌───[>|]───┬───> +5V Main (Regulated, Opto Feedback)
                                            │        ┌─┴─┐
                                      ┌─────┤        │   │ C1
                                      │     │        └─┬─┘
                   Primary Winding    │     Secondary 2│
  +Vin DC ───[ Np ]───┤               │     ┌───[>|]───┼───> +15V Gate Drive Rail (Cross-Regulated)
                      │               ├─────┤        ┌─┴─┐
                      Q1              │     │        │   │ C2
                      │               │     │        └─┬─┘
                   GND_PRI            │     Secondary 3│
                                      │     ┌───[>|]───┼───> -15V Negative Gate Rail
                                      └─────┤        ┌─┴─┐
                                            │        │   │ C3
                                            └────────┴─┬─┘
                                                    GND_SEC
```

### The Cross-Regulation Challenge:
Only the main output (+5 V) is enclosed within the optocoupler feedback loop. Auxiliary rails (+15 V, -15 V) rely on magnetic coupling. Imperfect winding coupling (leakage flux) causes auxiliary rails to sag under load or spike during light loads.
- **Solution**: Sandwich winding geometry, bifilar auxiliary winding, or post-regulation using linear LDOs.
