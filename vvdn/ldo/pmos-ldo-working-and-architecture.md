# PMOS LDO: Working Mechanism, Loop Dynamics & Architecture

## 1. Architectural Topology & Circuit Schematic

In a **PMOS-based Low-Dropout Regulator**, the series pass transistor is a P-channel enhancement-mode MOSFET configured in a **Common-Source (CS)** amplifier topology.

```text
       Unregulated Input (Vin)
                │
                ├─── Source (S)
                │   ┌───────────────┐
                │   │  PMOS Pass    │
                └───┤  Transistor   │
                    │   (W/L Large) │
       Gate (G) <───┤               │
                    └───────┬───────┘
                            │ Drain (D)
                            ├──────────────────────────────┬───────────────> Regulated Vout
                            │                              │
                            │                             [R1] Feedback
                            │                              │   Resistors
                            │                              ├─── (V_FB)
              ┌─────────────┴─────────────┐                │
              │  Error Amplifier (EA)     │               [R2]
              │                           │                │
   V_REF ────>│ (+) Non-inverting Input   │               GND
   V_FB  ────>│ (-) Inverting Input       │
              │                           │
              │ Output sinks gate current ┼─── Gate Drive (V_GATE)
              └───────────────────────────┘
```

### 1.1 Pin and Terminal Polarities
- **Source (S)**: Connected directly to the raw input supply voltage rail (V_IN).
- **Drain (D)**: Connected directly to the output voltage rail (V_OUT).
- **Gate (G)**: Driven by the output of the high-gain Error Amplifier.
- **Substrate / N-Well Body (B)**: Tied internally to the Source (V_IN) to prevent forward-biasing the source-body junction.

---

## 2. Operating Mechanism & Gate Drive Physics

### 2.1 Negative Gate-to-Source Drive (V_GS)
A PMOS transistor conducts when its Gate voltage is pulled lower than its Source voltage by at least its threshold voltage magnitude (|V_th|):
```
V_GS = V_GATE - V_IN < -|V_th| <=> V_GATE < V_IN - |V_th|
```

Because the source is connected to the highest positive voltage in the system (V_IN), the Error Amplifier simply has to **pull the gate voltage down towards Ground (0V)** to turn the transistor ON:

```
Max Available Gate Overdrive |V_GS(max)| = V_IN - V_GATE(min) ≈ V_IN - 0.2 V
```

> [!IMPORTANT]
> **Single-Supply Simplicity**: Unlike NMOS LDOs, the PMOS pass element requires **no gate voltage higher than V_IN**. This allows the PMOS LDO to run entirely from a single input rail without an auxiliary supply pin (V_BIAS) or an on-chip charge pump.

### 2.2 Dropout Voltage Mechanics in Triode (Linear) Region

When V_IN approaches V_OUT (at low headroom), the PMOS transistor is driven fully ON and enters its **linear / triode ohmic region**. The regulator behaves as a small resistor:
```
R_DS(on) = 1 / (µ_p C_ox (W / L) (|V_GS| - |V_th|))
```

The minimum dropout voltage (V_DO) is given directly by Ohm's Law:
```
V_DO = I_LOAD * R_DS(on)
```

Where:
- V_DO: Dropout voltage of the PMOS regulator (V)
- I_LOAD: DC output load current (A)
- R_DS(on): On-resistance of PMOS pass element (Ω)

*Numerical Example*:
For a target dropout of V_DO <= 100 mV at I_LOAD = 1.0 A:
```
R_DS(on) <= 100 mV / 1.0 A = 0.10 Ω = 100 mΩ
```

### 2.3 The Silicon Area & Gate Capacitance Penalty
Because holes have significantly lower mobility than electrons (µ_p ≈ 1 / 2.5 µ_n to 1 / 3 µ_n in silicon):
- A PMOS pass transistor requires **2.5* to 3* larger channel width (W)** than an equivalent NMOS transistor to achieve the same R_DS(on).
- This physical enlargement dramatically increases silicon die area, cost, and parasitic gate capacitance (C_gate = C_GS + C_GD). A large PMOS pass element can easily present 500 pF ... 2000 pF of gate capacitance to the error amplifier output!

---

## 3. Small-Signal Loop Dynamics & The Two-Pole Stability Challenge

The primary engineering challenge in PMOS LDO design is **loop stability across varying load currents**.

```text
       ┌───────────┐         ┌───────────┐         ┌───────────────┐
       │   Error   │ V_gate  │   PMOS    │  V_out  │  Feedback     │ V_fb
──(+)─>│ Amplifier ├────────>│ Pass FET  ├────────>│ Divider       ├───(-)
       │ A_EA(s)   │         │ -gm_p*ro  │         │ β = R2/(R1+R2)│
       └─────┬─────┘         └─────┬─────┘         └───────────────┘
             │                     │
          Pole 1:               Pole 2:
         Internal              Load-Dependent
         Gate Pole              Output Pole
         (p_gate)               (p_out)
```

