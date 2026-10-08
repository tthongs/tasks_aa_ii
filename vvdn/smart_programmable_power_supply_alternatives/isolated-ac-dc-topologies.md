# Isolated AC-DC Primary Topologies: Active PFC + LLC, Two-Switch Forward & Direct Variable Flyback

Welcome to the **VVDN Engineering Hub Technical Dossier on Isolated AC-DC Primary Converter Topologies** for the Smart Programmable Power Supply. This document provides mathematical derivations, circuit schematics, magnetic calculations, and engineering trade-off evaluations for three primary alternatives to the baseline Quasi-Resonant (QR) Flyback converter:

1. **Active Boost PFC + Half-Bridge LLC Resonant Converter** (High efficiency, ZVS, low EMI, PF > 0.98).
2. **Two-Switch Forward Converter** (Clamped switch voltage stress, non-dissipative magnetic reset, high reliability).
3. **Direct Single-Stage Variable QR Flyback Converter** (Minimalist BOM, single transformer, 5V–20V direct secondary regulation).

---

## 1. Primary Stage Requirements & Comparison Overview

The primary isolated converter must convert universal grid AC ($85\,\text{V} \dots 265\,\text{V}$ AC RMS, $47\,\text{Hz} \dots 63\,\text{Hz}$) into a galvanically isolated DC rail delivering up to $72\,\text{W}$ continuous power ($60\,\text{W}$ output plus post-regulator conversion headroom and efficiency margin) with reinforced safety isolation ($\ge 3000\,\text{V}_{\text{RMS}}$ dielectric withstand).

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       ISOLATED AC-DC PRIMARY TOPOLOGIES: ARCHITECTURAL COMPARISON                                      │
├──────────────────────────────┬──────────────────────────────┬──────────────────────────────┬───────────────────────────────────────────┤
│ Parameter / Metric           │ Baseline: QR Flyback (24V)   │ Option 1: Active PFC + LLC   │ Option 2: Two-Switch Forward              │ Option 3: Direct Variable Flyback         │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┼───────────────────────────────────────────┤
│ **Intermediate DC Rail**     │ $+24.0\,\text{V}$ (Fixed)    │ $+36.0\,\text{V}$ (Fixed)    │ $+24.0\,\text{V}$ (Fixed)                 │ $5.0\,\text{V} \dots 20.0\,\text{V}$ (Var)│
│ **Input Power Factor (PF)**  │ $0.55 \dots 0.65$ (Passive)  │ $\mathbf{> 0.98}$ (Active PFC)│ $0.55 \dots 0.65$ (Passive)               │ $0.55 \dots 0.65$ (Passive)               │
│ **Peak Stage Efficiency**    │ $91.5\%$                     │ $\mathbf{94.2\%}$ (PFC + LLC)│ $90.8\%$                                  │ $88.5\%$                                  │
│ **Primary Switch Voltage**   │ $V_{bulk} + nV_o \approx 550V│ \mathbf{400\,\text{V}}$ Clamped│ $\mathbf{V_{bulk} \le 375\,\text{V}}$ Clamped│ $V_{bulk} + nV_o \approx 550V$            │
│ **Primary Switching Loss**   │ Low (Valley switching)       │ **Near Zero (Full ZVS)**     │ Medium (Hard-switched turn-off)           │ Low to Medium (Valley switching)          │
│ **Magnetic Elements**        │ 1 Coupled Inductor (PQ26/20) │ 1 PFC Choke + 1 LLC Xfmr     │ 1 Xfmr (ETD29) + 1 Output Filter Inductor │ 1 Coupled Inductor (PQ26/20)              │
│ **Output Filter Required**   │ Capacitive bank only         │ Capacitive bank only         │ **Inductor + Capacitor (LC filter)**      │ Capacitive bank only (Large required)     │
│ **Auxiliary Bias Stability** │ Rock solid (+16V constant)   │ Rock solid (+12V from PFC)   │ Rock solid (+15V constant)                │ **Severe 4:1 voltage swing issue!**       │
│ **Relative Hardware Cost**   │ $1.00\times$ (Reference)     │ $1.55\times$                 │ $1.20\times$                              │ **$0.70\times$ (Lowest primary cost)**    │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────┴───────────────────────────────────────────┘
```

---

## 2. Option 1: Active Boost PFC + Half-Bridge LLC Resonant Converter

For high-end laboratory instruments and industrial test benches where line power factor, harmonic distortion (IEC 61000-3-2), and high efficiency are non-negotiable, the **Active Boost PFC + Half-Bridge LLC Resonant Converter** is the premier architecture.

```text
====================================================================================================================================================
               OPTION 1 ARCHITECTURE: ACTIVE BOOST PFC (400V DC) + HALF-BRIDGE LLC RESONANT CONVERTER (+36V DC OUT)
