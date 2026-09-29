# Active Power Factor Correction (PFC) Rectifiers: Boost, Totem-Pole GaN & Vienna

Welcome to the **VVDN Engineering Hub Technical Dossier on Active Power Factor Correction (PFC) Rectifiers**. To comply with international grid harmonic regulations (**IEC 61000-3-2 Class D** and **IEEE 519**), every offline power supply exceeding $75\,\text{W}$—from server power supplies and laptop adapters to EV on-board chargers and telecom rectifiers—must incorporate Active PFC.

This guide provides an exhaustive hardware engineering analysis of the classic **Active Boost PFC Pre-regulator**, the ultra-high-efficiency **Bridgeless Totem-Pole GaN PFC**, and the multi-megawatt **Three-Phase Three-Level Vienna Rectifier**.

---

## 1. Why Active PFC? Regulatory Mandates & Power Quality

A passive diode rectifier draws narrow current spikes, resulting in poor power factor ($\text{PF} \approx 0.60$) and massive harmonic injection ($\text{THD}_i > 80\%$). 

```text
               Passive Diode Current vs. Active PFC Current Waveforms
   PASSIVE RECTIFIER:                           ACTIVE PFC RECTIFIER:
   v_in, i_in ^                                 v_in, i_in ^
              │     Pulsed Current Spikes                  │    Input Current i_in is pure SINUSOID
              │        |             |                     │    in PERFECT PHASE with Voltage v_in!
              │       / \           / \                    │        /\            /\
              │  .---'   '---. .---'   '---.               │  .---./  \.-.   .---./  \.-.
              │ /  Voltage    \           /                │ /    /    \  \ /    /    \  \
           0V ┼/───────────────\─────────/──> Time      0V ┼/────/──────\──\────/──────\──\──> Time
              │ PF = 0.60, THDi = 110%                     │ PF = 0.998, THDi = 2.5%
              │ (FAILS IEC 61000-3-2)                      │ (COMPLIES WITH IEC 61000-3-2 CLASS D)
```

### True Power Factor Decomposition:
$$\text{PF} = \frac{\text{Real Power } (P)}{\text{Apparent Power } (S)} = \frac{1}{\sqrt{1 + \text{THD}_i^2}} \cdot \cos \phi_1$$
To achieve $\text{PF} \approx 1.0$, the power supply must concurrently:
1. Drive phase displacement angle to zero ($\cos \phi_1 \rightarrow 1.0$).
2. Force harmonic distortion to near zero ($\text{THD}_i \rightarrow 0 \implies \frac{1}{\sqrt{1 + \text{THD}_i^2}} \rightarrow 1.0$).

---

## 2. Classic Active Boost PFC Topology & Dual-Loop Control

The standard **Active Boost PFC** cascades a full-wave diode bridge with a high-frequency step-up boost converter:

```text
                        Single-Phase Active Boost PFC Converter
                                    L_pfc (Boost Inductor)     D_pfc (SiC Schottky)
   AC Line ───┬───[ Bridge Rect ]─────^^^^^^^^────────┬──────────────[>|]─────────┬───> +Vdc (400V)
              │   (D1 - D4)                           │                           │
              │                                   Drain (D)                      ┌┴┐
              │                                   ┌───┴───┐ Q1 (MOSFET / GaN)    │ │ C_bulk
              │                                   │  SW   │                      └┬┘ (Hold-up)
              │                                   └───┬───┘                       │
              │                                       │ Source (S)                │
   AC Neut ───┴───[             ]─────────────────────┴───────[ R_shunt ]─────────┴───> -Vdc (GND)
                                                              (Current Sense)
```

### 2.1 The Boost Requirement ($V_{dc} = 400\,\text{V}$):
Because a Boost converter can only step *up* voltage ($V_{out} > V_{in}$), the regulated DC bus must exceed the peak of the highest AC input line voltage:
- Universal AC Mains: $85\,\text{V} \dots 265\,\text{V}_{rms}$
- Maximum Peak AC Line: $V_{pk,max} = \sqrt{2} \cdot 265\,\text{V} \approx 375\,\text{V}$
- Standard Industry DC Bus: **$V_{dc} = 390\,\text{V} \dots 400\,\text{V}$ DC**.

---

### 2.2 Dual-Loop Average Current-Mode Control:

```text
                     Dual-Loop Average Current-Mode Controller
                                      400V DC Bus
                                           │
                                     [ Voltage Divider ]
                                           │
                                           v  V_fb
      V_ref (2.5V) ──────>( - )            │
                           [ Error Amp 1 ]<┘
                           (Voltage Loop)
                                 │
                                 v  V_comp (Slow Outer Loop: ~10 Hz Bandwidth)
   |v_in(t)|                     │
   (Rectified Sine) ────────────( X ) MULTIPLIER
                                 │
                                 v  i_ref(t) = k * V_comp * |v_in(t)| (Reference Current)
                                 │
                                 v
                          ┌─────( - )
                          │ [ Error Amp 2 ] (Inner Fast Current Loop: ~15 kHz)
                          │      │
                          │      v
                          │   [ PWM Modulator ] ───> Gate Q1 (100 kHz)
                          │      ^
                          │      │
   Inductor Current i_L ──┴──────┘
```

1. **Slow Outer Voltage Loop ($\sim 10 \dots 20\,\text{Hz}$)**:
   - Compares the $400\,\text{V}$ DC bus with a reference to maintain voltage regulation.
   - **Crucial Engineering Rule**: The loop bandwidth must be strictly below $20\,\text{Hz}$ to avoid tracking the $100\,\text{Hz} / 120\,\text{Hz}$ rectified AC line ripple. If the voltage loop were fast, it would distort the input current reference!
2. **Fast Inner Current Loop ($\sim 10 \dots 20\,\text{kHz}$)**:
   - Multiplies the voltage error signal $V_{comp}$ by the instantaneous rectified AC line waveform $|v_{in}(t)|$ to construct an instantaneous reference current $i_{ref}(t)$.
   - Modulates the switch duty cycle cycle-by-cycle to force the inductor current $i_L(t)$ to perfectly match $i_{ref}(t)$.

---

## 3. Advanced Bridgeless Totem-Pole GaN PFC

Conventional Boost PFC suffers conduction losses from the diode bridge ($2 \times V_F \approx 2 \times 0.8\,\text{V} = 1.6\,\text{V}$ drop $\implies 16\,\text{W}$ lost at $10\,\text{A}$). The **Bridgeless Totem-Pole PFC** eliminates the diode bridge entirely:

```text
                     Bridgeless Totem-Pole PFC Power Stage
                      L_pfc
   AC Line ───────────^^^^^^──────┬───────────────────────────────┐
                                  │                               │
                              Drain (D)                       Drain (D)
                              ┌───┴───┐ Q1 (GaN HEMT)         ┌───┴───┐ S1 (Si Superjunction)
                              │  HS   │ High-Frequency        │  LS   │ Low-Frequency
                              └───┬───┘ (100kHz - 1MHz)       └───┬───┘ Line Synchronous
                                  │ Source                        │ Source (50Hz)
                                  ├── Midpoint HF ──┐             ├── Midpoint LF ──┐
                                  │                 │             │                 │
                              Drain (D)             │         Drain (D)             │
                              ┌───┴───┐ Q2 (GaN HEMT)│         ┌───┴───┐ S2 (Si Superjunction)
                              │  LS   │ High-Frequency│        │  LS   │ Low-Frequency
                              └───┬───┘ (100kHz - 1MHz)│       └───┬───┘ Line Synchronous
                                  │ Source          │             │ Source (50Hz)   │
   GND_DC ────────────────────────┴─────────────────┼─────────────┴─────────────────┼─── GND_DC
                                                    │                               │
   AC Neutral ──────────────────────────────────────┼───────────────────────────────┘
                                                    │
                                                   ┌┴┐ C_bulk (400V DC)
                                                   │ │
                                                   └┬┘
```

### 3.1 Why Silicon MOSFETs Fail in Totem-Pole (The GaN Revolution):
- In the totem-pole configuration, the high-frequency switches operate in continuous conduction mode (CCM) half-bridge hard switching.
- Standard silicon MOSFETs possess massive body-diode reverse recovery charge ($Q_{rr} \approx 500 \dots 2000\,\text{nC}$). When the opposite switch turns ON, this $Q_{rr}$ causes destructive shoot-through spikes and extreme switching losses.
- **Gallium Nitride (GaN) HEMTs have ZERO reverse recovery ($Q_{rr} = 0\,\text{nC}$)**.
- GaN enables the Totem-Pole topology to operate in CCM at $> 100\,\text{kHz}$, achieving unprecedented **$99.2\%$ conversion efficiency**!

