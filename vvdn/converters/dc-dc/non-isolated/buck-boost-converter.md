# Buck-Boost DC-DC Converters: Inverting vs 4-Switch Non-Inverting Architecture

Welcome to the **VVDN Engineering Hub Technical Dossier on Buck-Boost DC-DC Converters**. When the input DC voltage can be higher, equal to, or lower than the desired regulated output rail—such as automotive battery cranking (6 V ... 28 V to 12 V), lithium-ion battery discharge profiles (2.7 V ... 4.2 V to 3.3 V), or USB Power Delivery (5 V ... 20 V)—the Buck-Boost topology is mandatory.

This guide provides an exhaustive hardware analysis of the classic **Inverting Buck-Boost Converter** and the modern industrial workhorse: the **4-Switch Synchronous Non-Inverting Buck-Boost Converter (FSBB)**.

---

## 1. Classic Inverting Buck-Boost Converter

The classic single-switch Buck-Boost converter produces an output voltage whose polarity is inverted with respect to the input source ground:

```text
========================================================================================
    DETAILED HARDWARE SCHEMATIC: CLASSIC INVERTING BUCK-BOOST CONVERTER (+12V -> -12V/3A)
========================================================================================

    +VIN (+12V DC) ─────────────────────────────────────────────────────────────┐
        │                                                                       │
       [F1: 5A Fuse]                                                            │
        │                                                                       │
       ┌┴─────────────────┐                                                     │
       │ CIN_BULK         │                                                     │
      ┌┴┐ 150µF/35V Poly ┌┴┐ CIN_CER                                            │
      │ │ (Low-ESR 15mΩ) │ │ 2x 10µF/25V X7R                                    │
      └┬┘                └┬┘                                                    │
       │                  │                                                     │
       │                  │   +---[ HIGH-SIDE P-MOSFET / LEVEL-SHIFT DRIVER ]---+
       │                  │   |                                                 |
       │                  │   | Gate Pull-Up: [ R_pullup: 10kΩ ]                |
       │                  │   | Turn-On:      [ R_g: 4.7Ω ]                     |
       │                  │   | Level-Shifter: NPN BJT (MMBT3904) / Optocoupler |
       │                  │   +-------------------------+-----------------------+
       │                  │                             │
       │                  │                       Gate  │
       │                  │                     +-------+
       │                  │                     |
       │                  │                     │ Source (S)
       │                  │                  ┌──┴───────────────┐
       │                  │                  │ Q1: P-MOSFET     │
       │                  │                  │ FDS4685          │
       │                  │                  │ (40V, 27mΩ)      │
       │                  │                  └──┬───────────────┘
       │                  │                     │ Drain (D)
       │                  │                     │
       │                  │                     +=== SWITCHING NODE (SW)
       │                  │                     |    (Swings +12V to -12.5V)
       │                  │                     |
       │                  │     +---------------+---[ R_snub: 3.3Ω / 1W ]
       │                  │     |               |         │
       │                  │     |               |   [ C_snub: 680pF/100V ]
       │                  │     |               |         │
       │                  │     |               |        GND
       │                  │     |               |
       │                  │     |      ENERGY STORAGE INDUCTOR
       │                  │     |   +---[ L1: 22µH / 6.5A Shielded ]---+
       │                  │     |   |   Bourns SRR1260-220M            |
       │                  │     |   |   (DCR = 40mΩ, Isat = 7.0A)      |
       │                  │     |   +-----------------+----------------+
       │                  │     |                     │
       │                  │     |                     │
       │                  │     |                    GND (Positive Reference)
       │                  │     |
       │                  │     +---[ D1: Schottky Diode (Cathode) ]
       │                  │         V30100P (100V / 30A Dual Trench)
       │                  │         [ Anode ]
       │                  │             │
       │                  │             +=== -VOUT (-12V / 3A Regulated)
       │                  │             │
       │                  │            ┌┴──────────────────┐
       │                  │            │ COUT_BULK         │
       │                  │           ┌┴┐ 2x 220µF/25V    ┌┴┐ COUT_CER
       │                  │           │ │ Poly (ESR=14mΩ) │ │ 3x 10µF/25V
       │                  │           └┬┘ (+) to GND      └┬┘ X7R 1210
       │                  │            │ (-) to -VOUT      │
   GND ┴──────────────────┴────────────+───────────────────┴─────────────────── GND (0V Rail)
                                       │
                                       +---[ OP-AMP INVERTING LEVEL-SHIFTER ]---> V_FB (To PWM IC)
                                           TLV9061: Transmits -12V as +1.2V       (V_ref = 1.20V)
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VIN_FILT** | Fuse F_1 Terminal 2 | C_in bank (+), Q_1 Source (Pins 1-3) | Positive input voltage rail | High-side P-channel configuration uses Source at +V_IN. |
| **SW (Switching Node)** | Q_1 Drain (Pins 5-8) | Inductor L_1 Pin 1, Diode D_1 Cathode, Snubber | High-voltage bidirectional swinging node | Maximum voltage stress across Q_1 is V_IN + \|V_o\| = 12 V + 12 V = 24 V. |
| **INDUCTOR_RET** | Inductor L_1 Pin 2 | System GND (0V Common Plane) | Inductor current discharge return | Connects to central GND plane; carries total sum of input and output average currents. |
| **-VOUT (Negative Rail)**| Diode D_1 Anode | C_out Negative terminal, Load (-) | Inverted negative DC output rail | Polarity is inverted: C_out positive terminal must connect to GND, negative terminal to -V_OUT. |
| **V_FB_INV** | Inverting Op-Amp Output | PWM Controller Feedback (FB) Pin | Inverted sense voltage (+1.2 V) | Negative voltage cannot connect directly to standard positive PWM controller; requires op-amp or PNP level-shifter. |
| **GND** | System Ground Return | Inductor L_1 Pin 2, C_in (-), C_out (+) | Reference zero volt plane | Heavy copper pour; serves as positive reference for the output load. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1** | High-Side P-MOSFET | ON Semi FDS4685 | V_DS = -40 V, I_D = -8.2 A, R_DS(on) = 27 mΩ, Q_g = 29 nC | V_DS rating must exceed V_IN + \|V_o\| = 24 V with minimum 40\% safety margin. |
| **D_1** | Inverting Rectifier Diode | Vishay V30100P | V_RRM = 100 V, I_F = 30 A, V_F = 0.52 V, t_rr < 25 ns | High reverse voltage rating required: sees V_IN + \|V_o\| = 24 V plus inductive spike. |
| **L_1** | Power Choke Inductor | Bourns SRR1260-220M | L = 22 µH, I_sat = 7.0 A, I_rms = 4.2 A, DCR = 40 mΩ | Must handle combined input and load currents: I_L,avg = I_in + I_o = 3 A + 3 A = 6 A. |
| **C_in,bulk**| Input Bulk Cap | Panasonic 35SVPF150M | 150 µF, 35 V, OS-CON Polymer, ESR = 15 mΩ | Withstands discontinuous pulsating input current waveforms. |
| **C_out,bulk**| Output Bulk Cap | Panasonic 25SVPF220M | 2 * 220 µF, 25 V, Polymer, ESR = 14 mΩ | **Observe Polarity**: Positive terminal to GND, negative terminal to -V_OUT. |
| **C_out,cer**| Output Ceramic MLCC | Murata GRM32ER71E106K | 3 * 10 µF, 25 V, X7R, 1210 package | Shunts high-frequency discontinuous current pulses delivered by D_1. |
| **U_1 (Level Shift)**| Inverting Sense Op-Amp | TI TLV9061IDBVR | V_DD = 5 V, Rail-to-Rail I/O, GBW = 10 MHz | Inverts and attenuates negative output to positive controller reference (0 ... 1.2 V). |


### 1.1 Operating Mechanism:
1. **Switch ON (0 < t <= D * T_s)**:
   - Q_1 is ON; Diode D_1 is reverse-biased by -V_o and V_IN.
   - Inductor L is connected directly between V_IN and GND. Inductor current ramps up:
     ```
