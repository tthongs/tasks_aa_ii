# Dossier 5: Schematics, PCB Layout & Bill of Materials

Welcome to **Dossier 5** of the Step-by-Step 4-Switch Synchronous Buck-Boost Post-Regulator Design Guide. This document provides the pin-level ASCII schematic of the complete power stage, critical high-frequency PCB layout rules, and the complete engineering Bill of Materials (BOM).

---

## Step 11: Complete Component-Level Hardware Schematic

Below is the complete component-level hardware schematic of the 4-switch synchronous Buck-Boost post-regulator based on the **Texas Instruments LM5176** multi-mode controller:

```text
====================================================================================================================================================
                        COMPLETE 4-SWITCH SYNCHRONOUS BUCK-BOOST POST-REGULATOR (24V IN -> 5-20V / 3A PROGRAMMABLE OUT)
====================================================================================================================================================

  +24V Intermediate DC Bus ───┬─────────────────────────────────────────────────────────────────────────┐
  (From Isolated Flyback)     │                                                                         │
                            ┌─┴─┐ C_IN_CER                                                            ┌─┴─┐ C_IN_POLY
                            │   │ 2x 22µF / 35V MLCC                                                  │   │ 100µF / 35V Polymer
                            └─┬─┘ (TDK C3225X7R1V226M)                                                └─┬─┘ (Panasonic 35SVPF100M)
                              │                                                                         │
                           PGND_SEC                                                                  PGND_SEC
                              │
                           Drain (D)
                        ┌─────┴─────┐
                        │    Q_A    │ BSC034N04LS (40V, 3.4mΩ)
        BUCK_HO1 ───────┤           │ Buck High-Side Switch
                        └─────┬─────┘
                              │ Source (S)
                              ├────────────── SW1 Switching Node ─────────────┐
                              │                                               │
                           Drain (D)                                        ┌─┴─┐
                        ┌─────┴─────┐                                       │   │ Power Inductor L
                        │    Q_B    │ BSC034N04LS                           │   │ 10µH / 8.5A Flat-Wire
        BUCK_LO1 ───────┤           │ Buck Low-Side Sync Switch             └─┬─┘ (Wurth 7443321000)
                        └─────┬─────┘                                         │
                              │ Source (S)                                    │
                           PGND_SEC                                           ├────────────── SW2 Switching Node ─────────────┐
                                                                              │                                               │
                                                                           Source (S)                                      Drain (D)
                                                                        ┌─────┴─────┐                                   ┌─────┴─────┐
                                                                        │    Q_D    │ BSC034N04LS                       │    Q_C    │ BSC034N04LS
                                                   BOOST_HO2 ───────────┤           │ Boost High-Side Sync              │           │ Boost Low-Side Sw
                                                                        └─────┬─────┘                      BOOST_LO2 ───┤           │
                                                                              │ Drain (D)                               └─────┬─────┘
                                                                              │                                               │ Source (S)
                                                                              ├──────────────────────────┐                 PGND_SEC
                                                                              │                          │
                                                                            ┌─┴─┐                      ┌─┴─┐
                                                        Kelvin Force Lead 1 │   │ R_shunt              │   │ C_OUT_POLY
                                                                            └─┬─┘ 10mΩ / 0.1% / 3W     │   │ 100µF / 25V Polymer
                                                        Kelvin Force Lead 2   ├───┐                    └─┬─┘ (ESR = 12mΩ)
                                                                              │   │                      │
                                                                              │ ┌─┴─┐ C_OUT_CER       PGND_SEC
                                                                              │ │   │ 4x 22µF / 25V MLCC
                                                                              │ └─┬─┘ (Murata 1210)
                                                                              │   │
                                                                              │ PGND_SEC
                                                                              │
  +V_OUT Programmable Rail ───────────────────────────────────────────────────┴───────────────────────────────────────────────────────> +V_OUT (5V-20V/3A)
  (To Load & Dual Metering)                                                   │
                                                                              ├──────────────────────────┐
                                                                              │                          │
                                                                            ┌─┴─┐ R_top                ┌─┴─┐ C_FF
                                                                            │   │ 49.9kΩ (0.1%)        │   │ 47pF
                                                                            └─┬─┘                      └─┬─┘
                                                                              │                          │
                                                                              ├─── FB Summing Node ──────┘
                                                                              │    (Held at V_REF = 1.20V)
                                                              ┌───────────────┼───────────────────────────────┐
                                                              │               │                               │
                                                            ┌─┴─┐           ┌─┴─┐                           ┌─┴─┐
                                                      R_DAC │   │ 11.0kΩ    │   │ R_bot                     │   │
                                                      (0.1%)└─┬─┘           └─┬─┘ 3.65kΩ (0.1%)             │   │ LM5176PWPR
                                                              │               │                             │ F │ Error Amp Pin
  MCU_DAC1 (0.0V - 3.3V) ─────────────────────────────────────┘            AGND_SEC                         │ B │
  (Voltage Setpoint: 20V down to 5V)                                                                        └───┘
                                                                                                              │
                                                                                                            ┌─┴─┐
                                                                                                            │ C │
  From CC Analog Clamp Diode (BAT54) ───────────────────────────────────────────────────────────────────────┤ O │ COMP Pin
                                                                                                            │ M │
                                                                                                            │ P │
                                                                                                            └─┬─┘
                                                                                                              │
                                                                                                              ├───[ R_comp: 10.0kΩ ]───┬───[ C_comp1: 2.2nF ]──┐
                                                                                                              │                        │                       │
                                                                                                              ├───[ C_comp2: 47pF ]────┴───────────────────────┤
                                                                                                              │                                                │
                                                                                                              └───────────────────────────────────────────── AGND_SEC
====================================================================================================================================================
```

