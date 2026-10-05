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
- **Drain (D)**: Connected directly to the low-voltage power supply rail (V_IN, e.g. 1.05 V ... 1.5 V). The heavy load current flows through Drain to Source.
- **Source (S)**: Connected directly to the output voltage rail (V_OUT, e.g. 0.8 V ... 1.2 V).
- **Gate (G)**: Driven by the Error Amplifier. Must be biased to a voltage higher than both V_OUT and V_IN.
- **Auxiliary Bias Pin (V_BIAS)**: Provides the elevated headroom voltage (3.3 V ... 5.5 V) required by the error amplifier to drive the NMOS gate above V_IN.

---

## 2. Operating Mechanism & The Gate Headroom Challenge

### 2.1 Source-Follower Physics & Local Negative Feedback
The NMOS pass transistor operates in **Common-Drain (Source-Follower)** configuration:
- The input to the transistor is applied to the **Gate**, and the output is taken from the **Source**.
- **Intrinsic Local Feedback**: In this configuration, the effective gate-to-source overdrive is:
  ```
V_GS = V_GATE - V_OUT
```

Where:
- V_GS: Gate-to-Source voltage across the NMOS pass transistor (V)
- V_GATE: Voltage applied to the NMOS gate terminal by driver / charge pump (V)
- V_OUT: Output voltage at the NMOS source terminal (V)
- *Instantaneous Reaction*: If a sudden load surge causes V_OUT to droop by 50 mV, V_GS **instantly increases by 50 mV without waiting for the outer error amplifier loop to respond**!
- The increased V_GS immediately forces the NMOS channel to conduct more current, actively clamping the output droop. This confers NMOS LDOs with vastly superior load transient response compared to PMOS regulators.

---

### 2.2 The Gate Headroom Constraint (V_GATE > V_IN)

To turn an NMOS transistor fully ON into its linear triode region:
```
V_GATE >= V_OUT + V_th + V_ov
```

Where:
- V_GATE: Minimum gate drive voltage required to keep transistor in conduction (V)
- V_OUT: Regulated output voltage at source (V)
- V_th: NMOS threshold voltage including body effect (V)
- V_ov: Gate overdrive voltage, V_ov = V_GS - V_th, needed to support load current (V)

Where:
- V_th is the NMOS threshold voltage (typically 0.6 V ... 1.2 V).
- V_ov is the overdrive voltage required for low R_DS(on) (typically 0.3 V ... 0.6 V).

#### The Fundamental Headroom Dilemma:
Consider an embedded core supply requiring V_OUT = 0.90 V from a V_IN = 1.05 V input rail (headroom = 150 mV):
```
V_GATE = V_OUT + V_GS = 0.90 V + 1.20 V = 2.10 V
```

Notice that the required Gate voltage (2.10 V) is **more than 1.0 V higher than the input supply rail (1.05 V)**:
```
V_GATE (2.10 V) > V_IN (1.05 V)
```

> [!CAUTION]
> If an NMOS LDO attempts to operate from a single supply rail without an elevated voltage source, the maximum gate voltage cannot exceed V_IN. The resulting dropout voltage would be:
> ```
V_DO = V_IN - V_OUT >= V_GS ≈ 1.0 V ... 1.5 V
```
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

### 3.1 Dual-Supply Architecture (V_BIAS Pin)
- **High-Current Power Path (V_IN)**: Connects to a low-voltage, high-current switching rail (e.g. 1.05 V ... 1.5 V from an efficient intermediate buck converter).
- **Control Path (V_BIAS)**: Connects to an available system auxiliary rail (typically 3.3 V or 5.0 V). The V_BIAS pin draws only a tiny quiescent current (1 mA ... 5 mA) to power the internal reference and error amplifier.
- **Engineering Advantages**:
  - Achieves the world's lowest dropout voltages: **30 mV ... 60 mV at 2.0 A ... 4.0 A**.
  - Extremely high overall efficiency:
    ```
η ≈ (V_OUT * I_LOAD) / (V_IN * I_LOAD) = 0.90 V / 1.05 V ≈ 85.7\%
```
  - Pristine, noise-free DC gate drive with zero switching ripple.

### 3.2 Single-Supply Architecture with Internal Charge Pump
- If an auxiliary V_BIAS supply is not available on the PCB, the LDO incorporates an on-chip **switched-capacitor charge pump** (voltage doubler):
  - Operates at high frequency (1 MHz ... 5 MHz) driven by an internal ring oscillator.
  - Generates an internal boosted voltage:
    ```
V_BOOST ≈ 2 * V_IN - V_diode
```
  - Powers the error amplifier, allowing single-supply operation down to V_IN = 0.8 V.
