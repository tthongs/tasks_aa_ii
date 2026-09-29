# Vertical Double-Diffused MOSFETs (VDMOS / Planar Power): Physics & Applications

A **Vertical Double-Diffused MOSFET** (**VDMOS**), frequently referred to as a **Planar Power MOSFET**, was the foundational architecture that catalyzed the solid-state power electronics revolution (pioneered as International Rectifier HEXFET®). Fabricated using sequential thermal double-diffusions of p-type body and n-type source regions beneath a planar surface gate, the VDMOS routes current vertically through an epitaxial drift layer to the backside drain. 

Even in the era of trench and superjunction devices, VDMOS remains irreplaceable in applications demanding **high avalanche energy ($E_{AS}$)** ruggedness, wide **Safe Operating Area (SOA)** for linear-mode operation, and extreme immunity to inductive surge transients.

---

## 1. Semiconductor Physics & Device Cross-Section

```text
                     Source Metal (Al)
          ───────────────────────────────────────────
          ┌────────┐                       ┌────────┐
          │   n+   │                       │   n+   │ Source
          ├────────┴─────┐           ┌─────┴────────┤
          │   p-Body     │  Channel  │    p-Body    │
          └──────────────┤  <=====>  ├──────────────┘
                         │   JFET    │
                   ┌─────┴───Neck────┴─────┐
                   │   SiO2 Gate Oxide     │
                   ├───────────────────────┤
                   │   Poly-Si Gate (G)    │
                   └───────────────────────┘
          ───────────────────────────────────────────
          │                                         │
          │         n- Epitaxial Drift Layer        │ (High-voltage blocking)
          │                                         │
          ───────────────────────────────────────────
          │               n+ Substrate              │
          ───────────────────────────────────────────
          │           Drain Metal (Backside)        │
```

### Self-Aligned Double-Diffusion Mechanics:
1. **P-Body Diffusion**: P-type dopants (Boron) are implanted through openings in the gate oxide and thermally diffused deeply both vertically and laterally beneath the polysilicon gate edge.
2. **N+ Source Diffusion**: N-type dopants (Phosphorus/Arsenic) are subsequently implanted using the **exact same gate mask edge** as a reference. Because boron diffuses faster and further laterally than arsenic, the difference in lateral penetration precisely defines the **sub-micron channel length ($L_{ch} \approx 0.5\,\mu\text{m} - 1.5\,\mu\text{m}$)** without demanding expensive sub-micron lithography alignment!
3. **Current Path**:
   - Current flows horizontally through the surface channel in the p-body.
   - It converges into the planar neck between adjacent p-wells—known as the **JFET region**.
   - It expands and flows vertically through the lightly doped $n^-$ drift region down to the drain header.

---

## 2. Linear Mode Operation & The Spirito Effect (Thermal Instability)

When a MOSFET is operated not as a switch, but as an active linear pass element (such as in **Electronic DC Loads**, **Hot-Swap Inrush Controllers**, or **Linear Audio Amplifiers**), the transistor operates continuously in its saturation region ($V_{DS} \gg 0$, $I_D \gg 0$):

```text
                  Safe Operating Area (SOA) Comparison
       Id ^
          │      100µs Pulse (Bondwire limit)
          │──┐
          │  │\
          │  │ \  1ms Pulse
          │  │  \
          │  │   \  DC Operating Limit
          │  │    \
          │  │     \   Modern Trench FET (Severe Spirito instability!)
          │  │      \   (Channel current concentrates into hot spots)
          │  │       \   . . . . . . . . . . . . . . . . .
          │  │        \                                   :
          │  │         \   Planar VDMOS (Robust Linear SOA)
          │  │          \  (Uniform temperature distribution)
          └───────────────────────────────────────────────> Vds
```

### Why VDMOS Outperforms Trench FETs in Linear Mode:
- **Temperature Coefficient of Threshold Voltage ($V_{TH}$)**:
  $V_{TH}$ has a negative temperature coefficient ($\approx -4\,\text{mV}/^\circ\text{C}$). As a silicon cell gets hotter, its threshold drops, which encourages *more* drain current to flow through that localized spot.