---

## Step 12: High-Frequency PCB Layout Guidelines

The PCB is architected as a high-density **4-layer board ($1.6\,\text{mm}$ FR-4, $2\,\text{oz}$ copper outer layers, $1\,\text{oz}$ inner layers)**:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 4-LAYER PCB STACKUP ALLOCATION                                   │
├───────┬──────────────────────────┬────────┬──────────────────────────────────────────────────────┤
│ Layer │ Layer Name               │ Copper │ Signal & Power Plane Allocation                      │
├───────┼──────────────────────────┼────────┼──────────────────────────────────────────────────────┤
│ **L1**│ Top Layer (High Power)   │ 2.0 oz │ Power MOSFETs, Inductor, C_IN, C_OUT, high-current   │
│ **L2**│ Inner Layer 1 (Ground)   │ 1.0 oz │ Continuous, solid ground return (PGND plane)         │
│ **L3**│ Inner Layer 2 (Power)    │ 1.0 oz │ +5V controller VCC, +3.3V MCU, gate drive power      │
│ **L4**│ Bottom Layer (Signals)   │ 2.0 oz │ Sensitive FB traces, Kelvin shunt lines, I2C buses   │
└───────┴──────────────────────────┴────────┴──────────────────────────────────────────────────────┘
```

```text
                    MINIMIZING HIGH di/dt POWER LOOPS ON LAYER 1
       BUCK INPUT POWER LOOP                              BOOST OUTPUT POWER LOOP
       (Area < 0.8 cm²!)                                  (Area < 0.8 cm²!)
    +VIN ──────────────┐                               Inductor L ─────────┐
      │                │                                   │               │
    ┌─┴─┐ C_IN       ┌─┴─┐ Q_A                           ┌─┴─┐ Q_D       ┌─┴─┐ C_OUT
    │   │ MLCC       │   │ Buck HS                       │   │ Boost HS  │   │ MLCC
    └─┬─┘            └─┬─┘                               └─┬─┘           └─┬─┘
      │                │                                   │               │
      │              ┌─┴─┐ Q_B                             │             ┌─┴─┐ Q_C
      │              │   │ Buck LS                         │             │   │ Boost LS
      │              └─┬─┘                                 │             └─┬─┘
      │                │                                   │               │
    PGND ──────────────┴─── PGND                         PGND ─────────────┴─── PGND