- **Design Trade-Off**:
  - The charge pump introduces a slight quiescent current overhead (1 mA ... 3 mA) and switching clock harmonics that require rigorous internal low-pass filtering.

---

## 4. Small-Signal Loop Dynamics & Inherent Wideband Stability

While PMOS LDOs struggle with two competing low-frequency poles, the **NMOS Source-Follower architecture is inherently stable**.

### 4.1 Ultra-Low Source-Follower Output Impedance (R_OUT)
In a Source-Follower, the small-signal output resistance looking into the Source terminal is governed by the transistor's transconductance (g_m):
```
R_OUT = (1 / g_m) || r_ds || R_LOAD ≈ 1 / g_m
```

Where:
- R_OUT: Small-signal open-loop output impedance looking into the source terminal (Ω)
- g_m: Transconductance of the NMOS pass transistor (S or A/V)
- r_ds: Small-signal drain-to-source channel resistance (Ω)
- R_LOAD: Effective DC load resistance, R_LOAD = V_OUT / I_LOAD (Ω)

For a power NMOS pass element delivering 1 A ... 4 A, g_m is large (typically 2 S ... 10 S):
```
R_OUT ≈ 1 / (2 S ... 10 S) = 0.10 Ω ... 0.50 Ω
```

### 4.2 Pushing the Output Pole Out of Band

Because R_OUT is tens to hundreds of times smaller than a PMOS Common-Source output impedance, the **Output Pole (p_out)** is pushed to extremely high frequencies:
```
p_out = 1 / (2π * R_OUT * C_OUT) = g_m / (2π * C_OUT)
```

*Worked Numerical Example*:
With g_m = 5 S and C_OUT = 10 µF:
```
p_out = 5 / (2π * 10 * 10^-6) ≈ 79.6 kHz
```
At light load or with smaller capacitors, p_out pushes past 500 kHz ... 2 MHz!

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
- Because the loop contains **only one dominant low-frequency pole (p_int)** within the unity-gain bandwidth, the loop gain rolls off at a stable -20 dB/decade slope.
- Total phase lag is only -90°, providing an inherent **Phase Margin of +70° ... +90°**!
- **Zero-ESR MLCC Ceramic Stability**: NMOS LDOs **do not require an ESR zero** to achieve stability. They are unconditionally stable with pure, ultra-low ESR multi-layer ceramic capacitors (R_ESR = 1 mΩ ... 50 mΩ).

---

## 5. Body Effect & Triple-Well CMOS Fabrication

In standard bulk CMOS processes, the P-type substrate is tied to the most negative potential in the circuit (Ground).
- In an NMOS pass transistor, the Source terminal sits at the output voltage (V_OUT = 0.9 V ... 1.8 V).
- This creates a reverse source-to-body bias:
  ```
V_SB = V_OUT - 0 V > 0 V
```

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
When V_SB > 0, the depletion region widens, increasing the threshold voltage:
```
V_th = V_th0 + γ ( sqrt(2φ_F + V_SB) - sqrt(2φ_F) )
```
An increase of Δ V_th ≈ 200 mV ... 400 mV demands an even higher gate drive voltage to achieve low on-resistance.

### 5.2 The Triple-Well Silicon Solution
High-performance NMOS LDO ICs are fabricated on **Triple-Well CMOS processes**:
- The NMOS pass transistor is placed inside an isolated P-well enclosed by a Deep N-well barrier.
- This allows the transistor's P-well Body to be **tied directly to its Source (V_OUT)**.
- Because V_SB = 0 V, the body effect is completely eliminated, minimizing threshold voltage and maximizing channel transconductance.

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
- **TI `TPS7A84` / `TPS7A85`**: High-current 3.0 A / 4.0 A dual-rail NMOS LDO with 100 µV dropout at 3 A, 4.4 µV_RMS ultra-low noise, designed for FPGA SerDes and ASIC core rails.
- **TI `TPS7A54`**: 4.0 A single-supply NMOS regulator with an internal charge pump, allowing single-rail operation down to 0.8 V without an external V_BIAS pin.
- **ADI `ADP1740`**: 2.0 A low-dropout NMOS regulator operating from input rails down to 1.6 V.
