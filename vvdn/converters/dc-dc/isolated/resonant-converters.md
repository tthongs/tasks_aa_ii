# Isolated Resonant DC-DC Converters: SRC, PRC & LLC Half-Bridge Masterclass

Welcome to the **VVDN Engineering Hub Technical Dossier on Isolated Resonant DC-DC Converters**. Resonant power conversion is the gold standard for high-density, ultra-high-efficiency power systems—including 80 PLUS Titanium server power supplies, telecom rectifiers, electric vehicle (EV) DC-DC converters, and renewable energy interfaces. 

This document explores the mathematical principles of resonant tanks, compares **Series Resonant Converters (SRC)** and **Parallel Resonant Converters (PRC)**, and conducts a deep dive into the industry-dominant **LLC Resonant Half-Bridge Converter**, including First Harmonic Approximation (FHA), gain curves $M(f_n, Q, L_n)$, ZVS/ZCS boundary conditions, and a complete hardware design methodology.

---

## 1. Why Resonant Conversion? Hard vs. Soft Switching

Conventional PWM converters (Forward, Flyback, Full-Bridge) suffer from hard switching: switches turn on and turn off while carrying full voltage and current simultaneously.

```text
                  Hard Switching vs. Soft Switching (ZVS)
   HARD SWITCHING (Turn-On):                 SOFT SWITCHING / ZVS (Turn-On):
      V_DS   I_D                                 V_DS   I_D
       ^      ^                                   ^      ^
       │\    /│                                   │\     │
       │ \  / │  Overlapping Area                 │ \    │   V_DS reaches 0V
       │  \/  │  = Turn-On Energy                 │  \   │   BEFORE I_D rises!
       │  /\  │    Loss (E_on)                    │   \  │   E_on = 0 Joules!
       │ /  \ │                                   │    \_│______
       0───────┴─────────> Time                   0──────┴─────────────> Time
```

### Limitations of Hard-Switched PWM:
1. **Switching Losses**: $P_{sw} = \left( E_{on} + E_{off} \right) \cdot f_s$. As switching frequency increases above $100\,\text{kHz}$, switching losses dominate, severely limiting power density.
2. **Capacitive Turn-On Loss**: Energy stored in MOSFET parasitic drain-source capacitance ($\frac{1}{2} C_{oss} V_{DS}^2$) is dissipated internally as heat every turn-on cycle.
3. **Diode Reverse Recovery**: Secondary diodes snapped off at high $di/dt$ suffer reverse-recovery current spikes, inducing ringing and electromagnetic interference (EMI).

### The Resonant Solution:
Resonant converters introduce an LC tank network that shapes the switch voltage or current into smooth sinusoids:
- **Zero-Voltage Switching (ZVS)**: Voltage across the switch drops to zero before gate drive turn-on, eliminating $E_{on}$ and $C_{oss}$ losses.
- **Zero-Current Switching (ZCS)**: Current through the switch or rectifier diode drops to zero before turn-off, eliminating turn-off losses and reverse-recovery phenomena.

---

## 2. Resonant Converter Taxonomy: SRC vs. PRC vs. LLC

```text
                               Resonant Converter Topologies
         Series Resonant (SRC)       Parallel Resonant (PRC)         LLC Resonant (LLC)
               Cr     Lr                   Cr     Lr                     Cr     Lr
     +Vin ────[  ]───^^^^──┐     +Vin ────[  ]───^^^^──┬───     +Vin ────[  ]───^^^^──┬───
                           │                           │                              │
                          ( ) Xfmr                    ┌┴┐                            ┌┴┐
                          ( ) Primary                 │ │ Cp                         │ │ Lm (Magnetizing)
                           │                          └┬┘                            └┬┘
                           │                           │                              │
                           │                          ( ) Xfmr                       ( ) Xfmr
                           │                          ( ) Primary                    ( ) Primary
     GND  ─────────────────┴───  GND  ─────────────────┴───     GND  ─────────────────┴───
```

### Comprehensive Comparison:

| Feature / Metric | Series Resonant Converter (SRC) | Parallel Resonant Converter (PRC) | LLC Resonant Converter |
| :--- | :--- | :--- | :--- |
| **Resonant Tank Elements** | $L_r, C_r$ (2 elements) | $L_r, C_p$ (2 elements) | $L_r, C_r, L_m$ (3 elements) |
| **No-Load / Light-Load Regulation** | **Fails**: At no load ($R_L \rightarrow \infty$), gain is fixed at 1; frequency must go to $\infty$. | **Good**: Can regulate down to zero load with finite frequency change. | **Excellent**: Regulates seamlessly from full load down to zero load. |
| **Circulating Energy at Light Load** | Minimal (current drops with load). | Extremely high (tank current flows through $C_p$ regardless of load). | Minimal (magnetizing current circulates only enough to guarantee ZVS). |
| **Output Filter** | Capacitive ($C_o$ only). | Inductive ($L_o + C_o$). | Capacitive ($C_o$ only, no inductor). |
| **Efficiency at Wide Range** | Poor across wide $V_{IN}$ variations. | Poor at light load. | **Peak Industry Standard** ($> 97\%$). |

---

## 3. The LLC Resonant Half-Bridge Converter: Architecture & Physics

The **LLC Resonant Converter** utilizes three reactive elements: a series resonant capacitor $C_r$, a series resonant inductor $L_r$ (often integrated as transformer primary leakage inductance), and the transformer primary magnetizing inductance $L_m$:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: LLC RESONANT HALF-BRIDGE CONVERTER (400V -> 12V/40A, 500W SERVER PSU)
========================================================================================================================

                  +-----------------[ D_boot: DFLS1100 ]<------+ +VCC_DRV (+12V)
                  |                 [ 100V / 1A Schottky]      |
                  |                                           [R_boot: 2.2Ω]
                  |                                            |
                  |     +-----------[ C_boot: 0.1µF/50V X7R ]--+
                  |     |                                      |
                  |     |   +---[ RESONANT LLC CONTROLLER IC (e.g. UCC256403 / L6599A) ]---+
                  |     |   |                                                              |
                  +-------->| BOOT      [HO] Pin 16 ---[ R_g1: 4.7Ω ]----+                 |
                        |   |                                            |                 |
                        +-->| PHASE/HB  [LO] Pin 11 ---[ R_g2: 4.7Ω ]--+ |                 |
                            |                                          | |                 |
         OPTO_FB ---------->| FB (VCO)  [VCC] Pin 12 <-- +12V          | |                 |
         ISEN_IN ---------->| ISEN      [GND] Pin 10 --> GND_PRI       | |                 |
                            +------------------------------------------|-|-----------------+
                                                                       | |
    +V_BUS (+400V DC Rail) ───────────────┬────────────────────────────|─|───────────────────────┐
        │                                 │                            │ │                       │
       ┌┴─────────────────┐           Drain (D)                        │ │                      ┌┴┐
       │ C_BUS_BULK       │          ┌────┴──────────┐                 │ │                      │ │ C_CER
       │ 330µF / 450V     │          │ Q1: HS N-MOS  │<----------------+ │                      └┬┘ 2x 1µF/630V
       │ Aluminum Elec.   │          │ IPW60R099CP   │                   │                       │   Poly Film
       └┬─────────────────┘          │ (650V, 99mΩ)  │                   │                       │
        │                            └────┬──────────┘                   │                       │
        │                           Source│                              │                       │
        │                                 │                              │                       │
        │                                 +=== HALF-BRIDGE MID (HB)      │                       │
        │                                 |    (0V to +400V Square Wave) │                       │
        │                                 |                              │                       │
        │       +-------------------------+--[ Cr: 24nF / 630V MKP ]     │                       │
        │       |                         |  SERIES RESONANT CAP         │                       │
        │       |                         |  (Low-Loss Polypropylene)    │                       │
        │       |                         |                              │                       │
        │       |                         +--[ Lr: 22µH Resonant Choke ]-+                       │
        │       |                         |  (Integrated Leakage / Ext)  |                       │
        │       |                         |                              |                       │
        │       |                     Drain (D)                          |                       │
        │       |                    ┌────┴──────────┐                   |                       │
        │       |                    │ Q2: LS N-MOS  │<------------------+                       │
        │       |                    │ IPW60R099CP   │                                           │
        │       |                    │ (650V, 99mΩ)  │                                           │
        │       |                    └────┬──────────┘                                           │
        │       |                   Source│                                                      │
        │       |                         +---[ CT1: Resonant Current ]                          │
        │       |                         │   Sense Transformer -> ISEN                          │
        │       |                         │                                                      │
    GND_PRI ────┴─────────────────────────┴──────────────────────────────────────────────────────┴─── GND_PRI
                                          │
                                          +=== TANK EXCITATION NODE
                                          |
                                          ├──[ Lm: 110µH Magnetizing Inductance ]──┐
                                          │  (Integrated Transformer Core Gap)     │
                                          │                                        │
                                          +---[ Transformer Primary Winding Np ]───┤ (Np: 18T)
                                          |   * (Dot at Tank Node)                 |
                                          |                                        |
                                          +----------------------------------------+
                                          |
   =======================================│===================================== ISOLATION BARRIER =================
                                          |
    GND_SEC ──────────────────────────────┼───+─────────────────────────────────────────────────────────┬─── GND_SEC
                                          │   │                                                         │
                                          │   │                        SECONDARY CENTER-TAP             │
                                          │   │                        (Ns1: 1T, Ns2: 1T Cu-Foil)       │
                                          │   │                                   │                     │
                                          │   │                     +-------------+-------------+       │
                                          │   │                     |                           |       │
                                          │   │               SECONDARY WINDING 1         SECONDARY WINDING 2
                                          │   │               (Ns1: 1T Foil)              (Ns2: 1T Foil)│
                                          │   │               * (Dot at SR1 Drain)        |             │
                                          │   │                     |                     * (Dot at Center-Tap)
                                          │   │                 Drain (D)                 |             │
                                          │   │               ┌─────┴──────────┐      Drain (D)         │
                                          │   │               │ Q_SR1: SYNC FET│     ┌────┴──────────┐  │
                                          │   │               │ BSC014N04LS    │     │ Q_SR2: SYNC   │  │
                                          │   │        +----->│ (40V, 1.4mΩ)   │ +-->│ BSC014N04LS   │  │
                                          │   │        | Gate └─────┬──────────┘ |   └────┬──────────┘  │
                                          │   │        |      Source│            |  Source│             │
                                          │   │        |            │            |        │             │
                                          │   │   +----+------------|------------+--------+             │
                                          │   │   | DUAL SYNCHRONOUS RECTIFIER CONTROLLER               │
                                          │   │   | (e.g. MP6922 / TEA1995: Zero-Current Sensing)       │
                                          │   │   +-----------------+-----------------------------------+
                                          │   │                     │
                                          │   │                  GND_SEC
                                          │   │
                                          │   +===================================+=== +VOUT (+12V/40A, 500W)
                                          │                                       │    (Pure Capacitive Filter!)
                                          │                                      ┌┴──────────────────┐
                                          │                                      │ COUT_BULK         │
                                          │                                     ┌┴┐ 6x 470µF/16V    ┌┴┐ COUT_CER
                                          │                                     │ │ Poly (ESR=4mΩ)  │ │ 8x 47µF/16V
                                          │                                     └┬┘                 └┬┘ X7R 1210
                                          │                                      │                   │
                                          │            +VOUT                     │      +VOUT        │
                                          │              │                       │        │          │
                                          │           [ 1kΩ ]                    │     [ R_fb1: 38.3kΩ ]
                                          │              │                       │        │
                                          │     [ Anode: Pin 1 ]                 │        +---> TL431 REF
                                          │     PC817 OPTOCOUPLER                │        │     (V_ref=2.50V)
                                          │     [ Cathode: Pin 2 ]               │     [ R_fb2: 10.0kΩ ]
                                          │              │                       │        │
                                          │              +----[ CATHODE: TL431 ]─+       GND_SEC
                                          │              |    (Precision Shunt)  |        │
                                          │              +----[ ANODE: GND_SEC ]─+        │
                                          │                                               │
    GND_SEC ──────────────────────────────┴───────────────────────────────────────────────┴─── GND_SEC (Return)
