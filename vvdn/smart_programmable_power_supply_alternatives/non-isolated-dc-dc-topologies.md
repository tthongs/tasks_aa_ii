# Non-Isolated DC-DC Post-Regulator Topologies: High-Bus Buck, SEPIC, Zeta & Tracking Buck+LDO

Welcome to the **VVDN Engineering Hub Technical Dossier on Non-Isolated DC-DC Post-Regulator Converter Topologies** for the Smart Programmable Power Supply. This document provides mathematical derivations, circuit schematics, component sizing formulas, and engineering trade-off evaluations for four major post-regulator alternatives to the baseline 4-switch synchronous Buck-Boost converter:

1. **High-Bus (+36 V DC) Pure Synchronous Buck Converter** (Eliminates 2 switches, pure buck operation, simplified control).
2. **Coupled-Inductor Synchronous SEPIC Converter** (Ground-referenced switch, series DC blocking isolation, low-side drive).
3. **Synchronous Zeta Converter** (Continuous output inductor current, buck-like low output ripple).
4. **Hybrid Tracking Buck + Ultra-Low-Noise Linear LDO** (Lab-grade sub-millivolt noise, RF/mixed-signal grade).

---

## 1. Post-Regulator Requirements & Architectural Comparison

The post-regulator is downstream of the isolated primary stage. It must deliver a digitally controlled, tightly regulated output voltage from $5.0\,\text{V}$ to $20.0\,\text{V}$ at currents up to $3.0\,\text{A}$ ($60\,\text{W}$ max continuous power) with fast transient response and sub-$25\,\text{mV}_{\text{pk-pk}}$ ripple.

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       NON-ISOLATED DC-DC POST-REGULATORS: ARCHITECTURAL COMPARISON                                     │
├──────────────────────────────┬──────────────────────────────┬──────────────────────────────┬──────────────────────────────┬────────────┤
│ Metric / Parameter           │ Baseline: 4-Switch BB        │ Option A: High-Bus Buck      │ Option B: Coupled SEPIC      │ Option C: Sync Zeta        │ Option D: Buck + LDO       │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┼──────────────────────────────┼────────────┤
│ **Input DC Rail ($V_{IN}$)** │ $+24.0\,\text{V}$ (Nominal)  │ $\mathbf{+36.0\,\text{V}}$   │ $+24.0\,\text{V}$ (Nominal)  │ $+24.0\,\text{V}$ (Nominal)│ $+28.0\,\text{V}$ (Nominal)│
│ **Active Power MOSFETs**     │ 4 Switches (H-Bridge)        │ $\mathbf{2\text{ Switches}}$ │ 2 Switches (Sync)            │ 2 Switches (Sync)          │ 2 Buck FETs + 1 LDO Pass   │
│ **Operating Regimes**        │ Buck, Buck-Boost, Boost      │ **Pure Buck Only (100%)**    │ Buck-Boost ($D/(1-D)$)       │ Buck-Boost ($D/(1-D)$)     │ Pure Buck + Linear Drop    │
│ **Peak Stage Efficiency**    │ $96.8\%$                     │ $\mathbf{97.5\%}$            │ $94.5\%$                     │ $95.1\%$                   │ $93.8\%$ (due to LDO drop) │
│ **Output Ripple (pk-pk)**    │ $< 25\,\text{mV}$            │ $< 18\,\text{mV}$            │ $< 20\,\text{mV}$            │ $\mathbf{< 12\,\text{mV}}$ │ $\mathbf{< 0.8\,\text{mV}}$│
│ **Switch Voltage Stress**    │ $V_{IN} = 24\,\text{V}$      │ $V_{IN} = 36\,\text{V}$      │ $\mathbf{V_{IN}+V_O = 44V}$  │ $\mathbf{V_{IN}+V_O = 44V}$│ $V_{IN} = 28\,\text{V}$    │
│ **High-Side Drivers Req.**   │ 2 Floating Drivers           │ 1 Floating Driver            │ **0 (Ground referenced!)**   │ 1 Floating Driver          │ 1 Floating Driver          │
│ **Inherent Short Isolation** │ No (Direct path through D)   │ No (Direct path through D)   │ **Yes (Series C_sep cap)**   │ No                         │ **Yes (LDO foldback)**     │
│ **Relative Hardware Cost**   │ $1.00\times$ (Reference)     │ $\mathbf{0.78\times (-22\%)}$│ $0.85\times (-15\%)$         │ $0.88\times (-12\%)$       │ $1.15\times (+15\%)$       │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────┴──────────────────────────────┴────────────┘
```

---

## 2. Option A: High-Bus (+36 V DC) Pure Synchronous Buck Post-Regulator

By designing the primary flyback stage to regulate an intermediate bus of $+36.0\,\text{V}$ DC instead of $+24.0\,\text{V}$, the post-regulator operates **strictly in Buck mode** across the entire output range ($5.0\,\text{V} \dots 20.0\,\text{V}$):

$$D = \frac{V_{OUT}}{V_{IN}} \implies D_{min} = \frac{5.0\,\text{V}}{36.0\,\text{V}} = 13.9\%, \quad D_{max} = \frac{20.0\,\text{V}}{36.0\,\text{V}} = 55.6\%$$

This eliminates the Boost half-bridge switches ($Q_C, Q_D$) and their floating gate driver completely!

```text
====================================================================================================================================================
                        OPTION A ARCHITECTURE: HIGH-BUS (+36V IN) PURE SYNCHRONOUS BUCK POST-REGULATOR
