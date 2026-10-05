# Ćuk DC-DC Converter: Capacitive Energy Transfer & Zero-Ripple Physics

Welcome to the **VVDN Engineering Hub Technical Dossier on the Ćuk DC-DC Converter**. Invented by Dr. Slobodan Ćuk at Caltech, this topology is unique among switched-mode power converters: it uses an intermediate capacitor for energy transfer rather than an inductor's magnetic field, and features **continuous current at both input and output ports**, resulting in exceptionally low electromagnetic interference (EMI).

This document explores the circuit topology, derives the volt-second and charge-balance equations, examines switch stresses, and details the **Coupled-Inductor Zero-Ripple Phenomenon**.

---

## 1. Operating Principle & Ćuk Topology

The **Ćuk Converter** comprises two inductors (L_1, L_2), an active switch (Q_1), a diode (D_1), an energy-transfer coupling capacitor (C_1), and an output filter capacitor (C_o):

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: INVERTING ĆUK DC-DC CONVERTER (+12V -> -12V/3A WITH ZERO-RIPPLE CAPABILITY)
========================================================================================================================

    +VIN (+12V DC) ─────────────────────────────────────────────────────────────┐
        │                                                                       │
       [F1: 5A Fuse]                                                            │
        │                                                                       │
       ┌┴─────────────────┐                                                     │
       │ CIN_BULK         │                                                     │
      ┌┴┐ 150µF/35V Poly ┌┴┐ CIN_CER                                            │
      │ │ (Low-ESR 14mΩ) │ │ 2x 10µF/25V X7R                                    │
      └┬┘                └┬┘                                                    │
       │                  │                                                     │
       │                  │        INPUT CHOKE INDUCTOR                         │
       │                  │    +---[ L1: 33µH / 5.5A Shielded ]---+             │
       │                  │    |   Wurth 7443320330               |             │
       │                  │    |   (DCR = 16mΩ, Isat = 6.2A)      |             │
       │                  │    +----------------------------------+             │
       │                  │                                       │             │
       │                  │                                       +=== NODE SW1 (Switching Node)
       │                  │                                       |    (0V to +24.5V pulse)
       │                  │                                       |
       │                  │              ENERGY TRANSFER CAPACITOR|
       │                  │       +------[ C1: 10µF / 50V X7R ]---+
       │                  │       |      TDK C3225X7R1H106M
       │                  │       |      (Carries high RMS ripple)
       │                  │       |                               |
       │                  │       |      Drain (D)                +---[ R_snub: 3.3Ω / 1W ]
       │                  │       |     ┌┴──────────────┐         |         │
       │                  │       |     │ Q1: N-MOSFET  │         |   [ C_snub: 470pF ]
       │                  │       |     │ BSC040N10NS5  │         |         │
       │                  │       |  +->│ (100V, 4.0mΩ) │         |        PGND
       │                  │       |  |  └┬──────────────┘         |
       │                  │       |  |   │ Source (S)             |
       │                  │       |  |   │                        |
       │                  │       |  |   +---[ CS+ ]              |
       │                  │       |  |   │                        |
       │                  │       |  |  ┌┴┐ R_shunt: 10mΩ / 2W    |
       │                  │       |  |  │ │ Metal Alloy           |
       │                  │       |  |  └┬┘ (Current Sense)       |
       │                  │       |  |   │                        |
       │                  │       |  |  PGND                      |
       │                  │       |  |                            |
       │                  │       |  |  GATE DRIVER INTERFACE     |
       │                  │       |  +--[ R_g: 4.7Ω ]<-- UCC27517 |
       │                  │       |                               |
       │                  │       +=== NODE SW2 (Diode Node)      |
       │                  │       |    (-24.5V to 0V pulse)       |
       │                  │       |                               |
       │                  │       +---[ D1: Schottky Diode ]      |
       │                  │       |   V30100P (100V / 30A)        |
       │                  │       |   [ Cathode to SW2 ]          |
       │                  │       |   [ Anode to PGND ]           |
       │                  │       |         │                     |
       │                  │       |        PGND                   |
       │                  │       |                               |
       │                  │       |        OUTPUT CHOKE INDUCTOR  |
       │                  │       +---[ L2: 33µH / 5.5A Shielded ]+
       │                  │           Wurth 7443320330            |
       │                  │           (DCR = 16mΩ)                |
       │                  │                                       |
       │                  │                                       +=== -VOUT (-12V/3A)
       │                  │                                       │
       │                  │                                      ┌┴──────────────────┐
       │                  │                                      │ COUT_BULK         │
       │                  │                                     ┌┴┐ 2x 220µF/25V    ┌┴┐ COUT_CER
       │                  │                                     │ │ Poly (ESR=12mΩ) │ │ 3x 10µF/25V
       │                  │                                     └┬┘ (+) to PGND     └┬┘ X7R 1210
       │                  │                                      │ (-) to -VOUT      │
   PGND┴──────────────────┴──────────────────────────────────────+───────────────────┴─── PGND (0V Rail)
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VIN_FILT** | Fuse F_1 Output | C_in bank (+), Inductor L_1 Pin 1 | Filtered positive input DC bus | Carries smooth DC current with minimal ripple due to input inductor L_1. |
| **SW1 (Switch Node 1)** | Inductor L_1 Pin 2, Q_1 Drain | Transfer Capacitor C_1 Left Plate, Snubber | High-voltage switching node (0 V ... V_IN + \|V_o\|) | Trace must withstand V_IN + \|V_o\| = 24 V plus inductive spike. |
| **SW2 (Switch Node 2)** | Transfer Capacitor C_1 Right Plate | Diode D_1 Cathode, Inductor L_2 Pin 1 | Negative-swinging switching node | Swings between -(V_IN + \|V_o\|) when Q_1 is ON and 0 V when Q_1 is OFF. |
| **-VOUT (Negative Rail)** | Inductor L_2 Pin 2 | C_out Negative terminal, Load (-) | Continuous-current regulated negative rail | Because L_2 is in series with output, output ripple current is pure triangular and very low. |
| **PGND** | C_in (-), R_shunt (-), Diode D_1 Anode, C_out (+) | System power ground return | Common zero-volt reference | Diode D_1 anode connects directly to PGND; carries continuous freewheeling return current. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1** | Low-Side N-MOSFET | Infineon BSC040N10NS5 | V_DS = 100 V, I_D = 100 A, R_DS(on) = 4.0 mΩ, Q_g = 27 nC | Low ground-referenced driver complexity; V_DS stress equals V_IN + \|V_o\| = 24 V. |
| **D_1** | Catch Schottky Diode | Vishay V30100P | V_RRM = 100 V, I_F = 30 A, V_F = 0.55 V, t_rr < 20 ns | Anode grounded; cathode tied to C_1/L_2. Must handle combined current I_L1 + I_L2. |
| **C_1** | Energy Transfer Capacitor | TDK C3225X7R1H106M | 10 µF, 50 V, X7R Ceramic, 1210 package | **Crucial Component**: Carries full AC load current ripple (I_C1,rms ≈ 4.5 A); must use low-loss MLCC or film. |
| **L_1, L_2** | Coupled / Dual Inductors | Würth Elektronik 7443320330 | 2 * 33 µH, I_sat = 6.2 A, DCR = 16 mΩ | Can be wound on a single shared core to steer ripple to zero on either input or output side! |
| **C_out,bulk** | Output Bulk Capacitor | Panasonic 25SVPF220M | 2 * 220 µF, 25 V, OS-CON Polymer, ESR = 12 mΩ | Positive terminal grounded; negative terminal connected to -V_OUT. |


