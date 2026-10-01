# Dual Active Bridge (DAB) DC-DC Converter: Bidirectional Physics, Modulation & ZVS

Welcome to the **VVDN Engineering Hub Technical Dossier on the Dual Active Bridge (DAB) Converter**. This guide provides an advanced mathematical and hardware analysis of the DAB topology—the premier isolated bidirectional DC-DC architecture for Electric Vehicle (EV) onboard chargers, Vehicle-to-Grid (V2G) systems, battery energy storage systems (BESS), and solid-state transformers (SST).

---

## 1. Operating Principle & Bidirectional Architecture

The **Dual Active Bridge (DAB)** converter comprises two active full-bridge (H-bridge) switching stages coupled across a high-frequency isolation transformer with an energy-transfer power inductance ($L$):

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
| **+V1 (Port 1 Rail)** | High-Voltage Battery / DC Bus | $C_{1}$ bank (+), $S_1$ Drain, $S_3$ Drain | Stiff 400V DC input/output rail | Polypropylene film capacitors handle high continuous RMS switching current ($I_{rms} \approx 10\,\text{A}$). |
| **NODE_A / NODE_B** | Primary Half-Bridge Legs A & B | Series Inductor $L_{ext}$, Transformer Primary $N_1$ | High-frequency AC excitation port ($v_{ac1}$) | 50% square wave at switching frequency $f_s = 100\,\text{kHz}$; amplitude is $\pm 400\,\text{V}$. |
| **TANK_AC_LOOP** | Node A -> Inductor $L_{ext}$ Pin 1 | Transformer $N_1$ Pin 1 -> Node B | High-frequency inductive power transfer branch | Power is transferred by driving current through $L_{ext}$; current is quasi-trapezoidal/sinusoidal. |
| **NODE_C / NODE_D** | Secondary Half-Bridge Legs C & D | Transformer Secondary $N_2$ | Low-voltage AC excitation port ($v_{ac2}$) | 50% square wave phase-shifted by angle $\phi$ relative to Port 1; amplitude is $\pm 48\,\text{V}$. |
| **+V2 (Port 2 Rail)** | Low-Voltage Battery / DC Bus | $C_{2}$ bank (+), $S_5$ Drain, $S_7$ Drain | Stiff 48V DC input/output rail | Very low ESR polymer capacitor bank absorbs high circulating RMS currents ($I_{rms} \approx 70\,\text{A}$). |
| **GND_1 / GND_2** | Port 1 Ground / Port 2 Ground | Galvanic isolation barrier | Fully isolated system grounds | Galvanic isolation barrier rated for $> 3000\,\text{V}_{RMS}$ withstand; creepage $\ge 8.0\,\text{mm}$. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **$S_1 \dots S_4$** | Primary SiC Power MOSFETs | Wolfspeed C3M0065090D | $V_{DS} = 900\,\text{V}, I_D = 36\,\text{A}, R_{DS(on)} = 65\,\text{m}\Omega, Q_g = 30\,\text{nC}$ | Silicon carbide (SiC) provides zero reverse-recovery and ultra-low switching loss at $100\,\text{kHz}$. |
| **$S_5 \dots S_8$** | Secondary LV N-MOSFETs | Infineon IPT012N08N5 | $V_{DS} = 80\,\text{V}, I_D = 300\,\text{A}, R_{DS(on)} = 1.2\,\text{m}\Omega, Q_g = 178\,\text{nC}$ | OptiMOS 5 in 8-pin PowerBlock package handles high secondary RMS current ($I_{rms} \approx 55\,\text{A}$). |
| **$L_{ext}$** | Energy Transfer Inductor | Würth Elektronik 7443641800 | $L = 18\,\mu\text{H}, I_{sat} = 28\,\text{A}, I_{rms} = 22\,\text{A}, DCR = 4.8\,\text{m}\Omega$ | Determines maximum bidirectional power transfer: $P_{max} = \frac{n V_1 V_2}{8 f_s L_{ext}}$. |
| **$T_1$** | Planar Isolation Transformer | Custom E64 Planar Core (3C95) | Turns: $16:2 (8:1), L_m = 1.2\,\text{m}\text{H}, L_{lk} < 0.8\,\mu\text{H}$ | Multi-layer heavy copper PCB planar windings achieve $> 99\%$ transformer efficiency and low leakage. |
| **$C_1$ Bank** | Port 1 DC Link Film Caps | KEMET C4AEGBW5300A3FJ | $470\,\mu\text{F}, 450\,\text{V}_{\text{DC}}, \text{Metallized Polypropylene Film}$ | Handles continuous high-frequency triangular ripple current without dielectric breakdown. |
| **$C_2$ Bank** | Port 2 DC Link Polymer Caps | Panasonic 63SVPF220M | $6 \times 220\,\mu\text{F}, 63\,\text{V}, \text{OS-CON Polymer}, ESR = 12\,\text{m}\Omega$ | Paralleled array yields $< 2\,\text{m}\Omega$ net ESR to prevent low-voltage bus voltage ripple. |
| **$U_{drv1-4}$** | Isolated Dual Gate Drivers | TI UCC21520DW | $5.7\,\text{kV}_{RMS}$ reinforced isolation, $4\,\text{A} / 6\,\text{A}$ sink/source | High CMTI ($> 100\,\text{V/ns}$) prevents false gate triggering during fast SiC switching edges. |
| **$U_{ctrl}$** | Central Digital Controller | TI TMS320F28379D | Dual-Core 200MHz C28x DSP, 150ps HRPWM resolution | Controls phase-shift angle $\phi$ in real-time based on bus current and voltage demand. |


