# LDO: Calculations, Feedback Sizing & Thermal Engineering

## 1. Power Dissipation, Efficiency & Thermal Mechanics

Unlike switching power supplies that store and transfer energy reactively via inductors and capacitors, a linear regulator drops excess voltage entirely through resistive dissipation across the active channel of its pass transistor.

---

### 1.1 Power Dissipation Equations

The total power dissipated as heat inside an LDO package (P_D) consists of two distinct components:

```
P_D = P_pass + P_Q
```

Where:
- P_D: Total power dissipated as heat inside the regulator package (W)
- P_pass: Power dissipated in the series pass transistor channel (W)
- P_Q: Quiescent control power consumed internally by bandgap and bias networks (W)

#### A. Pass Transistor Dissipation (P_pass):
The power burned dropping the unregulated input voltage (V_IN) down to the regulated output voltage (V_OUT) while supplying load current (I_LOAD):
```
P_pass = (V_IN - V_OUT) * I_LOAD = V_drop * I_LOAD
```

#### B. Quiescent Control Dissipation (P_Q):
The power consumed internally by the bandgap reference, error amplifier, and internal bias circuits:
```
P_Q = V_IN * I_Q
```

#### Total Power Dissipation (P_D):
```
P_D = (V_IN - V_OUT) * I_LOAD + (V_IN * I_Q)
```

Where:
- P_D: Total power dissipated as heat in the regulator package (W)
- V_IN: Unregulated DC input voltage (V)
- V_OUT: Regulated DC output voltage (V)
- I_LOAD: Output load current (A)
- I_Q: Internal quiescent current flowing to ground (A)

> [!NOTE]
> In normal full-load operation where I_LOAD >> I_Q (e.g., I_LOAD = 1.0 A and I_Q = 2.0 mA), the quiescent power contributes less than 0.2\% of total heat dissipation and is often negligible:
> ```
P_D ≈ (V_IN - V_OUT) * I_LOAD
```

---

### 1.2 Electrical Efficiency (η)

The conversion efficiency of a linear regulator is fundamentally bounded by the ratio of output voltage to input voltage:

```
η = P_OUT / P_IN * 100\% = (V_OUT * I_LOAD) / (V_IN * (I_LOAD + I_Q)) * 100\%
```

When I_LOAD >> I_Q:
```
η ≈ V_OUT / V_IN * 100\%
```

*Efficiency Benchmark Comparisons*:
- Stepping 5.0 V down to 3.3 V: η ≈ 3.3 / 5.0 = 66.0\% (34\% lost as pure heat).
- Stepping 3.3 V down to 1.8 V: η ≈ 1.8 / 3.3 = 54.5\% (45.5\% lost as heat).
- Stepping 1.2 V down to 1.0 V (using an ultra-low dropout NMOS LDO):
  ```
η ≈ 1.0 / 1.2 = 83.3\%
```
  *(Notice: At low headroom, linear regulators rival the efficiency of switching buck converters while providing zero ripple!).*

---

## 2. Thermal Resistance Network & Junction Temperature (T_J)

All heat generated inside the silicon die must travel through the IC packaging into the surrounding ambient air. The thermal behavior is modeled using **Thermal Ohm's Law**:

```
Δ T = P_D * θ_JA
```
```
T_J = T_A + (P_D * θ_JA)
```

Where:
- T_J: Silicon Junction Temperature (Maximum safe limit typically **+125°C** for commercial/industrial and **+150°C** for automotive).
- T_A: Ambient Air Operating Temperature (e.g., +25°C laboratory, +50°C industrial enclosure, +85°C automotive engine compartment).
- θ_JA: Junction-to-Ambient Thermal Resistance (°C/W).
- P_D: Total Power Dissipated in Watts.

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

```
θ_JA = θ_JC + θ_CS + θ_SA
```

---

### 2.1 Worked Numerical Example: Thermal Verification

**Operating Conditions**:
- V_IN = 5.0 V
- V_OUT = 3.3 V
- I_LOAD = 800 mA (0.8 A)
- Ambient Temperature: T_A = 50°C
- LDO Package: **SOT-223** with standard PCB layout (θ_JA = 65°C/W).

1. Calculate Power Dissipation:
   ```
P_D ≈ (5.0 V - 3.3 V) * 0.8 A = 1.7 V * 0.8 A = 1.36 W
```
2. Calculate Temperature Rise (Δ T):
   ```
Δ T = 1.36 W * 65°C/W = 88.4°C
```
3. Calculate Junction Temperature (T_J):
   ```
T_J = T_A + Δ T = 50°C + 88.4°C = 138.4°C
```
4. **Thermal Verdict**: **FAIL!**
   T_J exceeds the maximum safe limit (125°C) by 13.4°C. The LDO will enter thermal shutdown and cycle ON/OFF.

