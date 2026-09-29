# Depletion-Mode MOSFETs (d-MOSFET): Physics, Architecture & Applications

A **Depletion-Mode MOSFET** (**d-MOSFET**) is a unique class of field-effect transistor that is **normally-on** at zero gate-to-source bias ($V_{GS} = 0\,\text{V}$). Unlike enhancement-mode devices where a channel must be electrostatically induced, a depletion MOSFET features a physically doped semiconductor conduction channel formed during fabrication between the Source and Drain.

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
1. **Depletion Mode ($V_{GS} < 0\,\text{V}$ for N-Channel)**:
   - Applying a negative voltage to the gate repels electrons away from the oxide interface, squeezing and depleting the pre-existing $n$-channel.
   - When $V_{GS} \le V_{GS(off)}$ (the **Pinch-Off Voltage**, typically $-1.5\,\text{V} \dots -5.0\,\text{V}$), the channel is completely depleted of free electrons, choking off drain current ($I_D \approx 0$).
2. **Zero Bias ($V_{GS} = 0\,\text{V}$)**:
   - The device conducts naturally with drain saturation current $I_{DSS}$.
3. **Enhancement Mode ($V_{GS} > 0\,\text{V}$ for N-Channel)**:
   - If the gate is driven positively, additional electrons are attracted into the already conductive channel, further decreasing $R_{DS(on)}$ and increasing current capacity beyond $I_{DSS}$.

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
In the saturation region ($V_{DS} \ge V_{GS} - V_{GS(off)}$):
$$I_D = I_{DSS} \left( 1 - \frac{V_{GS}}{V_{GS(off)}} \right)^2$$
Where:
- $I_{DSS}$ is the drain current at $V_{GS} = 0\,\text{V}$.
- $V_{GS(off)}$ (or $V_P$) is the gate-to-source cutoff threshold (negative for N-channel, positive for P-channel).

---

## 3. High-Value Industrial Circuit Applications

### 1. Ultra-Low Standby Loss Offline SMPS High-Voltage Startup:
In universal AC-DC power converters ($85\,\text{V}_{AC} \dots 265\,\text{V}_{AC}$ rectified to $400\,\text{V}_{DC}$), high-value resistive bleeders ($100\,\text{k}\Omega$) waste continuous power during normal operation. A high-voltage depletion MOSFET (such as Supertex/Microchip DN2540) achieves **zero-standby startup**:

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
1. **Mains Applied**: At initial power-on, the PWM IC is dead ($V_{CC} = 0\,\text{V}$). The depletion MOSFET gate is at $0\,\text{V}$ ($V_{GS} = 0\,\text{V}$), so it conducts immediately, acting as a current source charging the bulk $V_{CC}$ capacitor.
2. **IC Boot**: Once $V_{CC}$ charges to the Under-Voltage Lockout threshold ($V_{UVLO} \approx 12\,\text{V}$), the PWM controller starts switching and powers itself from an auxiliary transformer winding.
3. **Lossless Disconnect**: The controller turns ON an auxiliary small-signal FET connected to the depletion MOSFET's gate, pulling the gate to ground while the source is at $+12\,\text{V}$. Thus:
   $$V_{GS} = V_G - V_S = 0\,\text{V} - 12\,\text{V} = -12\,\text{V} < V_{GS(off)}$$
   The depletion MOSFET is driven into total cutoff, drawing negligible leakage ($< 1\,\mu\text{A}$) and reducing standby power to $< 5\,\text{mW}$ to comply with Energy Star / EU CoC Tier 2 regulations.

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
Current flowing through $R_{SET}$ generates a voltage drop:
$$V_S = I_D \times R_{SET}$$
Since the gate is tied to the lower end of $R_{SET}$, $V_G = 0\,\text{V}$ relative to that node:
$$V_{GS} = V_G - V_S = -I_D \times R_{SET}$$
If $I_D$ attempts to surge due to an input voltage transient, $V_{GS}$ becomes more negative, constricting the channel and forcing the current back down to the target setpoint:
$$I_D = \frac{|V_{GS(off)}| \cdot \left(1 - \sqrt{I_D / I_{DSS}}\right)}{R_{SET}}$$

---

## 4. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | $V_{DS(max)}$ | $I_{DSS(min)}$ | $V_{GS(off)}$ Range | Typical Use-Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BSS126** | Infineon | SOT-23 | $600\,\text{V}$ | $30\,\text{mA}$ | $-1.4\,\text{V} \dots -2.1\,\text{V}$ | Offline SMPS startup, high-voltage active clamps |
| **BSP135** | Infineon | SOT-223 | $600\,\text{V}$ | $120\,\text{mA}$ | $-1.0\,\text{V} \dots -2.2\,\text{V}$ | Telecom line feeds, surge limiters |
| **DN2540** | Microchip (Supertex)| TO-220 / TO-92 | $400\,\text{V}$ | $150\,\text{mA}$ | $-1.5\,\text{V} \dots -3.5\,\text{V}$ | High-fidelity audio CCS, piezo drivers |
| **LND150** | Microchip (Supertex)| SOT-89 / TO-92 | $500\,\text{V}$ | $1.0\,\text{mA}$ | $-1.0\,\text{V} \dots -3.0\,\text{V}$ | Ultra-low power current limiters, smoke detectors |
| **IXTY02N120P**| IXYS / Littelfuse | TO-252 (DPAK) | $1200\,\text{V}$ | $200\,\text{mA}$ | $-2.0\,\text{V} \dots -4.5\,\text{V}$ | Industrial solar inverter startup (1000V bus) |