### 1.1 Core Energy Transfer Mechanism:
1. Both primary and secondary bridges generate high-frequency AC square-wave voltages ($v_{ac1}$ and $v_{ac2}$) with $50\%$ duty cycle at frequency $f_s$ ($50\,\text{kHz} \dots 200\,\text{kHz}$).
2. Power transfer is **not** controlled by varying duty cycle or frequency; instead, it is governed by the **Phase-Shift Angle ($\phi$)** between the primary AC square wave and the secondary AC square wave across the energy-transfer inductor ($L$):
   - **Forward Power Flow ($P_{1 \rightarrow 2}$)**: Primary leads Secondary ($\phi > 0$).
   - **Reverse Power Flow ($P_{2 \rightarrow 1}$)**: Secondary leads Primary ($\phi < 0$).
   - **Zero Power Flow ($P = 0$)**: Bridges are in exact phase synchronization ($\phi = 0$).

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
Defining the normalized phase-shift ratio $d = \frac{\phi}{\pi}$ (where $-1 \le d \le 1$):

$$P = \frac{V_1 \cdot V_2'}{2\pi f_s L} \cdot \phi \left(1 - \frac{|\phi|}{\pi}\right) = \frac{V_1 \cdot (n V_2)}{2 f_s L} \cdot d (1 - |d|)$$
where:
- $V_1$: DC voltage of Port 1
- $V_2' = n \cdot V_2$: DC voltage of Port 2 reflected to primary ($n = N_1 / N_2$)
- $L = L_{ext} + L_{leakage}$: Total series energy-transfer inductance
- $f_s$: Switching frequency ($\text{Hz}$)

### 2.2 Maximum Transferred Power:
The power parabolic curve peaks at a phase shift of **$90^\circ$ ($\phi = \pi/2$, or $d = 0.5$)**:
$$P_{max} = \frac{V_1 \cdot V_2'}{8 f_s L}$$
*Engineering Design Guideline*: Normal operating power is sized at $d_{nom} \approx 0.2 \dots 0.35$ ($\phi \approx 36^\circ \dots 63^\circ$) to reserve dynamic margin and maintain high efficiency.

---

## 3. Zero-Voltage Switching (ZVS) Soft-Switching Boundaries

The DAB topology achieves ultra-high efficiency ($> 97.5\%$) by operating with **Zero-Voltage Switching (ZVS)** on all 8 switches:
- Before each MOSFET turns on, the circulating inductive current $i_L(t)$ discharges the output capacitance ($C_{oss}$) of the incoming switch and charges $C_{oss}$ of the outgoing switch.
- When $V_{DS}$ drops to zero, the anti-parallel body diode clamps the switch to zero volts, allowing lossless turn-on ($P_{sw(on)} = 0$).

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
Defining the voltage conversion ratio $M = \frac{n V_2}{V_1}$:
1. **Primary Bridge ZVS Condition**:
   $$d \ge \frac{M - 1}{2 M} \quad (\text{For } M > 1)$$
2. **Secondary Bridge ZVS Condition**:
   $$d \ge \frac{1 - M}{2} \quad (\text{For } M < 1)$$
- When $M = 1.0$ (perfectly matched transformer ratio), **ZVS is maintained down to virtually zero load**!
- When $M \neq 1.0$ at light loads, inductive energy is insufficient to completely discharge $C_{oss}$, causing loss of ZVS and increased switching dissipation.

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
│ (SPS)**             │ Freedom ($\phi$)  │ high circulating current at light load. │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Extended Phase    │ 2 Degrees         │ Introduces inner duty cycle on primary  │
│ Shift (EPS)**       │ ($\phi, D_1$)     │ bridge; expands ZVS down to 20% load.   │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Dual Phase Shift  │ 2 Degrees         │ Synchronized inner duty cycles          │
│ (DPS)**             │ ($\phi, D_1=D_2$) │ ($D_1 = D_2$); slashes reactive power.  │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Triple Phase Shift│ 3 Degrees         │ Independent control of $\phi, D_1, D_2$;│
│ (TPS)**             │ ($\phi, D_1, D_2$)│ Global minimum RMS current optimization.│
└─────────────────────┴───────────────────┴─────────────────────────────────────────┘
```

---

## 5. Industrial Design Example: 10 kW EV Fast-Charging DAB Stage

- **Port 1 (DC Bus)**: $V_1 = 400\,\text{V}$ DC
- **Port 2 (EV Battery)**: $V_2 = 300\,\text{V} \dots 450\,\text{V}$ DC (Nominal $400\,\text{V}$)
- **Target Power**: $P = 10.0\,\text{kW}$
- **Switching Frequency**: $f_s = 100\,\text{kHz}$
- **Transformer Ratio**: $n = N_1 / N_2 = 1.0$
- **Nominal Phase Shift**: $d = 0.25$ ($\phi = 45^\circ$)

### Energy-Transfer Inductor Sizing ($L$):
$$L = \frac{V_1 \cdot (n V_2)}{2 f_s \cdot P} \cdot d(1 - d) = \frac{400 \times 400}{2 \cdot 100000 \cdot 10000} \cdot 0.25(1 - 0.25) = \frac{160000}{2 \times 10^9} \cdot 0.1875 = \mathbf{15.0\,\mu\text{H}}$$
*Inductor Realization*: High-frequency low-loss Sendust / Nanocrystalline distributed-gap toroidal inductor carrying $35\,\text{A}_{\text{RMS}}$ AC current.
