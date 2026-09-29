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
- **Source (S)**: Connected directly to the raw input supply voltage rail ($V_{IN}$).
- **Drain (D)**: Connected directly to the output voltage rail ($V_{OUT}$).
- **Gate (G)**: Driven by the output of the high-gain Error Amplifier.
- **Substrate / N-Well Body (B)**: Tied internally to the Source ($V_{IN}$) to prevent forward-biasing the source-body junction.

---

## 2. Operating Mechanism & Gate Drive Physics

### 2.1 Negative Gate-to-Source Drive ($V_{GS}$)
A PMOS transistor conducts when its Gate voltage is pulled lower than its Source voltage by at least its threshold voltage magnitude ($|V_{th}|$):
$$V_{GS} = V_{GATE} - V_{IN} < -|V_{th}| \quad \Longleftrightarrow \quad V_{GATE} < V_{IN} - |V_{th}|$$

Because the source is connected to the highest positive voltage in the system ($V_{IN}$), the Error Amplifier simply has to **pull the gate voltage down towards Ground (0V)** to turn the transistor ON:

$$\text{Max Available Gate Overdrive } |V_{GS(max)}| = V_{IN} - V_{GATE(min)} \approx V_{IN} - 0.2\,\text{V}$$

> [!IMPORTANT]
> **Single-Supply Simplicity**: Unlike NMOS LDOs, the PMOS pass element requires **no gate voltage higher than $V_{IN}$**. This allows the PMOS LDO to run entirely from a single input rail without an auxiliary supply pin ($V_{BIAS}$) or an on-chip charge pump.

### 2.2 Dropout Voltage Mechanics in Triode (Linear) Region

When $V_{IN}$ approaches $V_{OUT}$ (at low headroom), the PMOS transistor is driven fully ON and enters its **linear / triode ohmic region**. The regulator behaves as a small resistor:
$$R_{DS(on)} = \frac{1}{\mu_p C_{ox} \left(\frac{W}{L}\right) (|V_{GS}| - |V_{th}|)}$$

The minimum dropout voltage ($V_{DO}$) is given directly by Ohm's Law:
$$V_{DO} = I_{LOAD} \times R_{DS(on)}$$

*Numerical Example*:
For a target dropout of $V_{DO} \le 100\,\text{mV}$ at $I_{LOAD} = 1.0\,\text{A}$:
$$R_{DS(on)} \le \frac{100\,\text{mV}}{1.0\,\text{A}} = 0.10\,\Omega = 100\,\text{m}\Omega$$

### 2.3 The Silicon Area & Gate Capacitance Penalty
Because holes have significantly lower mobility than electrons ($\mu_p \approx \frac{1}{2.5} \mu_n$ to $\frac{1}{3} \mu_n$ in silicon):
- A PMOS pass transistor requires **$2.5\times$ to $3\times$ larger channel width ($W$)** than an equivalent NMOS transistor to achieve the same $R_{DS(on)}$.
- This physical enlargement dramatically increases silicon die area, cost, and parasitic gate capacitance ($C_{gate} = C_{GS} + C_{GD}$). A large PMOS pass element can easily present $500\,\text{pF} \dots 2000\,\text{pF}$ of gate capacitance to the error amplifier output!

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

### 3.1 High Common-Source Output Impedance ($r_o$)
Because the PMOS operates in Common-Source, its small-signal drain output impedance is naturally high:
$$R_{OUT} = r_{ds} \parallel (R_1 + R_2) \parallel R_{LOAD} \approx r_{ds} \parallel R_{LOAD}$$

### 3.2 The Two Competing Low-Frequency Dominant Poles

The open-loop transfer function contains two distinct low-frequency poles:

#### 1. The Output Pole ($p_{out}$):
Formed by the high output resistance ($R_{OUT}$) and the output filter capacitor ($C_{OUT}$):
$$p_{out} = \frac{1}{2\pi \cdot R_{OUT} \cdot C_{OUT}} \approx \frac{1}{2\pi \cdot \left(\frac{V_{OUT}}{I_{LOAD}}\right) \cdot C_{OUT}}$$
- *Critical Observation*: Because $R_{LOAD} = V_{OUT} / I_{LOAD}$, **the output pole frequency moves drastically with load current**!
  - At full load ($I_{LOAD} = 1\,\text{A}$, $V_{OUT} = 3.3\,\text{V}$, $C_{OUT} = 10\,\mu\text{F}$):
    $$R_{LOAD} = 3.3\,\Omega \implies p_{out} = \frac{1}{2\pi \times 3.3\,\Omega \times 10\,\mu\text{F}} \approx 4.8\,\text{kHz}$$
  - At light load ($I_{LOAD} = 1\,\text{mA}$, $R_{LOAD} = 3300\,\Omega$):
    $$p_{out} = \frac{1}{2\pi \times 3300\,\Omega \times 10\,\mu\text{F}} \approx 4.8\,\text{Hz}$$
  The output pole shifts by **three orders of magnitude** across normal operating currents!