====================================================================================================================================================

  85-265V AC In ──[ EMI Filter ]──[ Bridge ]──┬───[ PFC Inductor L_pfc: 350µH ]───┬───[ PFC Boost Diode (SiC 650V) ]───┬───> +V_BUS (400V Regulated)
                                              │                                   │                                    │
                                            ┌─┴─┐ C_in                            │  Drain (D)                       ┌─┴─┐ C_BULK
                                            │   │ 470nF/450V                      ├───┐                              │   │ 150µF/450V
                                            └─┬─┘                                 │  ┌┴───────────┐                  └─┬─┘ Nichicon 105°C
                                              │                                   │  │ Q_PFC      │                    │
                                             GND                                  └──┤ (600V SJ) │                   GND_PRI
                                                                                     └┬───────────┘
                                                                                      │ Source (S)
                                                                                     GND

  +V_BUS (400V DC) ───────────────────────────┬────────────────────────────────────────────────────────┐
                                              │ Drain (D)                                              │
                                           ┌──┴────────────┐                                           │
                              PFC_HO ──────┤ Q_HB1 (High)  │                                           │
                                           └──┬────────────┘                                           │
                                              │ Source (S)                                             │
                                              ├───────────── HB Switching Node ────────┐               │
                                              │ Drain (D)                              │               │
                                           ┌──┴────────────┐                           │               │
                              PFC_LO ──────┤ Q_HB2 (Low)   │                         ┌─┴─┐ C_r         │
                                           └──┬────────────┘                         │   │ Resonant Cap│
                                              │ Source (S)                           └─┬─┘ (22nF/630V) │
                                           GND_PRI                                     │               │
                                                                                       ├───[ L_r: 45µH ]
                                                                                       │    Resonant Inductor
                                                                                       │
                                                                             ┌─────────┴─────────┐
                                                                             │  Transformer      │
                                                                             │  (PQ32/20 Core)   │
                                                                             │  L_m = 225µH      │
                                                                             │  Np = 32 Turns    │
                                                                             └─────────┬─────────┘
  =============================================================================│=======================│============================================
                               REINFORCED SAFETY ISOLATION BARRIER (>= 6.4mm)  │                       │
  =============================================================================│=======================│============================================
                                                                             ┌─────────┴─────────┐     │
                                                                             │  Secondary 1 (6T) │     │
                                                                             └─────────┬─────────┘     │
                                                                                       │               │
                                                          Q_SR1 (BSC052N06NS) ───[ Drain ]             │
                                                                                       │               │
                                                                                       ├───────────────┴───┬───> +36.0V Intermediate Bus (72W)
                                                                                       │                   │
                                                          Q_SR2 (BSC052N06NS) ───[ Drain ]               ┌─┴─┐ C_OUT
                                                                                       │                 │   │ (4x 22µF MLCC + 220µF Polymer)
                                                                             ┌─────────┴─────────┐       └─┬─┘
                                                                             │  Secondary 2 (6T) │         │
                                                                             └─────────┬─────────┘      GND_SEC
                                                                                       │
  Secondary Center-Tap Return ─────────────────────────────────────────────────────────┴─────────────────────── GND_SEC
