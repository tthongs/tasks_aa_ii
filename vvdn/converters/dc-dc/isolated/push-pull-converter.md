# Isolated Push-Pull DC-DC Converter: Topology, Flux Walking & Low-Voltage Design

Welcome to the **VVDN Engineering Hub Technical Dossier on the Push-Pull DC-DC Converter**. This guide provides an exhaustive hardware engineering analysis of the Push-Pull topology, covering its center-tapped primary structure, ground-referenced dual low-side switching, the severe **Transformer Flux Walking** dynamic core saturation hazard, 2 * V_IN switch voltage stress, and component sizing rules for low-voltage battery-fed applications.

---

## 1. Operating Principle & Push-Pull Architecture

The **Push-Pull Converter** utilizes a center-tapped transformer primary winding powered by two ground-referenced switches operated alternately:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: ISOLATED PUSH-PULL DC-DC CONVERTER (24V -> 12V/15A, 180W)
========================================================================================================================

    +VIN (+24V DC Input Rail) ─────────────────────────┬────────────────────────────────────────────────────────┐
        │                                              │                                                        │
       ┌┴─────────────────┐                            │                                                       ┌┴┐
       │ CIN_BULK         │                 +----------┴----------+                                            │ │ CIN_CER
       │ 470µF / 50V      │                 | PRIMARY CENTER-TAP  |                                            └┬┘ 4x 10µF/50V
       │ Low-ESR Poly     │                 +----------+----------+                                             │   X7R 1210
       └┬─────────────────┘                            │                                                        │
        │                       +----------------------+----------------------+                                 │
        │                       |                                             |                                 │
        │                  PRIMARY WINDING 1                             PRIMARY WINDING 2                      │
        │                  (Np1: 6T)                                     (Np2: 6T)                              │
        │                  * (Dot at Center-Tap)                         |                                      │
        │                       |                                        * (Dot at Drain Q2)                    │
        │                       +=== NODE DRAIN_Q1 (SW1)                      +=== NODE DRAIN_Q2 (SW2)          │
        │                       |    (Swings 0V to +48V)                      |    (Swings 0V to +48V)          │
        │                       |                                             |                                 │
        │      +----------------+--[ R_snub1: 4.7Ω / 2W ]                     +--[ R_snub2: 4.7Ω / 2W ]         │
        │      |                |         │                                   |         │                       │
        │      |                |   [ C_snub1: 1nF / 100V ]                   |   [ C_snub2: 1nF / 100V ]       │
        │      |                |         │                                   |         │                       │
        │      |                |      GND_PRI                                |      GND_PRI                    │
        │      |                |                                             |                                 │
        │      |                │ Drain (D)                                   │ Drain (D)                       │
        │      |               ┌┴──────────────┐                             ┌┴──────────────┐                  │
        │      |               │ Q1: N-MOSFET  │                             │ Q2: N-MOSFET  │                  │
        │      |               │ IPP045N10N5   │                             │ IPP045N10N5   │                  │
        │      |        +----->│ (100V, 4.5mΩ) │                      +----->│ (100V, 4.5mΩ) │                  │
        │      |        | Gate └┬──────────────┘                      | Gate └┬──────────────┘                  │
        │      |        |       │ Source (S)                          |       │ Source (S)                      │
        │      |        |       +-------------------+-----------------+       │                                 │
        │      |        |                           │                         │                                 │
        │      |        |                          ┌┴┐ R_shunt: 5.0mΩ / 3W    │                                 │
        │      |        |                          │ │ 1% Metal Strip         │                                 │
        │      |        |                          └┬┘ (Total Primary Current)│                                 │
        │      |        |                           │                         │                                 │
        │      |        |                        GND_PRI                      │                                 │
        │      |        |                                                     │                                 │
        │      |        |   +---[ DUAL LOW-SIDE DRIVER (e.g. UCC27524) ]---+  │                                 │
        │      |        +---| OUTA (Pin 7) -------[ R_g1: 4.7Ω ]           |  │                                 │
        │      |            | OUTB (Pin 5) -------[ R_g2: 4.7Ω ]-----------+--+                                 │
        │      |            | INA / INB <--- Push-Pull PWM (Dead-time >= 150ns)                                 │
        │      |            | VDD = +12V, GND = GND_PRI                                                         │
        │      |            +-----------------------------------------------------------------------------------+
        │      |
    GND_PRI ───┴────────────────────────────────────────────────────────────────────────────────────────────────┴─── GND_PRI
        │
       ┌┴┐ CY1: Safety Y2 Capacitor (2.2nF / 250VAC Across Galvanic Barrier)
       └┬┘
        │
   ============================================= ISOLATION BARRIER =====================================================
        │
    GND_SEC ────────────────────+───────────────────────────────────────────────────────────────────────────────┬─── GND_SEC
        │                       │                                                                               │
        │            SECONDARY CENTER-TAP                                                                       │
        │            (Ns1: 4T, Ns2: 4T)                                                                         │
        │                       │                                                                               │
        │         +-------------+-------------+                                                                 │
        │         |                           |                                                                 │
        │   SECONDARY WINDING 1         SECONDARY WINDING 2                                                     │
        │   (Ns1: 4T)                   (Ns2: 4T)                                                               │
        │   * (Dot at Anode D1)         |                                                                       │
        │         |                     * (Dot at Center-Tap)                                                   │
        │         +---[>|] D1           |                                                                       │
        │             V40100P           +---[>|] D2 (V40100P Schottky)                                          │
        │             [Cathode]             [Cathode]                                                           │
        │                 │                     │                                                               │
        │                 +==========+==========+=== NODE RECT_CATHODE                                          │
        │                            |               (Rectified +16V AC)                                        │
        │                            |                                                                          │
        │                            ├──[ R_snub_sec: 3.3Ω / 2W ]                                               │
        │                            │         │                                                                │
        │                            │   [ C_snub_sec: 1.5nF / 100V ]                                           │
        │                            │         │                                                                │
        │                            │      GND_SEC                                                             │
        │                            │                                                                          │
        │                            +---[ Lo: 10µH / 20A Power Choke ]──+=== +VOUT (+12V/15A)                  │
        │                                Coilcraft AGP4233-103           │                                      │
        │                                (DCR = 2.8mΩ, Isat = 24A)      ┌┴──────────────────┐                   │
        │                                                               │ COUT_BULK         │                   │
        │                                                              ┌┴┐ 4x 330µF/25V    ┌┴┐ COUT_CER         │
        │                                                              │ │ Poly (ESR=6mΩ)  │ │ 6x 22µF/25V      │
        │                                                              └┬┘                 └┬┘ X7R 1210         │
        │                                                               │                   │                   │
    GND_SEC ────────────────────────────────────────────────────────────┴───────────────────┴───────────────────┴─── GND_SEC
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VIN_RAW** | Input Connector Pin 1 | C_in bank (+), Transformer Primary Center-Tap | +24V DC power feed | Center-tap connection carries continuous DC current; requires low-inductance busbar/plane. |
| **DRAIN_Q1 (SW1)**| Transformer Primary N_p1 Pin 1 | Q_1 Drain (Tab), Snubber R_snub1 | Alternating primary switching node | Swings to 2 V_IN = 48 V when Q_2 is ON due to autotransformer action of center-tap. |
| **DRAIN_Q2 (SW2)**| Transformer Primary N_p2 Pin 2 | Q_2 Drain (Tab), Snubber R_snub2 | Alternating primary switching node | Symmetrical layout with SW1 is mandatory to prevent flux walking and transformer core saturation. |
| **RECT_CATHODE** | Diodes D_1, D_2 Common Cathodes | Output Choke L_o Pin 1, Secondary Snubber | Full-wave rectified DC pulse train | Frequency is doubled (2 f_s); ripple frequency is twice the switching frequency. |
| **+VOUT** | Output Choke L_o Pin 2 | C_out bank (+), Feedback network, Load (+) | High-current regulated +12V DC rail | Wide copper plane pour; sized for 15A continuous current. |
| **GND_SEC** | Transformer Secondary Center-Tap | C_out bank (-), Secondary Return | Secondary isolated power ground | Center-tap carries full load return current (15 A). |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1, Q_2** | Primary Low-Side N-FETs | Infineon IPP045N10N5 | V_DS = 100 V, I_D = 120 A, R_DS(on) = 4.5 mΩ, Q_g = 44 nC | Rated for 100 V; must withstand 2 V_IN = 48 V plus inductive leakage spikes. |
| **T_1** | Push-Pull Transformer | Custom ETD39 Core (3C95) | Turns: (6+6):(4+4), L_m = 650 µH, L_lk < 1.2 µH | Primary windings must be bifilar wound to guarantee tightly matched leakage inductance. |
| **R_snub1/2, C_snub1/2** | Primary Drain RC Snubbers | Vishay CRCW1206 / TDK C0G | R = 4.7 Ω / 2 W, C = 1.0 nF / 100 V C0G | Damp primary leakage oscillations that occur when each switch turns OFF. |
| **D_1, D_2** | Secondary Dual Schottky | Vishay V40100P | V_RRM = 100 V, I_F = 40 A, V_F = 0.58 V | Common cathode TO-247 package mounted on secondary heatsink. |
| **L_o** | Output Filter Inductor | Coilcraft AGP4233-103ME | L = 10 µH, I_sat = 24 A, I_rms = 18 A, DCR = 2.8 mΩ | Flat-copper winding handles 15 A DC current with < 1 W winding loss. |
| **C_out,bulk** | Output Bulk Capacitor | Panasonic 25SVPF330M | 4 * 330 µF, 25 V, OS-CON Polymer, ESR = 6 mΩ | Ultra-low equivalent ESR of 1.5 mΩ maintains < 15 mV output ripple. |
| **U_1 (Driver)** | Dual High-Speed Driver | TI UCC27524D | 5 A peak sink/source, dual non-inverting | Symmetrical gate drives ensure matched switch turn-on and turn-off delays. |


