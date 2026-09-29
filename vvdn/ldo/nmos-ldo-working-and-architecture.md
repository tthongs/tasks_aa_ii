# NMOS LDO: Working Mechanism, Gate Drive & Architecture

## 1. Architectural Topology & Circuit Schematic

In an **NMOS-based Low-Dropout Regulator**, the series pass element is an N-channel enhancement-mode MOSFET configured in a **Source-Follower (Common-Drain)** topology.

```text
                                +---------------------------+
                                |  Auxiliary High-Voltage   |
                                |  Rail (V_BIAS = 3.3V/5V)  |
                                +-------------┬-------------+
                                              │
       Unregulated Input (Vin = 1.05V)        │
                │                             │
                ├─── Drain (D)                │
                │   ┌───────────────┐         │
                │   │  NMOS Pass    │         │
                └───┤  Transistor   │         │
                    │ (Source-Follower)       │
       Gate (G) <───┤   (High gm)   │         │
                    └───────┬───────┘         │
                            │ Source (S)      │
                            ├─────────────────┼────────────┬───────────────> Regulated Vout (0.90V)
                            │                 │            │
                            │                 │           [R1] Feedback
                            │                 │            │   Resistors
              ┌─────────────┴─────────────┐   │            ├─── (V_FB)
              │  High-Voltage Error Amp   ├───┘            │
              │  (Powered by V_BIAS)      │               [R2]
   V_REF ────>│ (+) Non-inverting Input   │                │
   V_FB  ────>│ (-) Inverting Input       │               GND
              │                           │
              │ Output drives Gate HIGH   ┼─── Gate Drive (V_GATE = 2.1V)
              └───────────────────────────┘
```

### 1.1 Pin and Terminal Polarities
- **Drain (D)**: Connected directly to the low-voltage power supply rail ($V_{IN}$, e.g. $1.05\,\text{V} \dots 1.5\,\text{V}$). The heavy load current flows through Drain to Source.
- **Source (S)**: Connected directly to the output voltage rail ($V_{OUT}$, e.g. $0.8\,\text{V} \dots 1.2\,\text{V}$).
- **Gate (G)**: Driven by the Error Amplifier. Must be biased to a voltage higher than both $V_{OUT}$ and $V_{IN}$.
- **Auxiliary Bias Pin ($V_{BIAS}$)**: Provides the elevated headroom voltage ($3.3\,\text{V} \dots 5.5\,\text{V}$) required by the error amplifier to drive the NMOS gate above $V_{IN}$.

---

## 2. Operating Mechanism & The Gate Headroom Challenge

### 2.1 Source-Follower Physics & Local Negative Feedback
The NMOS pass transistor operates in **Common-Drain (Source-Follower)** configuration:
- The input to the transistor is applied to the **Gate**, and the output is taken from the **Source**.
- **Intrinsic Local Feedback**: In this configuration, the effective gate-to-source overdrive is:
  $$V_{GS} = V_{GATE} - V_{OUT}$$
- *Instantaneous Reaction*: If a sudden load surge causes $V_{OUT}$ to droop by $50\,\text{mV}$, $V_{GS}$ **instantly increases by $50\,\text{mV}$ without waiting for the outer error amplifier loop to respond**!
- The increased $V_{GS}$ immediately forces the NMOS channel to conduct more current, actively clamping the output droop. This confers NMOS LDOs with vastly superior load transient response compared to PMOS regulators.

---

### 2.2 The Gate Headroom Constraint ($V_{GATE} > V_{IN}$)

To turn an NMOS transistor fully ON into its linear triode region:
$$V_{GATE} \ge V_{OUT} + V_{th} + V_{ov}$$

Where:
- $V_{th}$ is the NMOS threshold voltage (typically $0.6\,\text{V} \dots 1.2\,\text{V}$).
- $V_{ov}$ is the overdrive voltage required for low $R_{DS(on)}$ (typically $0.3\,\text{V} \dots 0.6\,\text{V}$).

#### The Fundamental Headroom Dilemma:
Consider an embedded core supply requiring $V_{OUT} = 0.90\,\text{V}$ from a $V_{IN} = 1.05\,\text{V}$ input rail (headroom $= 150\,\text{mV}$):
$$V_{GATE} = V_{OUT} + V_{GS} = 0.90\,\text{V} + 1.20\,\text{V} = 2.10\,\text{V}$$

Notice that the required Gate voltage ($2.10\,\text{V}$) is **more than $1.0\,\text{V}$ higher than the input supply rail ($1.05\,\text{V}$)**:
$$V_{GATE} (2.10\,\text{V}) > V_{IN} (1.05\,\text{V})$$

> [!CAUTION]
> If an NMOS LDO attempts to operate from a single supply rail without an elevated voltage source, the maximum gate voltage cannot exceed $V_{IN}$. The resulting dropout voltage would be:
> $$V_{DO} = V_{IN} - V_{OUT} \ge V_{GS} \approx 1.0\,\text{V} \dots 1.5\,\text{V}$$
> This completely destroys the "low-dropout" capability of the regulator!

