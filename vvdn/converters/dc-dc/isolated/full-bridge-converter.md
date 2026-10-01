# Isolated Full-Bridge DC-DC Converter: Hard-Switched vs Phase-Shifted ZVS Mechanics

Welcome to the **VVDN Engineering Hub Technical Dossier on the Isolated Full-Bridge DC-DC Converter**. This document delivers an in-depth hardware engineering analysis of the Full-Bridge topology, focusing on the industrial workhorse: the **Phase-Shifted Full-Bridge (PSFB) Zero-Voltage-Switching (ZVS)** converter. It covers bipolar transformer utilization, leading-leg vs. lagging-leg commutation physics, duty-cycle loss ($\Delta D$), secondary diode voltage ringing suppression, and practical design equations for kilowatts-scale power supplies.

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
| **+V_BUS** | PFC Pre-Regulator Bus | $C_{bus}$ (+), $Q_1$ Drain, $Q_3$ Drain | High-voltage 400V DC input rail | Symmetrical high-frequency decoupling film capacitors placed adjacent to each half-bridge leg. |
| **MID_A (Leading Leg)**| $Q_1$ Source, $Q_2$ Drain | Shim Inductor $L_{shim}$ Pin 1 | High-speed ZVS leading leg switching node | Driven by $50\%$ complementary PWM with fixed dead-time ($t_{dead} \approx 200\,\text{ns}$). |
| **MID_B (Lagging Leg)**| $Q_3$ Source, $Q_4$ Drain | Transformer Primary $N_p$ Pin 2 | Phase-shifted lagging leg switching node | Phase-shifted by angle $\phi$ relative to Leg A; achieves ZVS using energy stored in $L_{shim}$. |
| **PRIM_RESONANT** | Shim Inductor $L_{shim}$ Pin 2 | Series DC Blocking Cap $C_b$, Current Transformer CT1 | Primary resonant energy transfer loop | $L_{shim}$ supplements transformer leakage inductance to ensure ZVS down to $20\%$ light load. |
| **SEC_RECT** | SiC Diodes $D_1, D_2$ Common Cathodes | Output Filter Choke $L_o$ Pin 1, Snubber | High-frequency rectified DC pulse train | Operating frequency is $2 f_s = 200\,\text{kHz}$; SiC diodes eliminate reverse-recovery voltage overshoot. |
| **+VOUT** | Output Choke $L_o$ Pin 2 | $C_{out}$ bank (+), Feedback network, Load (+) | High-power regulated +48V DC bus | Power copper plane designed for 20A continuous load current. |
| **GND_SEC** | Transformer Secondary Center-Tap | $C_{out}$ bank (-), Secondary Return | Secondary isolated power ground | Carries total load return current ($20\,\text{A}$). |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **$Q_1 \dots Q_4$** | Primary High-Voltage N-FETs | Infineon IPW60R045CP | $V_{DS} = 650\,\text{V}, I_D = 60\,\text{A}, R_{DS(on)} = 45\,\text{m}\Omega, C_{oss} = 160\,\text{pF}$ | Low $R_{DS(on)}$ and well-defined output capacitance $C_{oss}$ enable complete ZVS discharge during dead-time. |
| **$L_{shim}$** | External Resonant Inductor | Würth Elektronik 7443640850 | $L = 8.5\,\mu\text{H}, I_{sat} = 22\,\text{A}, I_{rms} = 16\,\text{A}, DCR = 3.2\,\text{m}\Omega$ | High-frequency gapped core handles circulating primary reactive energy without thermal runaway. |
| **$C_b$** | DC Blocking Film Cap | Vishay MKP1848520704K2 | $0.22\,\mu\text{F}, 700\,\text{V}_{\text{DC}}, \text{Metallized Polypropylene}$ | Prevents net DC volt-second imbalance from walking the transformer core into saturation. |
| **$T_1$** | Main PSFB Transformer | Custom ETD49 Core (3C95) | Turns: $16:(3+3), L_m = 2.4\,\text{m}\text{H}, L_{lk} = 1.5\,\mu\text{H}$ | Triple-insulated wire, interleaved secondary copper foil for low proximity loss and leakage control. |
| **$D_1, D_2$** | Secondary SiC Diodes | Infineon IDH12G65C6 | $V_{RRM} = 650\,\text{V}, I_F = 12\,\text{A}, Q_c = 17\,\text{nC}, V_F = 1.35\,\text{V}$ | SiC Schottky eliminates diode reverse recovery snap-off, allowing smaller snubbers and higher efficiency. |
| **$L_o$** | Output Filter Inductor | Coilcraft AGP4233-223ME | $L = 22\,\mu\text{H}, I_{sat} = 28\,\text{A}, I_{rms} = 22\,\text{A}, DCR = 3.6\,\text{m}\Omega$ | Heavy edge-wound copper ribbon choke maintains CCM across entire active load spectrum. |
| **$C_{out,bulk}$** | Output Bulk Capacitor | Panasonic 63SVPF220M | $4 \times 220\,\mu\text{F}, 63\,\text{V}, \text{OS-CON Polymer}, ESR = 12\,\text{m}\Omega$ | Low equivalent impedance ($3\,\text{m}\Omega$) absorbs inductor current ripple with $< 25\,\text{mV}$ ripple. |
| **$U_1$ (Controller)** | Phase-Shifted PWM IC | TI UCC28951-Q1 | Advanced ZVS controller with adaptive delay, sync rect drive | Independent programmable dead-time control for leading and lagging legs. |


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