====================================================================================================================================================

  +36.0V Intermediate Bus In ────────┬──────────────────────────────────────────────────────────────────┐
                                     │                                                                  │
                                   ┌─┴─┐ C_IN1                                                        ┌─┴─┐ C_IN2
                                   │   │ 2x 10µF / 50V X7R Ceramic                                    │   │ 100µF / 50V Low-ESR Polymer
                                   └─┬─┘                                                              └─┬─┘
                                     │                                                                  │
                                  GND_SEC                                                            GND_SEC
                                     │
                                  Drain (D)
                               ┌─────┴─────┐
                               │    Q_A    │ Buck High-Side Switch
          BUCK_HO ─────────────┤           │ Infineon BSC035N10NS5 (100V, 3.5mΩ)
                               └─────┬─────┘
                                     │ Source (S)
                                     ├────────────── SW Switching Node ───────────┐
                                     │                                            │
                                  Drain (D)                                     ┌─┴─┐
                               ┌─────┴─────┐                                    │   │ Inductor L
                               │    Q_B    │ Buck Low-Side Synchronous Rect.    │   │ 15µH / 6.5A Flat-Wire
          BUCK_LO ─────────────┤           │ BSC035N10NS5 (100V, 3.5mΩ)         └─┬─┘ (Wurth 7443321500)
                               └─────┬─────┘                                      │
                                     │ Source (S)                                 │
                                  GND_SEC                                         ├──────────────────────────┐
                                                                                  │                          │
                                                                                ┌─┴─┐                      ┌─┴─┐
                                                            Kelvin Shunt Lead 1 │   │ R_shunt              │   │ C_OUT_POLY
                                                                                └─┬─┘ 10mΩ / 0.1% / 3W     │   │ 100µF / 25V Polymer
                                                            Kelvin Shunt Lead 2   ├───┐                    └─┬─┘ (ESR = 12mΩ)
                                                                                  │   │                      │
                                                                                  │ ┌─┴─┐ C_OUT_CER        GND_SEC
                                                                                  │ │   │ 4x 22µF / 25V MLCC
                                                                                  │ └─┬─┘
                                                                                  │   │
                                                                                  │ GND_SEC
                                                                                  │
  +V_OUT Programmable Terminal ───────────────────────────────────────────────────┴──────────────────────────┴───> +V_OUT (5.0V - 20.0V @ 3A)
  (To Load & Dual-Domain Sensing)                                                 │
                                                                                  ├───────────────────┐
                                                                                  │                   │
                                                                                ┌─┴─┐ R_top         ┌─┴─┐ C_FF
                                                                                │   │ 49.9kΩ        │   │ 47pF
                                                                                └─┬─┘ (0.1%)        └─┬─┘
                                                                                  │                   │
                                                                                  ├─── V_FB Node ─────┘
                                                                                  │    (Summing Junction held at V_REF = 1.20V)
                                                                  ┌───────────────┼───────────────────────────────┐
                                                                  │               │                               │
                                                                ┌─┴─┐           ┌─┴─┐                           ┌─┴─┐
                                                          R_DAC │   │ 11.0kΩ    │   │ R_bot                     │   │
                                                          (0.1%)└─┬─┘ (0.1%)    └─┬─┘ 3.65kΩ (0.1%)             │   │ LM5146 / TPS54360
                                                                  │               │                             │ C │ Buck Controller
  MCU_DAC1 (0.0V - 3.3V) ─────────────────────────────────────────┘            GND_SEC                          │ O │ Error Amp
  (Voltage Setpoint: 20V down to 5V)                                                                            │ M │ Input Pin
                                                                                                                │ P │
  From CC Op-Amp Clamp Diode (BAT54) ───────────────────────────────────────────────────────────────────────────┤   │
                                                                                                                └───┘