====================================================================================================================================================
```

### 2.1 Stage 1A: Continuous Conduction Mode (CCM) Boost PFC Design
* **PFC Controller**: TI UCC28180 or ON Semi NCP1654.
* **Output Voltage**: Regulated strictly to $V_{BUS} = 400.0\,\text{V}$ DC across all universal line inputs ($85\,\text{V} \dots 265\,\text{V}$ AC).
* **Inductor Sizing ($L_{PFC}$)**:
  Operating at switching frequency $f_{sw(PFC)} = 100\,\text{kHz}$, target ripple current ratio $\Delta I_{L} / I_{pk} = 30\%$:
  $$I_{in(rms,max)} = \frac{P_{in}}{\eta_{PFC} \cdot V_{AC(min)}} = \frac{80\,\text{W}}{0.95 \times 85\,\text{V}} = 0.99\,\text{A} \implies I_{pk} = \sqrt{2} \times 0.99\,\text{A} = 1.40\,\text{A}$$
  $$\Delta I_L = 0.30 \times 1.40\,\text{A} = 0.42\,\text{A}$$
  $$L_{PFC} = \frac{V_{AC(min)} \cdot \sqrt{2} \cdot \left(1 - \frac{V_{AC(min)} \cdot \sqrt{2}}{V_{BUS}}\right)}{\Delta I_L \cdot f_{sw(PFC)}} = \frac{120.2 \cdot \left(1 - \frac{120.2}{400}\right)}{0.42 \cdot 100000} = \frac{84.07}{42000} \approx \mathbf{350\,\mu\text{H}}$$
* **Boost Switch**: Infineon IPP60R180P7 ($600\,\text{V}$, $R_{DS(on)} = 0.18\,\Omega$, TO-220).
* **Boost Diode**: Wolfspeed C3D1P7060Q ($600\,\text{V}$, $1.7\,\text{A}$ Silicon Carbide Schottky, zero reverse recovery $Q_{rr} = 0$).

### 2.2 Stage 1B: Half-Bridge LLC Resonant Tank Design
The LLC converter operates with an inductor ratio of $k = \frac{L_m}{L_r} = 5.0$ and resonant frequency $f_0 = 100\,\text{kHz}$.
1. **Transformer Turns Ratio ($n$)**:
   The half-bridge applies a square wave of amplitude $V_{BUS} / 2 = 200\,\text{V}$ across the resonant tank:
   $$n = \frac{N_p}{N_s} = \frac{V_{BUS} / 2}{V_{OUT} + V_{SR}} = \frac{200\,\text{V}}{36.0\,\text{V} + 0.05\,\text{V}} = 5.54 \longrightarrow \mathbf{n = 5.33 \quad (N_p = 32\,\text{T}, N_s = 6\,\text{T})}$$
2. **Equivalent AC Load Resistance ($R_{ac}$)**:
   $$R_o = \frac{V_{OUT}}{I_{OUT}} = \frac{36.0\,\text{V}}{2.0\,\text{A}} = 18.0\,\Omega$$
   $$R_{ac} = \frac{8 \cdot n^2}{\pi^2} R_o = \frac{8 \times (5.33)^2}{9.8696} \times 18.0\,\Omega = 419\,\Omega$$
3. **Resonant Tank Components**:
   Target Quality Factor $Q = 0.45$:
   $$Z_0 = Q \cdot R_{ac} = 0.45 \times 419\,\Omega = 188.5\,\Omega$$
   $$C_r = \frac{1}{2\pi \cdot f_0 \cdot Z_0} = \frac{1}{2\pi \cdot 100000 \cdot 188.5} = 8.44\,\text{nF} \longrightarrow \mathbf{Selected: 10\,\text{nF} / 630\,\text{V Polypropylene}}$$
   $$L_r = \frac{Z_0}{2\pi \cdot f_0} = \frac{188.5}{2\pi \cdot 100000} \approx \mathbf{45.0\,\mu\text{H}}$$
   $$L_m = k \cdot L_r = 5.0 \times 45.0\,\mu\text{H} = \mathbf{225.0\,\mu\text{H}}$$

### 2.3 Why LLC Outperforms Flyback in High-Performance Equipment:
* **Zero-Voltage Switching (ZVS)**: Primary half-bridge MOSFETs turn on when the body diode is already conducting during the resonant dead time ($t_{dead} \approx 250\,\text{ns}$). Capacitive turn-on losses ($0.5 C_{oss} V_{ds}^2 f_{sw}$) are **completely zero**!
* **Zero-Current Switching (ZCS)** on Secondary: Synchronous rectifiers turn off at zero current, eliminating reverse recovery ringing and voltage spikes.
* **Low EMI**: Resonant sinusoidal current waveforms contain almost zero high-frequency harmonics, slashing EMI filter requirements.

---

## 3. Option 2: Two-Switch Forward Converter (+24 V Clamped Bus)

For rugged industrial environments requiring high reliability and clamped voltage stresses, the **Two-Switch Forward Converter** is a compelling alternative. Unlike a single-switch forward converter that requires a tertiary demagnetizing winding or high-voltage RCD reset clamp, the two-switch topology clamps primary switch voltages strictly to the DC bulk rail.

```text
====================================================================================================================================================
                        OPTION 2 ARCHITECTURE: TWO-SWITCH FORWARD CONVERTER (+24V DC ISOLATED BUS)
