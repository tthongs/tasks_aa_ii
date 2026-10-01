# Controlled Phase-Rectifiers: Semi-Converters, Full-Converters & Quadrant Inversion

Welcome to the **VVDN Engineering Hub Technical Dossier on Controlled Phase-Rectifiers**. Controlled rectifiers replace passive silicon diodes with Silicon-Controlled Rectifiers (SCRs / Thyristors) to provide variable, regulated DC voltage from an AC power grid. 

Controlled rectifiers are the backbone of high-power DC motor drives (cranes, electric locomotives, rolling mills), battery charging stations, electrochemical chlor-alkali plants, and High-Voltage Direct Current (HVDC) transmission converter stations.

This guide provides an exhaustive hardware analysis covering single-phase and three-phase semi-converters and full-converters, firing delay angle $\alpha$ derivations, R-L-E load dynamics, and **Quadrant IV Line-Commutated Inversion** for regenerative braking.

---

## 1. Operating Principle & Rectifier Architectures

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: SINGLE-PHASE FULLY-CONTROLLED THYRISTOR BRIDGE (230V AC -> 0-200V DC / 25A)
========================================================================================================================

    AC LINE (230V RMS) ──[ F1: 30A Fast ]──┬─────────────────────────────────────────────────────────────┐
                                           │                                                             │
                                          ┌┴┐ MOV1: 275V RMS                                             │
                                          │ │ (Surge Clamp)                                              │
                                          └┬┘                                                            │
    AC NEUTRAL ────────────────────────────┼───────────────────────────┬─────────────────────────────────┼───+
                                           │                           │                                 │   │
                                           │                           │                                 │   │
                                       Anode (A)                   Anode (A)                             │   │
                                      ┌────┴──────────┐           ┌────┴──────────┐                      │   │
                                      │ T1: THYRISTOR │           │ T3: THYRISTOR │                      │   │
                                      │ Vishay 40TPS12│           │ Vishay 40TPS12│                      │   │
                               +----->│ (1200V, 35A)  │    +----->│ (1200V, 35A)  │                      │   │
                               | Gate └────┬──────────┘    | Gate └────┬──────────┘                      │   │
                               |     Cath  │               |     Cath  │                                 │   │
                               |           │               |           │                                 │   │
                               |           +---------------+-----------+=== COMMON CATHODE DC+           │   │
                               |           |                                (0V to +207V Controlled)     │   │
                               |           |                                                             │   │
                               |           ├──[ R_snub: 22Ω / 5W ]         +=== LOAD TERMINAL +          │   │
                               |           │         │                     |                             │   │
                               |           │   [ C_snub: 0.1µF / 630V ]    +---[ L_filter: 50mH / 25A ]--+   │
                               |           │         │                         (DC Smoothing Choke)      │   │
                               |           │      AC LINE                                                │   │
                               |           │                                                             │   │
                               |       Cath│                                                           ┌─┴─┐ │
                               |      ┌────┴──────────┐                                                │ R │ │
                               |      │ T4: THYRISTOR │                                                │ L │ │
                               |      │ Vishay 40TPS12│                                                │ O │ │
                               |   +->│ (1200V, 35A)  │                                                │ A │ │
                               |   |  └────┬──────────┘                                                │ D │ │
                               |   |  Anode│                                                           └─┬─┘ │
                               |   |       │                                                             │   │
                               |   |       +---------------------------+=== COMMON ANODE DC-             │   │
                               |   |                                   |    (Return Reference)           │   │
                               |   |                                   |                                ┌┴┐  │
                               |   |                               Cath│                                │-│  │
                               |   |                              ┌────┴──────────┐                     │E│  │
                               |   |                              │ T2: THYRISTOR │                     │+│  │
                               |   |                              │ Vishay 40TPS12│                     └┬┘  │
                               |   |                       +----->│ (1200V, 35A)  │                      │   │
                               |   |                       | Gate └────┬──────────┘                      │   │
                               |   |                       |      Anode│        (DC Motor Back-EMF)      │   │
                               |   |                       |           │                                 │   │
                               |   |                       |           +─────────────────────────────────┼───+
                               |   |                       |           │                                 │
                               +---|-----------------------|-----------|---[ PULSE TRANSFORMER TX1: GATE 1 & 2 ]
                                   +-----------------------+-----------|---[ PULSE TRANSFORMER TX2: GATE 3 & 4 ]
                                                                       │     (Isolated Trigger: 1:1, 100mA Firing Pulse)
                                                                       │
    AC NEUTRAL ────────────────────────────────────────────────────────┴────────────────────────────────────────
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **AC_LINE** | AC Mains Live Feed | $T_1$ Anode, $T_4$ Cathode, Snubber | Input AC phase branch 1 | Line input connects between upper and lower thyristors of Leg 1. |
| **AC_NEUTRAL** | AC Mains Neutral Feed | $T_3$ Anode, $T_2$ Cathode, Snubber | Input AC phase branch 2 | Neutral connects between upper and lower thyristors of Leg 2. |
| **DC_POS (+)** | Thyristors $T_1, T_3$ Cathodes | DC Smoothing Choke $L_{filter}$ Input | Controlled DC positive bus | Average DC voltage is $V_{dc} = \frac{2 V_m}{\pi} \cos \alpha$; can invert when $\alpha > 90^\circ$. |
| **DC_NEG (-)** | Thyristors $T_4, T_2$ Anodes | DC Motor / Load Negative Terminal | Controlled DC return rail | Commutated return carrying continuous unidirectional DC current. |
| **GATE_1_4** | Pulse Transformer TX1 Secondary | Thyristors $T_1, T_2$ Gate-Cathode Pins | Synchronized gate firing pulse train | Fired simultaneously at angle $\alpha$ during positive utility half-cycle. |
| **GATE_3_2** | Pulse Transformer TX2 Secondary | Thyristors $T_3, T_4$ Gate-Cathode Pins | Synchronized gate firing pulse train | Fired simultaneously at angle $\pi + \alpha$ during negative utility half-cycle. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **$T_1 \dots T_4$** | Phase-Control Thyristors | Vishay Semiconductors 40TPS12 | $V_{RRM} = 1200\,\text{V}, I_{T(AV)} = 35\,\text{A}, I_{GT} = 150\,\text{mA}, V_{TM} = 1.45\,\text{V}$ | $1200\,\text{V}$ rating easily withstands $325\,\text{V}$ peak grid voltage plus motor back-EMF spikes. |
| **$R_{snub}, C_{snub}$**| Thyristor RC Snubbers | Ohmite 280 / KEMET PHE450 | $R = 22\,\Omega / 5\,\text{W Wirewound}, C = 0.1\,\mu\text{F} / 630\,\text{V Film}$ | Restricts rate of off-state voltage rise to $\frac{dv}{dt} < 500\,\text{V}/\mu\text{s}$ to prevent false $dv/dt$ triggering. |
| **$TX_1, TX_2$** | Gate Pulse Transformers | Pulse Electronics PE-64936 | Ratio: $1:1, V_{isolation} = 3000\,\text{V}_{RMS}, E-T = 150\,\text{V}\cdot\mu\text{s}$ | Delivers sharp $150\,\text{mA}, 10\,\mu\text{s}$ firing pulses with steep rise time ($< 100\,\text{ns}$). |
| **$L_{filter}$** | DC Smoothing Inductor | Hammond Mfg 195J25 | $L = 50\,\text{mH}, I_{DC} = 25\,\text{A}, DCR = 85\,\text{m}\Omega$ | Heavy laminated iron core choke guarantees continuous conduction down to $5\%$ rated current. |


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