di_L / dt = V_IN / L
```
   - Energy is stored in inductor L. Capacitor C_out independently supplies the load.
2. **Switch OFF (D * T_s < t <= T_s)**:
   - Q_1 turns OFF. The inductor forces node SW negative to maintain continuous current flow.
   - Diode D_1 is forward-biased, pulling current out of the negative output rail through the inductor to GND.
   - Inductor current decays:
     ```
di_L / dt = (-|V_o|) / L
```
   - Output voltage is **strictly negative** with respect to GND.

### 1.2 Transfer Function & Volt-Second Balance:
```
int_0^T_s v_L(t) dt = V_IN * D * T_s + (-|V_o|) * (1 - D) * T_s = 0
```
```
|V_o| = V_IN * D / (1 - D) => V_o = -V_IN * D / (1 - D)
```
- When D < 0.5 => |V_o| < V_IN (Step-Down / Buck Mode)
- When D = 0.5 => |V_o| = V_IN (Unity Gain)
- When D > 0.5 => |V_o| > V_IN (Step-Up / Boost Mode)

### 1.3 Severe Switch Stress:
Both the switch Q_1 and the diode D_1 see a peak reverse voltage equal to the **sum of input and output voltages**:
```
V_stress = V_IN + |V_o|
```
*Engineering Drawback*: The negative output polarity and severe switch voltage stress make the classic topology inconvenient for standard single-rail consumer and automotive electronics.

---

## 2. Four-Switch Synchronous Non-Inverting Buck-Boost (FSBB)

The **4-Switch Buck-Boost (FSBB)** combines a synchronous buck leg and a synchronous boost leg connected via a single central power inductor:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: 4-SWITCH SYNCHRONOUS BUCK-BOOST CONVERTER (6V-36V IN -> 12V/5A OUT)
========================================================================================================================

           +----[ D_boot1: DFLS1100 ]<----+ VCC_DRV (+5V / +7V) +----[ D_boot2: DFLS1100 ]<----+
           |                              |                     |                              |
          ┌┴┐ C_boot1                    ┌┴┐ C_boot2           ┌┴┐ C_boot1                    ┌┴┐ C_boot2
          │ │ 0.1µF/50V                  │ │ 0.1µF/50V         │ │ (Buck Bootstrap)           │ │ (Boost Bootstrap)
          └┬┘                            └┬┘                   └┬┘                            └┬┘
           |                              |                     |                              |
           +---> [BOOT1: Pin 1]           +---------------------+---> [BOOT2: Pin 28]          |
           |     [SW1:   Pin 3]           |                           [SW2:   Pin 26]          |
           |                              |                                                    |
           |   +--------------------------+----------------------------------------------------+
           |   |       CENTRAL 4-SWITCH SYNCHRONOUS BUCK-BOOST CONTROLLER (e.g. LM5176 / LT8390)
           |   |       - HDRV1 (Pin 2)  ---> Gate QA via R_g1 (2.2Ω)
           |   |       - LDRV1 (Pin 4)  ---> Gate QB via R_g2 (1.0Ω)
           |   |       - HDRV2 (Pin 27) ---> Gate QD via R_g4 (2.2Ω)
           |   |       - LDRV2 (Pin 25) ---> Gate QC via R_g3 (1.0Ω)
           |   |       - CSP / CSN      ---> Inductor Current Sense Shunt (R_sense: 5mΩ)
           |   |       - FB             <--- Output Voltage Feedback Divider (R_fb1 / R_fb2)
           |   +--------------------------+----------------------------------------------------+
           |                              |
    +VIN (6V-36V) ────────────────────────┼────────────────────────┐
        │                                 │                        │
       [F1: 15A Fuse]                     │                        │
        │                                 │                        │
       ┌┴─────────────────┐               │                        │
       │ CIN_BULK         │               │                        │
      ┌┴┐ 150µF/50V Poly ┌┴┐ CIN_CER      │                        │
      │ │ (ESR = 18mΩ)   │ │ 2x 10µF/50V  │                        │
      └┬┘                └┬┘ X7R 1210     │                        │
       │                  │               │                        │
       │                  │       Drain   │                        │
       │                  │      ┌────────┴──────┐                 │
       │                  │      │ QA: BUCK HS   │<-- HDRV1        │
       │                  │      │ BSC035N10NS5  │                 │
       │                  │      └────────┬──────┘                 │
       │                  │        Source │                        │
       │                  │               │                        │
       │                  │               +=== SWITCHING NODE 1    │
       │                  │               |    (SW1: Buck Switch)  │
       │                  │               |                        │
       │                  │      Drain    ├──[ R_snub1: 2.2Ω ]     │
       │                  │      ┌────────┴──────┐    │            │
       │                  │      │ QB: BUCK LS   │  [ C_snub1 ]    │
       │                  │      │ BSC035N10NS5  │    │ 1nF/50V    │
       │                  │      └────────┬──────┘   PGND          │
       │                  │        Source │                        │
       │                  │               │                        │
   PGND┴──────────────────┴───────────────┴────────────────────────┼───────────────────────────+
                                                                   │                           │
                               +===================================+===================+       │
                               |   CENTRAL POWER INDUCTOR & CURRENT SENSING            |       │
                               +===================================+===================+       │
                                                                   │                           │
   NODE SW1 ──────[ L1: 10µH / 14A Shielded Choke ]────[ R_sense: 5mΩ ]────+=== NODE SW2       │
                  Wurth 74435561100 (DCR = 8.2mΩ)      Vishay WSL2512       |    (Boost Switch)│
                                                       (Kelvin CSP/CSN)     |                  │
                                                                            │ Drain            │
                                                      +---------------------+──────────┐       │
                                                      │                     │ QC: BOOST│       │
                                                      │                     │ LS N-FET │<-- LDRV2
                                                      │                     │ (35mΩ)   │       │
                                                      │                     └─────┬────┘       │
                                                      │                    Source │            │
                                                      │                           │            │
                                                      │                       PGND┴────────────+
                                                      │
                                                      │ Source
                                                     ┌┴───────────────┐
                                                     │ QD: BOOST HS   │<-- HDRV2
                                                     │ BSC035N10NS5   │
                                                     └┬───────────────┘
                                                      │ Drain
                                                      │
                                                      +=== +VOUT (+12V/5A Regulated)
                                                      │
                                                     ┌┴──────────────────┐
                                                     │ COUT_BULK         │
                                                    ┌┴┐ 220µF/25V Poly  ┌┴┐ COUT_CER
                                                    │ │ (ESR = 12mΩ)    │ │ 4x 22µF/25V
                                                    └┬┘                 └┬┘ X7R 1210
                                                     │                   │
                                                     │      +VOUT        │
                                                     │        │          │
                                                     │     [ R_fb1: 90.9kΩ, 0.1% ]
                                                     │        │
                                                     │        +---> V_FB (To Controller FB Pin)
                                                     │        │     (V_ref = 1.200V)
                                                     │     [ R_fb2: 10.0kΩ, 0.1% ]
                                                     │        │
                                                     │       AGND (Quiet Ground)
                                                     │        │
                                                     │     (Single Star Point)
   PGND (Power Ground Plane) ────────────────────────┴────────+────────────────────────> GND (Return)
```

