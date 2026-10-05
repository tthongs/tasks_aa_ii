# SEPIC DC-DC Converter: Non-Inverting Buck-Boost with DC Isolation & Sizing

Welcome to the **VVDN Engineering Hub Technical Dossier on the Single-Ended Primary-Inductor Converter (SEPIC)**. The SEPIC topology is widely utilized in automotive electronic control units (ECUs), LED lighting, and battery chargers where the input voltage fluctuates above and below the regulated output rail (e.g., 12 V rail during automotive cold-crank down to 4.5 V and load-dump up to 40 V).

This guide provides a comprehensive hardware analysis of the SEPIC converter, covering its non-inverting operation, series DC blocking capacitor mechanics, inherent short-circuit shutdown capability, coupled-inductor optimization, and component selection criteria.

---

## 1. Operating Principle & SEPIC Topology

The **SEPIC Converter** uses two inductors (L_1, L_2), a ground-referenced active switch (Q_1), a series AC coupling capacitor (C_sep), a diode (D_1), and an output filter capacitor (C_o):

```text
========================================================================================================================
       DETAILED HARDWARE SCHEMATIC: NON-INVERTING SEPIC DC-DC CONVERTER (9V-18V IN -> 12V/4A OUT)
========================================================================================================================

    +VIN (9V-18V DC) ───────────────────────────────────────────────────────────┐
        │                                                                       │
       [F1: 8A Fuse]                                                            │
        │                                                                       │
       ┌┴─────────────────┐                                                     │
       │ CIN_BULK         │                                                     │
      ┌┴┐ 220µF/35V Poly ┌┴┐ CIN_CER                                            │
      │ │ (Low-ESR 12mΩ) │ │ 2x 10µF/35V X7R                                    │
      └┬┘                └┬┘                                                    │
       │                  │                                                     │
       │                  │        PRIMARY INDUCTOR                             │
       │                  │    +---[ L1: 22µH / 6.0A Shielded ]---+             │
       │                  │    |   Coilcraft MSD1278-223          |             │
       │                  │    |   (DCR = 32mΩ, Isat = 6.8A)      |             │
       │                  │    +----------------------------------+             │
       │                  │                                       │             │
       │                  │                                       +=== NODE SW1 (Switching Node)
       │                  │                                       |    (0V to +30V pulse)
       │                  │                                       |
       │                  │              SEPIC DC BLOCKING CAP    |
       │                  │       +------[ C_sep: 10µF / 50V ]----+
       │                  │       |      TDK C3225X7R1H106M       |
       │                  │       |      (Carries high RMS ripple)|
       │                  │       |                               |
       │                  │       |      Drain (D)                +---[ R_snub: 3.3Ω / 1W ]
       │                  │       |     ┌┴──────────────┐         |         │
       │                  │       |     │ Q1: N-MOSFET  │         |   [ C_snub: 470pF ]
       │                  │       |     │ BSC035N10NS5  │         |         │
       │                  │       |  +->│ (100V, 3.5mΩ) │         |        PGND
       │                  │       |  |  └┬──────────────┘
       │                  │       |  |   │ Source (S)
       │                  │       |  |   │
       │                  │       |  |   +---[ CS+ ]
       │                  │       |  |   │
       │                  │       |  |  ┌┴┐ R_shunt: 8.0mΩ / 2W
       │                  │       |  |  │ │ Metal Alloy
       │                  │       |  |  └┬┘ (Current Sense)
       │                  │       |  |   │
       │                  │       |  |  PGND
       │                  │       |  |
       │                  │       |  |  GATE DRIVER INTERFACE
       │                  │       |  +--[ R_g: 4.7Ω ]<-- UCC27517 (Low-Side Driver)
       │                  │       |
       │                  │       +=== NODE SW2 (Diode Anode Node)
       │                  │       |    (Swings -12V to +18V)
       │                  │       |
       │                  │       |        SECONDARY INDUCTOR
       │                  │       +---[ L2: 22µH / 6.0A Shielded ]---+
       │                  │       |   Coilcraft MSD1278-223          |
       │                  │       |   (DCR = 32mΩ)                   |
       │                  │       |                                  │
       │                  │       |                                 PGND (Return)
       │                  │       |
       │                  │       +---[ D1: Schottky Diode (Anode) ]
       │                  │           V30100P (100V / 30A Trench)
       │                  │           [ Cathode ]
       │                  │               │
       │                  │               +=== +VOUT (+12V/4A Regulated)
       │                  │               │
       │                  │              ┌┴──────────────────┐
       │                  │              │ COUT_BULK         │
       │                  │             ┌┴┐ 2x 270µF/25V    ┌┴┐ COUT_CER
       │                  │             │ │ Poly (ESR=10mΩ) │ │ 3x 22µF/25V
       │                  │             └┬┘                 └┬┘ X7R 1210
       │                  │              │                   │
       │                  │              │      +VOUT        │
       │                  │              │        │          │
       │                  │              │     [ R_fb1: 90.9kΩ, 0.1% ]
       │                  │              │        │
       │                  │              │        +---> V_FB (To Controller FB Pin)
       │                  │              │        │     (V_ref = 1.200V)
       │                  │              │     [ R_fb2: 10.0kΩ, 0.1% ]
       │                  │              │        │
       │                  │              │       AGND (Quiet Ground)
       │                  │              │        │
       │                  │              │     (Single Star Point)
   PGND┴──────────────────┴──────────────┴────────+───────────────────┴─── PGND (0V Rail)
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VIN_FILT** | Fuse F_1 Output | C_in bank (+), Inductor L_1 Pin 1 | Filtered positive input DC bus | Carries continuous DC input current with triangular ripple. |
| **SW1 (Switching Node)** | Inductor L_1 Pin 2, Q_1 Drain | Coupling Cap C_sep Pin 1, Snubber | High-voltage pulsating switching node | Maximum switch voltage stress is V_stress = V_IN + V_o = 18 V + 12 V = 30 V. |
| **SW2 (Diode Node)** | Coupling Cap C_sep Pin 2 | Inductor L_2 Pin 1, Diode D_1 Anode | AC-coupled pulsating diode node | Swings between -V_IN when Q_1 is ON and +V_o when Q_1 is OFF. |
| **+VOUT** | Diode D_1 Cathode | C_out bank (+), Feedback R_fb1, Load (+) | Non-inverted regulated +12V DC output rail | Smooth DC output rail; capacitors absorb discontinuous diode current pulses. |
| **PGND** | C_in (-), R_shunt (-), Inductor L_2 Pin 2, C_out (-) | System power ground return | Common zero-volt power ground | Inductor L_2 return connects directly to PGND; solid copper plane recommended. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1** | Low-Side N-MOSFET | Infineon BSC035N10NS5 | V_DS = 100 V, I_D = 100 A, R_DS(on) = 3.5 mΩ, Q_g = 28 nC | Low ground-referenced driver complexity; 100 V rating easily withstands 30 V peak stress. |
| **D_1** | Output Schottky Diode | Vishay V30100P | V_RRM = 100 V, I_F = 30 A, V_F = 0.52 V, t_rr < 20 ns | Must be rated for peak reverse voltage V_R = V_IN + V_o = 30 V plus inductive overshoot. |
| **C_sep** | SEPIC Coupling Capacitor | TDK C3225X7R1H106M | 10 µF, 50 V, X7R Ceramic, 1210 package | **High RMS Current**: I_Csep,rms = I_o * sqrt(V_o / V_IN) ≈ 4.6 A. Must use high-grade MLCCs in parallel. |
| **L_1, L_2** | Coupled / Dual Inductors | Coilcraft MSD1278-223MLD | 2 * 22 µH, I_sat = 6.8 A, DCR = 32 mΩ | Coupled winding on single core cuts component count in half and eliminates inductor AC ripple cancellation issues. |
| **C_out,bulk** | Output Bulk Capacitor | Panasonic 25SVPF270M | 2 * 270 µF, 25 V, OS-CON Polymer, ESR = 10 mΩ | Supplies output current while Q_1 is ON and D_1 is reverse-biased. |


### 1.1 Conduction Intervals:
1. **Interval 1: Switch ON (0 < t <= D * T_s)**:
   - Switch Q_1 is ON, pulling node SW to GND (0 V).
   - Input voltage V_IN is applied across L_1; current i_L1 ramps up:
     ```