#### 2. The Internal Gate Pole ($p_{gate}$):
Formed by the high output impedance of the error amplifier stage ($R_{EA}$) and the massive gate capacitance of the PMOS pass transistor ($C_{gate}$):
$$p_{gate} = \frac{1}{2\pi \cdot R_{EA} \cdot C_{gate}}$$
Because both $R_{EA}$ and $C_{gate}$ are large, $p_{gate}$ typically falls in the range of **$100\,\text{Hz} \dots 50\,\text{kHz}$**.

#### The Stability Threat:
With two dominant poles located closely in frequency, each contributing $-90^\circ$ of phase lag, the total open-loop phase shift reaches **$-180^\circ$** before the loop gain drops to unity ($0\,\text{dB}$). According to the Barkhausen stability criterion, this produces a negative phase margin, causing **spontaneous, violent oscillation on the $V_{OUT}$ rail**!

---

## 4. Frequency Compensation & The ESR Stability Tunnel

To stabilize a PMOS LDO, a **phase-lead zero ($z_{esr}$)** must be inserted into the loop to cancel one of the dominant poles and boost phase margin back above $+45^\circ \dots +60^\circ$.

### 4.1 The Output Capacitor ESR Zero

Every real-world capacitor exhibits internal **Equivalent Series Resistance (ESR)** ($R_{ESR}$). In series with $C_{OUT}$, it creates a transfer function zero:
$$z_{esr} = \frac{1}{2\pi \cdot R_{ESR} \cdot C_{OUT}}$$

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

- **Why Too Low ESR Causes Instability ($R_{ESR} < 50\,\text{m}\Omega$)**:
  Modern multi-layer ceramic capacitors (MLCCs) have ultra-low ESR ($5\,\text{m}\Omega \dots 15\,\text{m}\Omega$). With such tiny resistance, the zero is pushed to megahertz frequencies ($z_{esr} > 5\,\text{MHz}$), well past the unity-gain crossover. The zero arrives too late to rescue the phase margin, and the regulator oscillates!
- **Why Too High ESR Causes Instability ($R_{ESR} > 3\,\Omega$)**:
  Excessive ESR (common in aged electrolytic capacitors) introduces a secondary high-frequency pole ($p_{esr}$) and produces unacceptable transient output voltage spikes ($\Delta V = I_{step} \times R_{ESR}$).

### 4.3 Modern MLCC Ceramic-Stable PMOS LDOs

To allow engineers to use modern low-ESR ceramic capacitors without oscillation, modern PMOS LDOs integrate **internal frequency compensation networks**:
1. **Internal Damping Zero Generation**: The IC internally senses output current and synthesizes an internal resistor-capacitor zero in the feedback path, providing phase lead regardless of external capacitor ESR.
2. **Feedforward Capacitor ($C_{FF}$)**: A small capacitor ($10\,\text{pF} \dots 100\,\text{pF}$) placed across top feedback resistor $R_1$:
   $$z_{ff} = \frac{1}{2\pi \cdot R_1 \cdot C_{FF}}$$
   This injects phase lead directly into the error amplifier's inverting terminal.

---

## 5. Reverse Current Protection & Parasitic Body Diode

A critical vulnerability of standard PMOS LDOs is the **intrinsic parasitic P-N body diode** formed between the Drain ($V_{OUT}$, P-type diffusion) and the N-Well Substrate ($V_{IN}$, N-type diffusion).

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
- If $V_{OUT}$ ever exceeds $V_{IN}$ by more than **$0.6\,\text{V}$** (such as when the input power is abruptly switched off while a large, charged output capacitor holds $V_{OUT}$ high, or if an active battery is connected to $V_{OUT}$), the parasitic body diode conducts.
- Uncontrolled current surges backwards from $V_{OUT}$ into the input supply rail, frequently melting the internal silicon bond wires or destroying the input supply.

### 5.2 Silicon Protection Techniques
1. **External Reverse Schottky Diode**: Connecting an external low-voltage drop Schottky diode from $V_{OUT}$ (Anode) to $V_{IN}$ (Cathode) clamps the reverse voltage to $< 0.3\,\text{V}$, preventing the internal silicon body diode from turning on.
2. **True Reverse-Current Blocking ICs (Back-to-Back PMOS / Body-Switching)**:
   - Modern ICs incorporate a second internal PMOS transistor in series back-to-back, so their body diodes point in opposite directions.
   - Alternatively, an internal comparator continuously compares $V_{IN}$ and $V_{OUT}$. When $V_{OUT} > V_{IN}$, the comparator dynamically switches the N-Well substrate connection from $V_{IN}$ to $V_{OUT}$, keeping the parasitic diode reverse-biased under all conditions.

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
- **TI `TPS7A4700`**: High-performance $1.0\,\text{A}$ PMOS LDO featuring $4.17\,\mu\text{V}_{RMS}$ ultra-low noise, $82\,\text{dB}$ PSRR at $100\,\text{Hz}$, and internal pin-programmable voltage dividers.
- **ADI / Linear Tech `LT1763`**: Industry-standard $500\,\text{mA}$ micropower PMOS LDO with $20\,\mu\text{V}_{RMS}$ noise, ideal for battery-operated RF transceivers.
- **TI `TPS795`**: $500\,\text{mA}$ PMOS regulator with high bandwidth and low dropout ($110\,\text{mV}$ at $500\,\text{mA}$).