### 2.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VIN_FILT** | Fuse F_1 Output | C_in bank (+), Q_A Drain (Pins 5-8) | Filtered wide-range input rail (6 V ... 36 V) | Ceramic capacitors C_in,cer must bridge directly to Q_B source ground pad. |
| **SW1 (Buck Node)** | Q_A Source, Q_B Drain | Inductor L_1 Pin 1, Controller SW1, C_boot1 (-) | Pulsating buck switching node | High dv/dt rectangular node; keep surface area small to mitigate capacitive coupling. |
| **INDUCTOR_CS** | Inductor L_1 Pin 2 | Shunt R_sense Terminal 1 | Filtered inter-stage inductor rail | Inductor carries continuous DC current with triangular AC ripple in all modes. |
| **SW2 (Boost Node)** | Shunt R_sense Terminal 2 | Q_C Drain, Q_D Source, Controller SW2, C_boot2 (-) | Pulsating boost switching node | Symmetrical layout with SW1 to ensure matched parasitic loop inductances. |
| **+VOUT** | Q_D Drain (Pins 5-8) | C_out bank (+), Feedback R_fb1, Load (+) | Regulated +12V DC output bus | Low-impedance plane pour; C_out,cer placed directly at Q_D drain and Q_C source. |
| **BOOT1 / BOOT2** | D_boot1/2 Cathodes | Controller BOOT1 / BOOT2 Pins | High-side floating gate supplies | Refreshed whenever low-side switches (Q_B / Q_C) conduct and pull SW nodes to GND. |
| **PGND** | Q_B Source, Q_C Source, Filter caps (-) | Power ground plane | Circulating power stage ground | Solid ground plane; provides high thermal heat-sinking for MOSFET packages. |

