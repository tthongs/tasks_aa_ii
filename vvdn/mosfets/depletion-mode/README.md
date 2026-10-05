# Depletion-Mode MOSFETs (d-MOSFET): Physics, Architecture & Applications

A **Depletion-Mode MOSFET** (**d-MOSFET**) is a unique class of field-effect transistor that is **normally-on** at zero gate-to-source bias (V_GS = 0 V). Unlike enhancement-mode devices where a channel must be electrostatically induced, a depletion MOSFET features a physically doped semiconductor conduction channel formed during fabrication between the Source and Drain.

---

## 1. Semiconductor Physics & Device Structure

```text
                             Gate (G)
                                │
                          ┌─────┴─────┐ Poly-Si / Metal Gate
                          │   GATE    │
                     ┌────┴───────────┴────┐
                     │  Gate Oxide (SiO2)  │
     ┌───────────────┴─────────────────────┴───────────────┐
     │  Source (n+)                          Drain (n+)    │
  ───┤  ┌───────┐     Physically Implanted     ┌───────┐   ├───
 (S) │  │  n+   │  == n-Channel Layer (Doped) =│  n+   │   │  (D)
     └──┴───────┴──────────────────────────────┴───────┴───┘
     │            Depletion Layer (Wdep)                   │
     │  - - - - - - - - - - - - - - - - - - - - - - - - -  │
     │                 p-type Substrate                    │
     │                                                     │
     └──────────────────────────┬──────────────────────────┘
                                │
                            Body (B)
```

### Modes of Operation (Dual-Mode Flexibility):
1. **Depletion Mode (V_GS < 0 V for N-Channel)**:
   - Applying a negative voltage to the gate repels electrons away from the oxide interface, squeezing and depleting the pre-existing n-channel.
   - When V_GS <= V_GS(off) (the **Pinch-Off Voltage**, typically -1.5 V ... -5.0 V), the channel is completely depleted of free electrons, choking off drain current (I_D ≈ 0).
2. **Zero Bias (V_GS = 0 V)**:
   - The device conducts naturally with drain saturation current I_DSS.
3. **Enhancement Mode (V_GS > 0 V for N-Channel)**:
   - If the gate is driven positively, additional electrons are attracted into the already conductive channel, further decreasing R_DS(on) and increasing current capacity beyond I_DSS.

---

## 2. Terminal Characteristic Curves & Mathematical Model

```text
     Drain Current (Id) vs Gate-to-Source Voltage (Vgs)
  Id ^
     │                             (Enhancement Mode: Vgs > 0)
     │                           /
     │                          /
Idss ├─────────────────────────*  (Vgs = 0V: Id = Idss)
     │                       /
     │                      /  (Depletion Mode: Vgs < 0)
     │                    /
     │                  /
     │                 /
   0 └────────────────*──────────────────────────────────> Vgs
                   Vgs(off) (Pinch-off)
```

### Mathematical Equation (Shockley / Depletion Model):
In the saturation region (V_DS >= V_GS - V_GS(off)):
```
I_D = I_DSS * [ 1 - (V_GS / V_GS(off)) ]^2
```

Where:
- I_D: Operating drain saturation current (A)
- I_DSS: Zero-bias drain saturation current at V_GS = 0V (A)
- V_GS: Applied gate-to-source voltage (V)
- V_GS(off): Pinch-off cutoff voltage threshold (negative for N-channel, positive for P-channel) (V)

---

## 3. High-Value Industrial Circuit Applications

### 1. Ultra-Low Standby Loss Offline SMPS High-Voltage Startup:
In universal AC-DC power converters (85 V_AC ... 265 V_AC rectified to 400 V_DC), high-value resistive bleeders (100 kΩ) waste continuous power during normal operation. A high-voltage depletion MOSFET (such as Supertex/Microchip DN2540) achieves **zero-standby startup**:

```text
       +400V DC High-Voltage Bus (Rectified Mains)
             │
          Drain (D)
             │
          ┌──┴──┐
          │     │ Depletion NMOS (DN2540: 400V rated)
          │     │ [Normally ON at Vgs = 0V]
          └──┬──┘
             │ Source (S)
             ├──────────────────┬──────────────────> VCC Rail to PWM Controller IC
             │                  │
            [R_bias]          ┌─┴─┐
             │                │   │ Bulk Cap (47µF, 25V)
             │                └─┬─┘
          Gate (G)              │
             │                 GND
             ├── Drain of Auxiliary N-FET (Controlled by PWM IC)
             │
            GND
```

#### Sequence of Events:
1. **Mains Applied**: At initial power-on, the PWM IC is dead (V_CC = 0 V). The depletion MOSFET gate is at 0 V (V_GS = 0 V), so it conducts immediately, acting as a current source charging the bulk V_CC capacitor.
2. **IC Boot**: Once V_CC charges to the Under-Voltage Lockout threshold (V_UVLO ≈ 12 V), the PWM controller starts switching and powers itself from an auxiliary transformer winding.
3. **Lossless Disconnect**: The controller turns ON an auxiliary small-signal FET connected to the depletion MOSFET's gate, pulling the gate to ground while the source is at +12 V. Thus:
   ```
V_GS = V_G - V_S = 0 V - 12 V = -12 V < V_GS(off)
```
   The depletion MOSFET is driven into total cutoff, drawing negligible leakage (< 1 µA) and reducing standby power to < 5 mW to comply with Energy Star / EU CoC Tier 2 regulations.

---

### 2. High-Precision Two-Terminal Constant-Current Source:
A depletion MOSFET combined with a single self-biasing source resistor forms a robust, floating two-terminal constant current regulator (CCR) requiring no external power supply:

```text
          (+) Input Terminal (up to 400V)
                 │
              Drain (D)
                 │
              ┌──┴──┐
              │     │ Depletion NMOS (e.g. LND150)
              └──┬──┘
                 │ Source (S)
                 ├───┐
                 │  [R_SET] (Sets current: R_SET = |Vgs| / I_target)
                 │   │
              Gate (G)
                 │   │
                 └───┴─────────────────────────────> (-) Output Terminal
```

#### Self-Biasing Negative Feedback:
Current flowing through R_SET generates a voltage drop:
```
V_S = I_D * R_SET
```
Since the gate is tied to the lower end of R_SET, V_G = 0 V relative to that node:
```
V_GS = V_G - V_S = -I_D * R_SET
```
If I_D attempts to surge due to an input voltage transient, V_GS becomes more negative, constricting the channel and forcing the current back down to the target setpoint:
```
I_D = [ |V_GS(off)| * (1 - sqrt(I_D / I_DSS)) ] / R_SET
```

Where:
- I_D: Regulated constant drain current delivered to the load (A)
- |V_GS(off)|: Absolute pinch-off cutoff threshold voltage (V)
- I_DSS: Zero-gate-bias saturation current (A)
- R_SET: Source degeneration current-setting resistor (Ω)
- V_S: Self-biasing voltage developed across R_SET, V_S = I_D * R_SET (V)
- V_GS: Negative gate-to-source self-bias voltage, V_GS = -I_D * R_SET (V)

---

## 4. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | V_DS(max) | I_DSS(min) | V_GS(off) Range | Typical Use-Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BSS126** | Infineon | SOT-23 | 600 V | 30 mA | -1.4 V ... -2.1 V | Offline SMPS startup, high-voltage active clamps |
| **BSP135** | Infineon | SOT-223 | 600 V | 120 mA | -1.0 V ... -2.2 V | Telecom line feeds, surge limiters |
| **DN2540** | Microchip (Supertex)| TO-220 / TO-92 | 400 V | 150 mA | -1.5 V ... -3.5 V | High-fidelity audio CCS, piezo drivers |
| **LND150** | Microchip (Supertex)| SOT-89 / TO-92 | 500 V | 1.0 mA | -1.0 V ... -3.0 V | Ultra-low power current limiters, smoke detectors |
| **IXTY02N120P**| IXYS / Littelfuse | TO-252 (DPAK) | 1200 V | 200 mA | -2.0 V ... -4.5 V | Industrial solar inverter startup (1000V bus) |
