# Step-by-Step Design Guide: 4-Switch Synchronous Buck-Boost Post-Regulator (5–20 V, 3 A DC Output)

Welcome to the **VVDN Engineering Hub Comprehensive Step-by-Step Design Guide** for the **4-Switch Synchronous Buck-Boost Post-Regulator**. This engineering dossier is structured as a complete, pedagogical, practical hardware design blueprint for developing the digitally controlled DC-DC post-regulator stage of the Smart Programmable Power Supply (SPPS).

---

## 1. Executive Summary & Design Scope

The post-regulator operates downstream of the isolated primary Quasi-Resonant (QR) Flyback converter ($+24.0\,\text{V} \pm 1.0\%$ DC bus). It provides a digitally programmable output voltage from **$5.0\,\text{V}$ to $20.0\,\text{V}$ DC** at continuous currents up to **$3.0\,\text{A}$** ($60.0\,\text{W}$ maximum continuous output power).

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      4-SWITCH SYNCHRONOUS BUCK-BOOST ENGINEERING SPECIFICATIONS                  │
├────────────────────────────┬─────────────────────────────┬───────────────────────────────────────┤
│ Parameter / Specification  │ Target Value                │ Engineering Condition / Margin        │
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Input Voltage ($V_{IN}$)**│ $+24.0\,\text{V} \pm 1.0\%$ │ From Primary Flyback Stage            │
│ **Input Voltage Range**    │ $22.0\,\text{V} \dots 26.0\,\text{V}$│ Dynamic tolerance during transients   │
│ **Programmable Output ($V_O$)│ $5.0\,\text{V} \dots 20.0\,\text{V}$ DC│ Digitally set via 12-bit MCU DAC      │
│ **Voltage Step Resolution**│ $\le 10\,\text{mV}$ Step    │ Calculated: $3.65\,\text{mV / LSB}$   │
│ **Continuous Output ($I_O$)│ $0.1\,\text{A} \dots 3.0\,\text{A}$ │ Programmable hardware CC clamp limit  │
│ **Current Step Resolution**│ $\le 10\,\text{mA}$ Step    │ Secondary DAC current limit setpoint  │
│ **Maximum Continuous Power**│ $60.0\,\text{W}$            │ Natural convection, fanless enclosure │
│ **Switching Frequency**    │ $250\,\text{kHz}$ Fixed PWM │ Optimized for inductor size vs loss   │
│ **Peak Power Efficiency**  │ $\ge 96.5\%$ @ 15V / 3A     │ All-NMOS synchronous rectification    │
│ **Output Voltage Ripple**  │ $< 25\,\text{mV}_{\text{pk-pk}}$│ Full load $20\,\text{V} / 3\,\text{A}$, 20MHz BW  │
│ **Load Transient Recovery**│ $< 120\,\mu\text{s}$ to 1%  │ $50\% \rightarrow 100\%$ load step ($1.5A \rightarrow 3.0A$)│
│ **Operating Regimes**      │ Pure Buck, Buck-Boost, Boost│ Automatic seamless 3-mode transitions │
└────────────────────────────┴─────────────────────────────┴───────────────────────────────────────┘
```

---

## 2. Step-by-Step Design Roadmap

This guide is organized into 6 modular engineering dossiers walking through every design calculation, schematic, layout rule, and bench bring-up procedure:

```text
buck_boost_step_by_step_design/
├── README.md                                       # Master Roadmap, specs & design workflow
├── 01-specifications-and-topology-selection.md     # Step 1: Specs | Step 2: 4-Switch topology & multi-mode operation
├── 02-power-stage-magnetics-and-filters.md         # Step 3: Inductor sizing | Step 4: Input cap | Step 5: Output cap
├── 03-mosfets-gate-drivers-and-thermal.md          # Step 6: MOSFET selection & losses | Step 7: Bootstrap gate drive
├── 04-control-loops-dac-and-cc-clamping.md         # Step 8: DAC summing node | Step 9: CC clamp | Step 10: Small-signal loop
├── 05-schematics-pcb-layout-and-bom.md             # Step 11: Complete schematic | Step 12: PCB layout | Step 13: Full BOM
└── 06-bringup-calibration-and-testing.md           # Step 14: Bring-up checklist | Step 15: Calibration | Step 16: RCA Matrix
```

### [Dossier 1: Specifications & Topology Selection](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply/buck_boost_step_by_step_design/01-specifications-and-topology-selection.md)
* **Step 1: System Requirements & Parameter Envelopes**: Complete electrical, dynamic, and thermal operating boundaries.
* **Step 2: Topology Selection & Operating Principles**: Why the 4-switch non-inverting H-bridge was selected over inverting buck-boost and single-switch topologies; multi-mode state machine (Pure Buck, Buck-Boost transition, Pure Boost).

### [Dossier 2: Power Stage Magnetics & Filter Sizing](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply/buck_boost_step_by_step_design/02-power-stage-magnetics-and-filters.md)
* **Step 3: Power Inductor Sizing ($L = 10\,\mu\text{H}$)**: Continuous conduction mode (CCM) verification, ripple current ratio ($r = 30\%$), peak current ($I_{pk} = 5.95\,\text{A}$), RMS current ($I_{rms} = 3.01\,\text{A}$), core saturation margin ($I_{sat} = 11.5\,\text{A}$), DCR and AC core loss.
* **Step 4: Input Capacitor Bank Sizing ($C_{IN}$)**: RMS ripple current calculations, bulk electrolytic vs ceramic MLCC sizing.
* **Step 5: Output Capacitor Bank Sizing ($C_{OUT}$)**: Capacitive and ESR ripple breakdown, ceramic MLCC DC voltage bias derating, hybrid bank ($4\times 22\,\mu\text{F}$ 1210 MLCC + $100\,\mu\text{F}$ OS-CON polymer).

### [Dossier 3: MOSFETs, Gate Drivers & Thermal Analysis](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply/buck_boost_step_by_step_design/03-mosfets-gate-drivers-and-thermal.md)
* **Step 6: Power MOSFET Selection & Losses**: Selection of 4x Infineon BSC034N04LS ($40\,\text{V}, 3.4\,\text{m}\Omega$). Mathematical models for conduction, switching, output capacitance dump ($C_{oss}$), reverse recovery ($Q_{rr}$), and body-diode dead-time losses. Junction temperature rise calculation ($T_j \le 68^\circ\text{C}$).
* **Step 7: Gate Driver & Bootstrap Circuit Design**: High-side floating drive, bootstrap diode and capacitor sizing ($C_{boot} = 0.22\,\mu\text{F}$), dead-time selection ($25\,\text{ns}$) to eliminate cross-conduction shoot-through.

### [Dossier 4: Control Loops, DAC Programming & CC Clamping](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply/buck_boost_step_by_step_design/04-control-loops-dac-and-cc-clamping.md)
* **Step 8: Digital Voltage Programming via DAC Feedback Injection**: Mathematical derivation of the 3-resistor summing network ($R_{top} = 49.9\,\text{k}\Omega, R_{DAC} = 11.0\,\text{k}\Omega, R_{bot} = 3.65\,\text{k}\Omega$), achieving $3.65\,\text{mV / LSB}$ programming resolution from $0.0\,\text{V} \dots 3.3\,\text{V}$ MCU DAC.
* **Step 9: Precision Hardware Constant-Current (CC) Clamp Loop**: Fast high-side Kelvin current sense amplifier (TI INA240A2, $50\,\text{V/V}$) paired with ultra-fast analog comparator (TLV3501, $4.5\,\text{ns}$) clamping the error amplifier `COMP` pin via a BAT54 Schottky diode within $< 5\,\mu\text{s}$.
* **Step 10: Control Loop Small-Signal Modeling & Compensation**: Right-Half-Plane (RHP) Zero analysis in boost mode, Type-II/Type-III compensation network sizing for $f_c = 15\,\text{kHz}$ crossover and $\ge 60^\circ$ phase margin.

### [Dossier 5: Schematics, PCB Layout & Bill of Materials](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply/buck_boost_step_by_step_design/05-schematics-pcb-layout-and-bom.md)
* **Step 11: Complete Component-Level Hardware Schematic**: Pin-by-pin ASCII schematic including LM5176 controller, power stage, bootstrap circuits, current sense, DAC summing junction, and filter banks.
* **Step 12: High-Frequency PCB Layout Guidelines**: Minimizing high $di/dt$ power loops, switch node copper polygon sizing (SW1, SW2), 4-wire differential Kelvin routing, ground plane partitioning (`PGND` vs `AGND`).
* **Step 13: Complete Bill of Materials (BOM)**: Comprehensive component table with manufacturer part numbers, packages, and ratings.

### [Dossier 6: Bring-Up, Calibration & Bench Testing](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply/buck_boost_step_by_step_design/06-bringup-calibration-and-testing.md)
* **Step 14: Step-by-Step Bring-Up Procedure**: Cold resistance checks, low-voltage bench power testing, open-loop gate drive checks, closed-loop voltage ramps.
* **Step 15: Calibration & Accuracy Verification**: 2-point linear DAC calibration matrix, current limit verification.
* **Step 16: Dynamic Load Transient & Thermal Soak Testing**: Step-load testing ($1.5A \rightarrow 3.0A$), ripple measurement with 20MHz bandwidth limit, 1-hour thermal soak.
* **Step 17: Bench Root Cause Analysis (RCA) Troubleshooting Matrix**: Diagnostic guide for output instability, thermal runaway, and transient overshoot.

---

## 3. High-Level System Architecture

```text
==================================================================================================================================
                 4-SWITCH SYNCHRONOUS BUCK-BOOST POST-REGULATOR (24V IN -> 5-20V / 3A PROGRAMMABLE OUT)