#### Sizing Maximum Permissible θ_JA with a Heat Sink / Thermal Vias:
```
θ_JA(max) <= (T_J(max) - T_A) / P_D = (125°C - 50°C) / 1.36 W = 75°C / 1.36 W ≈ 55.1°C/W
```
*Corrective Action*: Expand PCB thermal copper area or migrate to a **TO-263 (D2PAK)** package (θ_JA ≈ 30°C/W on 1 in^2 copper).

---

### 2.2 PCB Thermal Copper Sizing Rules
1. **Thermal Via Array**: Place a dense matrix of thermal vias (0.3 mm drill hole diameter, 1.0 mm ... 1.2 mm grid pitch) directly beneath the IC's exposed power thermal pad (PowerPAD / ePad).
2. **Internal Plane Stitching**: Connect thermal vias directly to internal and bottom-layer Ground/Power copper flood planes (1 oz or 2 oz copper) to distribute heat across the entire board surface.

---

## 3. Feedback Resistor Divider Network Sizing

For adjustable LDOs, the output voltage is configured using an external resistive voltage divider (R_1, R_2):

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
The feedback pin draws a minuscule input bias current (I_FB ≈ 10 nA ... 100 nA). The exact equation is:

```
V_OUT = V_REF * (1 + R1 / R2) + (I_FB * R1)
```

Where:
- V_OUT: Regulated DC output voltage (V)
- V_REF: Internal bandgap reference voltage (V)
- R1: Upper feedback divider resistor connected between V_OUT and FB pin (Ω)
- R2: Lower feedback divider resistor connected between FB pin and GND (Ω)
- I_FB: Input bias leakage current entering the error amplifier FB pin (A)

Because modern CMOS error amplifiers have I_FB < 50 nA, the second term is negligible when R_1 is sized reasonably (R_1 <= 100 kΩ):
```
V_OUT ≈ V_REF * (1 + R_1 / R_2)
```

Solving for the resistor ratio:
```
R_1 / R_2 = V_OUT / V_REF - 1
```

### 3.2 Sizing Guidelines & Current Trade-Offs
- **Divider Current (I_div)**: Sized to be at least 100* higher than I_FB to ensure thermal leakage currents do not cause output voltage drift:
  ```
I_div = V_REF / R_2 >= 100 * I_FB
```
- **Low-Power vs. High-PSRR Trade-Off**:
  - *Battery-operated micropower designs*: Select R_2 = 100 kΩ ... 500 kΩ (I_div ≈ 2 µA ... 10 µA) to maximize battery runtime.
  - *High-speed RF / Precision Analog designs*: Select R_2 = 1 kΩ ... 20 kΩ (I_div ≈ 60 µA ... 1.2 mA) to minimize Johnson-Nyquist thermal noise (e_n = sqrt(4k_B T R)) and prevent capacitive noise pick-up on the high-impedance FB node.

---

## 4. Feedforward Capacitor (C_FF) Phase-Lead Compensation

In adjustable LDO regulators, adding a small **Feedforward Capacitor (C_FF)** (10 pF ... 100 pF) in parallel with top resistor R_1 drastically improves dynamic performance:

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
With C_FF installed, the feedback impedance Z_1(s) = R_1 || 1 / (s C_FF). The transfer function from V_OUT to V_FB becomes:

```
V_FB(s) / V_OUT(s) = ( R_2 / (R_1 + R_2) ) * (1 + s R_1 C_FF) / (1 + s (R_1 || R_2) C_FF)
```

This introduces a **Phase-Lead Zero (f_z)** and a **High-Frequency Pole (f_p)**:

```
f_z_ff = 1 / (2π * R_1 * C_FF)
```
```
f_p_ff = 1 / (2π * (R_1 || R_2) * C_FF) = f_z_ff * (1 + R_1 / R_2)
```

### 4.2 Engineering Benefits of C_FF
1. **Phase Margin Boost**: The zero is placed near the unity-gain crossover frequency (10 kHz ... 100 kHz), injecting +20° ... +45° of phase boost to suppress transient ringing.
2. **Improved High-Frequency PSRR**: At higher frequencies, C_FF bypasses R_1, coupling output ripple directly to the inverting input of the error amplifier with unity gain rather than attenuated by R_2 / (R_1+R_2).
3. **Faster Load Step Recovery**: High-speed transient edges on V_OUT are fed directly to the error amplifier without experiencing the R_1 C_parasitic low-pass delay.

