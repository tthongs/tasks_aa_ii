# Superjunction MOSFETs (CoolMOS & Charge Balance): Physics & Applications

A **Superjunction MOSFET** (**SJ-MOSFET**, commercially recognized under brand names such as Infineon **CoolMOS™**, STMicroelectronics **MDmesh™**, and onsemi **SUPERFET®**) represents a revolutionary breakthrough in high-voltage ($500\,\text{V} \dots 900\,\text{V}$) Silicon power semiconductors. By leveraging the principle of **charge compensation** across alternating vertical p- and n-doped semiconductor columns, superjunction technology fundamentally shattered the theoretical "1D Silicon Limit," slashing specific on-resistance ($R_{DS(on)} \times A$) by up to $80\%$.

---

## 1. The Classical 1D Silicon Limit vs. Superjunction Physics

In conventional planar or VDMOS power transistors, blocking a high reverse breakdown voltage ($V_{(BR)DSS}$) requires an epitaxial drift layer that is both physically thick ($W_{drift}$) and lightly doped ($N_D$). The resulting electric field profile is triangular:

```text
       Conventional Planar Drift Region           Superjunction Column Architecture
     ┌────────────────────────────────────┐      ┌───────┬───────┬───────┬───────┐
     │                                    │      │ p-Col │ n-Col │ p-Col │ n-Col │
     │       Lightly Doped n- Drift       │      │ (Boron│(Phos) │ (Boron│(Phos) │
     │             (Low Doping)           │      │   )   │   )   │   )   │   )   │
     │                                    │      │       │       │       │       │
     └────────────────────────────────────┘      └───────┴───────┴───────┴───────┘
          Triangular Electric Field                   Rectangular Flat Electric Field
         Rds(on)*A ∝ V_BR^(2.5) [Severe!]            Rds(on)*A ∝ V_BR^(1.0 - 1.3) [Linear!]
```

### Mathematical Scaling Laws:
1. **Classical 1D Silicon Limit**:
   $$R_{DS(on)} \times A \approx 5.93 \times 10^{-9} \cdot (V_{(BR)DSS})^{2.5} \quad [\Omega \cdot \text{cm}^2]$$
   At $600\,\text{V}$, this power law dictates that Silicon chips had to become enormous and costly, with crippling gate charge and output capacitance.
2. **Superjunction Scaling**:
   $$R_{DS(on)} \times A \propto (V_{(BR)DSS})^{1.0 \dots 1.32}$$
   By balancing charges precisely:
   $$N_A \cdot W_p = N_D \cdot W_n$$
   When reverse voltage is applied across the Drain, the horizontal electric field between adjacent p- and n-columns completely sweeps away mobile carriers at very low voltage ($V_{DS} \approx 50\,\text{V}$). The entire drift region becomes fully depleted, creating a **uniform, rectangular electric field distribution**.
3. Because the field is rectangular rather than triangular, the drift region thickness can be halved, and the $n$-columns can be doped **an order of magnitude more heavily**, reducing conduction losses dramatically.

---

## 2. Dynamic Switching Behavior: Non-Linear $C_{oss}$ & Extreme $dv/dt$

The deep column depletion creates a unique electrical signature: a massively non-linear output capacitance ($C_{oss}$):

```text
       Coss vs Drain-to-Source Voltage (Vds)
  Coss ^
       │  10,000 pF (Un-depleted columns at low Vds)
       │  █
       │  █
       │   █
       │    █
       │     █  Colossal drop at ~50V column pinch-off!
       │      ████████████████████████████ 50 pF (High Vds)
       └───────────────────────────────────────────────> Vds
       0V       20V       50V                        400V
```

### High-Speed Switching Traps:
- **Ultra-Fast Voltage Slewing ($dv/dt > 50\,\text{V/ns}$ to $100\,\text{V/ns}$)**:
  Because $C_{oss}$ collapses to mere picofarads at high voltage, the drain node snaps upward with ferocious speed during turn-off.
- **Parasitic Package Oscillations**:
  This rapid $dv/dt$ interacts with trace and bondwire parasitic inductances ($L_{source}, L_{gate}$), generating high-frequency ringing ($50\,\text{MHz} - 200\,\text{MHz}$) and electromagnetic interference (EMI).
- **Remediation Techniques**:
  1. **Source Kelvin Pin**: Use 4-pin packages (e.g. TO-247-4 or PG-HDSOP) where the gate driver return has an independent source connection that bypasses high load $di/dt$.
  2. **Ferrite Beads**: Place an SMD ferrite bead (impedance $30\,\Omega - 60\,\Omega$ at $100\,\text{MHz}$) directly adjacent to the gate pin.
  3. **Tuned Turn-On Gate Resistor ($R_{G,on}$)**: Avoid making $R_G$ overly small; damp the turn-on transition to control peak diode recovery current.

---

## 3. Fast-Recovery Body Diode Variants (CFD / DM2)

In hard-switched bridge topologies (such as Phase-Shifted Full-Bridge or resonant LLC converters during abnormal transients/start-up), the MOSFET's intrinsic body diode must conduct freewheeling load current:

```text
       Topology Compatibility Comparison
   ┌─────────────────────────────────────────────────────────────┐
   │ Standard Superjunction FET  │ Fast-Recovery Body Diode (CFD)│
   ├─────────────────────────────┼───────────────────────────────┤
   │ High Qrr (> 4000 nC)        │ Low Qrr (< 400 nC)            │
   │ Long trr (> 400 ns)         │ Ultra-Fast trr (< 100 ns)     │
   │ Prone to body-diode dv/dt   │ Immune to diode latch-up      │
   │ latch-up in half-bridges    │                               │
   ├─────────────────────────────┼───────────────────────────────┤
   │ Ideal for: Single-switch PFC│ Ideal for: Resonant LLC,      │
   │ Boost, Single-Ended Flyback │ Full-Bridge ZVS, EV Chargers  │
   └─────────────────────────────┴───────────────────────────────┘
```

By introducing heavy metal lifetime killers (Platinum/Gold doping or Electron Irradiation) into the p-n column junction, manufacturers like Infineon (CoolMOS™ CFD series) crush minority carrier lifetime, preventing disastrous bridge shoot-through.

---

## 4. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | $V_{DS(max)}$ | $I_{D(max)}$ | $R_{DS(on)}$ | Diode Class | Target Application |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **IPW60R099CP** | Infineon (CoolMOS CP)| TO-247 | $650\,\text{V}$ | $31\,\text{A}$ | $99\,\text{m}\Omega$ | Standard | High-efficiency CCM Power Factor Correction (PFC) |
| **IPW60R045CFD7**| Infineon (CoolMOS CFD7)| TO-247 | $600\,\text{V}$ | $50\,\text{A}$ | $45\,\text{m}\Omega$ | Fast CFD | Resonant LLC converter, Server Power, EV On-Board Charger |
| **STW48N60M2** | STMicroelectronics | TO-247 | $600\,\text{V}$ | $42\,\text{A}$ | $76\,\text{m}\Omega$ | Standard | Telecom rectifiers, Solar micro-inverters |
| **TK20A60U** | Toshiba (DTMOS) | TO-220SIS | $600\,\text{V}$ | $20\,\text{A}$ | $165\,\text{m}\Omega$ | Standard | Consumer flat-panel TV power supplies |