### 3.1 High Common-Source Output Impedance (r_o)
Because the PMOS operates in Common-Source, its small-signal drain output impedance is naturally high:
```
R_OUT = r_ds || (R1 + R2) || R_LOAD ≈ r_ds || R_LOAD
```

Where:
- R_OUT: Small-signal open-loop output impedance of the Common-Source stage (Ω)
- r_ds: Small-signal channel resistance of PMOS transistor (Ω)
- R1, R2: Upper and lower feedback divider resistors (Ω)
- R_LOAD: Effective DC load resistance, R_LOAD = V_OUT / I_LOAD (Ω)

### 3.2 The Two Competing Low-Frequency Dominant Poles

The open-loop transfer function contains two distinct low-frequency poles:

#### 1. The Output Pole (p_out):
Formed by the high output resistance (R_OUT) and the output filter capacitor (C_OUT):
```
p_out = 1 / (2π * R_OUT * C_OUT) ≈ 1 / (2π * (V_OUT / I_LOAD) * C_OUT)
```
- *Critical Observation*: Because R_LOAD = V_OUT / I_LOAD, **the output pole frequency moves drastically with load current**!
  - At full load (I_LOAD = 1 A, V_OUT = 3.3 V, C_OUT = 10 µF):
    ```
R_LOAD = 3.3 Ω => p_out = 1 / (2π * 3.3 Ω * 10 µF) ≈ 4.8 kHz
```
  - At light load (I_LOAD = 1 mA, R_LOAD = 3300 Ω):
    ```
p_out = 1 / (2π * 3300 Ω * 10 µF) ≈ 4.8 Hz
```
  The output pole shifts by **three orders of magnitude** across normal operating currents!

#### 2. The Internal Gate Pole (p_gate):
Formed by the high output impedance of the error amplifier stage (R_EA) and the massive gate capacitance of the PMOS pass transistor (C_gate):
```
p_gate = 1 / (2π * R_EA * C_gate)
```
Because both R_EA and C_gate are large, p_gate typically falls in the range of **100 Hz ... 50 kHz**.

#### The Stability Threat:
With two dominant poles located closely in frequency, each contributing -90° of phase lag, the total open-loop phase shift reaches **-180°** before the loop gain drops to unity (0 dB). According to the Barkhausen stability criterion, this produces a negative phase margin, causing **spontaneous, violent oscillation on the V_OUT rail**!

---

## 4. Frequency Compensation & The ESR Stability Tunnel

To stabilize a PMOS LDO, a **phase-lead zero (z_esr)** must be inserted into the loop to cancel one of the dominant poles and boost phase margin back above +45° ... +60°.

### 4.1 The Output Capacitor ESR Zero

Every real-world capacitor exhibits internal **Equivalent Series Resistance (ESR)** (R_ESR). In series with C_OUT, it creates a transfer function zero:
```
z_esr = 1 / (2π * R_ESR * C_OUT)
```

```text
 Loop Gain (dB)
  60 |──────┐ (p_out)
     |       \ -20 dB/dec
  40 |        \────────┐ (p_gate)
     |                  \ -40 dB/dec
  20 |                   \       ┌────── (z_esr restores slope to -20 dB/dec!)
     |                    \     /
   0 |─────────────────────\───/────────────── 0 dB Crossover (UGBW)
     +────────+─────────────+─/───+───────> Frequency
             p_out         p_gate z_esr
```

### 4.2 The ESR Stability "Tunnel" (Horseshoe Curve)

Because the stability of early PMOS LDOs depended entirely on the ESR zero, the output capacitor had to fall within a strictly bounded "tunnel":

```text
 Capacitor ESR (Ω)
  10.0 |─────────────────────────────────────────────
       |            UNSTABLE REGION
   5.0 |───────[ Upper ESR Limit (p_esr) ]───────────
   1.0 |
       |            STABLE TUNNEL
   0.1 |         (Phase Margin > 45°)
  0.05 |───────[ Lower ESR Limit (z_esr too high) ]──
       |            UNSTABLE REGION (Pure Ceramic MLCC)
  0.001+─────────────────────────────────────────────
       0.1 mA               Load Current           1.0 A
```

- **Why Too Low ESR Causes Instability (R_ESR < 50 mΩ)**:
  Modern multi-layer ceramic capacitors (MLCCs) have ultra-low ESR (5 mΩ ... 15 mΩ). With such tiny resistance, the zero is pushed to megahertz frequencies (z_esr > 5 MHz), well past the unity-gain crossover. The zero arrives too late to rescue the phase margin, and the regulator oscillates!