### 1.1 Conduction Intervals:
1. **Interval 1: Switch OFF (D * T_s < t <= T_s)**:
   - Switch Q_1 is OFF. Diode D_1 is forward-biased.
   - Input inductor L_1 charges coupling capacitor C_1 via diode D_1.
   - Output inductor L_2 delivers stored energy through diode D_1 into output capacitor C_out and the load.
   - The voltage across C_1 in steady state settles to:
     ```
V_C1 = V_IN + |V_o|
```
2. **Interval 2: Switch ON (0 < t <= D * T_s)**:
   - Switch Q_1 turns ON, pulling the left terminal of C_1 to GND (0 V).
   - The right terminal of C_1 drops to -(V_IN + |V_o|), reverse-biasing diode D_1.
   - Energy stored in C_1 is transferred directly into output inductor L_2 and the load.
   - Concurrently, input inductor L_1 draws energy directly from V_IN to GND.

---

## 2. Voltage and Current Waveforms

```text
                          Ćuk Converter Key Waveforms
   i_L1    ^   Continuous Input Current
           │           / \                    / \
           │──────────/   \──────────────────/   \───────────────────> Time
   i_L2    ^   Continuous Output Current
           │           / \                    / \
           │──────────/   \──────────────────/   \───────────────────> Time
   V_Q1    ^
   Vin+|Vo|┼──────────────┐                      ┌──────────────┐
           │              │                      │              │
        0V ┼──────────────┴──────────────────────┴──────────────┴────> Time
           │◄─── D*Ts ───►│◄──── (1-D)*Ts ──────►│
```