```

### 3.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+V_BUS** | PFC 400V Bulk Bus | $C_{bus}$ (+), $Q_1$ Drain, Controller $V_{IN}$ | Stiff DC high-voltage rail | Symmetrical high-frequency MLCC bypass directly at half-bridge drain. |
| **HB (Switch Node)** | $Q_1$ Source, $Q_2$ Drain | Resonant Cap $C_r$ Pin 1, Driver PHASE | High-speed ZVS switching midpoint | Swings between $0\,\text{V}$ and $+400\,\text{V}$ at variable frequency ($80\,\text{kHz} \dots 200\,\text{kHz}$). |
| **RESONANT_TANK** | Resonant Cap $C_r$ Pin 2 | Series Resonant Choke $L_r$ Pin 1 | High-current AC resonant loop | $C_r$ sees high peak AC voltage ($\pm 600\,\text{V}_{pk}$); must use low-loss MKP dielectric. |
| **TANK_XFMR** | Resonant Choke $L_r$ Pin 2 | Transformer Primary $N_p$ Pin 1, $L_m$ | Transformer excitation node | Sinusoidal current excitation produces zero EMI harmonics compared to hard-switched PWM. |
| **SR1_GATE / SR2_GATE**| SR Controller OUTA / OUTB | Synchronous Rectifier $Q_{SR1}, Q_{SR2}$ Gates | Ultra-fast sync rect gate signals | Senses $V_{DS}$ across FET to turn ON when channel conducts and turn OFF at exact zero-crossing (ZCS). |
| **+VOUT** | Transformer Secondary Center-Tap | $C_{out}$ bank (+), Feedback network, Load (+) | High-efficiency regulated +12V DC rail | **No Output Inductor Needed**: LLC functions as a smooth current source, feeding $C_o$ directly. |
| **GND_SEC** | Sync FETs $Q_{SR1}, Q_{SR2}$ Sources | $C_{out}$ bank (-), Secondary Return | Secondary high-current power return | Continuous plane pour handling 40A return current. |

### 3.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **$Q_1, Q_2$** | Resonant Half-Bridge FETs | Infineon IPW60R099CP | $V_{DS} = 650\,\text{V}, I_D = 31\,\text{A}, R_{DS(on)} = 99\,\text{m}\Omega, C_{oss} = 95\,\text{pF}$ | Low $C_{oss}$ allows fast zero-voltage switching transitions with modest magnetizing current $I_m$. |
| **$C_r$** | Series Resonant Capacitor | KEMET R76IR4240SE30K | $24\,\text{nF}, 630\,\text{V}_{\text{DC}}, \text{Double Metallized Polypropylene}$ | Ultra-low dissipation factor ($\tan \delta < 0.0005$); handles continuous $4\,\text{A}_{rms}$ resonant tank current. |
| **$L_r$** | Series Resonant Inductor | Custom PQ26/20 (3C95) | $L_r = 22\,\mu\text{H}, I_{pk} = 4.8\,\text{A}, DCR = 14\,\text{m}\Omega$ | High-frequency litz-wire winding minimizes AC resistance from skin and proximity effects. |
| **$T_1$ (LLC)** | LLC Power Transformer | Custom ETD44 Core (3C95) | Turns: $18:(1+1), L_m = 110\,\mu\text{H}, L_k \approx 4\,\mu\text{H}$ | Precisely gapped center leg controls magnetizing inductance ratio $k = L_m / L_r = 5.0$. |
| **$Q_{SR1}, Q_{SR2}$** | Synchronous Rectifier FETs | Infineon BSC014N04LS | $V_{DS} = 40\,\text{V}, I_D = 125\,\text{A}, R_{DS(on)} = 1.4\,\text{m}\Omega, Q_g = 35\,\text{nC}$ | Superjunction sync FETs in PowerPAK eliminate $> 15\,\text{W}$ of diode forward conduction loss. |
| **$C_{out,bulk}$** | Output Bulk Capacitor | Panasonic 16SEPC470M | $6 \times 470\,\mu\text{F}, 16\,\text{V}, \text{Conductive Polymer}, ESR = 4\,\text{m}\Omega$ | Net bank ESR $< 0.7\,\text{m}\Omega$; absorbs secondary resonant AC ripple current ($I_{rms} \approx 20\,\text{A}$). |
| **$U_1$ (Controller)** | LLC Resonant Controller | TI UCC256403DDBR | Variable frequency control ($35\,\text{kHz} \dots 1\,\text{MHz}$), soft start, burst mode | Built-in high-voltage startup and hybrid hysteretic control for lightning-fast transient response. |
| **$U_2$ (SR Driver)** | Dual Smart SR Controller | MPS MP6922GS | $V_{DS}$ sensing down to $-30\,\text{mV}$, $t_{prop} < 20\,\text{ns}$ | Prevents shoot-through by ensuring synchronous switches turn OFF cleanly before current reverses. |


### 3.1 Two Characteristic Resonant Frequencies:
1. **Series Resonant Frequency ($f_r$ or $f_0$)**:
   Determined by the resonant tank $L_r$ and $C_r$:
   $$f_r = \frac{1}{2\pi \sqrt{L_r \cdot C_r}}$$
2. **Lower Resonant Frequency ($f_m$ or $f_p$)**:
   Determined when $L_m$ is liberated from secondary clamping (magnetizing current resonates with $C_r$):
   $$f_m = \frac{1}{2\pi \sqrt{(L_r + L_m) \cdot C_r}} = \frac{f_r}{\sqrt{1 + L_n}}$$
   Where $L_n = \frac{L_m}{L_r}$ is the inductance ratio.

---

## 4. First Harmonic Approximation (FHA) & Voltage Gain Formulation

Under **First Harmonic Approximation (FHA)**, the square-wave voltages and currents are modeled by their fundamental sinusoidal Fourier components:

```text
                       LLC Resonant Equivalent AC Circuit (FHA Model)
                     Cr           Lr
          ───o─────[   ]────────^^^^^^───────┬────────────────o───
             +                               │                +
                                            ┌┴┐
            v_ac,in                         │ │ Lm           v_ac,out  (R_ac)
                                            └┬┘
             -                               │                -
          ───o───────────────────────────────┴────────────────o───
