# Dossier 2: Power Stage Magnetics & Filter Sizing

Welcome to **Dossier 2** of the Step-by-Step 4-Switch Synchronous Buck-Boost Post-Regulator Design Guide. This document details the mathematical sizing, saturation margins, component selection, and thermal loss calculations for the power inductor ($L$), input capacitor bank ($C_{IN}$), and output capacitor bank ($C_{OUT}$).

---

## Step 3: Power Inductor Sizing ($L$)

The inductor must maintain Continuous Conduction Mode (CCM) across the operational envelope while balancing peak saturation current, physical dimensions, core loss, and transient dynamic slew rate.

```text
                                 INDUCTOR CURRENT RIPPLE WAVEFORM (CCM)
  Inductor Current (I_L)
    ^
    │                               /|                           /|
    │                              / |                          / |
I_pk┼─────────────────────────────/──|─────────────────────────/──|──── Peak Current = 5.95 A
    │                            /   |                        /   |
    │                           /    |                       /    |
I_avg ─────────────────────────/─────|──────────────────────/─────|──── Average Current = 3.0 A
    │                         /      |                     /      |
    │                        /       |                    /       |
I_val ──────────────────────/        |                   /        |──── Valley Current = 2.1 A
    │                      /         |                  /         |
    │                     /          |                 /          |
 0A ┴────────────────────/           |────────────────/           |────> Time
                         <── D*Ts ───><── (1-D)*Ts ──>
```

### 3.1 Inductor Sizing Derivations:
1. **Target Ripple Current Ratio ($r$)**:
   A ripple ratio of $r = \frac{\Delta I_L}{I_{OUT}} = 30\%$ at rated current ($I_{OUT} = 3.0\,\text{A}$) provides the optimum balance between AC core losses and physical inductor size:
   $$\Delta I_L = 0.30 \times 3.0\,\text{A} = 0.90\,\text{A}$$
2. **Buck Mode Inductance Formula**:
   In buck mode, the inductor current ramps up during $t_{on} = D \cdot T_s$:
   $$L = \frac{(V_{IN} - V_{OUT}) \cdot D}{\Delta I_L \cdot f_{sw}} = \frac{V_{OUT} \cdot (V_{IN} - V_{OUT})}{\Delta I_L \cdot f_{sw} \cdot V_{IN}}$$
   The maximum ripple condition occurs at $V_{OUT} = \frac{V_{IN}}{2} = 12.0\,\text{V}$ ($D = 50\%$):
   $$L = \frac{12.0 \cdot (24.0 - 12.0)}{0.90 \cdot 250000 \cdot 24.0} = \frac{144}{5.4 \times 10^6} = 2.67 \times 10^{-5}\,\text{H} \approx 26.7\,\mu\text{H}$$
3. **Optimized Component Selection: $L = 10.0\,\mu\text{H}$**:
   While an ideal $30\%$ ripple at $12\,\text{V}$ dictates $26.7\,\mu\text{H}$, practical compact designs select **$10.0\,\mu\text{H}$** for the following engineering reasons:
   * **Transient Response**: Slew rate is inversely proportional to inductance:
     $$\frac{di}{dt} = \frac{V_L}{L} = \frac{24.0\,\text{V} - 12.0\,\text{V}}{10\,\mu\text{H}} = 1.20\,\text{A}/\mu\text{s} \quad (\text{vs. only } 0.45\,\text{A}/\mu\text{s} \text{ for } 26.7\,\mu\text{H})$$
     A $10\,\mu\text{H}$ inductor recovers from a $1.5\,\text{A} \rightarrow 3.0\,\text{A}$ load step **2.6x faster**!
   * **DCR & Footprint**: A $10\,\mu\text{H}$ flat-wire inductor has half the DC resistance ($11.8\,\text{m}\Omega$) of an equivalent $27\,\mu\text{H}$ inductor ($28\,\text{m}\Omega$), saving $0.15\,\text{W}$ in thermal losses.
   * **Ripple Current with $10\,\mu\text{H}$ at $20\,\text{V} / 3\,\text{A}$ (Buck-Boost regime)**:
     $$\Delta I_L = \frac{V_{IN} \cdot D}{\Delta L \cdot f_{sw}} \approx 1.20\,\text{A} \quad (\text{Well within continuous conduction limits}).$$

