# Controlled Phase-Rectifiers: Semi-Converters, Full-Converters & Quadrant Inversion

Welcome to the **VVDN Engineering Hub Technical Dossier on Controlled Phase-Rectifiers**. Controlled rectifiers replace passive silicon diodes with Silicon-Controlled Rectifiers (SCRs / Thyristors) to provide variable, regulated DC voltage from an AC power grid. 

Controlled rectifiers are the backbone of high-power DC motor drives (cranes, electric locomotives, rolling mills), battery charging stations, electrochemical chlor-alkali plants, and High-Voltage Direct Current (HVDC) transmission converter stations.

This guide provides an exhaustive hardware analysis covering single-phase and three-phase semi-converters and full-converters, firing delay angle $\alpha$ derivations, R-L-E load dynamics, and **Quadrant IV Line-Commutated Inversion** for regenerative braking.

---

## 1. Operating Principle & Rectifier Architectures

```text
                      Single-Phase Controlled Rectifier Architectures
   SEMI-CONVERTER (Half-Controlled: 2 SCRs + 2 Diodes)   FULL-CONVERTER (Fully-Controlled: 4 SCRs)
          Line ───┬──────────────────────┐                      Line ───┬──────────────────────┐
                  │                      │                              │                      │
                ┌─┴─┐ T1               ┌─┴─┐ T2                       ┌─┴─┐ T1               ┌─┴─┐ T3
                │SCR│                  │SCR│                          │SCR│                  │SCR│
                └─┬─┘                  └─┬─┘                          └─┬─┘                  └─┬─┘
                  ├──────────┬───────────┤                              ├──────────┬───────────┤
                  │          │           │                              │          │           │
                ┌─┴─┐ D1    ┌┴┐ D_FW   ┌─┴─┐ D2                       ┌─┴─┐ T4    ┌┴┐ Load   ┌─┴─┐ T2
                │>| │Diode  │ │ (Opt)  │>| │Diode                     │SCR│       │ │ R-L-E  │SCR│
                └─┬─┘       └┬┘        └─┬─┘                          └─┬─┘       └┬┘        └─┬─┘
                  │          │           │                              │          │           │
        Neutral ──┴──────────┴───────────┴─                  Neutral ───┴──────────┴───────────┴─
```

### 1.1 Semi-Converter vs. Full-Converter:
- **Semi-Converter (Single-Quadrant)**:
  - Consists of a mixture of diodes and SCRs (or includes a freewheeling diode).
  - Can only produce **positive DC voltage and positive DC current ($V_{dc} \ge 0, I_{dc} \ge 0$)**.
  - Operates exclusively in **Quadrant I** (Power flows strictly from AC grid to DC load).
  - Offers superior input power factor and lower reactive power consumption than full converters.
- **Full-Converter (Two-Quadrant)**:
  - All switching elements are thyristors (4 SCRs for single-phase; 6 SCRs for three-phase).
  - Current is unidirectional ($I_{dc} \ge 0$), but the average output DC voltage can be controlled **continuously from positive to negative ($-V_{max} \le V_{dc} \le +V_{max}$)** by varying firing angle $\alpha$ from $0^\circ$ to $180^\circ$.
  - Operates in **Quadrant I (Rectification)** and **Quadrant IV (Line-Commutated Inversion)**.

---

## 2. Operating Modes & Voltage Derivations

```text
               Full-Converter Output Voltage Waveforms Across Firing Angle
   v_out ^  Alpha = 30° (Rectification: Average Vdc > 0)
         │   /─\       /─\       /─\
      0V ┼──/───\─────/───\─────/───\───────────────────────────────────> Time
         │       \___/     \___/     \___/  (Vdc,avg is POSITIVE)
   v_out ^  Alpha = 90° (Zero Net Voltage: Vdc,avg = 0)
         │   /\        /\        /\
      0V ┼──/──\──────/──\──────/──\────────────────────────────────────> Time
         │      \    /    \    /    \    /  (Positive and Negative Areas Equal!)
         │       \  /      \  /      \  /
   v_out ^  Alpha = 120° (Inversion: Average Vdc < 0)
         │   /--\      /--\      /--\
      0V ┼──/────\────/────\────/────\──────────────────────────────────> Time
         │        \__/      \__/      \__/  (Vdc,avg is NEGATIVE!)
```

### 2.1 Single-Phase Full-Converter Formulation:
For continuous load current with an inductive load (R-L):
$$V_{dc,avg} = \frac{1}{\pi} \int_{\alpha}^{\pi + \alpha} V_m \sin(\omega t) \, d(\omega t) = \frac{V_m}{\pi} \left[ -\cos(\omega t) \right]_\alpha^{\pi + \alpha} = \frac{2 V_m}{\pi} \cos \alpha$$
Where $V_m = \sqrt{2} \cdot V_{ac,rms}$.
- **$\alpha = 0^\circ$**: $V_{dc} = \frac{2 \sqrt{2}}{\pi} V_{ac,rms} \approx 0.90 \cdot V_{ac,rms}$ (Maximum positive DC voltage).
- **$\alpha = 90^\circ$**: $V_{dc} = 0\,\text{V}$.
- **$\alpha > 90^\circ$**: $V_{dc}$ becomes **strictly negative**!