====================================================================================================================================================

  +V_BULK (120-375V DC) ──────────────┬────────────────────────────────────────────────────────┐
                                      │ Drain (D)                                              │ Cathode (K)
                                   ┌──┴─────────────┐                                        ┌─┴─┐ D_clamp2
                     GATE_HIGH ────┤ Q1 (Top Switch)│                                        │   │ (Ultrafast 600V)
                                   └──┬─────────────┘                                        └─┬─┘
                                      │ Source (S)                                             │ Anode (A)
                                      ├─────────────── Primary Dot Node (•)                    │
                                      │                     │                                  │
                                    ┌─┴─┐ D_clamp1          ├──[ Forward Transformer Np: 48T ]─┤
                                    │   │ (Ultrafast 600V)  │   (ETD29 Core, 3C90 Ferrite)     │
                                    └─┬─┘                   │                                  │
                                      │ Anode (A)           │                                  │
                                      │                     │ Drain (D)                        │
                                      │                  ┌──┴─────────────┐                    │
                                      │    GATE_LOW ─────┤ Q2 (Bottom Sw) │                    │
                                      │                  └──┬─────────────┘                    │
                                      │                     │ Source (S)                       │
                                   GND_PRI                  ├───[ R_sense: 0.15Ω ]─────────────┴─── GND_PRI
                                                            │
  ==========================================================│=======================================================================================
                               REINFORCED SAFETY ISOLATION BARRIER (>= 6.4mm)
  ==========================================================│=======================================================================================
                                                            │
                                  Secondary Dot Node (•) ───┤
                                  (Ns = 16 Turns)           │
                                                            ├───[ D_fwd: Schottky / Sync FET ]───┬───[ Output Inductor L_out: 47µH ]───┬───> +24V Out
                                                            │                                    │                                     │
                                                            │                                  ┌─┴─┐ D_free                            ┌─┴─┐ C_OUT
                                                            │                                  │   │ Freewheeling Diode                │   │ 220µF/35V
                                                            │                                  └─┬─┘ (Schottky / Sync FET)             └─┬─┘
  Secondary Non-Dot Return ─────────────────────────────────┴────────────────────────────────────┴───────────────────────────────────────┴─── GND_SEC
