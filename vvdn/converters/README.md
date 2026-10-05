# Power Electronics Converters: Complete Architectural, Design & Study Guide

Welcome to the **VVDN Engineering Hub Power Electronics Converters Knowledge Base**. This repository is an exhaustive, mathematically rigorous, and practical hardware engineering reference covering the four fundamental conversion domains: **DC-DC**, **AC-AC**, **DC-AC**, and **AC-DC**.

---

## 1. Universal Power Electronics Conversion Matrix

Power electronics converters transform electrical energy between direct current (DC) and alternating current (AC) with maximum efficiency using solid-state semiconductor switching devices (MOSFETs, IGBTs, Thyristors/SCRs, Diodes, and Wide-Bandgap SiC/GaN):

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                    The Four Fundamental Conversion Quadrants                      │
├─────────────────────┬─────────────────────────────────┬───────────────────────────┤
│ From \ To           │ DC (Direct Current)             │ AC (Alternating Current)  │
├─────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ **DC**              │ **DC-DC Converters**            │ **DC-AC Inverters**       │
│                     │ - Isolated: Forward, Flyback,   │ - Single-Phase: Half/Full │
│                     │   DAB, Full/Half-Bridge, Push-  │   Bridge, Bipolar/Unipolar│
│                     │   Pull, Resonant (LLC/SRC/PRC)  │ - Three-Phase: 6-Switch   │
│                     │ - Non-Isolated: Buck, Boost,    │   VSI, 180°/120°, SPWM,   │
│                     │   Buck-Boost, Cuk, SEPIC, Zeta  │   Space Vector PWM (SVPWM)│
├─────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ **AC**              │ **AC-DC Rectifiers**            │ **AC-AC Converters**      │
│                     │ - Uncontrolled: 1-Ph & 3-Ph     │ - Cycloconverters: Line-  │
│                     │   Diode Bridges, Ripple factor  │   commutated, frequency   │
│                     │ - Controlled: Thyristor Phase-  │   reduction (P/N banks)   │
│                     │   Controlled (Semi/Full Conv.)  │ - AC Voltage Controllers: │
│                     │ - Active PFC / AFE: Boost PFC,  │   Phase-angle control,    │
│                     │   Bridgeless, Vienna Rectifier  │   Integral cycle (TRIAC)  │
└─────────────────────┴─────────────────────────────────┴───────────────────────────┘
```

---

## 2. Directory Navigation & Modular Architecture

This repository is partitioned into dedicated domain directories, each containing specialized, technical dossiers:

### A. DC-DC Converters ([`dc-dc/README.md`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/README.md))
- **Isolated Topologies**:
  - [Forward Converter](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/forward-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/forward-converter.docx))
  - [Flyback Converter](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/flyback-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/flyback-converter.docx))
  - [Dual Active Bridge (DAB)](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/dual-active-bridge.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/dual-active-bridge.docx))
  - [Full-Bridge Converter (PSFB)](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/full-bridge-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/full-bridge-converter.docx))
  - [Half-Bridge Converter](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/half-bridge-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/half-bridge-converter.docx))
  - [Push-Pull Converter](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/push-pull-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/push-pull-converter.docx))
  - [Resonant Converters (SRC, PRC, LLC) [IMP]](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/resonant-converters.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/resonant-converters.docx))
- **Non-Isolated Topologies**:
  - [Buck Converter](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/buck-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/buck-converter.docx))
  - [Boost Converter](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/boost-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/boost-converter.docx))
  - [Buck-Boost Converter (Inverting & 4-Switch FSBB)](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/buck-boost-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/buck-boost-converter.docx))
  - [Ćuk Converter](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/cuk-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/cuk-converter.docx))
  - [SEPIC Converter](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/sepic-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/sepic-converter.docx))
  - [Zeta Converter](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/zeta-converter.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/zeta-converter.docx))

### B. AC-AC Converters ([`ac-ac/README.md`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-ac/README.md))
- [Cycloconverters](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-ac/cycloconverters.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-ac/cycloconverters.docx))
- [AC Voltage Controllers](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-ac/ac-voltage-controllers.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-ac/ac-voltage-controllers.docx))

### C. DC-AC Inverters ([`dc-ac/README.md`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-ac/README.md))
- [Single-Phase Inverters](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-ac/single-phase-inverters.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-ac/single-phase-inverters.docx))
- [Three-Phase Inverters & Space Vector PWM (SVPWM)](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-ac/three-phase-inverters.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-ac/three-phase-inverters.docx))

### D. AC-DC Rectifiers ([`ac-dc/README.md`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/README.md))
- [Uncontrolled Diode Rectifiers](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/uncontrolled-rectifiers.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/uncontrolled-rectifiers.docx))
- [Controlled Phase-Rectifiers (Semi/Full & Inversion)](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/controlled-rectifiers.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/controlled-rectifiers.docx))
- [Active PFC Rectifiers (Boost, Totem-Pole & Vienna)](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/active-pfc-rectifiers.md) ([DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/ac-dc/active-pfc-rectifiers.docx))

---

## 3. High-Level Comparison & Selection Benchmark

| Conversion Class | Typical Topologies | Power Range | Typical Efficiency | Dominant Semiconductor | Target Applications |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DC-DC Isolated** | Flyback, Forward, DAB, LLC, PSFB | 5 W ... 50 kW | 88\% ... 98\% | MOSFET / SiC / GaN | EV On-board Chargers, Server PSUs, Telecom bricks |
| **DC-DC Non-Isolated**| Buck, Boost, Buck-Boost, Cuk, SEPIC | 1 W ... 5 kW | 92\% ... 98.5\% | Low-R_DS(on) Trench FET | Point-of-Load (PoL), Battery chargers, LED drivers |
| **AC-AC Direct** | Cycloconverter, AC Voltage Controller | 1 kW ... 20 MW | 95\% ... 99\% | Phase-Control Thyristor / TRIAC | Heavy industrial grinding mills, soft starters, dimmers |
| **DC-AC Inverters** | 1-Phase & 3-Phase VSI, SVPWM | 500 W ... 1 MW | 95\% ... 99\% | IGBT / SiC MOSFET | EV Traction Inverters, Solar Grid-Tie, Motor Drives |
| **AC-DC Rectifiers** | Diode Bridge, Active Boost PFC | 10 W ... 500 kW | 90\% ... 98.5\% | Diode / Fast Recovery / SiC | Power supplies, EV DC Fast Chargers, Industrial DC bus |

---

## 4. Document Synchronization

All technical dossiers in this knowledge base are maintained simultaneously as **GitHub-Flavored Markdown (`.md`)** for version-controlled study and **Microsoft Word (`.docx`)** for enterprise sharing and mentor reviews using:

```bash
python3 tools/md_to_docx.py <path/to/document.md>
```
