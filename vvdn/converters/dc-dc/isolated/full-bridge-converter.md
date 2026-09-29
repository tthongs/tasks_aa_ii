# Isolated Full-Bridge DC-DC Converter: Hard-Switched vs Phase-Shifted ZVS Mechanics

Welcome to the **VVDN Engineering Hub Technical Dossier on the Isolated Full-Bridge DC-DC Converter**. This document delivers an in-depth hardware engineering analysis of the Full-Bridge topology, focusing on the industrial workhorse: the **Phase-Shifted Full-Bridge (PSFB) Zero-Voltage-Switching (ZVS)** converter. It covers bipolar transformer utilization, leading-leg vs. lagging-leg commutation physics, duty-cycle loss ($\Delta D$), secondary diode voltage ringing suppression, and practical design equations for kilowatts-scale power supplies.

---

## 1. Operating Principle & Full-Bridge Architecture

The **Full-Bridge DC-DC Converter** employs four primary semiconductor switches configured in an H-bridge configuration across a center-tapped or full-wave secondary stage:

```text
                       Phase-Shifted Full-Bridge (PSFB) Power Stage
   +Vin DC ────┬───────────────────────┬───────────────────────┐
               │                       │                       │
           Drain (D)               Drain (D)                   │
           ┌───┴───┐ Q1 (Leading)  ┌───┴───┐ Q3 (Lagging)     ┌┴┐
           │  S1   │               │  S3   │                  │ │ C_bulk
           └───┬───┘               └───┬───┘                  └┬┘
               │ Source (S)            │ Source (S)            │
               ├─── Leg A (Lead) ┐     ├─── Leg B (Lag) ─┐     │
               │                 │     │                 │     │
           Drain (D)             │ Drain (D)             │     │
           ┌───┴───┐ Q2 (Leading)│ ┌───┴───┐ Q4 (Lagging)│     │
           │  S2   │             │ │  S4   │             │     │
           └───┬───┘             │ └───┬───┘             │     │
               │ Source (S)      │     │ Source (S)      │     │
   GND_PRI ────┴─────────────────┴─────┴─────────────────┴─────┴── GND_PRI
                                 │     │
                                 ├──[ L_lk / L_ext ]───[ Primary Np ]───┐
                                 │  (Resonant/Leakage)       ││         │
                                 │                           ││         │
                                 └───────────────────────────┼──────────┘
                                                             ││
   =================================== ISOLATION BARRIER ===================================
                                                             ││
                                            Secondary        ││
                                            Center-Tap   ┌───[ Ns1 ]───[>|] D1 ──┬───[ Inductor Lo ]──┬───> +Vout
                                            Winding      │   ││                  │                    │
                                                         ├───┼───────────────────┤                   ┌┴┐
                                                         │   ││                  │                   │ │ Co
                                                         └───[ Ns2 ]───[>|] D2 ──┘                   └┬┘
                                                         │                                            │
                                              GND_SEC ───┴────────────────────────────────────────────┴─── GND_SEC
```

### 1.1 Hard-Switched Full-Bridge vs. Phase-Shifted Full-Bridge (PSFB)
- **Hard-Switched Full-Bridge**: Diagonal switch pairs (Q1-Q4 and Q2-Q3) are driven simultaneously via conventional pulse-width modulation (PWM). Turn-on and turn-off occur at high $V_{DS}$ and high $I_D$, leading to severe switching losses ($E_{sw} \propto f_s \cdot V_{in}^2 \cdot I$), preventing operation above $50\,\text{kHz}$.
- **Phase-Shifted Full-Bridge (PSFB)**: Each bridge leg operates at a fixed $\approx 50\%$ duty cycle with a small dead-time. Voltage regulation is achieved by **shifting the phase** of Leg B (Lagging Leg: Q3/Q4) relative to Leg A (Leading Leg: Q1/Q2). The primary leakage inductance ($L_{lk}$) and MOSFET parasitic output capacitances ($C_{oss}$) are utilized to achieve **Zero-Voltage Switching (ZVS)** at all switch transitions.

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
1. **Power Delivery Interval ($Q_1, Q_4$ ON)**: $V_{AB} = +V_{IN}$. Current flows through $Q_1$, $L_{lk}$, primary winding, and $Q_4$. Diode $D_1$ conducts, powering the output load and charging $L_o$.
2. **Leading-Leg Transition ($Q_1 \rightarrow Q_2$ Dead-Time)**: $Q_1$ turns OFF. The reflected output inductor current ($n \cdot I_{Lo}$) quickly charges $C_{oss,Q1}$ to $V_{IN}$ and discharges $C_{oss,Q2}$ to $0\,\text{V}$. The body diode of $Q_2$ clamps to ground, allowing $Q_2$ to turn ON under **ZVS**.
3. **Freewheeling Primary Interval ($Q_2, Q_4$ ON)**: $V_{AB} = 0\,\text{V}$. Primary current circulates through $Q_2$ and $Q_4$. On the secondary, both rectifier diodes $D_1$ and $D_2$ conduct simultaneously, shorting the transformer secondary and freewheeling $I_{Lo}$.
4. **Lagging-Leg Transition ($Q_4 \rightarrow Q_3$ Dead-Time)**: $Q_4$ turns OFF. Because secondary diodes are shorted, **only the energy stored in the primary leakage inductance ($L_{lk}$)** is available to discharge $C_{oss,Q3}$ and charge $C_{oss,Q4}$.
5. **Duty Cycle Loss ($\Delta D$) Interval**: $Q_3$ turns ON under ZVS (if energy was sufficient). $V_{AB} = -V_{IN}$, but secondary diodes remain shorted until the primary current reverses from $+I_{pk}$ to $-I_{pk}$ across $L_{lk}$. During this commutation interval, no energy transfers to the output.
6. **Reverse Power Delivery ($Q_2, Q_3$ ON)**: Primary current reaches $-I_{pk}$, diode $D_1$ reverse-biases, and $D_2$ supplies power to the load.