- **Why Too High ESR Causes Instability (R_ESR > 3 Ω)**:
  Excessive ESR (common in aged electrolytic capacitors) introduces a secondary high-frequency pole (p_esr) and produces unacceptable transient output voltage spikes (Δ V = I_step * R_ESR).

### 4.3 Modern MLCC Ceramic-Stable PMOS LDOs

To allow engineers to use modern low-ESR ceramic capacitors without oscillation, modern PMOS LDOs integrate **internal frequency compensation networks**:
1. **Internal Damping Zero Generation**: The IC internally senses output current and synthesizes an internal resistor-capacitor zero in the feedback path, providing phase lead regardless of external capacitor ESR.
2. **Feedforward Capacitor (C_FF)**: A small capacitor (10 pF ... 100 pF) placed across top feedback resistor R_1:
   ```
z_ff = 1 / (2π * R_1 * C_FF)
```
   This injects phase lead directly into the error amplifier's inverting terminal.

---

## 5. Reverse Current Protection & Parasitic Body Diode

A critical vulnerability of standard PMOS LDOs is the **intrinsic parasitic P-N body diode** formed between the Drain (V_OUT, P-type diffusion) and the N-Well Substrate (V_IN, N-type diffusion).

```text
               Vin (Source)
                 │
                 ├───┐
                 │   │
                 │   ▼ [PMOS Channel]
                 │   │
                 │   ├───┤◀├───┐ (Parasitic Body Diode)
                 │   │  Diode  │
                 │   ▼         │
                 └───┴─────────┼───> Vout (Drain)
                               │
               (When Vout > Vin: Diode conducts massive reverse current!)
```

### 5.1 The Reverse-Biased Failure Mode
- If V_OUT ever exceeds V_IN by more than **0.6 V** (such as when the input power is abruptly switched off while a large, charged output capacitor holds V_OUT high, or if an active battery is connected to V_OUT), the parasitic body diode conducts.
- Uncontrolled current surges backwards from V_OUT into the input supply rail, frequently melting the internal silicon bond wires or destroying the input supply.

### 5.2 Silicon Protection Techniques
1. **External Reverse Schottky Diode**: Connecting an external low-voltage drop Schottky diode from V_OUT (Anode) to V_IN (Cathode) clamps the reverse voltage to < 0.3 V, preventing the internal silicon body diode from turning on.
2. **True Reverse-Current Blocking ICs (Back-to-Back PMOS / Body-Switching)**:
   - Modern ICs incorporate a second internal PMOS transistor in series back-to-back, so their body diodes point in opposite directions.
   - Alternatively, an internal comparator continuously compares V_IN and V_OUT. When V_OUT > V_IN, the comparator dynamically switches the N-Well substrate connection from V_IN to V_OUT, keeping the parasitic diode reverse-biased under all conditions.

---

## 6. Real-World PMOS LDO ICs & Application Schematics

```text
                     Texas Instruments TPS7A4700 (PMOS LDO)
                             Ultra-Low Noise, 1A
                         ┌───────────────────────────┐
     Vin (3.8V - 5.5V) ──┤ IN                    OUT ├─────┬───────> Clean Vout (3.3V, 1A)
                         │                           │     │
                   ─┴─   │                      SENSE├─────┤  ─┴─  Output MLCC
      C_IN (10uF)  ─┬─   │                           │     │  ─┬─  (10uF, X7R, 16V)
                   GND   │ NR/FB                 GND ├─┐   │  GND
                         └────┬───────────────────┬──┘ │   │
                              │                   │    │   │
                         ─┴─ C_NR (10nF)         GND  GND  │
                         ─┬─ (Noise Reduct)                │
                         GND                               │
                         ┌─────────────────────────────────┴┐
                         │ ANY-OUT Pin Strapping Network    │
                         │ (Programs output voltage without │
                         │  external feedback resistors)    │
                         └──────────────────────────────────┘
```

### Representative Production PMOS LDOs:
- **TI `TPS7A4700`**: High-performance 1.0 A PMOS LDO featuring 4.17 µV_RMS ultra-low noise, 82 dB PSRR at 100 Hz, and internal pin-programmable voltage dividers.
- **ADI / Linear Tech `LT1763`**: Industry-standard 500 mA micropower PMOS LDO with 20 µV_RMS noise, ideal for battery-operated RF transceivers.
- **TI `TPS795`**: 500 mA PMOS regulator with high bandwidth and low dropout (110 mV at 500 mA).