---

## 3. Architectural Solutions to the Gate Headroom Constraint

Modern IC designers utilize two distinct architectural approaches to supply the elevated gate voltage:

```text
 Dual-Supply Architecture (V_BIAS Pin)         Single-Supply with Internal Charge Pump
 ┌────────────────────────────────────┐        ┌────────────────────────────────────┐
 │              LDO IC                │        │              LDO IC                │
 │ Vin (1.05V) ───────> Drain         │        │ Vin (1.05V) ──┬────> Drain         │
 │                                    │        │               │                    │
 │ V_BIAS (3.3V) ────> Error Amp VDD  │        │               ▼                    │
 │                     │              │        │        [Charge Pump]               │
 │                     ▼ Gate Drive   │        │               │                    │
 │                     (2.1V)         │        │               ▼ V_BOOST (2.5V)     │
 │                                    │        │        [Error Amp VDD]             │
 └────────────────────────────────────┘        └────────────────────────────────────┘
```

### 3.1 Dual-Supply Architecture ($V_{BIAS}$ Pin)
- **High-Current Power Path ($V_{IN}$)**: Connects to a low-voltage, high-current switching rail (e.g. $1.05\,\text{V} \dots 1.5\,\text{V}$ from an efficient intermediate buck converter).
- **Control Path ($V_{BIAS}$)**: Connects to an available system auxiliary rail (typically $3.3\,\text{V}$ or $5.0\,\text{V}$). The $V_{BIAS}$ pin draws only a tiny quiescent current ($1\,\text{mA} \dots 5\,\text{mA}$) to power the internal reference and error amplifier.
- **Engineering Advantages**:
  - Achieves the world's lowest dropout voltages: **$30\,\text{mV} \dots 60\,\text{mV}$ at $2.0\,\text{A} \dots 4.0\,\text{A}$**.
  - Extremely high overall efficiency:
    $$\eta \approx \frac{V_{OUT} \times I_{LOAD}}{V_{IN} \times I_{LOAD}} = \frac{0.90\,\text{V}}{1.05\,\text{V}} \approx 85.7\%$$
  - Pristine, noise-free DC gate drive with zero switching ripple.

### 3.2 Single-Supply Architecture with Internal Charge Pump
- If an auxiliary $V_{BIAS}$ supply is not available on the PCB, the LDO incorporates an on-chip **switched-capacitor charge pump** (voltage doubler):
  - Operates at high frequency ($1\,\text{MHz} \dots 5\,\text{MHz}$) driven by an internal ring oscillator.
  - Generates an internal boosted voltage:
    $$V_{BOOST} \approx 2 \times V_{IN} - V_{diode}$$
  - Powers the error amplifier, allowing single-supply operation down to $V_{IN} = 0.8\,\text{V}$.
- **Design Trade-Off**:
  - The charge pump introduces a slight quiescent current overhead ($1\,\text{mA} \dots 3\,\text{mA}$) and switching clock harmonics that require rigorous internal low-pass filtering.

---

## 4. Small-Signal Loop Dynamics & Inherent Wideband Stability

While PMOS LDOs struggle with two competing low-frequency poles, the **NMOS Source-Follower architecture is inherently stable**.

### 4.1 Ultra-Low Source-Follower Output Impedance ($R_{OUT}$)
In a Source-Follower, the small-signal output resistance looking into the Source terminal is governed by the transistor's transconductance ($g_m$):
$$R_{OUT} = \frac{1}{g_m} \parallel r_{ds} \parallel R_{LOAD} \approx \frac{1}{g_m}$$

For a power NMOS pass element delivering $1\,\text{A} \dots 4\,\text{A}$, $g_m$ is large (typically $2\,\text{S} \dots 10\,\text{S}$):
$$R_{OUT} \approx \frac{1}{2\,\text{S} \dots 10\,\text{S}} = 0.10\,\Omega \dots 0.50\,\Omega$$

### 4.2 Pushing the Output Pole Out of Band

Because $R_{OUT}$ is tens to hundreds of times smaller than a PMOS Common-Source output impedance, the **Output Pole ($p_{out}$)** is pushed to extremely high frequencies:
$$p_{out} = \frac{1}{2\pi \cdot R_{OUT} \cdot C_{OUT}} = \frac{g_m}{2\pi \cdot C_{OUT}}$$

*Worked Numerical Example*:
With $g_m = 5\,\text{S}$ and $C_{OUT} = 10\,\mu\text{F}$:
$$p_{out} = \frac{5}{2\pi \times 10 \times 10^{-6}} \approx 79.6\,\text{kHz}$$
At light load or with smaller capacitors, $p_{out}$ pushes past $500\,\text{kHz} \dots 2\,\text{MHz}$!

```text
 Loop Gain (dB)
  60 |──────┐ (Internal Dominant Pole: p_int)
     |       \ -20 dB/dec
  40 |        \
     |         \
  20 |          \
     |           \
   0 |────────────\─────────────────────────── 0 dB Crossover (UGBW ~ 100 kHz)
     |             \
 -20 |              \────────┐ (Output Pole: p_out sits well OUTSIDE the loop bandwidth!)
     +─────────────+──────────+──────────> Frequency
                  p_int      p_out
```

