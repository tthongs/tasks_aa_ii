# DC-DC Converters: Isolated & Non-Isolated Topologies Master Guide

Welcome to the **VVDN Engineering Hub DC-DC Converters Knowledge Base**. This module provides an exhaustive architectural, analytical, and design guide covering all primary **Isolated** and **Non-Isolated** switched-mode DC-DC power conversion topologies.

---

## 1. DC-DC Taxonomy & Classification Tree

```text
                                       DC-DC Converter Topologies
                                                   │
         ┌─────────────────────────────────────────┴─────────────────────────────────────────┐
         ▼                                                                                   ▼
  Isolated Topologies (Transformer Isolation)                        Non-Isolated Topologies (Direct Inductor)
  ├── 1. Forward Converter (Tertiary / 2-Switch Reset)              ├── 1. Buck Converter (Step-Down, Vout < Vin)
  ├── 2. Flyback Converter (Coupled Inductor, DCM/CCM)              ├── 2. Boost Converter (Step-Up, Vout > Vin)
  ├── 3. Dual Active Bridge (DAB: Bidirectional Phase-Shift)        ├── 3. Buck-Boost Converter (Inverting / 4-Switch)
  ├── 4. Full-Bridge Converter (Phase-Shifted ZVS / PSFB)           ├── 4. Cuk Converter (Capacitive Transfer, Low EMI)
  ├── 5. Half-Bridge Converter (Capacitive Divider Split)           ├── 5. SEPIC Converter (Non-Inverting Buck-Boost)
  ├── 6. Push-Pull Converter (Center-Tapped Primary)                └── 6. Zeta Converter (Inverse SEPIC, Cont. Iout)
  └── 7. Resonant Converters [HIGH IMPORTANCE]
         ├── Series Resonant Converter (SRC)
         ├── Parallel Resonant Converter (PRC)
         └── LLC Resonant Half-Bridge Converter (ZVS / ZCS)
```

---

## 2. Comprehensive Topology Benchmark & Comparison Matrix

| Topology | Isolation? | Voltage Gain (V_OUT / V_IN) | Power Spectrum | Switch Voltage Stress (V_sw) | Switch Current Stress (I_sw) | Magnetic Core Utilization | Target Applications |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Buck** | No | D | 1 W ... 2 kW | V_IN | I_OUT | Single inductor, DC bias | PoL, CPU VRM, battery chargers |
| **Boost** | No | 1 / (1 - D) | 5 W ... 5 kW | V_OUT | I_OUT / (1 - D) | Single inductor, DC bias | PFC pre-regulators, Solar boost, LED |
| **Buck-Boost** | No | -D / (1 - D) | 5 W ... 500 W | V_IN + V_OUT | I_OUT / (1 - D) | Single inductor, DC bias | Automotive battery systems, Handhelds |
| **Cuk** | No | -D / (1 - D) | 10 W ... 1 kW | V_IN + V_OUT | I_OUT / (1 - D) | Dual inductors (can couple)| Low-noise bipolar rails, audio |
| **SEPIC** | No | D / (1 - D) | 5 W ... 500 W | V_IN + V_OUT | I_OUT / (1 - D) | Dual inductors / coupled | Battery-powered devices, LED drivers |
| **Zeta** | No | D / (1 - D) | 5 W ... 500 W | V_IN + V_OUT | I_OUT / (1 - D) | Dual inductors / coupled | Telecom low-ripple supplies |
| **Flyback** | Yes | n * D / (1 - D) | 1 W ... 150 W | V_IN + n V_OUT | I_OUT / (n(1 - D)) | Unipolar coupled inductor | Standby supplies, AC adapters, Gate bias |
| **Forward** | Yes | n * D (D < 0.5) | 50 W ... 500 W | 2 V_IN (1-switch) | (n I_OUT) / D | Unipolar transformer + reset| Industrial telecom bricks, DC-DC isolated |
| **Push-Pull** | Yes | 2n * D | 100 W ... 1.5 kW | 2 V_IN | n I_OUT | Bipolar (Symmetric quadrants) | 12V/24V inverters, automotive DC-DC |
| **Half-Bridge**| Yes | n * D | 100 W ... 1.5 kW | V_IN | 2n I_OUT | Bipolar (Symmetric quadrants) | PC power supplies, server auxiliary |
| **Full-Bridge**| Yes | 2n * D (PSFB) | 1 kW ... 20 kW | V_IN | n I_OUT | Bipolar (Symmetric quadrants) | EV fast charging, industrial welders |
| **Dual Active Bridge**| Yes | n * (φ(π - |φ|)) / (π^2 f L) | 1 kW ... 100 kW | V_IN / V_OUT | Continuous AC peak | Bipolar AC transformer | Solid-state transformers, V2G EV chargers |
| **LLC Resonant**| Yes | n * M(f_n, Q, k) | 100 W ... 10 kW | V_IN (ZVS turn-on) | Resonant sinusoidal | Bipolar resonant transformer | Server PSUs, Flat-panel TV, EV OBC |