### 2.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_A, Q_B** | Buck Leg N-MOSFETs | Infineon BSC035N10NS5 | V_DS = 100 V, I_D = 100 A, R_DS(on) = 3.5 mΩ, Q_g = 28 nC | Low figure-of-merit (R_DS(on) * Q_g) for high efficiency in Buck mode. |
| **Q_C, Q_D** | Boost Leg N-MOSFETs | Infineon BSC035N10NS5 | V_DS = 100 V, I_D = 100 A, R_DS(on) = 3.5 mΩ, Q_g = 28 nC | Symmetrical quad-FET selection simplifies thermal design and inventory management. |
| **L_1** | High-Current Power Choke | Würth Elektronik 74435561100 | L = 10 µH, I_sat = 14 A, I_rms = 11.5 A, DCR = 8.2 mΩ | Flat-wire wound core minimizes skin effect AC copper losses at 300 kHz ... 500 kHz. |
| **R_sense** | Inductor Current Shunt | Vishay WSL2512R0050FEA | 5.0 mΩ, 2.0 W, 1\%, Kelvin 4-Terminal | Ultra-low thermal EMF (< 3 µV/°C) ensures accurate current loop stability. |
| **C_in,bulk** | Input Bulk Capacitor | Panasonic 50SVPF150M | 150 µF, 50 V, OS-CON Polymer, ESR = 18 mΩ | 50 V rating safely absorbs automotive load-dump surges up to 36 V. |
| **C_out,cer** | Output Ceramic MLCC | TDK C3225X7R1E226M | 4 * 22 µF, 25 V, X7R, 1210 package | Provides low output impedance across wide dynamic load range (0.1 A ... 5 A). |
| **U_1 (Controller)** | Synchronous FSBB IC | TI LM5176PWPR | Wide V_IN (3.5 V ... 55 V), integrated 2A drivers | Automatically transitions smoothly between Buck, Buck-Boost, and Boost operating regimes. |