---

## 5. Output Capacitor Dynamic Sizing & ESR Zero

### 5.1 Sizing C_OUT for Load Transient Undershoot

When a digital load (such as a microcontroller awakening from sleep) suddenly steps its current demand from 0 to I_step in time t_edge ≈ 10 ns, the LDO error amplifier requires finite response time (t_response ≈ 2 µs ... 10 µs) to adjust the pass transistor gate.

During this brief window, **100\% of the step current must be supplied by the output capacitor (C_OUT)**:

```
Δ V_OUT ≈ (I_step * t_response) / C_OUT + (I_step * R_ESR)
```

Solving for the minimum required output capacitance:
```
C_OUT(min) >= (I_step * t_response) / (Δ V_allowed - (I_step * R_ESR))
```

*Worked Example*:
- Load step: I_step = 1.0 A
- Regulator response time: t_response = 5 µs
- Allowable voltage droop: Δ V_allowed = 100 mV
- Output capacitor ESR: R_ESR = 15 mΩ (I_step * R_ESR = 15 mV)

```
C_OUT(min) >= (1.0 A * 5 * 10^-6 s) / (0.100 V - 0.015 V) = (5.0 * 10^-6) / 0.085 V ≈ 58.8 µF
```

> [!WARNING]
> **Ceramic Capacitor DC Bias Derating Trap**:
> Multi-layer ceramic capacitors (MLCCs with X5R / X7R dielectrics) suffer severe loss of effective capacitance under DC voltage bias. A capacitor rated at 47 µF in an 0805 package may lose **40\% ... 70\%** of its capacitance when biased at 3.3 V or 5.0 V! Always inspect the manufacturer's DC Bias derating curves and parallel two or three capacitors to guarantee minimum C_OUT under operating voltage.

---

## 6. Root Cause Analysis (RCA) Troubleshooting Matrix

When debugging linear regulator circuits on the bench, consult this diagnostic reference:

| Observed Symptom | Oscilloscope Signature | Probable Root Cause | Verification & Corrective Action |
| :--- | :--- | :--- | :--- |
| **Output exhibits high-frequency continuous oscillation (100kHz - 2MHz).** | Sinusoidal AC waveform riding on V_OUT with peak-to-peak amplitude from 50 mV to > 1 V. | **Capacitor ESR outside the stability tunnel** (typically using an ultra-low ESR MLCC on an older PMOS LDO requiring ESR). | Check LDO datasheet stability curve. Insert a 0.5 Ω ... 1.0 Ω series carbon resistor in series with C_OUT to test. Add feedforward capacitor C_FF across R_1, or replace with a modern MLCC-stable LDO. |
| **Output voltage sags below nominal target under heavy load.** | V_OUT drops proportionally to I_LOAD; DC level is stable but low. | **Input voltage violation (V_IN - V_OUT < V_DO)**: The LDO has dropped out of regulation into its ohmic triode region. | Measure input voltage with an oscilloscope probe right at the IC's V_IN pin. Check for voltage drops across input wiring, PCB traces, or upstream filter ferrites. |
| **LDO operates for a few seconds, shuts off, cools down, and turns back on repeatedly.** | Sawtooth thermal cycling on V_OUT; IC package becomes scalding hot (> 130°C). | **Thermal overload shutdown**: Package power dissipation exceeds PCB heat dissipation capability (P_D * θ_JA). | Calculate P_D = (V_IN - V_OUT) * I_LOAD. Reduce V_IN headroom, increase PCB copper thermal pad area, add a heatsink, or pre-drop voltage with a switching buck converter. |
| **LDO is destroyed immediately upon powering down the system.** | Short circuit between V_IN and V_OUT or between V_IN and GND; silicon crater on die. | **Reverse current conduction**: Large C_OUT discharged backwards through the PMOS parasitic body diode into an unpowered input. | Install an external low-drop Schottky diode (e.g. `MBR0520`) with Anode on V_OUT and Cathode on V_IN to bypass reverse current, or select an LDO with internal reverse-current blocking. |
| **Excessive output ripple and noise matching upstream switching frequency.** | High-frequency triangular or sinusoidal ripple (500 kHz ... 2 MHz) passing through to V_OUT. | **Poor high-frequency PSRR** of the LDO, or capacitive noise coupling through feedback resistors. | Add a Noise Reduction capacitor (C_NR) on the bandgap pin. Add a feedforward capacitor (C_FF). Ensure feedback traces are kept short and shielded away from switching inductors. |
