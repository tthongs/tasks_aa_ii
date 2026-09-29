# MOSFET (Metal-Oxide-Semiconductor Field-Effect Transistor): Comprehensive Engineering & Study Guide

Welcome to the **VVDN Engineering Hub MOSFET Knowledge Base**. This repository serves as an exhaustive, mathematically rigorous, and practical hardware engineering reference for studying, selecting, designing, and troubleshooting **MOSFETs** across small-signal, power switching, automotive, high-frequency RF, and nanoscale VLSI applications.

---

## 1. Executive Summary & Physics Foundations

A **MOSFET** (**Metal-Oxide-Semiconductor Field-Effect Transistor**) is a four-terminal (Drain, Source, Gate, Body/Substrate), voltage-controlled semiconductor device. Unlike current-controlled Bipolar Junction Transistors (BJTs) where a base current $I_B$ controls collector current $I_C$ ($I_C = \beta \cdot I_B$), a MOSFET controls drain-to-source current ($I_{DS}$) by modulating the electric field across an insulating dielectric gate oxide layer ($\text{SiO}_2$ or High-$\kappa$ dielectric):

```text
                             Gate Terminal (G)
                                    │
                               ┌────┴────┐ (Metal / Poly-Si Gate)
                               │  GATE   │
                         ┌─────┴─────────┴─────┐
                         │   Gate Oxide (SiO2)  │  <-- Dielectric Insulator (tox ~ 5-100nm)
     ┌───────────────────┴─────────────────────┴───────────────────┐
     │  Source (n+)                                    Drain (n+)  │
  ───┤  ┌────────┐       Induced Channel [e-]        ┌────────┐   ├───
 (S) │  │  n+    │  ...............................  │   n+   │   │  (D)
     └──┴────────┴───────────────────────────────────┴────────┴───┘
     │                                                             │
     │                      p-type Substrate (Body)                │
     │                                                             │
     └──────────────────────────────┬──────────────────────────────┘
                                    │
                             Body Terminal (B) (Usually shorted to Source)
```

### Core Semiconductor Working Mechanisms:
1. **Electrostatic Gate Accumulation, Depletion, and Inversion**:
   - Applying a voltage $V_{GS}$ establishes a perpendicular electric field across the gate insulator.
   - For an **N-channel enhancement device**, when $V_{GS} = 0\,\text{V}$, two back-to-back p-n junctions ($n^+-p$ and $p-n^+$) block current flow between Drain and Source ($I_{DS} \approx 0$).
   - As $V_{GS}$ increases positively, mobile holes ($h^+$) are repelled from the semiconductor surface beneath the gate, forming a **depletion region**.
   - When $V_{GS}$ exceeds the **Threshold Voltage ($V_{TH}$)**, the surface potential bends sufficiently such that minority electrons are attracted to the oxide interface, creating a conducting **inversion layer** (the $n$-channel) directly connecting the Source and Drain $n^+$ diffusions.
2. **Channel Modulation by $V_{DS}$ (Linear vs. Saturation)**:
   - For low $V_{DS}$, the channel behaves as an ohmic, resistive path whose conductance is modulated by the overdrive voltage $(V_{GS} - V_{TH})$.
   - As $V_{DS}$ increases, the potential difference across the gate oxide at the drain end drops to $(V_{GS} - V_{DS})$. When $V_{DS} \ge V_{GS} - V_{TH}$, the inversion layer thickness at the drain end collapses to zero—a phenomenon known as **channel pinch-off**.
   - Beyond pinch-off, the drain current saturates, entering the **constant-current (saturation)** regime.

---

## 2. Universal MOSFET Taxonomy & Classification Tree

MOSFETs are categorized along several fundamental engineering dimensions:

```text
                                  MOSFET Classification
                                            │
        ┌───────────────────────────────────┴───────────────────────────────────┐
        ▼                                                                       ▼
 Enhancement Mode (Normally OFF)                                  Depletion Mode (Normally ON)
 Channel formed only when |Vgs| > |Vth|                          Channel exists naturally at Vgs = 0V
   ├── N-Channel (NMOS: Vgs_th > 0)                                ├── N-Channel (Vgs_off < 0)
   └── P-Channel (PMOS: Vgs_th < 0)                                └── P-Channel (Vgs_off > 0)
        │                                                                       │
        └───────────────────────────────────┬───────────────────────────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
     Power Topologies                 Specialized Drive / RF         Advanced Multi-Gate
   ├── Trench-Gate (UMOS)          ├── Logic-Level MOSFETs         ├── FinFET (3D tri-gate)
   │   (Low Vds: 20V-100V)         │   (Vgs_th: 1V-2V, direct MCU) ├── GAAFET (Nanosheets, <=3nm)
   ├── VDMOS (Planar Power)        ├── LDMOS (Lateral Power RF)    └── FD-SOI (Fully Depleted)
   │   (Med Vds: 100V-600V)        │   (High fT, GHz base stations)
   ├── Superjunction (CoolMOS)     └── Dual-Gate MOSFET
   │   (High Vds: 500V-900V)           (Tetrode, AGC, RF Mixers)
   └── Wide-Bandgap (SiC)
       (Ultra Vds: 650V-3.3kV)
```

---

## 3. Directory Navigation & Study Modules

This repository is structured into dedicated, modular technical dossiers for every major MOSFET category:

| Directory | Core Focus | Voltage Range | Typical Application Domains |
| :--- | :--- | :--- | :--- |
| [**`n-channel-enhancement/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/n-channel-enhancement/README.md) | Standard e-NMOS, electron conduction, low-side switching, conduction losses | $20\,\text{V} \dots 600\,\text{V}+$ | Low-side switches, synchronous buck low-side, motor H-bridge |
| [**`p-channel-enhancement/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/p-channel-enhancement/README.md) | Standard e-PMOS, hole mobility, high-side switching, reverse battery protection | $20\,\text{V} \dots 200\,\text{V}$ | High-side power distribution, reverse polarity protection, CMOS |
| [**`depletion-mode/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/depletion-mode/README.md) | Normally-ON d-MOSFET, channel pinch-off, negative gate cutoff | $50\,\text{V} \dots 800\,\text{V}$ | SMPS high-voltage startup circuits, constant-current sources, fail-safe disconnects |
| [**`power-trench-mosfet/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/power-trench-mosfet/README.md) | Vertical trench gate, ultra-dense cell pitch, minimum $R_{DS(on)}$ | $20\,\text{V} \dots 100\,\text{V}$ | Automotive $12\,\text{V}/48\,\text{V}$ systems, BMS battery protection, PoL converters |
| [**`power-vdmos/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/power-vdmos/README.md) | Vertical double-diffused planar power, avalanche ruggedness ($E_{AS}$) | $100\,\text{V} \dots 600\,\text{V}$ | Inductive solenoid drivers, industrial relays, linear power amplifiers |
| [**`superjunction-mosfet/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/superjunction-mosfet/README.md) | Multi-epi charge balance, breaking the Silicon limit, CoolMOS physics | $500\,\text{V} \dots 900\,\text{V}$ | Offline AC-DC flyback/forward, PFC stages, server PSUs, EV Onboard Chargers |
| [**`sic-mosfet/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/sic-mosfet/README.md) | Wide-bandgap $3.26\,\text{eV}$ SiC, zero reverse recovery, extreme temp | $650\,\text{V} \dots 1700\,\text{V}+$ | EV main traction inverters, 800V DC fast chargers (EVSE), solar inverters |
| [**`logic-level-mosfet/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/logic-level-mosfet/README.md) | Thin oxide low-$V_{TH}$ ($1-2\,\text{V}$), direct $3.3\,\text{V}/5\,\text{V}$ MCU GPIO drive | $20\,\text{V} \dots 60\,\text{V}$ | Microcontroller peripherals, LED dimming, relay drives, direct logic gates |
| [**`ldmos-rf/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/ldmos-rf/README.md) | Lateral DMOS, high-frequency power, low $C_{rss}$, ground flange | $28\,\text{V} \dots 100\,\text{V}$ | 4G/5G cellular base stations, RF broadcast, radar transmitters, ISM generators |
| [**`finfet-and-gaafet/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/finfet-and-gaafet/README.md) | 3D multi-gate, FinFET, GAA nanosheets, FD-SOI, short-channel mitigation | $< 1.2\,\text{V}$ | Advanced VLSI processors, mobile SoCs, GPUs, AI tensor cores |
| [**`dual-gate-mosfet/`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/dual-gate-mosfet/README.md) | Integrated series cascode tetrode, two control gates, low Miller cap | $10\,\text{V} \dots 25\,\text{V}$ | RF mixers, low-noise VHF/UHF amplifiers, automatic gain control (AGC) |