====================================================================================================================================================
```

### 3.1 Two-Switch Forward Mechanics & Voltage Stress
1. **Simultaneous Switching**: $Q_1$ and $Q_2$ are driven ON simultaneously by an isolated dual-gate driver (e.g. TI UCC27712).
2. **Power Transfer Interval**: When $Q_1$ and $Q_2$ are ON, energy transfers directly across the transformer into output inductor $L_{out}$ and the load:
   $$V_{sec} = V_{bulk} \times \left(\frac{N_s}{N_p}\right)$$
3. **Non-Dissipative Demagnetization Clamp**:
   When $Q_1$ and $Q_2$ turn OFF, the magnetizing current forces diodes $D_{clamp1}$ and $D_{clamp2}$ into forward conduction.
   * This connects the primary winding directly across $+V_{BULK}$ with reversed polarity!
   * The magnetizing energy is returned **100% loss-free back into the bulk capacitor**!
   * **Absolute Clamped Voltage Stress**:
     $$V_{DS1(max)} = V_{BULK(max)} = 375\,\text{V}$$
     $$V_{DS2(max)} = V_{BULK(max)} = 375\,\text{V}$$
   * Unlike the flyback converter where $V_{DS} = V_{bulk} + V_R + V_{spike} \approx 550\,\text{V}$, the switches **never see more than $375\,\text{V}$**! Standard, inexpensive $500\,\text{V}$ or $600\,\text{V}$ MOSFETs can be used with massive safety margins.

### 3.2 Duty Cycle Constraint ($D_{max} < 50\%$):
Because the demagnetization voltage equals the forward excitation voltage ($V_{reset} = V_{bulk}$), the demagnetization time equals the ON time ($t_{reset} = t_{on}$). Therefore:
$$D_{max} < 0.50 \quad (50\%)$$
Operating at $D_{max} = 0.45$ under $V_{bulk(min)} = 90\,\text{V}$:
$$n = \frac{N_p}{N_s} = \frac{V_{bulk(min)} \cdot D_{max}}{V_{OUT} + V_{diode}} = \frac{90\,\text{V} \times 0.45}{24.0\,\text{V} + 0.4\,\text{V}} = \frac{40.5}{24.4} = 1.66 \longrightarrow \mathbf{N_p = 48\,\text{T}, N_s = 29\,\text{T}}$$

### 3.3 Output Inductor Sizing ($L_{out}$):
Continuous conduction mode (CCM) inductor with $\Delta I_L = 0.30 \times 3.0\,\text{A} = 0.90\,\text{A}$ at $f_{sw} = 100\,\text{kHz}$:
$$L_{out} = \frac{(V_{sec(max)} - V_{OUT}) \cdot (1 - D)}{f_{sw} \cdot \Delta I_L} = \frac{(375 \cdot \frac{29}{48} - 24.0) \cdot (1 - 0.12)}{100000 \cdot 0.90} \approx \mathbf{47.0\,\mu\text{H}}$$

---

## 4. Option 3: Direct Single-Stage Variable QR Flyback Converter (5V–20V Direct Out)

The most enticing topology from a pure Bill-of-Materials (BOM) cost perspective is the **Direct Single-Stage Variable Flyback**, which eliminates the second DC-DC stage entirely. The flyback secondary directly regulates the programmable $5.0\,\text{V} \dots 20.0\,\text{V}$ output rail.

```text
====================================================================================================================================================
               OPTION 3 ARCHITECTURE: DIRECT VARIABLE QR FLYBACK CONVERTER (5.0V - 20.0V / 3A DIRECT OUTPUT)