### 1.1 Conduction Intervals:
1. **Interval 1: Switch Q1 ON (0 < t <= D * T_s)**:
   - Switch Q_1 turns ON, pulling the bottom terminal of winding N_p1 to ground (0 V).
   - The full DC input V_IN is impressed across N_p1.
   - Secondary winding N_s1 generates a positive voltage, forward-biasing diode D_1 and charging the output filter inductor L_o.
   - **Autotransformer Action on Q2**: The center-tapped primary behaves as an autotransformer. The voltage induced across N_p2 is equal to +V_IN. Therefore, the drain of the non-conducting switch Q_2 swings to:
     ```
V_DS,Q2 = V_IN + V_Np2 = 2 * V_IN
```
2. **Interval 2: Dead-Time (D * T_s < t <= 0.5 T_s)**:
   - Both switches Q_1 and Q_2 are OFF. Primary currents drop to zero.
   - Secondary diodes D_1 and D_2 both conduct simultaneously, freewheeling the output inductor current I_Lo and clamping the secondary to 0 V.
3. **Interval 3: Switch Q2 ON (0.5 T_s < t <= (0.5 + D) * T_s)**:
   - Switch Q_2 turns ON, impressing V_IN across winding N_p2 in the opposite magnetic orientation.
   - Diode D_2 conducts, supplying output current through L_o.
   - The drain of switch Q_1 now sees 2 * V_IN.