### 3.2 Peak & RMS Inductor Current:
Under full-load $20.0\,\text{V} / 3.0\,\text{A}$ operation ($P_{OUT} = 60.0\,\text{W}$), input current is:
$$I_{IN} = \frac{P_{OUT}}{\eta \cdot V_{IN}} = \frac{60.0\,\text{W}}{0.96 \times 24.0\,\text{V}} = 2.60\,\text{A}$$
* **Peak Inductor Current ($I_{L(pk)}$)**:
  $$I_{L(pk)} = I_{IN} + I_{OUT} + \frac{\Delta I_L}{2} = 2.60\,\text{A} + 3.00\,\text{A} + 0.60\,\text{A} = \mathbf{5.95\,\text{A}}$$
* **RMS Inductor Current ($I_{L(rms)}$)**:
  $$I_{L(rms)} = \sqrt{I_{L(avg)}^2 + \frac{\Delta I_L^2}{12}} = \sqrt{(3.00)^2 + \frac{(1.20)^2}{12}} = \sqrt{9.0 + 0.12} = \mathbf{3.02\,\text{A}_{\text{RMS}}}$$

### 3.3 Inductor Component Selection:
* **Selected Part**: **Wurth Elektronik 7443321000** (WE-HCC flat-wire shielded power inductor):
  * Nominal Inductance: $10.0\,\mu\text{H} \pm 20\%$
  * Rated Continuous Current ($I_{rms}$): $8.5\,\text{A}$ ($\Delta T = 40^\circ\text{C}$ rise)
  * Saturation Current ($I_{sat}$ at $30\%$ drop): **$11.5\,\text{A}$**
  * **Saturation Margin**:
    $$\text{Margin} = \frac{I_{sat} - I_{L(pk)}}{I_{sat}} = \frac{11.5\,\text{A} - 5.95\,\text{A}}{11.5\,\text{A}} = \mathbf{48.3\% \text{ safety margin over peak!}}$$
  * DC Resistance ($R_{DC}$): $11.8\,\text{m}\Omega \pm 10\%$
  * Copper Conduction Loss:
    $$P_{cu} = I_{L(rms)}^2 \times R_{DC} = (3.02\,\text{A})^2 \times 0.0118\,\Omega = \mathbf{0.108\,\text{W}}$$
  * Core Loss ($P_{core}$ via Steinmetz model): $\approx 0.14\,\text{W}$ at $250\,\text{kHz}$.
  * Total Inductor Thermal Dissipation: $P_{ind} = 0.108 + 0.14 = \mathbf{0.248\,\text{W}}$ (runs cool at $\Delta T \approx 12^\circ\text{C}$).

---

## Step 4: Input Capacitor Bank Sizing ($C_{IN}$)

In buck and buck-boost operation, the high-side switch $Q_A$ draws chopped, high $di/dt$ rectangular current pulses from the input bus.

```text
                                INPUT CAPACITOR CURRENT WAVEFORM
  Input Current (I_in)
    ^
I_L ┼──────────────┌────────────────┐                             ┌────────────────┐
    │              │                │                             │                │
    │              │                │                             │                │
 0A ┴──────────────┴────────────────┴─────────────────────────────┴────────────────┴────> Time
    <── D*Ts ──────><────── (1-D)*Ts ────────────────────────────>
```

### 4.1 RMS Ripple Current Stress:
Worst-case input RMS ripple current occurs in buck mode at $D = 50\%$:
$$I_{Cin(rms)} = I_{OUT} \cdot \sqrt{D \cdot (1 - D)} = 3.0\,\text{A} \times \sqrt{0.5 \times 0.5} = \mathbf{1.50\,\text{A}_{\text{RMS}}}$$

### 4.2 Capacitance Sizing:
Allowing a maximum input ripple of $\Delta V_{IN} \le 40\,\text{mV}_{\text{pk-pk}}$:
$$C_{IN(min)} = \frac{I_{OUT} \cdot D \cdot (1 - D)}{f_{sw} \cdot \Delta V_{IN}} = \frac{3.0 \times 0.25}{250000 \times 0.040} = 7.5 \times 10^{-5}\,\text{F} = \mathbf{75\,\mu\text{F}}$$

### 4.3 Capacitor Bank Configuration:
1. **High-Frequency MLCCs**: $2\times 22\,\mu\text{F} / 35\,\text{V}$ 1210 X7R Ceramic capacitors (TDK C3225X7R1V226M) placed directly across the drain of $Q_A$ and source of $Q_B$. Absorbs high $di/dt$ edges ($< 5\,\text{ns}$).
2. **Bulk Electrolytic / Polymer**: $1\times 100\,\mu\text{F} / 35\,\text{V}$ Panasonic OS-CON Aluminum Polymer (25SVPF100M, $\text{ESR} = 16\,\text{m}\Omega$, rated ripple current $2.8\,\text{A}_{\text{RMS}}$).