---

## 3. Mathematical Formulations & Component Derivations

### 3.1 Effective Duty Cycle and Voltage Conversion:
Because of the duty cycle loss ($\Delta D$) during primary current reversal:
$$D_{eff} = D - \Delta D$$
$$\Delta D = \frac{4 \cdot f_s \cdot L_{lk} \cdot I_o}{n \cdot V_{IN}}$$
Where $n = \frac{N_p}{N_s}$ is the primary-to-secondary turns ratio.

The DC output voltage is:
$$V_{out} = 2 \cdot \frac{N_s}{N_p} \cdot V_{IN} \cdot D_{eff} = 2 \cdot \frac{N_s}{N_p} \cdot V_{IN} \cdot \left( D - \frac{4 \cdot f_s \cdot L_{lk} \cdot I_o}{n \cdot V_{IN}} \right)$$

### 3.2 ZVS Energy Criterion (Leading vs. Lagging Leg):
- **Leading Leg Transition**:
  Assisted by both the leakage inductance and the reflected output filter inductance ($L_o$):
  $$\frac{1}{2} (L_{lk} + n^2 L_o) I_{pk}^2 > \frac{4}{3} C_{oss} V_{IN}^2$$
  *Result*: Leading leg achieves ZVS over virtually the entire load range ($10\% \dots 100\%$).

- **Lagging Leg Transition**:
  During the freewheeling state, the secondary is shorted, isolating $L_o$. ZVS relies purely on primary leakage inductance $L_{lk}$:
  $$\frac{1}{2} L_{lk} I_{pk}^2 > \frac{4}{3} C_{oss} V_{IN}^2$$
  *Hardware Consequence*: At light load ($I_{pk}$ low), the energy $\frac{1}{2} L_{lk} I_{pk}^2$ is insufficient to discharge $C_{oss}$, causing the lagging leg to **lose ZVS and suffer hard switching**.

### 3.3 Dead-Time Calculation:
$$t_{dead,lead} \ge \frac{2 \cdot C_{oss} \cdot V_{IN}}{I_{pk,lead}}$$
$$t_{dead,lag} \approx \frac{\pi}{2} \sqrt{L_{lk} \cdot (2 C_{oss})}$$

---

## 4. Hardware Engineering Challenges & Mitigation

| Engineering Challenge | Physical Mechanism | Hardware Mitigation Solution |
| :--- | :--- | :--- |
| **Lagging Leg ZVS Loss at Light Load** | $L_{lk}$ energy drops with $I_{load}^2$; cannot overcome MOSFET $C_{oss}$. | Add an external shim inductor in series with primary, or introduce auxiliary commutating inductors / saturated inductors. |
| **Secondary Diode Voltage Ringing** | Resonance between secondary diode junction capacitance $C_j$ and transformer leakage inductance $L_{lk}$. Ringing voltage can exceed $2 \cdot V_{sec}$. | Install primary auxiliary clamping diodes (clamping to $V_{IN}$ rails), active secondary clamps, or RC snubbers across $D_1, D_2$. |
| **Transformer DC Flux Walking** | Unequal gate drive delays or asymmetric switch $R_{DS(on)}$ create DC voltage offset, saturating the core. | Insert a low-loss polypropylene DC blocking capacitor in series with primary winding, or implement peak current-mode control. |
| **Loss of Effective Duty Cycle ($\Delta D$)** | Increasing $L_{lk}$ expands ZVS range but steals duty cycle, requiring a higher turns ratio and higher secondary voltage stress. | Optimize $L_{lk}$ carefully; utilize planar transformers with controlled leakage and low $C_{oss}$ GaN/SiC FETs. |

---

## 5. Comprehensive Design Example: 3.3 kW Telecom Power Supply

- **Input Voltage**: $380\,\text{V} \dots 420\,\text{V}$ DC (PFC Output, Nominal $400\,\text{V}$)
- **Output Voltage**: $48\,\text{V} \dots 54\,\text{V}$ DC (Nominal $50\,\text{V}$ at $66\,\text{A}$)
- **Switching Frequency**: $100\,\text{kHz}$
- **Turns Ratio Selection ($n = N_p / N_s$)**:
  $$D_{max} = 0.42, \quad \Delta D_{est} = 0.05 \implies D_{eff} = 0.37$$
  $$n \le \frac{2 \cdot V_{in,min} \cdot D_{eff}}{V_o + V_{drop}} = \frac{2 \cdot 380\,\text{V} \cdot 0.37}{50.5\,\text{V}} \approx 5.56 \implies \text{Select } N_p = 16, N_s = 3 \quad (n = 5.33)$$
- **Leakage Inductor Sizing**:
  $$L_{lk} \approx \frac{\Delta D \cdot n \cdot V_{IN}}{4 \cdot f_s \cdot I_o} = \frac{0.05 \cdot 5.33 \cdot 400}{4 \cdot 100\,000 \cdot 66} \approx 4.0\,\mu\text{H}$$
- **Primary Switch Selection**:
  $650\,\text{V}$ Superjunction MOSFETs with ultra-low $C_{oss}$ (e.g., $C_{o(er)} \approx 120\,\text{pF}$) or $650\,\text{V}$ GaN HEMTs.