4. **Interval 4: Dead-Time ((0.5 + D) * T_s < t <= T_s)**:
   - Both switches OFF; secondary diodes freewheel until cycle repeats.

---

## 2. Voltage and Current Waveforms

```text
                     Push-Pull Key Operating Waveforms
   Gate Q1  ───┐        ┌──────────────┐
               └────────┘              └─────────────────────────────
   Gate Q2  ───────────────────────────┐        ┌──────────────┐
            ───────────────────────────┘        └──────────────┘
               │◄─ D ─►│
   V_DS,Q1  2*Vin ─────────────────────┐        ┌────────────────────
                                       │        │
               ┌────────┐              └────────┘
            ───┘        └────────────────────────────────────────────
   V_DS,Q2                             ┌────────┐
            ───┐        ┌──────────────┘        └────────────────────
               │        │
               └────────┘
   I_Lo         / \                      / \                      / \
            ───/   \────────────────────/   \────────────────────/   \
```

---

## 3. The Fatal Hazard: Transformer Flux Walking

In a Push-Pull converter, there is **no series DC blocking capacitor** because each primary winding is tied directly to the positive DC rail.

```text
                Dynamic Flux Walking Towards Core Saturation
          B (Flux Density) ^
                     +B_sat ┼─────────────────────── Core Saturation Boundary
                            │               .◄────── Progressive Drift (Cycle N)
                            │              /│
                            │             / │
                            │   Cycle 2  /  │
                            │           /   │
                            │  Cycle 1 /    │
                            │         /     │
          -H (Field Force) ─┼────────/──────┼───────────────> +H
                            │       /       │
                            │      /        │
                     -B_sat ┼─────'─────────┴───────
```