### 2.2 Three-Phase Six-Pulse Full-Converter Formulation:
The 6-pulse bridge conducts two thyristors simultaneously at any instant (one from top row, one from bottom row):
$$V_{dc,avg} = \frac{3}{\pi} \int_{\frac{\pi}{3} + \alpha}^{\frac{2\pi}{3} + \alpha} v_{LL}(t) \, d(\omega t) = \frac{3 \sqrt{2} \cdot V_{LL,rms}}{\pi} \cos \alpha \approx 1.35 \cdot V_{LL,rms} \cdot \cos \alpha$$

### 2.3 Single-Phase Semi-Converter Formulation:
Because the diodes (or freewheeling diode) clamp the output voltage to $0\,\text{V}$ whenever the AC line crosses zero, negative voltage excursions are prohibited:
$$V_{dc,avg} = \frac{1}{\pi} \int_{\alpha}^{\pi} V_m \sin(\omega t) \, d(\omega t) = \frac{V_m}{\pi} (1 + \cos \alpha) = \frac{\sqrt{2} V_{ac,rms}}{\pi} (1 + \cos \alpha)$$
Notice that $V_{dc,avg} \ge 0$ for all values of $\alpha$ ($0 \le \alpha \le \pi$).

---

## 3. Quadrant IV: Line-Commutated Inversion & Regenerative Braking

In industrial DC motor drives (such as elevators, cranes, and electric trains), decelerating an inertia load generates back-EMF energy. A fully-controlled converter allows this mechanical kinetic energy to be converted into electrical power and **pumped back into the AC utility grid**.

```text
               Two-Quadrant Operation of Full-Converter
                 +V_dc ^
                       │
          QUADRANT II  │  QUADRANT I: RECTIFICATION
          (Not Poss)   │  (0° <= Alpha < 90°)
                       │  Power: AC Grid -> DC Motor
         ──────────────┼─────────────────────────────> +I_dc
                       │
          QUADRANT III │  QUADRANT IV: INVERSION
          (Not Poss)   │  (90° < Alpha < 180°)
                       │  Power: DC Motor (Back-EMF) -> AC Grid
                 -V_dc v  (Regenerative Braking!)
```

### 3.1 Conditions for Inverter Operation:
1. **Firing Angle Delay**: Set $\alpha > 90^\circ$ (typically $\alpha = 120^\circ \dots 150^\circ$). This makes the converter terminal voltage $V_{dc}$ negative.
2. **Reversed DC Source Polarity**: The load DC source (motor back-EMF $E$ or battery) must be connected with its polarity opposing the converter's forward conducting direction ($E < 0$).
3. **Continuous Current**: An inductor in series with the DC circuit ensures the current remains continuous.
4. **Power Flow**:
   $$P = V_{dc} \cdot I_{dc} = (-|V_{dc}|) \cdot (+I_{dc}) < 0 \quad (\text{Power flows into the AC supply})$$

### 3.2 Commutation Failure Margin ($\gamma$):
A thyristor requires a finite turn-off recovery time ($t_q \approx 50 \dots 200\,\mu\text{s}$) to recombine internal minority carriers before positive forward voltage is reapplied.
- The extinction angle margin $\gamma$ must satisfy:
  $$\gamma = 180^\circ - (\alpha + u) \ge \omega \cdot t_q$$
  Where $u$ is the commutation overlap angle caused by AC line source inductance $L_s$.
- **Disaster Hazard**: If $\alpha$ is pushed too close to $180^\circ$ ($\alpha > 165^\circ$), the incoming SCR fails to turn off before forward voltage returns. The bridge enters **Commutation Failure**, causing a catastrophic DC short circuit that trips high-speed fuses!

---

## 4. Input Power Factor & Reactive Power Consumption

A major hardware disadvantage of phase-controlled thyristor rectifiers is their high demand for reactive power (VAR) from the electrical utility grid:
- **Displacement Power Factor**:
  $$\text{DPF} = \cos \alpha$$
- As the firing angle $\alpha$ increases to reduce output DC voltage (e.g., slowing down a DC motor), the phase displacement between input voltage and fundamental input current widens directly with $\alpha$.
- At $\alpha = 60^\circ$, $\text{DPF} = \cos(60^\circ) = 0.50$ lagging.
- The utility must supply massive reactive power even when the active real power delivered to the motor shaft is small, incurring heavy power factor utility penalties.