### 2.1 The Three Control Regimes:

To maximize efficiency (> 98\%), modern FSBB controllers (e.g., LM5176, LT8390, TPS55288) do not switch all 4 FETs simultaneously. Instead, they dynamically switch between three operating regions:

```text
               FSBB Operating Modes Across Input Voltage Sweep
      Efficiency
         100% ┼──────────.                 .──────────
              │           '.             .'
          95% ┼             '-----------'
              │              (4-Switch Region)
              0─────────────────────────────────────────> Vin
                  Vin < Vo        Vin ≈ Vo        Vin > Vo
                [Pure Boost]    [Buck-Boost]    [Pure Buck]
```

1. **Pure Buck Mode (V_IN > 1.15 * V_o)**:
   - Q_D is held continuously **ON** (100\% duty cycle).
   - Q_C is held continuously **OFF**.
   - Q_A and Q_B switch as a standard synchronous buck converter.
   - Only 2 switches toggle; switching losses are minimal.
2. **Pure Boost Mode (V_IN < 0.85 * V_o)**:
   - Q_A is held continuously **ON** (100\% duty cycle).
   - Q_B is held continuously **OFF**.
   - Q_C and Q_D switch as a standard synchronous boost converter.
3. **Buck-Boost Mode (0.85 * V_o <= V_IN <= 1.15 * V_o)**:
   - Both legs switch to provide seamless, monotonic output voltage regulation across the transition boundary without control loop instability or output voltage glitching.

---

## 3. Mathematical Formulations & Component Sizing

### 3.1 Inductor Sizing Formula:
The worst-case inductor ripple occurs in Boost mode at minimum input voltage:
```
L >= (V_IN,min^2 * (V_o - V_IN,min)) / (f_s * Δ I_L * V_o^2)
```
Choosing ripple current ratio r = 0.3 ... 0.4 relative to maximum average inductor current:
```
I_L,max = (V_o * I_o,max) / (η * V_IN,min)
```
```
L = (V_IN,min * (V_o - V_IN,min)) / (f_s * (r * I_L,max) * V_o)
```

### 3.2 Output Capacitor Sizing:
In boost and buck-boost modes, output current is discontinuous. C_out must support the load current during switch ON time:
```
C_out >= (I_o,max * D_boost) / (f_s * Δ V_o,allowable)
```

---

## 4. Hardware Engineering Trade-Offs

| Parameter | Inverting Buck-Boost | 4-Switch Synchronous Buck-Boost (FSBB) |
| :--- | :--- | :--- |
| **Output Polarity** | Negative (Inverted) | Positive (Common Ground) |
| **Component Count** | 1 Switch, 1 Diode, 1 Inductor | 4 MOSFETs, 1 Inductor, Dual Drivers |
| **Switch Voltage Stress** | V_IN + |V_o| | max(V_IN, V_o) |
| **Peak Efficiency** | 82\% ... 88\% | 96\% ... 98.5\% |
| **Primary Applications** | Low-cost negative bias rails (Op-Amps, LCDs) | USB-PD (5-20V), Automotive Infotainment, Drone ESCs |