```

### 4.1 Equivalent AC Resistance ($R_{ac}$):
Reflecting the DC load resistance $R_L = \frac{V_o}{I_o}$ across the secondary rectifier and transformer turns ratio $n = \frac{N_p}{N_s}$:
$$R_{ac} = \frac{8 \cdot n^2}{\pi^2} \cdot R_L$$

### 4.2 Normalized Parameters:
- Normalized switching frequency: $f_n = \frac{f_s}{f_r}$
- Inductance ratio: $L_n = \frac{L_m}{L_r}$ (typically between $3 \dots 8$)
- Quality factor: $Q = \frac{\sqrt{L_r / C_r}}{R_{ac}} = \frac{Z_o}{R_{ac}}$

### 4.3 DC Voltage Gain Formula:
The transfer function of the LLC resonant tank is:
$$M(f_n, Q, L_n) = \left| \frac{v_{ac,out}}{v_{ac,in}} \right| = \frac{1}{\sqrt{\left[ 1 + \frac{1}{L_n} \left( 1 - \frac{1}{f_n^2} \right) \right]^2 + Q^2 \left( f_n - \frac{1}{f_n} \right)^2}}$$

---

## 5. LLC Operating Regions & Gain Curve Analysis

```text
                        LLC Resonant Converter Gain Curves
         Gain M ^
                │                   Q = 0.2 (Light Load)
            1.6 ┼                 .-'""'-.
                │               .'        '.  Q = 0.5 (Nominal)
            1.4 ┼              /    /\      \
                │             /    /  \      \    Q = 1.0 (Full Load)
            1.2 ┼            /    /    \      '.
                │           /    /      \       \
       Unity 1.0┼──────────/────/────────\───────\──────── Resonance (fn = 1.0)
                │         /    /          \       \
            0.8 ┼        /    /            \       \
                │       /    /              \       \
            0.6 ┼──────'────'────────────────'───────'────
                │     │                  │
                0    f_m                f_r (fn=1.0)        ───> Normalized Frequency (fn)
                │◄── Capacitive ──►│◄─── Inductive ZVS Zone ────►│
                   (FORBIDDEN ZONE)