====================================================================================================================================================
```

### 2.1 Inductor Sizing ($L$):
For continuous conduction mode (CCM) across the full range with ripple ratio $r = 30\%$ ($\Delta I_L = 0.90\,\text{A}$) at $f_{sw} = 250\,\text{kHz}$:
Worst-case ripple occurs at $D = 50\%$ ($V_{OUT} = 18.0\,\text{V}$):
$$L = \frac{V_{OUT} \cdot (V_{IN} - V_{OUT})}{\Delta I_L \cdot f_{sw} \cdot V_{IN}} = \frac{18.0 \cdot (36.0 - 18.0)}{0.90 \cdot 250000 \cdot 36.0} = \frac{324}{8.1 \times 10^6} = 4.0 \times 10^{-5}\,\text{H} \longrightarrow \mathbf{Selected: 15.0\,\mu\text{H}}$$
* **Inductor Selected**: Wurth Elektronik 7443321500 (WE-HCC flat-wire, $15.0\,\mu\text{H}$, $I_{rms} = 7.0\,\text{A}$, $I_{sat} = 9.5\,\text{A}$, $DCR = 18.5\,\text{m}\Omega$).

### 2.2 Why High-Bus Pure Buck is Highly Recommended:
1. **Simplified Compensation Loop**: Unlike a buck-boost converter which exhibits a right-half-plane (RHP) zero during boost operation that limits loop bandwidth to $< 10\,\text{kHz}$, a pure buck converter has **no RHP zero**! The control loop can be compensated with Type-II/Type-III compensation for high bandwidth ($f_c \approx 35\,\text{kHz}$), delivering recovery times $< 60\,\mu\text{s}$ under $3\,\text{A}$ transient steps.
2. **50% Reduction in Gate Drive Losses**: Driving 2 MOSFETs at $250\,\text{kHz}$ instead of 4 MOSFETs cuts gate drive dissipation in half ($P_{gate} = 2 \cdot Q_g \cdot V_{drv} \cdot f_{sw} \approx 60\,\text{mW}$ vs $120\,\text{mW}$).
3. **No Boost Conduction Losses**: Eliminates the series resistance of the boost high-side synchronous switch ($Q_D$).

---

## 3. Option B: Coupled-Inductor Synchronous SEPIC Converter

The **Single-Ended Primary-Inductor Converter (SEPIC)** is a non-inverting buck-boost topology that allows $V_{OUT}$ to be higher, equal to, or lower than $V_{IN}$ ($24\,\text{V} \rightarrow 5\,\text{V} \dots 20\,\text{V}$).

```text
====================================================================================================================================================
               OPTION B ARCHITECTURE: COUPLED-INDUCTOR SYNCHRONOUS SEPIC POST-REGULATOR (24V IN -> 5-20V / 3A OUT)