---

## 4. Fundamental Mathematical Model & Operating Regions

For an N-Channel Enhancement MOSFET with channel width $W$, channel length $L$, oxide capacitance per unit area $C_{ox} = \frac{\varepsilon_{ox}}{t_{ox}}$, electron mobility $\mu_n$, and threshold voltage $V_{TH}$:

### Parameter Grouping:
$$\mu_n C_{ox} = k_n' \quad [\text{Process transconductance parameter, } \mu\text{A/V}^2]$$
$$K_n = \frac{1}{2} \mu_n C_{ox} \left(\frac{W}{L}\right) \quad [\text{Device conduction parameter}]$$

### 1. Cutoff Region:
$$V_{GS} < V_{TH}$$
$$I_D \approx 0 \quad (\text{Subthreshold leakage } I_{D,sub} \propto \exp\left(\frac{V_{GS} - V_{TH}}{n V_t}\right))$$

### 2. Linear (Triode / Ohmic) Region:
Condition: $V_{GS} > V_{TH}$ and $V_{DS} < V_{GS} - V_{TH}$ (or $V_{DS} < V_{DS(sat)}$):
$$I_D = \mu_n C_{ox} \left(\frac{W}{L}\right) \left[ (V_{GS} - V_{TH}) V_{DS} - \frac{1}{2} V_{DS}^2 \right]$$

For very small drain-to-source voltages ($V_{DS} \ll 2(V_{GS} - V_{TH})$), the quadratic term drops out, and the channel behaves as an ideal linear resistor ($R_{DS(on)}$):
$$R_{DS(on)} = \left( \frac{\partial I_D}{\partial V_{DS}} \right)^{-1} \approx \frac{1}{\mu_n C_{ox} \left(\frac{W}{L}\right) (V_{GS} - V_{TH})}$$

### 3. Saturation (Active) Region:
Condition: $V_{GS} > V_{TH}$ and $V_{DS} \ge V_{GS} - V_{TH}$:
$$I_D = \frac{1}{2} \mu_n C_{ox} \left(\frac{W}{L}\right) (V_{GS} - V_{TH})^2 (1 + \lambda V_{DS})$$
where $\lambda$ represents the **Channel Length Modulation parameter** (analogous to the Early voltage $V_A = 1/\lambda$ in BJTs).

Small-signal transconductance ($g_m$):
$$g_m = \left. \frac{\partial I_D}{\partial V_{GS}} \right|_{V_{DS}} = \mu_n C_{ox} \left(\frac{W}{L}\right) (V_{GS} - V_{TH}) = \sqrt{2 \mu_n C_{ox} \left(\frac{W}{L}\right) I_D} = \frac{2 I_D}{V_{GS} - V_{TH}}$$

---

## 5. Dynamic Switching Characteristics & Parasitics

In high-speed power electronics and converter design, steady-state DC resistance is only half the equation. The switching transient is governed by internal terminal parasitic capacitances and total gate charge:

```text
                          Drain (D)
                             │
                             ├──────────────┐
                             │              │
                           ┌─┴─┐          ┌─┴─┐
                      Cgd  │   │          │   │ Coss = Cds + Cgd
                     (Crss)│   │          │   │
                           └─┬─┘          └─┬─┘
                             │   Body     │
            Gate (G) ──┬─────┼── Diode ───┼
                       │     │    /│\     │
                     ┌─┴─┐   │   ──┼──    │
                Cgs  │   │   │     │      │
                     │   │   └───┬─┴──────┘
                     └─┬─┘       │
                       │         │
                       └─────────┴────────── Source (S)
                                 Ciss = Cgs + Cgd
```

### 1. Terminal Capacitance Relationships:
Datasheets report terminal capacitances measured at specific DC bias voltages (normally with $V_{GS} = 0\,\text{V}$):
- **Input Capacitance**: $C_{iss} = C_{gs} + C_{gd}$
- **Output Capacitance**: $C_{oss} = C_{ds} + C_{gd}$
- **Reverse Transfer (Miller) Capacitance**: $C_{rss} = C_{gd}$

### 2. The Gate Charge ($Q_g$) Curve & Miller Plateau:
When a gate driver supplies current to turn on a MOSFET, the gate voltage waveform exhibits distinct phases:

```text
  Vgs ^
      │                    Phase 3: Vgs rises to Vdrive
      │                    (Channel heavily enhanced, Rds_on reaches minimum)
      │               ┌─────────────────────── V_drive
      │      Phase 2: │ Miller Plateau (V_plateau)
      │      Vds falls│ [Vgs held constant while Cgd is discharged]
      │      ┌────────┘
      │     /
      │    / Phase 1: Charging Cgs from 0V up to Vth
      │   /  (Device in cutoff, Id = 0)
      └──┴────────────┴───────────────────────> Gate Charge (Qg) [nC]
         0           Qth       Qgs            Qgd           Qtotal
```
- **Phase 1 ($0 \rightarrow Q_{th}$)**: Gate driver charges $C_{gs}$. Gate voltage rises exponentially. No drain current flows until $V_{gs} = V_{TH}$.
- **Phase 2 ($Q_{gs} \rightarrow Q_{gd}$)**: The **Miller Plateau**. Drain current reaches maximum load current, and drain voltage $V_{DS}$ collapses from high bus voltage to near zero. All gate drive current is diverted to discharging the highly non-linear $C_{gd}$ capacitance. The gate voltage remains stuck at $V_{plateau} = V_{TH} + \frac{I_{LOAD}}{g_m}$.
- **Phase 3 ($Q_{gd} \rightarrow Q_{total}$)**: $V_{DS}$ has fallen to $I_D \cdot R_{DS(on)}$. The gate voltage rises up to the full gate driver output rail ($V_{drive}$), driving the channel into deep ohmic conduction to minimize $R_{DS(on)}$.

---

## 6. Power Loss Breakdown & Thermal Sizing

The total power dissipated by a MOSFET in a switching converter or power stage is given by:

$$P_{TOTAL} = P_{COND} + P_{SW} + P_{GATE} + P_{COSS} + P_{DIODE}$$

### 1. Conduction Loss ($P_{COND}$):
$$P_{COND} = I_{D,rms}^2 \times R_{DS(on)}(T_j)$$
*Caution*: $R_{DS(on)}$ has a strong positive temperature coefficient in Silicon (typically increasing by a factor of $1.5\times$ to $2.0\times$ between $+25^\circ\text{C}$ and $+150^\circ\text{C}$):
$$R_{DS(on)}(T_j) = R_{DS(on)}(25^\circ\text{C}) \times \left(1 + \frac{\alpha}{100}(T_j - 25^\circ\text{C})\right) \quad (\alpha \approx 0.4\% \dots 0.7\% / ^\circ\text{C})$$

### 2. Switching Losses ($P_{SW}$):
During each turn-on and turn-off transition, $V_{DS}$ and $I_D$ overlap, dissipating instantaneous energy:
$$P_{SW} = \frac{1}{2} V_{DS,bus} \cdot I_{D,load} \cdot (t_{rise} + t_{fall}) \cdot f_{sw}$$
where $t_{rise}$ and $t_{fall}$ are governed by the gate driver source/sink current capability and gate charge ($Q_{gs2} + Q_{gd}$).

### 3. Gate Drive Power Loss ($P_{GATE}$):
Power delivered by the gate driver supply rail to charge and discharge the input capacitance:
$$P_{GATE} = Q_g \times V_{GS,drive} \times f_{sw}$$
*(Note: Most of this loss is dissipated inside the gate resistor $R_G$ and gate driver output stage).*

### 4. Output Capacitive Stored Energy Loss ($P_{COSS}$):
During hard-switching turn-on, the energy stored in $C_{oss}$ is dissipated directly into the MOSFET channel:
$$P_{COSS} = \frac{1}{2} C_{oss(er)} \cdot V_{DS}^2 \cdot f_{sw} = f_{sw} \int_0^{V_{DS}} v \cdot C_{oss}(v) \, dv$$

### 5. Body Diode Conduction & Reverse Recovery Loss ($P_{DIODE}$):
In half-bridge and synchronous converters during dead-time:
$$P_{DIODE} = (V_{SD} \cdot I_{LOAD} \cdot t_{dead} \cdot f_{sw}) + (Q_{rr} \cdot V_{DS,bus} \cdot f_{sw})$$

### 6. Thermal Network Junction Temperature Calculation:
$$T_j = T_A + P_{TOTAL} \cdot (R_{\theta JC} + R_{\theta CS} + R_{\theta SA})$$
- $R_{\theta JC}$: Junction-to-case thermal resistance ($^\circ\text{C/W}$, from datasheet)
- $R_{\theta CS}$: Case-to-heatsink thermal interface resistance (thermal paste/sil-pad)
- $R_{\theta SA}$: Heatsink-to-ambient thermal resistance

