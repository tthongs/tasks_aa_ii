# Power Trench MOSFETs (UMOS & Shielded Gate): Physics, Architecture & Applications

A **Trench MOSFET** (historically termed **UMOS** or **TrenchFET**) is a vertical power transistor architecture designed to minimize on-resistance (R_DS(on)) in the low-to-medium voltage domain (20 V ... 100 V). By etching vertical trenches into the silicon and forming vertical conduction channels along the trench sidewalls, trench technology eliminates the parasitic JFET resistance inherent to planar power MOSFETs and achieves cellular densities exceeding 10^8 cells/cm^2.

---

## 1. Semiconductor Physics & Device Cross-Section

```text
               Source Contact (Al)
          ─────────────────────────────
          ┌────────┐         ┌────────┐
          │   n+   │         │   n+   │ Source Diffusions
          ├────────┴─┐     ┌─┴────────┤
          │  p-Body  │     │  p-Body  │ P-Well (Body)
          └──────────┤  G  ├──────────┘
                     │  A  │
                     │  T  │  <-- Trench Gate (Poly-Si)
                     │  E  │      with vertical SiO2 sidewall oxide
                     └─────┘
          ─────────────────────────────
          │                           │
          │     n- Drift Region       │ (Epi Layer: dictates V_BR)
          │                           │
          ─────────────────────────────
          │        n+ Substrate       │
          ─────────────────────────────
          │    Drain Contact (Back)   │
```

### The Planar Resistance Bottleneck & Trench Solution:
In planar power MOSFETs, the total on-resistance consists of:
```
R_DS(on) = R_source + R_ch + R_JFET + R_drift + R_sub + R_contact
```

Where:
- R_DS(on): Total device drain-to-source on-state resistance (Ω)
- R_source: N+ source diffusion region resistance (Ω)
- R_ch: Active vertical MOS inversion channel resistance (Ω)
- R_JFET: JFET neck resistance between cells (negligible in vertical trench structures) (Ω)
- R_drift: Low-doped N- epitaxial drift region resistance (Ω)
- R_sub: Heavily doped N+ silicon substrate resistance (Ω)
- R_contact: Ohmic contact resistance at source and drain metallization interfaces (Ω)
In low-voltage devices (< 100 V), the drift region resistance R_drift is very small. Consequently, the channel resistance R_ch and the **parasitic JFET neck resistance** (R_JFET) between adjacent p-body diffusions accounted for over 60\% of total losses.

**The Trench Revolution**:
1. Channels are formed **vertically** along the etched sidewalls of the trench.
2. The current flows vertically straight down from the top source into the drift region.
3. The parasitic JFET constriction region is **completely eliminated** (R_JFET -> 0).
4. The horizontal cell pitch can be shrunk aggressively, packing dramatically more channel width per unit silicon die area.

---

## 2. Advanced Evolution: Shielded Gate Trench (SGT / Split-Gate)

While standard trench MOSFETs drastically reduced R_DS(on), they suffered from large gate-to-drain capacitance (C_gd / C_rss) because the bottom of the conductive polysilicon gate was in direct capacitive contact with the high-voltage drain drift region:

```text
       Conventional Trench                    Shielded Gate Trench (SGT)
     ┌─────────────────────┐                   ┌─────────────────────┐
     │  Poly-Si Gate       │                   │  Poly-Si Gate (G)   │
     │  (Full Trench)      │                   ├─────────────────────┤ Thin Oxide
     │                     │                   │ Thick Shield Oxide  │
     │                     │                   ├─────────────────────┤
     │                     │                   │  Shield Poly (S)    │ <-- Tied to SOURCE!
     └─────────────────────┘                   └─────────────────────┘
        High Cgd (Crss)                            Ultra-Low Cgd (Crss)
     Severe Miller Plateau                     Slashes Switching Losses by 60%
```

### Advantages of Shielded Gate Trench (SGT):
1. **C_gd Decoupling**: The bottom portion of the trench houses a second polysilicon electrode tied directly to **Source potential** (Ground in low-side switches). This acts as an electrostatic Faraday shield, dropping Miller capacitance C_gd by up to 70\%.
2. **Reduced Figure-of-Merit (FOM = R_DS(on) * Q_g)**: Allows power converters to switch at frequencies above 1 MHz with high efficiency.
3. **Reshaped Electric Field**: The shield electrode flattens the vertical electric field profile, allowing a higher-doped (lower resistance) epitaxial drift region for the same breakdown voltage rating.

---

## 3. Top-FET vs. Bottom-FET Selection in Synchronous Buck Converters

In synchronous step-down (buck) DC-DC converters (e.g., 12 V -> 1.0 V for CPU/FPGA Core rails at 40 A), the design requirements for the High-Side (Control FET) and Low-Side (Sync FET) are fundamentally divergent:

```text
           +12V Input Rail
                 │
             Drain (D)
             ┌───┴───┐
             │       │ High-Side MOSFET (Control FET)
    PWM_HS ──┤  HS   │ Duty cycle D = Vout / Vin = 1V / 12V = 8.3%
             └───┬───┘
                 │
                 ├── Switch Node (SW) ──[ Inductor L ]──┬──> +1.0V Vcore
                 │                                      │
             Drain (D)                                [Cap]
             ┌───┴───┐                                  │
             │       │ Low-Side MOSFET (Sync FET)      GND
    PWM_LS ──┤  LS   │ Duty cycle (1 - D) = 91.7%
             └───┬───┘
                 │ Source (S)
                GND
```

### Engineering Trade-Offs:
1. **High-Side (HS) Control FET**:
   - Operates for only 8.3\% of the time.
   - Dominated by **switching losses** (P_sw proportional to Q_g, Q_gd).
   - **Optimization Target**: Choose an SGT trench MOSFET with lowest possible Q_gd and Q_g, even if R_DS(on) is slightly higher (e.g., 5 mΩ - 10 mΩ).
2. **Low-Side (LS) Synchronous Rectifier FET**:
   - Operates for 91.7\% of the time.
   - Dominated by **conduction losses** (P_cond = I_rms^2 * R_DS(on)).
   - **Optimization Target**: Minimize R_DS(on) at all costs (e.g., < 1.5 mΩ).
   - **Crucial Anti-Shoot-Through Ratio**: Must guarantee C_gs / C_gd > 2.0. If the switch node swings abruptly (dv/dt > 20 V/ns) when the High-Side FET turns on, displacement current through C_gd injects charge into the Low-Side gate. If C_gs is insufficient, V_GS(LS) bounces above V_TH, causing instantaneous bridge shoot-through and catastrophic destruction.

---

## 4. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | V_DS(max) | I_D(max) | R_DS(on) (@10V) | Q_g (Typ) | Target Application |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CSD18534Q5A** | Texas Instruments | SON 5* 6 mm | 60 V | 100 A | 7.8 mΩ | 13.5 nC | 24V/48V telecom buck, motor drives |
| **BSC014N04LS** | Infineon (OptiMOS) | SuperSO8 | 40 V | 198 A | 1.4 mΩ | 49 nC | Server CPU VRM low-side sync rectifier |
| **IPB014N06N** | Infineon (OptiMOS) | D2PAK | 60 V | 180 A | 1.4 mΩ | 137 nC | 48V mild hybrid automotive, battery isolation |
| **PSMN1R0-40YLD**| Nexperia | LFPAK56 | 40 V | 300 A | 1.0 mΩ | 65 nC | Ultra-dense high-reliability BLDC motor phase |