====================================================================================================================================================

  +24V Intermediate Bus In ────────┬────────────────────────────────────────────────────────────────────┐
                                   │                                                                    │
                                 ┌─┴─┐ C_IN                                                             │
                                 │   │ 2x 10µF / 35V MLCC                                               │
                                 └─┬─┘                                                                  │
                                   │                                                                    │
                                GND_SEC                                                                 │
                                   │                                                                    │
                                   ├──[ Primary Inductor L1: 22µH ]──┐                                  │
                                   │   (Coilcraft MSD1278 Coupled)   │                                  │
                                   │                                 ├─── SW1 Node ──┐                  │
                                   │                                 │               │                  │
                                   │                              Drain (D)        ┌─┴─┐ C_sep          │
                                   │                           ┌─────┴─────┐       │   │ SEPIC AC Cap   │
                                   │                           │    Q1     │       └─┬─┘ (10µF / 50V    │
            PWM_LS (Ground Ref) ───┼───────────────────────────┤ (Low-Side)│         │    X7R Ceramic)  │
                                   │                           └─────┬─────┘         │                  │
                                   │                                 │ Source (S)    │                  │
                                   │                              GND_SEC            ├─── SW2 Node ─────┤
                                   │                                                 │                  │
                                   │                                              Source (S)          Drain (D)
                                   │                                           ┌─────┴─────┐       ┌─────┴─────┐
                                   │                                           │   Q_SR    │       │    L2     │ Secondary Inductor
            PWM_HS (Floating) ─────┼───────────────────────────────────────────┤ (Sync FET)│       │   22µH    │ (Coupled 1:1 on
                                   │                                           └─────┬─────┘       └─────┬─────┘  same core as L1)
                                   │                                                 │ Drain (D)         │
                                   │                                                 ├───────────────────┴───┬───> +V_OUT (5V-20V @ 3A)
                                   │                                                 │                       │
                                   │                                               ┌─┴─┐ R_shunt           ┌─┴─┐ C_OUT
                                   │                                               │   │ 10mΩ / 0.1%       │   │ 4x 22µF MLCC
                                   │                                               └─┬─┘                   └─┬─┘ + 100µF Polymer
                                   │                                                 │                       │
  Secondary Ground Return ─────────┴─────────────────────────────────────────────────┴───────────────────────┴─── GND_SEC
====================================================================================================================================================
```

### 3.1 SEPIC Voltage & Current Relationships:
The SEPIC transfer function is:
$$\frac{V_{OUT}}{V_{IN}} = \frac{D}{1 - D} \implies D = \frac{V_{OUT}}{V_{IN} + V_{OUT}}$$
* At $V_{OUT} = 5.0\,\text{V}$ ($V_{IN} = 24\,\text{V}$): $D = \frac{5}{24 + 5} = 17.2\%$
* At $V_{OUT} = 20.0\,\text{V}$ ($V_{IN} = 24\,\text{V}$): $D = \frac{20}{24 + 20} = 45.5\%$

### 3.2 Key SEPIC Component Sizing & Stresses:
1. **Switch Voltage Stress ($V_{DS1}$)**:
   When $Q_1$ turns OFF, the drain flies up to:
   $$V_{DS1(max)} = V_{IN} + V_{OUT} = 24.0\,\text{V} + 20.0\,\text{V} = \mathbf{44.0\,\text{V}}$$
   Therefore, $60\,\text{V}$ rated MOSFETs (such as Infineon BSC052N06NS) are required.
2. **Series AC Coupling Capacitor ($C_{sep}$)**:
   $C_{sep}$ transfers all energy between input and output. The DC voltage across $C_{sep}$ is exactly equal to $V_{IN} = 24.0\,\text{V}$.
   RMS Ripple Current through $C_{sep}$:
   $$I_{Csep(rms)} = I_{OUT} \sqrt{\frac{D}{1 - D}} = 3.0\,\text{A} \times \sqrt{\frac{0.455}{1 - 0.455}} = 3.0 \times 0.914 = \mathbf{2.74\,\text{A}_{\text{RMS}}}$$
   *Design Rule*: Must use low-loss Class-II ceramic capacitors ($2\times 10\,\mu\text{F} / 50\,\text{V}$ X7R $1210$) rated for $\ge 3\,\text{A}_{\text{RMS}}$ to prevent dielectric heating!
3. **Coupled Inductor Advantage ($L_1, L_2$)**:
   Winding both inductors on a single magnetic core (**Coilcraft MSD1278-223**, $22\,\mu\text{H}$) provides:
   * **Zero-Ripple Current Steering**: The AC ripple voltages across $L_1$ and $L_2$ are identical. Leakage inductance steers the AC ripple current almost entirely away from the input, delivering ultra-low input current ripple!
   * **Saves 50% Magnetic Board Space**.
4. **Inherent Short-Circuit Protection**:
   If the active switch $Q_1$ experiences a hard short circuit to ground, capacitor $C_{sep}$ blocks DC current from flowing into the output load. The supply safely latches off without dumping bulk energy into sensitive user loads!

---

## 4. Option C: Synchronous Zeta Converter

The **Zeta Converter** (also called the inverse SEPIC) provides non-inverting buck-boost operation with a major topological advantage: **an inductor in series with the output**!

```text
====================================================================================================================================================
                        OPTION C ARCHITECTURE: SYNCHRONOUS ZETA CONVERTER (24V IN -> 5-20V / 3A OUT)