### 3.1 The Physical Mechanism of Flux Walking:
If there is the slightest mismatch in:
- Switch turn-on or turn-off propagation delays (Δ t = t_on,Q1 - t_on,Q2)
- Switch on-state resistances (R_DS(on),Q1 != R_DS(on),Q2)
- Winding DC copper resistances (R_cu,p1 != R_cu,p2)

The volt-seconds applied across the transformer during positive and negative half-cycles will not balance:
```
Δ (V * t) = int_0^D T_s V_p1(t) dt - Integral(0.5 T_s to (0.5+D) T_s) V_p2(t) dt != 0
```
This non-zero net DC volt-second integral acts like a DC voltage source applied directly to the magnetizing inductance. Every switching cycle, the operating flux density walks higher along the B-H curve until the core reaches +B_sat. When saturated:
1. Magnetizing inductance collapses: L_m -> 0.
2. The primary switch current spikes exponentially to hundreds of amperes.
3. Catastrophic MOSFET thermal overstress occurs within milliseconds.

### 3.2 Hardware Solutions to Eliminate Flux Walking:
1. **Peak Current-Mode Control (PCMC)**: **Mandatory** for Push-Pull converters. By terminating each switch's on-time when the peak primary switch current hits the control threshold, PCMC enforces identical peak magnetic flux excursions on alternate half-cycles, dynamically stabilizing the flux around zero.
2. **Small Transformer Air Gap**: Inserting a small physical air gap in the ferrite core lowers the effective magnetic permeability µ_r and tilts the B-H loop, dramatically increasing the saturation flux margin at the cost of higher magnetizing current.
3. **Primary RC / RCD Snubbers**: Absorb leakage-inductance voltage spikes that could trigger premature breakdown.

---

## 4. Mathematical Formulations & Component Sizing

### 4.1 Output Voltage Conversion Ratio:
```
V_out = 2 * N_s / N_p * V_IN * D
```
Where D <= 0.45 per switch (total duty ratio 2D < 0.90 to avoid overlap cross-conduction).

### 4.2 Switch Voltage Rating:
Because of transformer autotransformer action and leakage inductance ringing:
```
V_DS,pk = 2 * V_IN,max + V_spike
```
Where V_spike = I_pri,pk * sqrt(L_lk / C_oss).
*Design Rule*: Specify MOSFET drain rating with at least a 30\% safety derating:
```
V_DS,rating >= 2.6 * V_IN,max
```

### 4.3 Primary RMS Current:
```
I_pri,rms = N_s / N_p * I_o * sqrt(D)
```

---

## 5. Engineering Verdict & Application Domain

| Parameter | Push-Pull Assessment |
| :--- | :--- |
| **Driver Simplicity** | **Best in class**: Dual ground-referenced low-side drivers (no high-side level shifters or bootstrap circuits). |
| **Switch Voltage Stress** | **Poor**: 2 * V_IN + spike. Unsuitable for universal AC/DC (400 V rail would require 1000 V+ switches). |
| **Input Voltage Domain** | **Ideal for low-voltage DC rails**: 12 V, 24 V, 48 V battery inputs (automotive, solar off-grid, telecom inverter front-ends). |
| **Transformer Utilization** | **High**: Full two-quadrant excitation (± Δ B). Primary winding requires bifilar center-tapped winding to minimize leakage mismatch. |
| **Control Complexity** | Requires cycle-by-cycle **Peak Current Mode Control** to prevent fatal flux walking. |