di_L1 / dt = V_IN / L_1
```
   - The right side of C_sep is pulled to -V_Csep = -V_IN, reverse-biasing diode D_1.
   - Inductor L_2 is connected in parallel with C_sep; current i_L2 ramps up drawing charge from C_sep:
     ```
di_L2 / dt = V_Csep / L_2 = V_IN / L_2
```
   - The output load is powered solely by capacitor C_out.
2. **Interval 2: Switch OFF (D * T_s < t <= T_s)**:
   - Q_1 turns OFF. The collapsing fields of L_1 and L_2 force node voltages upward.
   - Diode D_1 is forward-biased, conducting current into C_out and the load.
   - Inductor L_1 charges C_sep, while inductor L_2 delivers energy directly to the output.

---

## 2. Voltage and Current Waveforms

```text
                          SEPIC Key Operating Waveforms
   V_SW    ^
   Vin+Vo  ┼──────────────┐                      ┌──────────────
           │              │                      │
        0V ┼──────────────┴──────────────────────┴──────────────> Time
           │◄─── D*Ts ───►│◄──── (1-D)*Ts ──────►│
   i_L1    ^   Continuous Input Current
           │           / \                    / \
           │──────────/   \──────────────────/   \──────────────> Time
   i_D1    ^   Discontinuous Secondary Current
           │              |\                     |\
        0A ┼──────────────┴─\────────────────────┴─\────────────> Time
           │◄── Zero ────►│◄─ Pulsating Current ─►│