====================================================================================================================================================

  +V_BULK (120-375V DC) ──────────────┬────────────────────────────────────────────────────────┐
                                      │                                                        │
                                    ┌─┴─┐ C_BULK                                               ├──[ Transformer Primary: Np = 48T ]──┐
                                    │   │ 120µF/450V                                           │   (PQ26/20 Core, Lp = 240µH)        │
                                    └─┬─┘                                                      │                                     │
                                      │                                                        ├──[ RCD Snubber Clamp ]              │
                                     GND_PRI                                                   │                                     │
                                                                                               │                                  Drain (D)
                                  [ TAPPED AUXILIARY WINDING ]                                 │                                ┌────┴─────┐
                                  Aux High (12T) ──[<| D_aux1 (BAV21) ]──┐                     │                                │    Q1    │ 800V SJ FET
                                                                         ├──────> VCC_PRI      │                GATE_DRV ───────┤          │ (IPB80R290P7)
                                  Aux Low (6T)  ──[<| D_aux2 (BAV21) ]───┤        (12V-18V     │                                └────┬─────┘
                                                                         │         Stable)     │                                     │ Source (S)
                                                                       ┌─┴─┐ C_vcc             │                                     ├──[ R_sense: 0.2Ω ]── GND_PRI
                                                                       │   │ 22µF/25V          │                                     │
  Auxiliary Ground Return ─────────────────────────────────────────────┴───┴───────────────────┴─────────────────────────────────────┴── GND_PRI

  ==================================================================================================================================================
                               REINFORCED SAFETY ISOLATION BARRIER (>= 6.4mm)
  ==================================================================================================================================================

  Secondary Winding (Ns = 12T) ───────┬────────────────────────────────────────────────────────┬───> +V_OUT (5.0V - 20.0V @ 3.0A Direct Out)
                                      │                                                        │
                                      │   ┌───────────────────────────┐                      ┌─┴─┐ C_OUT_BANK
                                      │   │ MP6908 Fast SR Controller │                      │   │ 3x 470µF / 25V Low ESR Electrolytic
                                      │   │ (Wide VDD: 4.2V - 35V)    │                      └─┬─┘ + 4x 22µF Ceramic MLCC
                                      │   └─┬───────────────────────┬─┘                        │
                                      │     │ Gate                  │ Drain                  GND_SEC
                                      │   ┌─┴─┐                   ┌─┴─┐
                                      │   │   │ Q_SR              │   │
                                      │   └───┴───────────────────┴───┘
                                      │         BSC052N06NS (60V, 5.2mΩ)
                                      │
  Secondary Ground Return ────────────┴──────────────────────────────────────────────────────────── GND_SEC
                                                                                               │
                                                                                             ┌─┴─┐ R_top
                                                                                             │   │ 20.0kΩ (0.1%)
                                                                                             └─┬─┘
                                                                                               │
                                                                                               ├─── TL431 REF Node
                                                                                               │    (2.495V Setpoint)
                                                                                             ┌─┴─┐
                                                                                       R_DAC │   │ 6.04kΩ (0.1%)
                                                                                             └─┬─┘
                                                                                               │
                                              Secondary MCU DAC Output (0.0V - 3.3V) ──────────┘