---

## 4. Three-Phase Three-Level Vienna Rectifier

For high-power EV DC fast charging stations ($50\,\text{kW} \dots 350\,\text{kW}$) and megawatt data centers, the **Vienna Rectifier** is the premier unidirectional active PFC topology:

```text
                     Three-Phase Three-Level Vienna Rectifier
                   L1
   Phase A ───────^^^^^──┬───[>|]─┬───[>|]─────────────────────────────┬───> +400V (Vdc/2)
                         │   D1   │   D2                               │
                         ├──[~]───┤                                   ┌┴┐
                         │   Q1   │ Bidirectional                     │ │ C1
                         │ (MOS)  │ Midpoint Switch                   └┬┘
                         │        │                                    ├─── Neutral (0V)
                         ├──[|<]──┴───[|<]─────────────────────────┐   │
                         │   D3       D4                           │  ┌┴┐
                         │                                         │  │ │ C2
                         └──────── Neutral Midpoint (0V) ──────────┼──└┬┘
                                                                   │   │
                                                                   └───┴───> -400V (-Vdc/2)
                                                                       Total Vdc = 800V
```

### Key Engineering Advantages:
1. **Three-Level Voltage Synthesis**: Node voltages switch between $+\frac{V_{dc}}{2}, 0\,\text{V},$ and $-\frac{V_{dc}}{2}$.
2. **Halved Switch Voltage Stress**: Each MOSFET switch $Q_1$ experiences only half the total DC-link voltage ($400\,\text{V}$ stress on an $800\,\text{V}$ EV bus!), allowing the use of low-cost, ultra-fast $650\,\text{V}$ Superjunction or GaN FETs instead of expensive $1200\,\text{V}$ SiC modules.
3. **Pristine Grid Quality**: Inherent 3-level PWM cuts inductor ripple in half, achieving $\text{THD}_i < 2.0\%$ and $\text{PF} > 0.998$.

---

## 5. Component Sizing & Bulk Capacitor Hold-Up Time

### 5.1 Inductor Sizing ($L_{pfc}$):
Worst-case ripple occurs at the peak of the minimum AC line voltage:
$$L_{pfc} \ge \frac{V_{in,pk,min} \cdot \left( 1 - \frac{V_{in,pk,min}}{V_{dc}} \right)}{f_s \cdot \Delta I_L}$$
Where $V_{in,pk,min} = \sqrt{2} \cdot 85\,\text{V} \approx 120\,\text{V}$, $V_{dc} = 400\,\text{V}$, and $\Delta I_L = 20\% \cdot I_{pk,max}$.

### 5.2 Bulk Capacitor Sizing for Hold-Up Time ($t_{hold}$):
Server and telecom specifications (e.g., Intel ATX / Open Compute) mandate that the DC bus must sustain full output power during a complete AC line dropout of $1 \dots 2$ missing AC cycles ($t_{hold} = 16.67\,\text{ms} \dots 20\,\text{ms}$) without $V_{dc}$ falling below the downstream DC-DC converter's minimum drop-out threshold ($V_{dc,min} \approx 300\,\text{V}$):

$$\Delta E = P_{out} \cdot t_{hold} = \frac{1}{2} C_{bulk} \left( V_{dc,nom}^2 - V_{dc,min}^2 \right)$$
$$C_{bulk} \ge \frac{2 \cdot P_{out} \cdot t_{hold}}{\eta \cdot \left( V_{dc,nom}^2 - V_{dc,min}^2 \right)}$$

#### Practical Sizing Example ($1000\,\text{W}$ Server PSU):
- $P_{out} = 1000\,\text{W}$, $\eta = 0.95$
- $V_{dc,nom} = 400\,\text{V}$, $V_{dc,min} = 300\,\text{V}$
- $t_{hold} = 20\,\text{ms}$ ($0.020\,\text{s}$)
$$C_{bulk} \ge \frac{2 \cdot 1000 \cdot 0.020}{0.95 \cdot (400^2 - 300^2)} = \frac{40}{0.95 \cdot (160000 - 90000)} = \frac{40}{66500} \approx 601\,\mu\text{F}$$
*Design Recommendation*: Specify two $330\,\mu\text{F} / 450\,\text{V}$ ($660\,\mu\text{F}$ total) high-temperature $105^\circ\text{C}$ aluminum electrolytic capacitors in parallel.