---

## 3. Mathematical Formulations & Transfer Function

### 3.1 Voltage Conversion Ratio:
Applying volt-second balance to input inductor L_1:
```
V_IN * D + (V_IN - V_C1) * (1 - D) = 0 => V_C1 = V_IN / (1 - D)
```

Applying volt-second balance to output inductor L_2:
```
(V_C1 - |V_o|) * D + (-|V_o|) * (1 - D) = 0 => V_C1 * D - |V_o| = 0 => |V_o| = D * V_C1
```

Substituting V_C1:
```
|V_o| = V_IN * D / (1 - D) => V_o = -V_IN * D / (1 - D)
```

### 3.2 Component Sizing Equations:
1. **Input Inductor (L_1)**:
   ```
L_1 = (V_IN * D) / (f_s * Δ I_L1)
```
2. **Output Inductor (L_2)**:
   ```
L_2 = (|V_o| * (1 - D)) / (f_s * Δ I_L2)
```
3. **Energy Transfer Capacitor (C_1)**:
   C_1 carries the full load current during switch ON time. To restrict capacitor ripple to Δ V_C1:
   ```
C_1 = (I_o * D) / (f_s * Δ V_C1)
```
4. **Switch & Diode Stresses**:
   Both the MOSFET Q_1 and diode D_1 must withstand the combined rail voltage:
   ```
V_DS,max = V_diode,rev = V_IN + |V_o|
```

---

## 4. The Coupled-Inductor Zero-Ripple Phenomenon

Because both inductors L_1 and L_2 experience identical AC voltage waveforms across their terminals ((V_IN - V_C1) and -|V_o|), they can be **wound onto a single magnetic core**:

```text
                     Coupled-Inductor Ćuk Configuration
                     L1 (Primary)            C1             L2 (Secondary)
   +Vin ─────────────^^^^^^──────┬──────────[  ]─────────┬───^^^^^^─────────┬───> -Vout
                       ││        │                       │     ││           │
                       ││ M      │                       │     ││ M        ┌┴┐
                       ││        │                       │     ││          │ │ Co
   GND  ─────────────────────────┴───────────────────────┴─────────────────┴─── GND
```

### 4.1 Ripple Steering Mechanism:
With mutual inductance M = k sqrt(L_1 L_2) between the two windings:
```
di_L1 / dt = (v_1 * (L_2 - M)) / (L_1 L_2 - M^2), di_L2 / dt = (v_2 * (L_1 - M)) / (L_1 L_2 - M^2)
```
If the turns ratio is selected such that:
```
M = L_2 => k sqrt(L_1 / L_2) = 1 => N_1 / N_2 = 1 / k
```
The AC ripple current in inductor L_2 is **driven identically to zero (Δ i_L2 = 0)**!
All AC switching ripple is "steered" into the input inductor L_1, yielding **completely DC, ripple-free current at the output** without requiring a massive electrolytic capacitor!

---

## 5. Engineering Trade-Offs & Application Domain

| Advantage | Engineering Challenge |
| :--- | :--- |
| **Continuous currents at both input and output** (ultra-low conducted EMI). | Inverted output voltage polarity. |
| **Zero output ripple** achievable via magnetic coupling. | High component count: 2 inductors + 2 capacitors. |
| Non-pulsating currents extend battery and capacitor lifetime. | High voltage stress (V_IN + |V_o|) on semiconductor switches. |
| Ideal for ultra-low noise instrumentation, audio amplifiers, RF PA bias. | Coupling capacitor C_1 carries high AC RMS ripple current (I_C1,rms ≈ I_o sqrt(D)). |
