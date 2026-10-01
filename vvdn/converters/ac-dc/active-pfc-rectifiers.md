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
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: CONTINUOUS CONDUCTION MODE (CCM) ACTIVE BOOST PFC (85V-265V AC -> 400V DC, 600W)
========================================================================================================================

    AC LINE (85-265V) ──[ F1: 8A Time-Lag ]──[ NTC: 5Ω/8A ]──┬──[ EMI FILTER ]──[ BRIDGE RECTIFIER ]──┬─────────────────┐
                                              (Relay K1 Bypass)│  (CX1, CMC1, CY1) (GBU808: 800V/8A)   │                 │
    AC NEUTRAL ────────────────────────────────────────────────┴──────────────────────────────────────┼─┐               │
                                                                                                      │ │               │
                                    +-----------------[ D_inrush: 10A / 600V Standard ]---------------+ │               │
                                    |                 (Direct Startup Inrush Bypass Path)               │               │
                                    |                                                                   │               │
                                    |                                                                   │               │
                                    |                                     PFC BOOST INDUCTOR            │               │
                                    |                                 +---[ L_pfc: 450µH / 8A ]---------+               │
                                    |                                 |   Sendust CS33125 Toroid        │               │
                                    |                                 |   (DCR = 45mΩ, Isat = 11A)     ┌┴┐ C_in_HF      │
                                    |                                 +----------------+               │ │ 1.0µF / 450V │
                                    |                                                  │               └┬┘ Poly Film    │
                                    |                                                  +=== NODE SW     │ (Absorbs HF)  │
                                    |                                                  |    (0V to 400V)│               │
                                    |                                                  |                │               │
                                    |                               Drain (D)          ├──[ R_snub ]    │               │
                                    |                              ┌────┴──────────┐   │    2.2Ω / 2W   │               │
                                    |                              │ Q1: N-MOSFET  │   │   [ C_snub ]   │               │
                                    |                              │ IPW60R045CP   │   │    470pF/630V  │               │
                                    |                       +----->│ (650V, 45mΩ)  │   │     GND_PWR    │               │
                                    |                       | Gate └────┬──────────┘   │                │               │
                                    |                       |      Source│             │                │               │
                                    |   GATE DRIVER IC      |           │              │                │               │
                                    |   UCC27517 (Low-Side) |           +--------------+                │               │
                                    |   OUT ----[ R_g: 4.7Ω ]+          │                               │               │
                                    |                                  ┌┴┐ R_shunt: 20mΩ / 3W 1%        │               │
                                    |                                  │ │ (Low-Side Inductor Sense)    │               │
                                    |                                  └┬┘                              │               │
                                    |                                   │                               │               │
                                    |                                GND_PWR ───────────────────────────┴───────────────┘
                                    |                                   │
                                    |      BOOST PFC RECTIFIER DIODE    │
                                    |      +---[ D_pfc: SiC Schottky ]--+
                                    |      |   Wolfspeed C3D06060A
                                    |      |   (600V, 6A, Qrr = 0)
                                    |      +---[ Anode  ->|  Cath ]-----+
                                    |                                   │
                                    +───────────────────────────────────+=== +VDC BUS (+400V DC Regulated)
                                                                        │
                                                                       ┌┴──────────────────┐
                                                                       │ C_BULK BANK       │
                                                                      ┌┴┐ 2x 330µF / 450V ┌┴┐ C_HF_CER
                                                                      │ │ Nichicon LGN    │ │ 2x 0.47µF / 630V
                                                                      └┬┘ (Hold-Up Cap)   └┬┘ Film Capacitor
                                                                       │                   │
                                                                       │      +VDC         │
                                                                       │        │          │
                                                                       │     [ R_fb1: 1.0MΩ / 0.5W ]
                                                                       │     [ R_fb2: 1.0MΩ / 0.5W ]
                                                                       │        │
                                                                       │        +---> V_FB (To PFC Controller)
                                                                       │        │     (V_ref = 2.500V)
                                                                       │     [ R_fb3: 12.7kΩ / 0.1% ]
                                                                       │        │
                                                                       │       AGND (Quiet Ground)
                                                                       │        │
                                                                       │     (Single Star Tie Point)
    GND_PWR (Power Ground Return) ─────────────────────────────────────┴────────+──────────┴───> -VDC (GND)
