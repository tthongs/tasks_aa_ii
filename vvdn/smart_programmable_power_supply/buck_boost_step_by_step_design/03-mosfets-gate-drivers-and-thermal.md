# Dossier 3: MOSFET Selection, Gate Drivers & Thermal Analysis

Welcome to **Dossier 3** of the Step-by-Step 4-Switch Synchronous Buck-Boost Post-Regulator Design Guide. This document provides mathematical loss modeling, junction temperature derivations, gate driver requirements, and bootstrap network sizing for the four power MOSFETs ($Q_A, Q_B, Q_C, Q_D$).

---

## Step 6: Power MOSFET Selection & Losses

The 4-switch Buck-Boost converter uses four N-channel power MOSFETs. Selection requires optimizing the trade-off between on-state resistance ($R_{DS(on)}$) to minimize conduction losses, and total gate charge ($Q_g$) / gate-to-drain charge ($Q_{gd}$) to minimize high-frequency switching losses at $250\,\text{kHz}$.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 POWER MOSFET SELECTION BENCHMARK                                 │
├────────────────────┬────────────────────┬───────────┬─────────────┬─────────────┬────────────────┤
│ Switch Identifier  │ Selected Part      │ $V_{DS}$  │ $R_{DS(on)}$│ $Q_g$ (Typ) │ Package        │
├────────────────────┼────────────────────┼───────────┼─────────────┼─────────────┼────────────────┤
│ **Q_A (Buck HS)**  │ Infineon BSC034N04 │ 40 V      │ 3.4 mΩ      │ 16 nC       │ SuperSO8 / TDSON│
│ **Q_B (Buck LS)**  │ Infineon BSC034N04 │ 40 V      │ 3.4 mΩ      │ 16 nC       │ SuperSO8 / TDSON│
│ **Q_C (Boost LS)** │ Infineon BSC034N04 │ 40 V      │ 3.4 mΩ      │ 16 nC       │ SuperSO8 / TDSON│
│ **Q_D (Boost HS)** │ Infineon BSC034N04 │ 40 V      │ 3.4 mΩ      │ 16 nC       │ SuperSO8 / TDSON│
└────────────────────┴────────────────────┴───────────┴─────────────┴─────────────┴────────────────┘
```

### 6.1 Breakdown of MOSFET Loss Mechanisms ($P_{loss}$):
Total dissipation per switch is the sum of five distinct loss components:
$$P_{total} = P_{cond} + P_{sw} + P_{coss} + P_{body} + P_{gate}$$

#### 1. Conduction Loss ($P_{cond}$):
Accounting for on-resistance thermal degradation at elevated junction temperatures ($T_j \approx 100^\circ\text{C}$, temperature coefficient factor $\approx 1.4$):
$$R_{DS(on),100^\circ C} = 3.4\,\text{m}\Omega \times 1.4 = \mathbf{4.76\,\text{m}\Omega}$$
* In Buck mode ($D \approx 50\%$, $I_{OUT} = 3.0\,\text{A}$):
  $$I_{Q_A(rms)} = I_{OUT} \sqrt{D} = 3.0 \times \sqrt{0.50} = 2.12\,\text{A}_{\text{RMS}}$$
  $$P_{cond(QA)} = (2.12\,\text{A})^2 \times 0.00476\,\Omega = \mathbf{0.021\,\text{W}}$$
* In Boost High-Side Sync ($Q_D$, permanently ON in Buck mode):
  $$P_{cond(QD)} = (3.0\,\text{A})^2 \times 0.00476\,\Omega = \mathbf{0.043\,\text{W}}$$

#### 2. Switching Loss ($P_{sw}$):
Switching losses occur during the overlapping voltage and current transition intervals:
$$t_{sw} = t_r + t_f \approx 8.0\,\text{ns} + 6.0\,\text{ns} = 14.0\,\text{ns}$$
$$P_{sw(QA)} = \frac{1}{2} \cdot V_{DS} \cdot I_D \cdot t_{sw} \cdot f_{sw} = \frac{1}{2} \times 24.0\,\text{V} \times 3.0\,\text{A} \times (14 \times 10^{-9}\,\text{s}) \times 250000\,\text{Hz} = \mathbf{0.126\,\text{W}}$$

#### 3. Output Capacitance Dump Loss ($P_{coss}$):
Energy stored in the MOSFET output capacitance ($C_{oss} = 650\,\text{pF}$) dissipated on each turn-on transition:
$$P_{coss} = \frac{1}{2} C_{oss} \cdot V_{DS}^2 \cdot f_{sw} = \frac{1}{2} \times (650 \times 10^{-12}) \times (24)^2 \times 250000 = \mathbf{0.047\,\text{W}}$$

#### 4. Body Diode Conduction Loss during Dead-Time ($P_{body}$):
During the adaptive dead-time ($t_{dead} = 25\,\text{ns}$) between high-side and low-side switching, the low-side body diode conducts load current with forward drop $V_F \approx 0.75\,\text{V}$:
$$P_{body} = 2 \cdot V_F \cdot I_{OUT} \cdot t_{dead} \cdot f_{sw} = 2 \times 0.75\,\text{V} \times 3.0\,\text{A} \times (25 \times 10^{-9}) \times 250000 = \mathbf{0.028\,\text{W}}$$

#### 5. Gate Drive Dissipation ($P_{gate}$):
$$P_{gate} = Q_g \cdot V_{drv} \cdot f_{sw} = (16 \times 10^{-9}\,\text{C}) \times 5.0\,\text{V} \times 250000\,\text{Hz} = \mathbf{0.020\,\text{W}}$$

#### Total Dissipation per Active Switch:
$$P_{total(QA)} = 0.021 + 0.126 + 0.047 + 0.028 + 0.020 = \mathbf{0.242\,\text{W}}$$
Across all four switches under full load ($20\,\text{V} / 3\,\text{A}$), total MOSFET thermal loss is **$< 1.10\,\text{W}$**!

### 6.2 Thermal Modeling & Junction Temperature Rise:
The SuperSO8 (PG-TDSON-8) package features an exposed thermal pad soldered directly to the PCB top copper polygon.
* **Thermal Resistance ($\theta_{JA}$)**: With a $200\,\text{mm}^2$ area of $2\,\text{oz}$ copper on Layer 1 and 6 thermal vias to Layer 2 ground plane, effective thermal resistance is:
  $$\theta_{JA} = 35.0^\circ\text{C/W}$$
* **Junction Temperature Rise ($\Delta T$)**:
  $$\Delta T = P_{total} \times \theta_{JA} = 0.242\,\text{W} \times 35^\circ\text{C/W} = \mathbf{8.47^\circ\text{C}}$$
* **Worst-Case Junction Temperature ($T_j$)**:
  At maximum specified ambient temperature $T_{amb} = 60^\circ\text{C}$:
  $$T_j = 60^\circ\text{C} + 8.47^\circ\text{C} = \mathbf{68.5^\circ\text{C}}$$
  This operates with a massive safety margin below the silicon maximum rated limit of $150^\circ\text{C}$!

---

## Step 7: Gate Driver & Bootstrap Circuit Design

Both $Q_A$ (Buck High-Side) and $Q_D$ (Boost High-Side) require floating N-channel gate drives referenced to switching nodes `SW1` and `SW2` respectively:

```text
                           BOOTSTRAP GATE DRIVE NETWORK (BUCK HIGH-SIDE Q_A)
              +5V VCC Bias Rail
                     │
                   ┌─┴─┐ D_boot1
                   │   │ Schottky Diode (PMEG6010: 60V, 1A)
                   └─┬─┘
                     │
                     ├─── To LM5176 BOOT1 Pin
                     │
                   ┌─┴─┐ C_boot1
                   │   │ 0.22µF / 50V X7R Ceramic
                   └─┬─┘
                     │
                     ├─── To LM5176 SW1 Pin ────────────────┐
                     │                                      │
                     │                 Drain (D)            │
                     │               ┌─────┴─────┐          │
                     │  GATE_HO1 ────┤    Q_A    │          │
                     │  (via 2.2Ω)   │ BSC034N04 │          │
                     │               └─────┬─────┘          │
                     │                     │ Source (S)     │
                     └─────────────────────┴────────────────┴─── SW1 Node (To Inductor L)