### 4.3 Immunity to the "ESR Stability Tunnel"
- Because the loop contains **only one dominant low-frequency pole ($p_{int}$)** within the unity-gain bandwidth, the loop gain rolls off at a stable $-20\,\text{dB/decade}$ slope.
- Total phase lag is only $-90^\circ$, providing an inherent **Phase Margin of $+70^\circ \dots +90^\circ$**!
- **Zero-ESR MLCC Ceramic Stability**: NMOS LDOs **do not require an ESR zero** to achieve stability. They are unconditionally stable with pure, ultra-low ESR multi-layer ceramic capacitors ($R_{ESR} = 1\,\text{m}\Omega \dots 50\,\text{m}\Omega$).

---

## 5. Body Effect & Triple-Well CMOS Fabrication

In standard bulk CMOS processes, the P-type substrate is tied to the most negative potential in the circuit (Ground).
- In an NMOS pass transistor, the Source terminal sits at the output voltage ($V_{OUT} = 0.9\,\text{V} \dots 1.8\,\text{V}$).
- This creates a reverse source-to-body bias:
  $$V_{SB} = V_{OUT} - 0\,\text{V} > 0\,\text{V}$$

```text
              NMOS Pass Transistor
             Drain (Vin)  Source (Vout)
                 │             │
                ┌┴┐           ┌┴┐
               ┌┘ └───────────┘ └┐
            N+ │                 │ N+
       ────────┴─────────────────┴────────
                   Isolated P-Well (Body) ──┐
       ───────────────────────────────────  │ Tie Body directly to Source!
                 Deep N-Well                │ (V_SB = 0V: Eliminates Body Effect!)
       ───────────────────────────────────  │
                 P-Substrate (GND)          │
       ───────────────────────────────────  │
                                            ▲
```

### 5.1 The Body Effect Problem
When $V_{SB} > 0$, the depletion region widens, increasing the threshold voltage:
$$V_{th} = V_{th0} + \gamma \left( \sqrt{2\phi_F + V_{SB}} - \sqrt{2\phi_F} \right)$$
An increase of $\Delta V_{th} \approx 200\,\text{mV} \dots 400\,\text{mV}$ demands an even higher gate drive voltage to achieve low on-resistance.

### 5.2 The Triple-Well Silicon Solution
High-performance NMOS LDO ICs are fabricated on **Triple-Well CMOS processes**:
- The NMOS pass transistor is placed inside an isolated P-well enclosed by a Deep N-well barrier.
- This allows the transistor's P-well Body to be **tied directly to its Source ($V_{OUT}$)**.
- Because $V_{SB} = 0\,\text{V}$, the body effect is completely eliminated, minimizing threshold voltage and maximizing channel transconductance.

---

## 6. Real-World NMOS LDO ICs & Application Schematics

```text
                Texas Instruments TPS7A84 (NMOS High-Current LDO)
                         3A, Dual-Rail, 100mV Dropout
                         ┌───────────────────────────┐
     Vin (1.1V - 1.4V) ──┤ IN                    OUT ├─────┬───────> Clean Vout (0.9V, 3A)
                         │                           │     │
                   ─┴─   │                      SENSE├─────┤  ─┴─  Output MLCC
      C_IN (10uF)  ─┬─   │                           │     │  ─┬─  (47uF, X7R, 6.3V)
                   GND   │ BIAS                  GND ├─┐   │  GND
     V_BIAS (3.3V) ──────┤                           │ │   │
                         │ EN                        │ │   │
                   ─┴─   │                           │ │   │
     C_BIAS (1uF)  ─┬─   │ SS/NR                 ANY ├─┤   │
                   GND   └────┬───────────────────┬──┘ │   │
                              │                   │    │   │
                         ─┴─ C_SS (10nF)         GND  GND  │
                         ─┬─ (Soft-Start)                  │
                         GND                               │
                         ┌─────────────────────────────────┴┐
                         │ ANY-OUT Pin Strapping Network    │
                         │ (Configures precise Vout without │
                         │  external resistor dividers)     │
                         └──────────────────────────────────┘
```

### Representative Production NMOS LDOs:
- **TI `TPS7A84` / `TPS7A85`**: High-current $3.0\,\text{A} / 4.0\,\text{A}$ dual-rail NMOS LDO with $100\,\mu\text{V}$ dropout at $3\,\text{A}$, $4.4\,\mu\text{V}_{RMS}$ ultra-low noise, designed for FPGA SerDes and ASIC core rails.
- **TI `TPS7A54`**: $4.0\,\text{A}$ single-supply NMOS regulator with an internal charge pump, allowing single-rail operation down to $0.8\,\text{V}$ without an external $V_{BIAS}$ pin.
- **ADI `ADP1740`**: $2.0\,\text{A}$ low-dropout NMOS regulator operating from input rails down to $1.6\,\text{V}$.