```

### Critical Layout Rules:
1. **Loop Area Minimization**: The Buck input loop ($C_{IN} \rightarrow Q_A \rightarrow Q_B \rightarrow PGND$) and Boost output loop ($Q_D \rightarrow C_{OUT} \rightarrow Q_C \rightarrow PGND$) carry pulsed currents with $di/dt > 1.5\,\text{A/ns}$. These loops must be placed directly adjacent with total enclosed surface area $< 0.8\,\text{cm}^2$ to minimize magnetic radiated EMI.
2. **Switch Nodes (SW1, SW2)**: The copper polygons connecting $Q_A/Q_B$ to the inductor (SW1) and the inductor to $Q_C/Q_D$ (SW2) experience rapid $dV/dt$ voltage transitions ($> 15\,\text{V/ns}$). Keep these polygons wide enough to carry $3.5\,\text{A}$ without overheating, but compact in surface area to avoid forming RF radiating patch antennas.
3. **4-Wire Kelvin Shunt Routing**: The differential sense traces from $R_{shunt}$ to the INA240A2 current sense amplifier must exit directly from the inner Kelvin pads of the 2512 package, running parallel on Layer 4 shielded by the Layer 2 ground plane.
4. **Single-Point Ground Star**: Analog Ground (`AGND`) for sensitive error amplifier resistors and controller references must be kept completely separated from Power Ground (`PGND`), joining together at **exactly one star connection directly beneath the output capacitor bank**.

---

## Step 13: Complete Bill of Materials (BOM)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BILL OF MATERIALS (BOM): 4-SWITCH BUCK-BOOST STAGE                                    │
├──────┬─────┬───────────────────────────┬─────────────────────────┬──────────────┬────────────────────────────────────────┤
│ Item │ Qty │ Reference Designator      │ Description             │ Package      │ Manufacturer & Part Number             │
├──────┼─────┼───────────────────────────┼─────────────────────────┼──────────────┼────────────────────────────────────────┤
│ 1    │ 1   │ U1 (Controller)           │ 4-Switch Sync BB IC     │ HTSSOP-28    │ Texas Instruments LM5176PWPR           │
│ 2    │ 4   │ Q_A, Q_B, Q_C, Q_D        │ Power MOSFET 40V 3.4mΩ  │ SuperSO8     │ Infineon BSC034N04LS                   │
│ 3    │ 1   │ L1                        │ Flat-Wire Inductor 10uH │ 10x10mm SMD  │ Wurth Elektronik 7443321000            │
│ 4    │ 1   │ R_shunt                   │ Kelvin Shunt 10mΩ 0.1%  │ 2512 SMD     │ Bourns CSS2H-2512R-L010F               │
│ 5    │ 1   │ U2 (Current Sense Amp)    │ High-Side Current Sense │ SOIC-8       │ Texas Instruments INA240A2D            │
│ 6    │ 1   │ U3 (Fast Comparator)      │ 4.5ns High-Speed Comp   │ SOT-23-6     │ Texas Instruments TLV3501AIDBVR        │
│ 7    │ 1   │ D_clamp                   │ Schottky Diode 30V 200mA│ SOT-23       │ Diodes Inc. BAT54                      │
│ 8    │ 2   │ D_boot1, D_boot2          │ Schottky Diode 60V 1.0A │ SOD-123F     │ Nexperia PMEG6010CEH                   │
│ 9    │ 2   │ C_boot1, C_boot2          │ Ceramic Cap 0.22µF 50V  │ 0805 X7R     │ Murata GRM21BR71H224KA01L              │
│ 10   │ 2   │ C_IN_CER                  │ Ceramic Cap 22µF 35V    │ 1210 X7R     │ TDK C3225X7R1V226M                     │
│ 11   │ 1   │ C_IN_POLY                 │ Polymer Cap 100µF 35V   │ Radial 8x10  │ Panasonic 35SVPF100M                   │
│ 12   │ 4   │ C_OUT_CER                 │ Ceramic Cap 22µF 25V    │ 1210 X7R     │ Murata GRM32ER71E226KE15L              │
│ 13   │ 1   │ C_OUT_POLY                │ Polymer Cap 100µF 25V   │ SMD 8x10.5   │ Panasonic 25SVPF100M                   │
│ 14   │ 1   │ R_top                     │ Resistor 49.9kΩ 0.1%    │ 0805 SMD     │ Vishay TNPW080549K9BEEA                │
│ 15   │ 1   │ R_DAC                     │ Resistor 11.0kΩ 0.1%    │ 0805 SMD     │ Vishay TNPW080511K0BEEA                │
│ 16   │ 1   │ R_bot                     │ Resistor 3.65kΩ 0.1%    │ 0805 SMD     │ Vishay TNPW08053K65BEEA                │
│ 17   │ 1   │ C_FF                      │ Ceramic Cap 47pF 50V    │ 0603 C0G/NP0 │ KEMET C0603C470J5GACTU                 │
│ 18   │ 1   │ R_comp                    │ Resistor 10.0kΩ 1.0%    │ 0603 SMD     │ Panasonic ERA-3AEB103V                 │
│ 19   │ 1   │ C_comp1                   │ Ceramic Cap 2.2nF 50V   │ 0603 X7R     │ Murata GRM188R71H222KA01D              │
│ 20   │ 1   │ C_comp2                   │ Ceramic Cap 47pF 50V    │ 0603 C0G/NP0 │ KEMET C0603C470J5GACTU                 │
│ 21   │ 4   │ R_gate1..R_gate4          │ Resistor 2.2Ω 5%        │ 0603 SMD     │ Panasonic ERJ-3GEYJ2R2V                │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