---

## 3. Directory Navigation & Technical Dossiers

### Isolated DC-DC Topologies:
- [**`isolated/forward-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/forward-converter.md): Forward converter operating mechanics, tertiary demagnetizing winding reset, two-switch forward, output inductor filter, and duty-cycle constraints (D < 50\%).
- [**`isolated/flyback-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/flyback-converter.md): Flyback coupled inductor, Discontinuous (DCM) vs Continuous (CCM) conduction, RCD clamp snubber calculation, and multi-output isolated generation.
- [**`isolated/dual-active-bridge.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/dual-active-bridge.md): Dual Active Bridge (DAB) bidirectional power conversion, single/dual/triple phase-shift modulation (SPS/DPS/TPS), leakage inductance energy transfer, and Zero-Voltage Switching (ZVS) boundaries.
- [**`isolated/full-bridge-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/full-bridge-converter.md): Phase-Shifted Full-Bridge (PSFB), diagonal vs phase-shift modulation, soft-switching ZVS mechanisms, secondary diode ringing, and active clamp snubbers.
- [**`isolated/half-bridge-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/half-bridge-converter.md): Isolated half-bridge DC-DC converter, capacitive voltage divider, automatic core volt-second balancing, and switch voltage clamping to V_IN.
- [**`isolated/push-pull-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/push-pull-converter.md): Push-pull topology, center-tapped transformer, ground-referenced primary low-side switches, core saturation / flux walking hazard and active balance control.
- [**`isolated/resonant-converters.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/isolated/resonant-converters.md): **[HIGH IMPORTANCE]** Deep dive into Series Resonant (SRC), Parallel Resonant (PRC), and LLC Resonant Half-Bridge converters. Resonant tank impedance (Z_r), quality factor (Q), inductance ratio (k), normalized voltage gain curves, and complete ZVS/ZCS design procedures.

### Non-Isolated DC-DC Topologies:
- [**`non-isolated/buck-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/buck-converter.md): Step-Down Buck converter, CCM/DCM boundary condition, inductor & capacitor ripple formulations, synchronous rectification, and closed-loop control.
- [**`non-isolated/boost-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/boost-converter.md): Step-Up Boost converter, Right-Half-Plane (RHP) zero stability challenge, inductor energy balance, and synchronous boost design.
- [**`non-isolated/buck-boost-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/buck-boost-converter.md): Inverting buck-boost and 4-switch synchronous non-inverting buck-boost topologies, operational mode transitions, and component sizing.
- [**`non-isolated/cuk-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/cuk-converter.md): Cuk converter, capacitive energy transfer, continuous non-pulsating input and output currents, low EMI signature, and coupled-inductor zero-ripple operation.
- [**`non-isolated/sepic-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/sepic-converter.md): Single-Ended Primary-Inductor Converter (SEPIC), non-inverting buck-boost operation, series DC blocking capacitor protecting against output short circuits.
- [**`non-isolated/zeta-converter.md`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/converters/dc-dc/non-isolated/zeta-converter.md): Zeta (Inverse SEPIC) converter, continuous output inductor current, capacitive energy transfer, and low output voltage ripple.