```

### 2.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **RECT_OUT (+)** | Full-Wave Bridge (+) | Inrush Diode $D_{inrush}$ Anode, Boost Choke $L_{pfc}$ Pin 1, $C_{in,HF}$ | 100Hz/120Hz rectified haversine input | High-frequency film cap $C_{in,HF}$ prevents 100kHz ripple from feeding back into bridge diodes. |
| **SW (PFC Node)** | Boost Choke $L_{pfc}$ Pin 2, $Q_1$ Drain | SiC Diode $D_{pfc}$ Anode, Snubber | High-voltage 100kHz boost switching node | Heavy trace routing; minimize loop area between $Q_1$ drain, $D_{pfc}$ anode, and $C_{bulk}$ return. |
| **+VDC (400V Bus)** | Diode $D_{pfc}$ Cathode, $D_{inrush}$ Cathode | $C_{bulk}$ bank (+), Feedback Divider, Downstream PSU | Regulated +400V DC intermediate bus | Inrush diode $D_{inrush}$ bypasses boost choke during plug-in to prevent core saturation. |
| **ISENSE_P / N** | Current Shunt $R_{shunt}$ Kelvin Pads | PFC Controller Current Loop Amplifier | Average inductor current sensing | Route as shielded differential pair; carries rectified sinusoidal current wave. |
| **V_FB** | Resistor Divider $R_{fb1-3}$ Junction | PFC Controller Voltage Loop Amp (Pin 1) | Output voltage regulation feedback | Total divider resistance $\approx 2\,\text{M}\Omega$ to minimize quiescent bleeder power dissipation. |
| **GND_PWR** | Bridge (-), $R_{shunt}$ (-), $C_{bulk}$ (-) | High-current power return plane | Circulating power stage ground | Solid ground plane; isolated from quiet analog signal ground AGND. |

### 2.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **$Q_1$** | PFC Boost N-MOSFET | Infineon IPW60R045CP | $V_{DS} = 650\,\text{V}, I_D = 60\,\text{A}, R_{DS(on)} = 45\,\text{m}\Omega, Q_g = 150\,\text{nC}$ | Superjunction CoolMOS provides ultra-low conduction losses at high RMS current ($I_{rms} \approx 6.5\,\text{A}$ at $90\,\text{V}_{ac}$). |
| **$D_{pfc}$** | SiC Boost Rectifier Diode | Wolfspeed C3D06060A | $V_{RRM} = 600\,\text{V}, I_F = 6\,\text{A}, Q_c = 14\,\text{nC}, V_F = 1.5\,\text{V}$ | **Zero Reverse Recovery ($Q_{rr} \approx 0$)**: Essential for continuous conduction mode (CCM) to avoid turn-on shoot-through. |
| **$D_{inrush}$** | Startup Inrush Bypass Diode | Diodes Inc. S10MC | $V_{RRM} = 1000\,\text{V}, I_F = 10\,\text{A}, I_{FSM} = 300\,\text{A}$ | Conducts initial $80\,\text{A}$ surge at AC plug-in; prevents $L_{pfc}$ saturation and protects $D_{pfc}$. |
| **$L_{pfc}$** | Boost PFC Inductor | Custom Sendust Core (CS33125) | $L = 450\,\mu\text{H}, I_{sat} = 11\,\text{A}, I_{rms} = 7.5\,\text{A}, DCR = 45\,\text{m}\Omega$ | Low-permeability Sendust material ($\mu_r = 60$) maintains soft saturation characteristics without overheating. |
| **$C_{bulk}$** | DC Bus Bulk Capacitors | Nichicon LGN2W331MELY | $2 \times 330\,\mu\text{F}, 450\,\text{V}_{\text{DC}}, 105^\circ\text{C}, ESR = 0.18\,\Omega$ | Accommodates 100Hz double-frequency ripple current ($I_{ripple} \approx 2.8\,\text{A}_{rms}$) and 20ms hold-up. |
| **$R_{shunt}$** | Inductor Current Sense Shunt | Isabellenhütte ISA-WELD | $20\,\text{m}\Omega, 3.0\,\text{W}, 1\%, TCR < 20\,\text{ppm}/^\circ\text{C}$ | Non-inductive electron-beam welded manganin construction ensures clean current measurement. |
| **$U_1$ (PFC IC)** | CCM PFC Controller | TI UCC28019A / UCC28180 | Continuous average current mode, internal ramp sync | Eliminates external AC voltage sensing; requires only current and output voltage sense. |


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
