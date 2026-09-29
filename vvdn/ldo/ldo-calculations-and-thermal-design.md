# LDO: Calculations, Feedback Sizing & Thermal Engineering

## 1. Power Dissipation, Efficiency & Thermal Mechanics

Unlike switching power supplies that store and transfer energy reactively via inductors and capacitors, a linear regulator drops excess voltage entirely through resistive dissipation across the active channel of its pass transistor.

---

### 1.1 Power Dissipation Equations

The total power dissipated as heat inside an LDO package ($P_D$) consists of two distinct components:

$$P_D = P_{pass} + P_Q$$

#### A. Pass Transistor Dissipation ($P_{pass}$):
The power burned dropping the unregulated input voltage ($V_{IN}$) down to the regulated output voltage ($V_{OUT}$) while supplying load current ($I_{LOAD}$):
$$P_{pass} = (V_{IN} - V_{OUT}) \times I_{LOAD} = V_{drop} \times I_{LOAD}$$

#### B. Quiescent Control Dissipation ($P_Q$):
The power consumed internally by the bandgap reference, error amplifier, and internal bias circuits:
$$P_Q = V_{IN} \times I_Q$$

#### Total Power Dissipation ($P_D$):
$$P_D = (V_{IN} - V_{OUT}) \times I_{LOAD} + (V_{IN} \times I_Q)$$

> [!NOTE]
> In normal full-load operation where $I_{LOAD} \gg I_Q$ (e.g., $I_{LOAD} = 1.0\,\text{A}$ and $I_Q = 2.0\,\text{mA}$), the quiescent power contributes less than $0.2\%$ of total heat dissipation and is often negligible:
> $$P_D \approx (V_{IN} - V_{OUT}) \times I_{LOAD}$$

---

### 1.2 Electrical Efficiency ($\eta$)

The conversion efficiency of a linear regulator is fundamentally bounded by the ratio of output voltage to input voltage:

$$\eta = \frac{P_{OUT}}{P_{IN}} \times 100\% = \frac{V_{OUT} \times I_{LOAD}}{V_{IN} \times (I_{LOAD} + I_Q)} \times 100\%$$

When $I_{LOAD} \gg I_Q$:
$$\eta \approx \frac{V_{OUT}}{V_{IN}} \times 100\%$$

*Efficiency Benchmark Comparisons*:
- Stepping $5.0\,\text{V}$ down to $3.3\,\text{V}$: $\eta \approx \frac{3.3}{5.0} = 66.0\%$ ($34\%$ lost as pure heat).
- Stepping $3.3\,\text{V}$ down to $1.8\,\text{V}$: $\eta \approx \frac{1.8}{3.3} = 54.5\%$ ($45.5\%$ lost as heat).
- Stepping $1.2\,\text{V}$ down to $1.0\,\text{V}$ (using an ultra-low dropout NMOS LDO):
  $$\eta \approx \frac{1.0}{1.2} = \mathbf{83.3\%}$$
  *(Notice: At low headroom, linear regulators rival the efficiency of switching buck converters while providing zero ripple!).*

---

## 2. Thermal Resistance Network & Junction Temperature ($T_J$)

All heat generated inside the silicon die must travel through the IC packaging into the surrounding ambient air. The thermal behavior is modeled using **Thermal Ohm's Law**:

$$\Delta T = P_D \times \theta_{JA}$$
$$T_J = T_A + (P_D \times \theta_{JA})$$

Where:
- $T_J$: Silicon Junction Temperature (Maximum safe limit typically **$+125^\circ\text{C}$** for commercial/industrial and **$+150^\circ\text{C}$** for automotive).
- $T_A$: Ambient Air Operating Temperature (e.g., $+25^\circ\text{C}$ laboratory, $+50^\circ\text{C}$ industrial enclosure, $+85^\circ\text{C}$ automotive engine compartment).
- $\theta_{JA}$: Junction-to-Ambient Thermal Resistance ($^\circ\text{C/W}$).
- $P_D$: Total Power Dissipated in Watts.

```text
  Silicon Junction (T_J)
          │
         [ ] Thermal Resistance Junction-to-Case (θ_JC)
          │
  IC Package Case (T_C)
          │
         [ ] Thermal Resistance Case-to-Heat-Sink / PCB (θ_CS)
          │
  Heat Sink / Copper Plane (T_S)
          │
         [ ] Thermal Resistance Sink-to-Ambient (θ_SA)
          │
  Ambient Air (T_A)
```