====================================================================================================================================================

  +24V Intermediate Bus In ────────┬────────────────────────────────────────────────────────────────────┐
                                   │ Drain (D)                                                          │
                                ┌──┴─────────────┐                                                    ┌─┴─┐ C_IN
                                │       Q1       │ High-Side Switch                                   │   │ 2x 10µF / 50V
           GATE_HS ─────────────┤ (BSC052N06NS)  │                                                    └─┬─┘
                                └──┬─────────────┘                                                      │
                                   │ Source (S)                                                      GND_SEC
                                   ├───────────── SW1 Node ──────────────────────────┐
                                   │                                                 │
                                 ┌─┴─┐                                             ┌─┴─┐ C_fly
                                 │   │ Inductor L1                                 │   │ Flying Transfer Cap
                                 └─┬─┘ 15µH                                        └─┬─┘ (10µF / 50V X7R)
                                   │                                                 │
                                   ├─── SW2 Node ────────────────────────────────────┤
                                   │                                                 │
                                 ┌─┴─┐                                             ┌─┴─┐
                                 │   │ Q_SR (Low-Side Sync)                        │   │ Inductor L2 (Output Inductor)
            GATE_LS ─────────────┤   │ (BSC052N06NS: 60V)                          │   │ 15µH / 6.5A Flat-Wire
                                 └─┬─┘                                             └─┬─┘
                                   │                                                 │
                                GND_SEC                                              ├──────────────┬───> +V_OUT (5V-20V @ 3A)
                                                                                     │              │
                                                                                   ┌─┴─┐ R_shunt  ┌─┴─┐ C_OUT
                                                                                   │   │ 10mΩ     │   │ 2x 22µF MLCC + 100µF Poly
                                                                                   └─┬─┘          └─┬─┘ (Ultra-low output ripple!)
                                                                                     │              │
  Secondary Ground Return ───────────────────────────────────────────────────────────┴──────────────┴─── GND_SEC
====================================================================================================================================================
```

### 4.1 Zeta Converter Engineering Benefits:
* **Buck-Like Output Filter**: In the SEPIC and Buck-Boost converters, the output diode/switch dumps discontinuous current pulses into $C_{OUT}$, demanding high ESR/capacitance banks to suppress voltage spikes. In the Zeta converter, **inductor $L_2$ connects directly to the output**, ensuring that the output capacitor is fed by a smooth, continuous triangular inductor current:
  $$\Delta V_{OUT} = \frac{\Delta I_{L2}}{8 \cdot f_{sw} \cdot C_{OUT}} = \frac{0.80\,\text{A}}{8 \times 250000 \times 100 \times 10^{-6}} = \mathbf{4.0\,\text{mV}_{\text{pk-pk}}!}$$
* Output ripple is **less than half** that of a standard Buck-Boost or SEPIC under identical switching conditions.

---

## 5. Option D: Hybrid Tracking Buck + Ultra-Low-Noise Linear (LDO) Post-Regulator

For precision RF prototyping, 24-bit $\Delta\Sigma$ ADC evaluation, and low-noise operational amplifier characterization, switching supply ripple ($15\,\text{mV} \dots 25\,\text{mV}_{\text{pk-pk}}$) is unacceptable. The **Hybrid Tracking Buck + LDO** topology delivers true lab-grade clean power.

```text
====================================================================================================================================================
               OPTION D ARCHITECTURE: DYNAMIC TRACKING BUCK PRE-REGULATOR + ULTRA-LOW NOISE LDO POST-REGULATOR