- **Zero Temperature Coefficient (ZTC) Point**:
  At high drain currents, the positive temperature coefficient of carrier mobility ($\mu_n(T) \propto T^{-1.5}$) counteracts the $V_{TH}$ effect. The current where these two effects cancel is the **ZTC point**.
- In modern ultra-dense **Trench MOSFETs**, the cell density is so high that the ZTC current is pushed to extreme levels ($> 50\,\text{A}$). When operated in linear mode at low-to-moderate currents, localized hot spots experience runaway current concentration (the **Spirito Effect**), causing thermal breakdown far below the rated DC power limit!
- In **Planar VDMOS**, the cell pitch is wider and the transconductance is lower, keeping the ZTC current well within normal operating envelopes and providing an inherently **rugged, hotspot-free linear Safe Operating Area**.

---

## 3. Unclamped Inductive Switching (UIS) & Avalanche Ruggedness

When an inductive load (solenoid, motor winding) is abruptly disconnected without a clamp diode, the collapsing magnetic field forces the MOSFET into reverse avalanche breakdown:

```text
          +V_DD Supply (48V)
              │
             [ L_LOAD ] (Inductor: 10mH)
              │
           Drain (D)
              │
           ┌──┴──┐
           │     │ VDMOS Under UIS Test
  Gate ───┤     │
  Pulse   └──┬──┘
             │ Source (S)
            GND
```

### Avalanche Energy Equation:
During avalanche breakdown, the drain voltage clamps at $V_{(BR)DSS}$, and the inductor current ramps down to zero:
$$E_{AS} = \frac{1}{2} L \cdot I_{AS}^2 \left( \frac{V_{(BR)DSS}}{V_{(BR)DSS} - V_{DD}} \right)$$

### Why VDMOS Has Superior $E_{AS}$:
Inside every MOSFET cell resides a parasitic $n^+-p-n^-$ Bipolar Junction Transistor (Source = Emitter, P-body = Base, Drift layer = Collector). If avalanche current flowing laterally through the p-body resistance ($R_{body}$) drops $> 0.7\,\text{V}$, the parasitic BJT latches ON, creating a localized second-breakdown short that destroys the FET.

VDMOS planar geometry allows designers to integrate a heavy, highly conductive $p^+$ center body plug beneath the source contact, keeping $R_{body}$ extremely low and preventing parasitic BJT turn-on even under brutal multi-joule avalanche discharge pulses.

---

## 4. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | $V_{DS(max)}$ | $I_{D(max)}$ | $R_{DS(on)}$ | Single Pulse $E_{AS}$ | Primary Application |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **IRF540N** | Infineon (IR) | TO-220AB | $100\,\text{V}$ | $33\,\text{A}$ | $44\,\text{m}\Omega$ | $260\,\text{mJ}$ | Industrial relays, solenoids, DC motor PWM |
| **IRF640N** | Infineon (IR) | TO-220AB | $200\,\text{V}$ | $18\,\text{A}$ | $150\,\text{m}\Omega$ | $247\,\text{mJ}$ | High-power audio output stages, UPS inverters |
| **IRF840** | Vishay Siliconix | TO-220AB | $500\,\text{V}$ | $8.0\,\text{A}$ | $850\,\text{m}\Omega$ | $510\,\text{mJ}$ | Legacy offline flyback SMPS, motor starters |
| **STP10NK60Z** | STMicroelectronics| TO-220 | $600\,\text{V}$ | $10\,\text{A}$ | $650\,\text{m}\Omega$ | $300\,\text{mJ}$ | Zener-protected high-voltage industrial drivers |
| **IXTH16N20D2** | Littelfuse / IXYS | TO-247 | $200\,\text{V}$ | $16\,\text{A}$ | $160\,\text{m}\Omega$ | Linear SOA Rated | Precision active DC electronic loads, current sinks |