```

---

## 3. Mathematical Formulations & Component Sizing

### 3.1 Voltage Conversion Ratio:
Applying volt-second balance across L_1 and L_2:
```
V_out = V_IN * D / (1 - D) => D = V_out / (V_IN + V_out)
```
- Note that unlike the classic buck-boost or Ćuk converter, the **output polarity is positive (non-inverting)** with respect to input ground.

### 3.2 Switch & Diode Voltage Stresses:
During switch turn-off, the voltage across Q_1 is:
```
V_DS,max = V_IN,max + V_out
```
Similarly, the peak reverse voltage across diode D_1 is:
```
V_diode,rev = V_IN,max + V_out
```

### 3.3 Inductor Value Calculations (L_1, L_2):
Selecting ripple ratio r ≈ 0.3 ... 0.4:
```
L_1 = (V_IN,min * D_max) / (f_s * Δ I_L1) = (V_IN,min * D_max) / (f_s * (r * I_IN,max))
```
```
L_2 = (V_IN,min * D_max) / (f_s * Δ I_L2) = (V_IN,min * D_max) / (f_s * (r * I_out,max))
```

### 3.4 Series Coupling Capacitor Sizing (C_sep):
Capacitor C_sep must support continuous AC RMS ripple current:
```
I_Csep,rms = I_out * sqrt(D_max / (1 - D_max))
```
To keep peak-to-peak ripple voltage Δ V_Csep <= 5\% * V_IN:
```
C_sep >= (I_out * D_max) / (f_s * Δ V_Csep)
```
*Engineering Recommendation*: Utilize multi-layer ceramic capacitors (MLCC X7R) or low-ESR film capacitors. Electrolytic capacitors fail due to excessive ESR heating under high AC RMS currents.

---

## 4. Key Advantages: DC Blocking & True Shutdown

```text
               DC Isolation Comparison: Standard Boost vs. SEPIC
   STANDARD BOOST:                               SEPIC:
    Vin ──[ L ]───[>|]─── Vo                      Vin ──[ L1 ]───[ C_sep ]───[>|]─── Vo
     │             │                               │                │          │
   (Direct DC path through diode!                (DC is BLOCKED by series capacitor!
    Short on Vo kills Vin rail!)                  Short on Vo draws ZERO DC current!)
```

1. **True Disconnect in Shutdown**: In a standard Boost converter, when the switch is disabled, V_IN is still directly connected to V_out through the inductor and diode. In a SEPIC, C_sep acts as an open circuit for DC, providing complete output disconnect when Q_1 is turned OFF.
2. **Short-Circuit Protection**: If the output rail is accidentally shorted to ground, C_sep blocks the DC input current, protecting the power supply from thermal destruction.
3. **Low-Side Switching Simplicity**: MOSFET Q_1 is referenced to ground, eliminating high-side level shifters or bootstrap gate-drive circuits.

---

## 5. Coupled-Inductor SEPIC Implementation

Inductors L_1 and L_2 can be wound onto a single magnetic core with 1:1 turns ratio:
- **Reduces footprint by 50\%**: One 1:1 dual inductor (e.g., Coilcraft MSD/MSV series) replaces two individual inductors.
- **Halves Required Inductance**: Because mutual coupling doubles effective inductance (L_eff = L (1+k)), each winding requires only half the inductance for the same ripple current:
  ```
L_1 = L_2 >= (V_IN,min * D_max) / (2 * f_s * Δ I_L)
```
