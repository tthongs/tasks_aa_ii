# DC-AC Power Inverters: Master Engineering Hub

Welcome to the **VVDN Engineering Hub DC-AC Inverters Master Guide**. DC-to-AC inverters convert a DC rail voltage (from solar photovoltaic arrays, battery energy storage systems, fuel cells, or an industrial DC bus) into a stabilized, low-distortion alternating current (AC) voltage at standard grid or motor frequencies (50 Hz, 60 Hz, 400 Hz, or variable frequency up to several kHz).

---

## 1. Classification of DC-AC Inverter Topologies

```text
                                DC-AC Inverter Topologies
                                             │
             ┌───────────────────────────────┴───────────────────────────────┐
             │                                                               │
     Voltage Source Inverters (VSI)                                  Current Source Inverters (CSI)
     (Stiff DC Voltage Source via Bulk Capacitors)                   (Stiff DC Current Source via Series Inductors)
             │                                                               │
     ┌───────┴───────────────────────┐                               ┌───────┴───────┐
     │                               │                               │               │
Single-Phase Inverters          Three-Phase Inverters           Thyristor-Based Industrial CSI
 (Half-Bridge & Full H-Bridge)   (6-Switch 2-Level & Multi-Level) High-Power Inductive Drives
```

---

## 2. Inverter Modulation & Performance Comparison

| Inverter Family | Typical Topologies | Modulation Techniques | DC-Bus Voltage Utilization | Typical THD (Filtered) | Primary Applications |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Single-Phase Inverters** | Half-Bridge, Full-Bridge (H-Bridge) | Square Wave, Quasi-Square, Bipolar SPWM, Unipolar SPWM | V_ac,fund = m_a * V_dc | < 3\% (IEEE 519 Compliant) | Residential solar micro-inverters, uninterruptible power supplies (UPS), RV power packs. |
| **Three-Phase Inverters** | 6-Switch Two-Level VSI, 3-Level NPC (Neutral Point Clamped) | 180° / 120° Six-Step, Third-Harmonic Injection (THIPWM), Space Vector PWM (SVPWM) | SVPWM achieves **15.5% higher DC utilization** (V_line,rms = 0.707 * V_dc) | < 2\% | Variable Frequency Drives (VFD), EV traction inverters, utility-scale solar farms, wind turbine converters. |

---

## 3. Detailed Technical Dossiers in this Directory

Explore each technical dossier for mathematical derivations, gate switching sequences, space vector math, and LC output filter designs:

1. [Single-Phase DC-AC Inverters: Topologies, Unipolar/Bipolar SPWM & Filter Design](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-ac/single-phase-inverters.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-ac/single-phase-inverters.docx))  
   *Covers: Half-bridge vs. Full-bridge H-bridge, square wave, quasi-square wave (modified sine), bipolar vs. unipolar Sinusoidal Pulse-Width Modulation (SPWM), switching frequency harmonic spectrum (f_s vs. 2f_s), LC low-pass filter design, and dead-time distortion.*

2. [Three-Phase DC-AC Inverters: 6-Switch VSI, THIPWM & Space Vector PWM (SVPWM)](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-ac/three-phase-inverters.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-ac/three-phase-inverters.docx))  
   *Covers: 6-switch two-level VSI, 180° and 120° six-step conduction, Third-Harmonic Injection PWM (THIPWM), and a complete mathematical deep dive into Space Vector PWM (SVPWM): the 8 switching states, α-β Clarke transform, rotating voltage space vector vec{V}_ref, sector identification, dwell-time equations (T_1, T_2, T_0), symmetric 7-segment switching patterns, and DC-bus voltage maximization.*