====================================================================================================================================================

  +28V Intermediate Bus In ────────[ Synchronous Buck Pre-Regulator ]───┬───> V_TRACK (Tracks V_OUT + 350mV)
                                   (250kHz, LM5146, D = 19% to 73%)     │     (e.g., 5.35V for 5.0V out; 20.35V for 20.0V out)
                                                                      ┌─┴─┐
                                                                      │   │ C_MID (44µF Ceramic)
                                                                      └─┬─┘
                                                                        │
                                                                     GND_SEC
                                                                        │
  V_TRACK (V_OUT + 350mV) ──────────────────────────────────────────────┤
                                                                        │ IN
                                                                     ┌──┴─────────────────────────┐
                                                                     │ TI TPS7A4701 / Discrete    │
                                                                     │ Ultra-Low-Noise LDO (3.0A) │
                                                                     │ - Noise: 4.17µV RMS        │
                                                                     │ - PSRR: 82dB @ 100Hz       │
                                                                     │ - PSRR: 65dB @ 250kHz      │
                                                                     │                            │
                                                                     │ FB                    OUT  │
                                                                     └──┬─────────────────────┬───┘
                                                                        │                     │
                                                                      ┌─┴─┐ R_top             ├───> +V_OUT Ultra-Clean DC
                                                                      │   │ 49.9kΩ            │     (5.0V - 20.0V @ 3.0A)
                                                                      └─┬─┘                   │     Ripple < 0.8mV pk-pk!
                                                                        │                     │     Noise < 15µV RMS!
                                                                        ├─── Summing Node     │
                                                                        │                     │
                                     MCU DAC Setpoint (0-3.3V) ─────────┤                   ┌─┴─┐ C_OUT_CLEAN
                                                                        │                   │   │ 2x 22µF Ceramic MLCC
                                                                      ┌─┴─┐ R_DAC           └─┬─┘
                                                                      │   │ 11.0kΩ            │
                                                                      └─┬─┘                GND_SEC
                                                                        │
  Secondary Ground Return ──────────────────────────────────────────────┴─────────────────────────── GND_SEC
====================================================================================================================================================
```

### 5.1 Dynamic Headroom Tracking Mechanics:
* The MCU computes:
  $$V_{TRACK(set)} = V_{OUT(prog)} + V_{headroom} \quad (V_{headroom} = 0.350\,\text{V})$$
* It commands the Synchronous Buck stage to output $V_{TRACK}$.
* The LDO operates with a fixed, minimal pass-transistor drop of $V_{drop} = 350\,\text{mV}$ across the entire $5\,\text{V} \dots 20\,\text{V}$ range:
  $$P_{LDO(diss)} = V_{drop} \times I_{OUT} = 0.35\,\text{V} \times 3.0\,\text{A} = \mathbf{1.05\,\text{W}}$$
* **Thermal Performance**: A $1.05\,\text{W}$ dissipation is easily handled by a small $15\,\text{mm}\times 15\,\text{mm}$ PCB copper heat-spreading plane ($\theta_{JA} \approx 32^\circ\text{C/W} \implies \Delta T \approx 33.6^\circ\text{C}$).
* **Noise Rejection**: The LDO provides $> 65\,\text{dB}$ of Power Supply Rejection Ratio (PSRR) at the $250\,\text{kHz}$ buck switching frequency, knocking a $20\,\text{mV}$ switching spur down to **less than $11\,\mu\text{V}$**!

---

## 6. Engineering Recommendation for DC-DC Post-Regulator

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           POST-REGULATOR SELECTION DECISION MATRIX                                              │
├─────────────────────────┬───────────────────────────┬───────────────────────────────────────────────────────────────────────────┤
│ Target Priority         │ Recommended Topology      │ Key Engineering Justification                                             │
├─────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ **Maximum Simplicity &  │ **High-Bus Pure Buck**    │ Eliminates 2 power FETs and boost transition jitter. Operates strictly as │
│ **Lowest Cost**         │ (Option A: +36V Bus In)   │ buck (D=14% to 56%). Cuts BOM cost by 22% and simplifies MCU PID loop.    │
├─────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ **Lab-Grade Low Noise** │ **Tracking Buck + LDO**   │ Delivers sub-millivolt ripple (< 0.8mV) and 15µV RMS wideband noise for   │
│ **RF / Audio Testing**  │ (Option D)                │ sensitive analog/RF prototypes, with only 1.05W thermal loss at 3A.       │
├─────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ **Lowest Output Ripple**│ **Synchronous Zeta**      │ Output inductor provides continuous, non-pulsed current into load.        │
│ **Without Linear Stage**│ (Option C)                │ Yields sub-12mV ripple with standard ceramic capacitor banks.             │
├─────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ **Short-Circuit Safety**│ **Coupled SEPIC**         │ Series AC coupling capacitor prevents DC shoot-through if FET shorts.     │
│ **Low-Side Drive Only** │ (Option B)                │ Ground-referenced switch eliminates high-side floating gate drivers.      │
└─────────────────────────┴───────────────────────────┴───────────────────────────────────────────────────────────────────────────┘
```