```

### 7.1 Bootstrap Capacitor Sizing ($C_{boot}$):
The bootstrap capacitor must supply gate charge $Q_g$ without suffering a voltage sag greater than $\Delta V_{boot} \le 100\,\text{mV}$:
$$C_{boot} \ge \frac{Q_g + (I_{leak} \cdot t_{on,max})}{\Delta V_{boot}}$$
$$C_{boot} \ge \frac{16\,\text{nC} + (10\,\mu\text{A} \times 3.0\,\mu\text{s})}{0.10\,\text{V}} = \frac{16\,\text{nC} + 0.03\,\text{nC}}{0.10\,\text{V}} = 0.16\,\mu\text{F}$$
* **Selected Component**: **$0.22\,\mu\text{F} / 50\,\text{V}$ X7R $0805$ Ceramic Capacitor** (Murata GRM21BR71H224KA01L). Provides $> 35\%$ margin against voltage droop.

### 7.2 Bootstrap Diode Selection ($D_{boot1}, D_{boot2}$):
* **Component**: **Nexperia PMEG6010CEH** ($60\,\text{V}$, $1.0\,\text{A}$ planar Schottky).
* Fast recovery ($t_{rr} \approx 0$) prevents reverse charge loss back into the $+5\,\text{V}$ internal bias rail when `SW1` swings up to $+24\,\text{V}$.

### 7.3 Gate Resistor Dampening ($R_g$):
A small $2.2\,\Omega$ $0603$ resistor in series with each gate lead damps high-frequency LC oscillations formed by the gate trace parasitic inductance ($L_{trace} \approx 5\,\text{nH}$) and MOSFET input capacitance ($C_{iss} = 2200\,\text{pF}$), preventing gate oxide puncture and false turn-on without sluggish switching delays.