==================================================================================================================================

  +24V Intermediate DC Bus In ────┬─────────────────────────────────────────────────────────────┐
  (From Isolated Primary Flyback) │                                                             │
                                ┌─┴─┐ C_IN1                                                   ┌─┴─┐ C_IN2
                                │   │ 2x 22µF / 35V MLCC                                      │   │ 100µF / 35V Low-ESR Polymer
                                └─┬─┘                                                         └─┬─┘
                                  │                                                             │
                               PGND_SEC                                                      PGND_SEC
                                  │
                               Drain (D)
                            ┌─────┴─────┐
                            │    Q_A    │ Buck High-Side Switch
       BUCK_HO ─────────────┤           │ Infineon BSC034N04LS (40V, 3.4mΩ)
                            └─────┬─────┘
                                  │ Source (S)
                                  ├────────────── SW1 Switching Node ────┐
                                  │                                      │
                               Drain (D)                               ┌─┴─┐
                            ┌─────┴─────┐                              │   │ Inductor L
                            │    Q_B    │ Buck Low-Side Synchronous    │   │ 10µH / 8.5A Flat-Wire
       BUCK_LO ─────────────┤           │ BSC034N04LS (40V, 3.4mΩ)     └─┬─┘ (Wurth 7443321000)
                            └─────┬─────┘                                │
                                  │ Source (S)                           │
                               PGND_SEC                                  ├────────────── SW2 Switching Node ────┐
                                                                         │                                      │
                                                                      Source (S)                             Drain (D)
                                                                   ┌─────┴─────┐                          ┌─────┴─────┐
                                                                   │    Q_D    │ Boost High-Side Sync     │    Q_C    │ Boost Low-Side Sw
                                              BOOST_HO ────────────┤           │ BSC034N04LS              │           │ BSC034N04LS
                                                                   └─────┬─────┘             BOOST_LO ────┤           │
                                                                         │ Drain (D)                      └─────┬─────┘
                                                                         │                                      │ Source (S)
                                                                         ├──────────────────────────┐        PGND_SEC
                                                                         │                          │
                                                                       ┌─┴─┐                      ┌─┴─┐
                                                   Kelvin Sense Lead 1 │   │ R_shunt              │   │ C_OUT_POLY
                                                                       └─┬─┘ 10mΩ / 0.1% / 3W     │   │ 100µF / 25V Polymer
                                                   Kelvin Sense Lead 2   ├───┐                    └─┬─┘ (ESR = 12mΩ)
                                                                         │   │                      │
                                                                         │ ┌─┴─┐ C_OUT_CER       PGND_SEC
                                                                         │ │   │ 4x 22µF / 25V MLCC
                                                                         │ └─┬─┘
                                                                         │   │
                                                                         │ PGND_SEC
                                                                         │
  +V_OUT Programmable Terminal ──────────────────────────────────────────┴────────────────────────────────────────────────> +V_OUT (5.0V - 20.0V @ 3A)
  (To Load & Dual-Domain Sensing)                                        │
                                                                         ├───────────────────┐
                                                                         │                   │
                                                                       ┌─┴─┐ R_top         ┌─┴─┐ C_FF
                                                                       │   │ 49.9kΩ        │   │ 47pF
                                                                       └─┬─┘ (0.1%)        └─┬─┘
                                                                         │                   │
                                                                         ├─── V_FB Node ─────┘
                                                                         │    (Held at V_REF = 1.20V)
                                                         ┌───────────────┼───────────────────────────────┐
                                                         │               │                               │
                                                       ┌─┴─┐           ┌─┴─┐                           ┌─┴─┐
                                                 R_DAC │   │ 11.0kΩ    │   │ R_bot                     │   │
                                                 (0.1%)└─┬─┘ (0.1%)    └─┬─┘ 3.65kΩ (0.1%)             │   │
                                                         │               │                             │ C │ LM5176
  MCU_DAC1 (0.0V - 3.3V) ────────────────────────────────┘            AGND_SEC                         │ O │ Error Amp
  (Voltage Setpoint: 20V down to 5V)                                                                   │ M │ Pin
                                                                                                       │ P │
  From CC Op-Amp Clamp Diode (BAT54) ──────────────────────────────────────────────────────────────────┤   │
                                                                                                       └───┘
==================================================================================================================================
```
