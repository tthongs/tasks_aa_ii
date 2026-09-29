# AC-DC Power Rectification: Master Engineering Hub

Welcome to the **VVDN Engineering Hub AC-DC Rectification Master Guide**. AC-to-DC converters (rectifiers) convert alternating current (AC) from the electrical power utility grid ($110\,\text{V}/230\,\text{V}$ single-phase, $400\,\text{V}/480\,\text{V}$ three-phase) into regulated, direct current (DC) rails required by all electronic systems, DC motor drives, battery energy storage, and industrial DC buses.

---

## 1. Classification of AC-DC Rectification Systems

```text
                                AC-DC Rectification Topologies
                                             │
             ┌───────────────────────────────┼───────────────────────────────┐
             │                               │                               │
    Uncontrolled Rectifiers         Controlled Rectifiers           Active PFC Rectifiers
   (Passive Silicon Diodes)      (Phase-Controlled Thyristors)     (High-Frequency Active Switch)
             │                               │                               │
     ┌───────┴───────┐               ┌───────┴───────┐               ┌───────┴───────┐
     │               │               │               │               │               │
Single-Phase    Three-Phase     Single-Phase    Three-Phase     Single-Phase    Three-Phase
 Bridge / CT    6-Pulse Bridge   Semi / Full     6-Pulse Full    Boost / Totem   Vienna Rectifier
 (Pulsed Diode   (Industrial     (Variable DC    (Regenerative   (PF > 0.99,     (3-Level PFC,
  Currents)       DC Drives)      Drives)         Inversion)      THD < 5%)       Low Stress)
```

---

## 2. AC-DC Performance & Power Quality Comparison

| Rectifier Family | Controllability | Power Factor (PF) | Input Current THD | DC Voltage Regulation | Primary Applications |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Uncontrolled Diode Bridges** | Fixed (Unregulated) | $0.60 \dots 0.75$ (Lagging) | $60\% \dots 120\%$ (Severe Peaks) | Load-dependent, significant ripple | Low-cost adapters, legacy linear power supplies, auxiliary supplies ($< 75\,\text{W}$). |
| **Controlled SCR Rectifiers** | Regulated ($0 \le \alpha \le 180^\circ$) | $0.4 \dots 0.9$ (Degrades with $\alpha$) | $30\% \dots 50\%$ | Direct control via firing angle | Heavy DC motor speed control, electrochemical smelting, HVDC transmission links. |
| **Active PFC Boost Rectifiers** | Dynamic Closed-Loop | **$> 0.99$** | **$< 3\% \dots 5\%$** (IEC 61000-3-2 Compliant) | Regulated stiff DC bus ($400\,\text{V}$) | Server PSUs, Telecom rectifiers, EV on-board chargers, medical equipment ($> 75\,\text{W}$). |
| **Vienna 3-Phase PFC Rectifier** | Dynamic Closed-Loop | **$> 0.995$** | **$< 2.5\%$** | Regulated $\pm 400\,\text{V}$ ($800\,\text{V}$ DC bus) | EV DC Ultra-Fast Chargers ($50\,\text{kW} \dots 350\,\text{kW}$), industrial drives. |

---

## 3. Power Quality Metrics Defined

Modern AC-DC converter engineering is governed by strict power quality standards (**IEC 61000-3-2** and **IEEE 519**):

1. **Total Harmonic Distortion of Current ($\text{THD}_i$)**:
   $$\text{THD}_i = \frac{\sqrt{\sum_{h=2}^{\infty} I_h^2}}{I_1} \times 100\%$$
2. **Displacement Power Factor ($\text{DPF}$)**:
   $$\text{DPF} = \cos \phi_1 \quad (\text{Phase displacement between fundamental current and voltage})$$
3. **True Power Factor ($\text{PF}$)**:
   Superposition of distortion and displacement:
   $$\text{PF} = \frac{P}{S} = \frac{I_1}{I_{rms}} \cdot \cos \phi_1 = \frac{1}{\sqrt{1 + \text{THD}_i^2}} \cdot \text{DPF}$$

---

## 4. Detailed Technical Dossiers in this Directory

1. [Uncontrolled Diode Rectifiers: 1-Phase & 3-Phase Bridge Physics & Sizing](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/uncontrolled-rectifiers.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/uncontrolled-rectifiers.docx))  
   *Covers: Single-phase half-wave, full-wave center-tapped, full-wave diode bridge, three-phase 6-pulse bridge, filter capacitor ripple equations, diode conduction angle, peak inverse voltage (PIV), inrush current limiting, and harmonic degradation.*

2. [Controlled SCR Rectifiers: Semi-Converters, Full-Converters & Quadrant Inversion](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/controlled-rectifiers.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/controlled-rectifiers.docx))  
   *Covers: Single-phase and three-phase phase-controlled rectifiers, firing angle delay $\alpha$, output DC voltage formulations, continuous vs. discontinuous conduction, Quadrant I (Rectification) vs. Quadrant IV (Line-Commutated Inversion for regenerative DC braking), and power factor implications.*

3. [Active Power Factor Correction (PFC) Rectifiers: CCM Boost, Totem-Pole & Vienna](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/active-pfc-rectifiers.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/active-pfc-rectifiers.docx))  
   *Covers: Active Boost PFC pre-regulators, average current-mode control (inner current + outer voltage loop), Critical Conduction Mode (CrM), Bridgeless Totem-Pole GaN PFC ($99\%$ efficiency), Three-Phase Three-Level Vienna Rectifier, and IEC 61000-3-2 Class D compliance.*