$$\theta_{JA} = \theta_{JC} + \theta_{CS} + \theta_{SA}$$

---

### 2.1 Worked Numerical Example: Thermal Verification

**Operating Conditions**:
- $V_{IN} = 5.0\,\text{V}$
- $V_{OUT} = 3.3\,\text{V}$
- $I_{LOAD} = 800\,\text{mA}$ ($0.8\,\text{A}$)
- Ambient Temperature: $T_A = 50^\circ\text{C}$
- LDO Package: **SOT-223** with standard PCB layout ($\theta_{JA} = 65^\circ\text{C/W}$).

1. Calculate Power Dissipation:
   $$P_D \approx (5.0\,\text{V} - 3.3\,\text{V}) \times 0.8\,\text{A} = 1.7\,\text{V} \times 0.8\,\text{A} = 1.36\,\text{W}$$
2. Calculate Temperature Rise ($\Delta T$):
   $$\Delta T = 1.36\,\text{W} \times 65^\circ\text{C/W} = 88.4^\circ\text{C}$$
3. Calculate Junction Temperature ($T_J$):
   $$T_J = T_A + \Delta T = 50^\circ\text{C} + 88.4^\circ\text{C} = \mathbf{138.4^\circ\text{C}}$$
4. **Thermal Verdict**: **FAIL!**
   $T_J$ exceeds the maximum safe limit ($125^\circ\text{C}$) by $13.4^\circ\text{C}$. The LDO will enter thermal shutdown and cycle ON/OFF.

#### Sizing Maximum Permissible $\theta_{JA}$ with a Heat Sink / Thermal Vias:
$$\theta_{JA(max)} \le \frac{T_{J(max)} - T_A}{P_D} = \frac{125^\circ\text{C} - 50^\circ\text{C}}{1.36\,\text{W}} = \frac{75^\circ\text{C}}{1.36\,\text{W}} \approx \mathbf{55.1^\circ\text{C/W}}$$
*Corrective Action*: Expand PCB thermal copper area or migrate to a **TO-263 (D2PAK)** package ($\theta_{JA} \approx 30^\circ\text{C/W}$ on $1\,\text{in}^2$ copper).

---

### 2.2 PCB Thermal Copper Sizing Rules
1. **Thermal Via Array**: Place a dense matrix of thermal vias ($0.3\,\text{mm}$ drill hole diameter, $1.0\,\text{mm} \dots 1.2\,\text{mm}$ grid pitch) directly beneath the IC's exposed power thermal pad (PowerPAD / ePad).
2. **Internal Plane Stitching**: Connect thermal vias directly to internal and bottom-layer Ground/Power copper flood planes ($1\,\text{oz}$ or $2\,\text{oz}$ copper) to distribute heat across the entire board surface.

---

## 3. Feedback Resistor Divider Network Sizing

For adjustable LDOs, the output voltage is configured using an external resistive voltage divider ($R_1, R_2$):

```text
 Vout ────────┬────────
              │
             [R1] (Top Resistor)
              │
              ├───────────> FB Pin (V_FB = V_REF)
              │
             [R2] (Bottom Resistor)
              │
             GND
```

### 3.1 Voltage Transfer Function
The feedback pin draws a minuscule input bias current ($I_{FB} \approx 10\,\text{nA} \dots 100\,\text{nA}$). The exact equation is:

$$V_{OUT} = V_{REF} \times \left(1 + \frac{R_1}{R_2}\right) + (I_{FB} \times R_1)$$

Because modern CMOS error amplifiers have $I_{FB} < 50\,\text{nA}$, the second term is negligible when $R_1$ is sized reasonably ($R_1 \le 100\,\text{k}\Omega$):
$$V_{OUT} \approx V_{REF} \times \left(1 + \frac{R_1}{R_2}\right)$$

Solving for the resistor ratio:
$$\frac{R_1}{R_2} = \frac{V_{OUT}}{V_{REF}} - 1$$

### 3.2 Sizing Guidelines & Current Trade-Offs
- **Divider Current ($I_{div}$)**: Sized to be at least $100\times$ higher than $I_{FB}$ to ensure thermal leakage currents do not cause output voltage drift:
  $$I_{div} = \frac{V_{REF}}{R_2} \ge 100 \times I_{FB}$$