---

## Step 5: Output Capacitor Bank Sizing ($C_{OUT}$)

The output capacitor bank filters the inductor ripple current and supplies energy during dynamic load steps ($1.5\,\text{A} \rightarrow 3.0\,\text{A}$).

### 5.1 Ripple Voltage Breakdown:
Total peak-to-peak output ripple is the sum of capacitive charge storage, ESR, and ESL:
$$\Delta V_{OUT} = \Delta V_C + \Delta V_{ESR} + \Delta V_{ESL}$$

1. **Capacitive Ripple Component**:
   $$\Delta V_C = \frac{\Delta I_L}{8 \cdot f_{sw} \cdot C_{OUT}} = \frac{1.20\,\text{A}}{8 \times 250000 \times 88 \times 10^{-6}} = \mathbf{6.8\,\text{mV}_{\text{pk-pk}}}$$
2. **ESR Ripple Component**:
   $$\Delta V_{ESR} = \Delta I_L \cdot \text{ESR}_{total} = 1.20\,\text{A} \times 2.5\,\text{m}\Omega = \mathbf{3.0\,\text{mV}_{\text{pk-pk}}}$$
3. **Total Combined Ripple**:
   $$\Delta V_{OUT} \approx \sqrt{(\Delta V_C)^2 + (\Delta V_{ESR})^2} = \sqrt{(6.8)^2 + (3.0)^2} = \mathbf{7.4\,\text{mV}_{\text{pk-pk}}}$$
   This easily beats the stringent target limit of $< 25\,\text{mV}_{\text{pk-pk}}$!

### 5.2 DC Voltage Bias Derating in Ceramic MLCCs:
> [!WARNING]
> Class-II ferroelectric dielectric materials (X5R, X7R) experience drastic capacitance loss when subjected to DC bias voltage. A $22\,\mu\text{F} / 25\,\text{V}$ 1210 ceramic capacitor loses **$\approx 55\%$ of its nominal capacitance** at $20.0\,\text{V}$ DC bias!

* **Effective Ceramic Bank Capacitance**:
  $$C_{cer(eff)} = 4 \times (22\,\mu\text{F} \times 0.45) = 4 \times 9.9\,\mu\text{F} = \mathbf{39.6\,\mu\text{F}}$$
* **Polymer Bulk Capacitor Addition**:
  To guarantee stability during $1.5\,\text{A} \rightarrow 3.0\,\text{A}$ load steps, $1\times 100\,\mu\text{F} / 25\,\text{V}$ Panasonic OS-CON Polymer capacitor ($\text{ESR} = 12\,\text{m}\Omega$) is placed in parallel.
* **Combined Output Bank**:
  * Nominal Capacitance: $4\times 22\,\mu\text{F} + 100\,\mu\text{F} = \mathbf{188\,\mu\text{F}}$
  * Effective Capacitance at 20V DC: $\approx \mathbf{140\,\mu\text{F}}$
  * Combined Parallel ESR: $\mathbf{< 2.5\,\text{m}\Omega}$

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             FILTER COMPONENT SPECIFICATION SUMMARY                               │
├─────────────────────┬──────────────┬──────────────┬──────────────┬───────────────────────────────┤
│ Component           │ Value / Unit │ Voltage / Pkg│ Manufacturer │ Part Number                   │
├─────────────────────┼──────────────┼──────────────┼──────────────┼───────────────────────────────┤
│ **Power Inductor L**│ 10.0 µH / 8.5A│ 10x10mm SMD  │ Wurth Elek.  │ 7443321000 (DCR=11.8mΩ)       │
│ **C_IN Ceramic**    │ 2x 22 µF     │ 35V / 1210   │ TDK          │ C3225X7R1V226M                │
│ **C_IN Polymer**    │ 1x 100 µF    │ 35V / Radial │ Panasonic    │ 35SVPF100M (ESR=16mΩ)         │
│ **C_OUT Ceramic**   │ 4x 22 µF     │ 25V / 1210   │ Murata       │ GRM32ER71E226KE15L            │
│ **C_OUT Polymer**   │ 1x 100 µF    │ 25V / SMD    │ Panasonic    │ 25SVPF100M (ESR=12mΩ)         │
└─────────────────────┴──────────────┴──────────────┴──────────────┴───────────────────────────────┘
```