====================================================================================================================================================
```

### 4.1 The Fundamental Challenge: The 4:1 Auxiliary VCC Problem
In a flyback converter, the auxiliary winding voltage tracks the secondary output voltage proportionally to the turns ratio:
$$V_{aux} \approx (V_{OUT} + V_{SR}) \cdot \left(\frac{N_{aux}}{N_s}\right) - V_{diode}$$

If sized for $V_{OUT} = 20.0\,\text{V}$ such that $V_{aux} = 18.0\,\text{V}$ (safe below controller maximum rating $V_{CC(max)} = 28\,\text{V}$):
$$\frac{N_{aux}}{N_s} = \frac{18.0 + 0.7}{20.0 + 0.1} = \frac{18.7}{20.1} = 0.93$$
When the user commands the power supply to $V_{OUT} = 5.0\,\text{V}$:
$$V_{aux} = (5.0 + 0.1) \cdot 0.93 - 0.7 = 4.74 - 0.7 = \mathbf{4.04\,\text{V}!}$$
Because the UCC28740 UVLO turn-off threshold is $V_{UVLO(off)} = 8.1\,\text{V}$, the controller immediately triggers Under-Voltage Lockout and resets, causing continuous hiccup reboots!

#### Engineering Solution: Dual-Tapped Auxiliary Winding with Schottky Diode ORing
To resolve this, the transformer is wound with **two auxiliary winding taps**:
1. **Tap 1 ($N_{aux1} = 6\,\text{T}$)**: Powers the controller during high-voltage operation ($V_{OUT} = 15\,\text{V} \dots 20\,\text{V}$), generating $V_{aux1} \approx 9.5\,\text{V} \dots 12.5\,\text{V}$.
2. **Tap 2 ($N_{aux2} = 14\,\text{T}$)**: Powers the controller during low-voltage operation ($V_{OUT} = 5\,\text{V} \dots 10\,\text{V}$), generating $V_{aux2} \approx 11.2\,\text{V}$.
Two fast Schottky diodes (e.g. BAV21 or BAT46) automatically OR the two rails:
$$V_{CC} = \max(V_{aux1}, V_{aux2})$$
This guarantees that $V_{CC}$ remains strictly between $11.0\,\text{V}$ and $18.5\,\text{V}$ across the entire $5.0\,\text{V} \dots 20.0\,\text{V}$ dynamic output range!

### 4.2 Optocoupler Dynamic Range & Loop Stability
In a single-stage variable supply, the loop gain of the optocoupler feedback network varies by $> 15\,\text{dB}$ across the operating space:
* At $V_{OUT} = 20\,\text{V}$, feedback current into the optocoupler LED is high; optocoupler current transfer ratio (CTR) is near saturation.
* At $V_{OUT} = 5\,\text{V}$, available loop voltage is low, reducing phase margin.
* Bandwidth must be constrained to $< 1.5\,\text{kHz}$ to maintain stability across all loads, resulting in **sluggish load transient response ($> 6\,\text{ms}$) compared to $< 120\,\mu\text{s}$ for the two-stage Buck-Boost design**.

---

## 5. Summary & Recommendation for AC-DC Stage

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                             PRIMARY STAGE SELECTION DECISION MATRIX                                             │
├─────────────────────────┬───────────────────────────┬───────────────────────────────────────────────────────────────────────────┤
│ Target Application      │ Recommended Topology      │ Key Engineering Justification                                             │
├─────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ **Cost-Optimized OEM**  │ **Direct Variable Flyback**│ Eliminates DC-DC post-regulator stage completely. Saves $30%-$38% BOM cost.│
│                         │ (Option 3 with Dual Aux)  │ Requires dual-tapped auxiliary bias and large secondary capacitor bank.   │
├─────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ **General Bench / Lab** │ **Quasi-Resonant Flyback** │ Fixed +24V or +36V bus provides rock-solid aux VCC, simple transformer,   │
│ (Baseline & Option 1B)  │ (Baseline Design)         │ high efficiency (>91%), and isolates transient response to the 2nd stage. │
├─────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ **High-Power / Premium**│ **Active Boost PFC + LLC**│ Delivers PF > 0.98, complies with IEC 61000-3-2 Class D, achieves >94%    │
│ (Option 1)              │ (Option 1)                │ efficiency via zero-voltage switching (ZVS), and has near-zero EMI.       │
├─────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ **Rugged Industrial**   │ **Two-Switch Forward**    │ Clamps switch voltage stress to Vbulk (max 375V). Zero snubber dissipation│
│ (Option 2)              │ (Option 2)                │ provides maximum reliability under harsh mains line surge environments.  │
└─────────────────────────┴───────────────────────────┴───────────────────────────────────────────────────────────────────────────┘
```