- **Low-Power vs. High-PSRR Trade-Off**:
  - *Battery-operated micropower designs*: Select $R_2 = 100\,\text{k}\Omega \dots 500\,\text{k}\Omega$ ($I_{div} \approx 2\,\mu\text{A} \dots 10\,\mu\text{A}$) to maximize battery runtime.
  - *High-speed RF / Precision Analog designs*: Select $R_2 = 1\,\text{k}\Omega \dots 20\,\text{k}\Omega$ ($I_{div} \approx 60\,\mu\text{A} \dots 1.2\,\text{mA}$) to minimize Johnson-Nyquist thermal noise ($e_n = \sqrt{4k_B T R}$) and prevent capacitive noise pick-up on the high-impedance FB node.

---

## 4. Feedforward Capacitor ($C_{FF}$) Phase-Lead Compensation

In adjustable LDO regulators, adding a small **Feedforward Capacitor ($C_{FF}$)** ($10\,\text{pF} \dots 100\,\text{pF}$) in parallel with top resistor $R_1$ drastically improves dynamic performance:

```text
 Vout ────────┬──────────┐
              │          │
             [R1]      ─┴─ C_FF (Feedforward Capacitor)
              │        ─┬─ (10pF - 100pF)
              ├──────────┘
              │
             [R2]
              │
             GND
```

### 4.1 Pole-Zero Derivation of the Feedback Network
With $C_{FF}$ installed, the feedback impedance $Z_1(s) = R_1 \parallel \frac{1}{s C_{FF}}$. The transfer function from $V_{OUT}$ to $V_{FB}$ becomes:

$$\frac{V_{FB}(s)}{V_{OUT}(s)} = \left( \frac{R_2}{R_1 + R_2} \right) \times \frac{1 + s R_1 C_{FF}}{1 + s (R_1 \parallel R_2) C_{FF}}$$

This introduces a **Phase-Lead Zero ($f_z$)** and a **High-Frequency Pole ($f_p$)**:

$$f_{z\_ff} = \frac{1}{2\pi \cdot R_1 \cdot C_{FF}}$$
$$f_{p\_ff} = \frac{1}{2\pi \cdot (R_1 \parallel R_2) \cdot C_{FF}} = f_{z\_ff} \times \left(1 + \frac{R_1}{R_2}\right)$$

### 4.2 Engineering Benefits of $C_{FF}$
1. **Phase Margin Boost**: The zero is placed near the unity-gain crossover frequency ($10\,\text{kHz} \dots 100\,\text{kHz}$), injecting $+20^\circ \dots +45^\circ$ of phase boost to suppress transient ringing.
2. **Improved High-Frequency PSRR**: At higher frequencies, $C_{FF}$ bypasses $R_1$, coupling output ripple directly to the inverting input of the error amplifier with unity gain rather than attenuated by $\frac{R_2}{R_1+R_2}$.
3. **Faster Load Step Recovery**: High-speed transient edges on $V_{OUT}$ are fed directly to the error amplifier without experiencing the $R_1 C_{parasitic}$ low-pass delay.

---

## 5. Output Capacitor Dynamic Sizing & ESR Zero

### 5.1 Sizing $C_{OUT}$ for Load Transient Undershoot

When a digital load (such as a microcontroller awakening from sleep) suddenly steps its current demand from $0$ to $I_{step}$ in time $t_{edge} \approx 10\,\text{ns}$, the LDO error amplifier requires finite response time ($t_{response} \approx 2\,\mu\text{s} \dots 10\,\mu\text{s}$) to adjust the pass transistor gate.

During this brief window, **$100\%$ of the step current must be supplied by the output capacitor ($C_{OUT}$)**:

$$\Delta V_{OUT} \approx \frac{I_{step} \times t_{response}}{C_{OUT}} + (I_{step} \times R_{ESR})$$

Solving for the minimum required output capacitance:
$$C_{OUT(min)} \ge \frac{I_{step} \times t_{response}}{\Delta V_{allowed} - (I_{step} \times R_{ESR})}$$