---

## 7. Comparative Benchmark Matrix: Major MOSFET Types

| Parameter / Feature | N-Channel Enhancement | P-Channel Enhancement | Power Trench MOSFET | Superjunction (CoolMOS) | SiC Power MOSFET | Logic-Level MOSFET |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Charge Carrier** | Electrons ($\mu_n \approx 1400$) | Holes ($\mu_p \approx 450$) | Electrons | Electrons | Electrons | Electrons |
| **Relative Die Area for Same $R_{DS(on)}$** | $1.0\times$ (Baseline) | $2.5\times \dots 3.0\times$ | $0.4\times \dots 0.6\times$ | $0.2\times$ (High V) | $0.1\times$ (High V) | $1.1\times$ |
| **Nominal Voltage Spectrum** | $20\,\text{V} \dots 600\,\text{V}$ | $20\,\text{V} \dots 150\,\text{V}$ | $20\,\text{V} \dots 100\,\text{V}$ | $500\,\text{V} \dots 900\,\text{V}$ | $650\,\text{V} \dots 3300\,\text{V}$ | $20\,\text{V} \dots 60\,\text{V}$ |
| **Typical $V_{GS(th)}$** | $2.0\,\text{V} \dots 4.0\,\text{V}$ | $-2.0\,\text{V} \dots -4.0\,\text{V}$ | $1.5\,\text{V} \dots 3.0\,\text{V}$ | $3.0\,\text{V} \dots 4.5\,\text{V}$ | $2.0\,\text{V} \dots 3.5\,\text{V}$ | **$0.8\,\text{V} \dots 2.0\,\text{V}$** |
| **Recommended Gate Drive Voltage** | $+10\,\text{V} \dots +12\,\text{V}$ | $-10\,\text{V} \dots -12\,\text{V}$ | $+10\,\text{V}$ | $+10\,\text{V} \dots +12\,\text{V}$ | **$+18\,\text{V} / -4\,\text{V}$** | **$+3.3\,\text{V} \dots +5.0\,\text{V}$** |
| **Reverse Recovery Charge ($Q_{rr}$)** | High | Moderate | Moderate to High | High (Low in CFD) | **Virtually Zero** | Low to Moderate |
| **Temperature Capability ($T_{j,max}$)** | $150^\circ\text{C} \dots 175^\circ\text{C}$ | $150^\circ\text{C}$ | $175^\circ\text{C}$ | $150^\circ\text{C}$ | **$175^\circ\text{C} \dots 200^\circ\text{C}$** | $150^\circ\text{C}$ |
| **Switching Speed ($dv/dt$)** | Moderate ($10-30\,\text{V/ns}$) | Moderate | Fast | Extremely Fast ($>50\,\text{V/ns}$) | Ultra-Fast ($>100\,\text{V/ns}$) | Moderate |
| **Key Circuit Topologies** | Low-side, H-bridge | High-side disconnect | PoL Buck, BMS | PFC, LLC, Flyback | EV Inverter, OBC, EVSE | Direct MCU switching |

---

## 8. CLI Engineering Tool: `mosfet_calc.py`

To assist hardware designers in calculating switching and conduction budgets, sizing gate resistors, and verifying junction thermal margins, the repository includes a dedicated CLI calculation utility located at [**`tools/mosfet_calc.py`**](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/mosfet_calc.py).

### Quick Usage Examples:
```bash
# Calculate power dissipation, switching losses, and thermal junction temperature:
python3 tools/mosfet_calc.py --loss --vds 48 --id 15 --rdson 0.005 --trise 25e-9 --tfall 20e-9 --fsw 150e3 --vgs 10 --qg 35e-9 --theta-ja 35 --ta 50

# Size gate resistor for peak driver current and target switching speed:
python3 tools/mosfet_calc.py --gate --vdrv 12 --vplat 4.2 --qgd 12e-9 --target-dt 30e-9 --idriver-max 2.0

# Evaluate body diode conduction and reverse recovery losses:
python3 tools/mosfet_calc.py --diode --vds 400 --iload 20 --vsd 1.2 --tdead 100e-9 --qrr 450e-9 --fsw 100e3
```