```

### The Three Operating Modes:

1. **Resonance Operation ($f_s = f_r \implies f_n = 1.0$)**:
   - The tank impedance is purely resistive ($Z_r = 0$).
   - Gain is identically **unity ($M = 1.0$)** independent of load $Q$.
   - Primary switches achieve perfect **ZVS turn-on**.
   - Secondary rectifier diodes turn off at zero current (**ZCS**), completely eliminating diode reverse recovery losses!
   - This is the highest efficiency operating point (typically designed for nominal input voltage).

2. **Below Resonance ($f_m < f_s < f_r \implies f_n < 1.0$) [Boost Mode]**:
   - Gain $M > 1.0$. The converter boosts output voltage to compensate for low $V_{IN}$ (e.g., during line sag or battery discharge).
   - Tank current resonates and falls to the magnetizing current $I_m$ before the half-cycle ends.
   - Secondary diode current terminates naturally to zero during the cycle: **perfect secondary ZCS**.
   - Primary MOSFETs maintain **ZVS turn-on**.

3. **Above Resonance ($f_s > f_r \implies f_n > 1.0$) [Buck Mode]**:
   - Gain $M < 1.0$. The converter steps down output voltage for high $V_{IN}$.
   - Primary MOSFETs maintain **ZVS turn-on**.
   - Secondary diode current is continuous and snapped off at switch turn-off: **ZCS is lost on secondary** (reverse-recovery occurs, requiring ultra-fast diodes or Schottky diodes).

4. **Capacitive Region ($f_s < f_m$) — THE FORBIDDEN ZONE**:
   - Tank current leads switch voltage. Primary switches lose ZVS and suffer **hard turn-on**.
   - Body diodes of the MOSFETs conduct reverse recovery current directly into the incoming switch, causing catastrophic switch shoot-through failure.
   - Modern LLC controller ICs (e.g., UCC25640x, HR1001) integrate **Capacitive Mode Prevention (CMP)** logic to clamp minimum switching frequency above the capacitive threshold.

---

## 6. Step-by-Step LLC Resonant Hardware Design Procedure

### Step 1: Establish Converter Specifications
- Input Voltage: $V_{IN,nom} = 390\,\text{V}$, $V_{IN,min} = 320\,\text{V}$, $V_{IN,max} = 420\,\text{V}$ (PFC Rail)
- Output: $V_o = 12\,\text{V}$, $I_o = 25\,\text{A}$ ($P_o = 300\,\text{W}$)
- Resonant frequency target: $f_r = 100\,\text{kHz}$

### Step 2: Transformer Turns Ratio ($n$)
Design for unity gain $M_{nom} = 1.0$ at nominal input $V_{IN,nom}$:
$$n = \frac{N_p}{N_s} = \frac{V_{IN,nom}}{2 \cdot (V_o + V_F)} = \frac{390\,\text{V}}{2 \cdot (12\,\text{V} + 0.4\,\text{V})} \approx 15.7 \implies \text{Select } n = 16$$

### Step 3: Calculate Required Minimum and Maximum Gain
$$M_{max} = \frac{n \cdot (V_o + V_F)}{V_{IN,min} / 2} = \frac{16 \cdot 12.4\,\text{V}}{320\,\text{V} / 2} = \frac{198.4}{160} = 1.24$$
$$M_{min} = \frac{n \cdot (V_o + V_F)}{V_{IN,max} / 2} = \frac{16 \cdot 12.4\,\text{V}}{420\,\text{V} / 2} = \frac{198.4}{210} = 0.94$$
Add $10\%$ design margin: $M_{peak,req} = 1.1 \cdot M_{max} = 1.36$.

### Step 4: Select Inductance Ratio ($L_n$) and Quality Factor ($Q$)
- An inductance ratio $L_n = \frac{L_m}{L_r} = 5$ provides an excellent balance between wide voltage regulation and low circulating current.
- From FHA gain curves for $L_n = 5$ and $M_{peak} = 1.36$, choose maximum full-load quality factor:
  $$Q_{max} = 0.40$$

### Step 5: Calculate Equivalent Load and Resonant Tank Values
$$R_L = \frac{V_o}{I_o} = \frac{12\,\text{V}}{25\,\text{A}} = 0.48\,\Omega$$
$$R_{ac} = \frac{8 \cdot n^2}{\pi^2} \cdot R_L = \frac{8 \cdot 16^2}{\pi^2} \cdot 0.48 = \frac{2048 \cdot 0.48}{9.8696} \approx 99.6\,\Omega$$

1. **Resonant Capacitor ($C_r$)**:
   $$C_r = \frac{1}{2\pi \cdot f_r \cdot Q \cdot R_{ac}} = \frac{1}{2\pi \cdot 100\,000 \cdot 0.40 \cdot 99.6} \approx 40\,\text{nF} \implies \text{Select } 39\,\text{nF (Polypropylene Film)}$$
2. **Resonant Inductor ($L_r$)**:
   $$L_r = \frac{1}{(2\pi \cdot f_r)^2 \cdot C_r} = \frac{1}{(2\pi \cdot 100\,000)^2 \cdot 39 \cdot 10^{-9}} \approx 65\,\mu\text{H}$$
3. **Magnetizing Inductance ($L_m$)**:
   $$L_m = L_n \cdot L_r = 5 \cdot 65\,\mu\text{H} = 325\,\mu\text{H}$$

### Step 6: Verify Primary ZVS Condition During Dead-Time
To guarantee ZVS at switch turn-on, the magnetizing current peak $I_{m,pk}$ must discharge the two MOSFET output capacitances ($2 C_{oss}$) during dead-time $t_d$:
$$I_{m,pk} = \frac{n \cdot V_o}{4 \cdot L_m \cdot f_r} = \frac{16 \cdot 12\,\text{V}}{4 \cdot 325\,\mu\text{H} \cdot 100\,000\,\text{Hz}} = \frac{192}{130} \approx 1.48\,\text{A}$$
Required dead-time $t_{d,min}$:
$$t_d \ge \frac{2 \cdot C_{oss} \cdot V_{IN}}{I_{m,pk}} = \frac{2 \cdot 150\,\text{pF} \cdot 400\,\text{V}}{1.48\,\text{A}} \approx 81\,\text{ns}$$
Setting dead-time $t_d = 250\,\text{ns} \dots 350\,\text{ns}$ guarantees complete, robust ZVS switching across all line and load variations.

---

## 7. Practical Engineering Summary

1. **Transformer Integration**: Rather than using a separate physical inductor for $L_r$, wind the transformer with intentional spatial separation or a magnetic shunt between primary and secondary sections to integrate $L_r$ directly as transformer leakage inductance ($L_{lk} = L_r$).
2. **Resonant Capacitor Selection**: The resonant capacitor carries full resonant AC current ($I_{Cr,rms} \approx 2 \dots 4\,\text{A}$). Never use ceramic MLCCs (due to DC bias capacitance drop and acoustic microphonics) or polyester film. **Always use High-Current Metalized Polypropylene (MKP) film capacitors**.
3. **Synchronous Rectification (SR)**: On the low-voltage high-current secondary ($12\,\text{V}, 25\,\text{A}$), replace Schottky diodes with low $R_{DS(on)}$ MOSFETs ($< 2\,\text{m}\Omega$) driven by specialized resonant SR controllers (e.g., TEA1995, MP6924) sensing drain-source $V_{DS}$ ringing.