*Worked Example*:
- Load step: $I_{step} = 1.0\,\text{A}$
- Regulator response time: $t_{response} = 5\,\mu\text{s}$
- Allowable voltage droop: $\Delta V_{allowed} = 100\,\text{mV}$
- Output capacitor ESR: $R_{ESR} = 15\,\text{m}\Omega$ ($I_{step} \times R_{ESR} = 15\,\text{mV}$)

$$C_{OUT(min)} \ge \frac{1.0\,\text{A} \times 5 \times 10^{-6}\,\text{s}}{0.100\,\text{V} - 0.015\,\text{V}} = \frac{5.0 \times 10^{-6}}{0.085\,\text{V}} \approx \mathbf{58.8\,\mu\text{F}}$$

> [!WARNING]
> **Ceramic Capacitor DC Bias Derating Trap**:
> Multi-layer ceramic capacitors (MLCCs with X5R / X7R dielectrics) suffer severe loss of effective capacitance under DC voltage bias. A capacitor rated at $47\,\mu\text{F}$ in an 0805 package may lose **$40\% \dots 70\%$** of its capacitance when biased at $3.3\,\text{V}$ or $5.0\,\text{V}$! Always inspect the manufacturer's DC Bias derating curves and parallel two or three capacitors to guarantee minimum $C_{OUT}$ under operating voltage.

---

## 6. Root Cause Analysis (RCA) Troubleshooting Matrix

When debugging linear regulator circuits on the bench, consult this diagnostic reference:

| Observed Symptom | Oscilloscope Signature | Probable Root Cause | Verification & Corrective Action |
| :--- | :--- | :--- | :--- |
| **Output exhibits high-frequency continuous oscillation (100kHz - 2MHz).** | Sinusoidal AC waveform riding on $V_{OUT}$ with peak-to-peak amplitude from $50\,\text{mV}$ to $> 1\,\text{V}$. | **Capacitor ESR outside the stability tunnel** (typically using an ultra-low ESR MLCC on an older PMOS LDO requiring ESR). | Check LDO datasheet stability curve. Insert a $0.5\,\Omega \dots 1.0\,\Omega$ series carbon resistor in series with $C_{OUT}$ to test. Add feedforward capacitor $C_{FF}$ across $R_1$, or replace with a modern MLCC-stable LDO. |
| **Output voltage sags below nominal target under heavy load.** | $V_{OUT}$ drops proportionally to $I_{LOAD}$; DC level is stable but low. | **Input voltage violation ($V_{IN} - V_{OUT} < V_{DO}$)**: The LDO has dropped out of regulation into its ohmic triode region. | Measure input voltage with an oscilloscope probe right at the IC's $V_{IN}$ pin. Check for voltage drops across input wiring, PCB traces, or upstream filter ferrites. |
| **LDO operates for a few seconds, shuts off, cools down, and turns back on repeatedly.** | Sawtooth thermal cycling on $V_{OUT}$; IC package becomes scalding hot ($> 130^\circ\text{C}$). | **Thermal overload shutdown**: Package power dissipation exceeds PCB heat dissipation capability ($P_D \times \theta_{JA}$). | Calculate $P_D = (V_{IN} - V_{OUT}) \times I_{LOAD}$. Reduce $V_{IN}$ headroom, increase PCB copper thermal pad area, add a heatsink, or pre-drop voltage with a switching buck converter. |
| **LDO is destroyed immediately upon powering down the system.** | Short circuit between $V_{IN}$ and $V_{OUT}$ or between $V_{IN}$ and GND; silicon crater on die. | **Reverse current conduction**: Large $C_{OUT}$ discharged backwards through the PMOS parasitic body diode into an unpowered input. | Install an external low-drop Schottky diode (e.g. `MBR0520`) with Anode on $V_{OUT}$ and Cathode on $V_{IN}$ to bypass reverse current, or select an LDO with internal reverse-current blocking. |
| **Excessive output ripple and noise matching upstream switching frequency.** | High-frequency triangular or sinusoidal ripple ($500\,\text{kHz} \dots 2\,\text{MHz}$) passing through to $V_{OUT}$. | **Poor high-frequency PSRR** of the LDO, or capacitive noise coupling through feedback resistors. | Add a Noise Reduction capacitor ($C_{NR}$) on the bandgap pin. Add a feedforward capacitor ($C_{FF}$). Ensure feedback traces are kept short and shielded away from switching inductors. |
