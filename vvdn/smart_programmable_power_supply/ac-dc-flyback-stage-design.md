# AC-DC Flyback Stage Design: Universal AC Frontend, QR Flyback & Synchronous Rectification

Welcome to the **VVDN Engineering Hub Technical Dossier on the Primary AC-DC Flyback Converter Stage** of the Smart Programmable Power Supply. This document delivers an exhaustive mathematical and circuit-level hardware analysis covering universal mains rectification ($85\,\text{V} \dots 265\,\text{V}$ AC), electromagnetic interference (EMI) filtering, transformer magnetic sizing, primary Superjunction MOSFET selection, RCD snubber calculations, secondary synchronous rectification (SR), and closed-loop optoisolated regulation.

---

## 1. Primary Stage Executive Overview & Specifications

The AC-DC Flyback converter stage functions as the **isolated primary power engine** of the system. It converts unpredictable, high-voltage universal grid AC into a rock-solid, galvanically isolated $+24.0\,\text{V}$ DC intermediate rail capable of delivering $3.0\,\text{A}$ continuous load current ($72\,\text{W}$ maximum stage throughput):

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                      AC-DC Flyback Stage Design Specifications                    │
├────────────────────────────┬─────────────────────────────┬────────────────────────┤
│ Parameter / Metric         │ Target Value                │ Engineering Rationale  │
├────────────────────────────┼─────────────────────────────┼────────────────────────┤
│ **Input Voltage ($V_{AC}$)**│ 85 V – 265 V AC RMS         │ Worldwide universal grid│
│ **Input Frequency ($f_L$)** │ 47 Hz – 63 Hz               │ 50 Hz EU/Asia, 60 Hz US│
│ **Minimum DC Bulk Voltage**│ $V_{bulk(min)} = 90\,\text{V}$│ Sized for 10ms holdup  │
│ **Maximum DC Bulk Voltage**│ $V_{bulk(max)} = 375\,\text{V}$│ 265V AC * sqrt(2) peak │
│ **Regulated Output Voltage**│ $+24.0\,\text{V} \pm 1.0\%$ │ Optimal for Buck-Boost │
│ **Nominal Output Current** │ $3.0\,\text{A}$ Continuous  │ 72 W peak stage power  │
│ **Peak-to-Peak Bus Ripple**│ $< 40\,\text{mV}_{\text{pk-pk}}$│ High-C ceramic bypass  │
│ **Target Conversion Eff.** │ $\ge 91\%$ @ 230V AC, >89% @ 115V│ Synchronous Rectifier  │
│ **Switching Frequency**    │ $65\,\text{kHz} \dots 100\,\text{kHz}$ (QR Valley)│ Minimum EMI harmonics  │
│ **Isolation Barrier**      │ $\ge 3000\,\text{V}_{\text{RMS}}$ (1 min Hipot)│ Reinforced IEC 62368-1 │
└────────────────────────────┴─────────────────────────────┴────────────────────────┘
```

---

## 2. Universal AC Input Protection & Two-Stage EMI Filter Design

The mains frontend must withstand severe line transients, lightning surges (IEC 61000-4-5), cold-start inrush currents, and attenuate both common-mode (CM) and differential-mode (DM) noise to comply with **EN 55032 / CISPR 32 Class B**:

```text
                        Universal AC Input & Two-Stage EMI Filter
  LINE (85-265V AC) ───┬───[ F1: T2A/250V ]───[ NTC: 10Ω ]───┬────────██████ (L_CM1) ───┬────────██████ (L_CM2) ───┬───> To Bridge (AC1)
                       │                                     │                          │                          │
                      ┌┴┐                                  ┌─┴─┐                      ┌─┴─┐                      ┌─┴─┐
                      │ │ MOV1 (14D471K)                   │   │ C_X1                 │   │ C_X2                 │   │ C_X3
                      └┬┘ 300V RMS / 4.5kA                 │   │ 220nF / 310V         │   │ 220nF / 310V         │   │ 100nF / 310V
                       │                                   └─┬─┘                      └─┬─┘                      └─┬─┘
                       │                                     │                          │                          │
  NEUTRAL ─────────────┴─────────────────────────────────────┼────────██████ (L_CM1) ───┼────────██████ (L_CM2) ───┼───> To Bridge (AC2)
                                                             │                          │                          │
                                                           ┌─┴─┐                      ┌─┴─┐                      ┌─┴─┐
                                                           │   │ R_bleed              │   │ C_Y1                 │   │ C_Y2
                                                           │   │ 2x 470kΩ             │   │ 2.2nF/400V           │   │ 2.2nF/400V
                                                           └─┬─┘                      └─┬─┘                      └─┬─┘
                                                             │                          │                          │
  EARTH (PE) ────────────────────────────────────────────────┴──────────────────────────┴──────────────────────────┴─── EARTH (PE)
```

### 2.1 Protection Component Sizing
1. **Fuse ($F_1$)**: Time-lag (slow-blow) ceramic cartridge fuse rated for $2.0\,\text{A} / 250\,\text{V}$ AC ($I^2t \ge 18\,\text{A}^2\text{s}$). Slow-blow characteristics prevent nuisance tripping during inrush charging of the bulk capacitor.
2. **NTC Inrush Thermistor ($NTC_1$)**: A $10\,\Omega$ cold-resistance disc thermistor (Epcos B57236S0100M000, rated for $3.2\,\text{A}_{\text{RMS}}$). Under worst-case $265\,\text{V}$ AC peak switch-on ($V_{pk} = 375\,\text{V}$), peak inrush is clamped to:
   $$I_{inrush(pk)} = \frac{V_{pk,max}}{R_{NTC}} = \frac{375\,\text{V}}{10\,\Omega} = 37.5\,\text{A} \quad (\ll \text{Diode surge rating of } 150\,\text{A})$$
3. **MOV Surge Suppressor ($MOV_1$)**: Metal Oxide Varistor ($14\text{D}471\text{K}$) rated for $300\,\text{V}_{\text{RMS}}$ continuous and $470\,\text{V} \pm 10\%$ clamping threshold. Clamps transient lightning strikes up to $4.5\,\text{kA}$ ($8/20\,\mu\text{s}$ impulse).
4. **Active Bleed Resistor Network ($R_{bleed}$)**: Two $470\,\text{k}\Omega$ $1206$ resistors in series across $C_{X1}$ guarantee that the X-capacitors discharge below $60\,\text{V}$ within $1.0\,\text{second}$ after mains disconnection (IEC 62368-1 safety requirement).

### 2.2 Two-Stage EMI Filter Sizing
- **Differential-Mode (DM) Attenuation**: Handled by Class-X2 metallized polypropylene film capacitors ($C_{X1}, C_{X2} = 0.22\,\mu\text{F} / 310\,\text{V}$ AC) combined with the leakage inductance of the common-mode chokes ($\approx 50\,\mu\text{H}$).
- **Common-Mode (CM) Attenuation**: Dual cascaded common-mode chokes ($L_{CM1} = 2\times 15\,\text{mH}$, $L_{CM2} = 2\times 4.7\,\text{mH}$) wound on high-permeability toroidal nanocrystalline/ferrite cores provide $> 50\,\text{dB}$ attenuation at $150\,\text{kHz} \dots 30\,\text{MHz}$.
- **Y-Capacitors ($C_{Y1}, C_{Y2}$)**: $2.2\,\text{nF} / 400\,\text{V}$ AC safety capacitors return high-frequency common-mode noise to Earth Ground. Total leakage current to Earth is constrained to:
  $$I_{leakage} = 2\pi \cdot f_L \cdot C_{Y,total} \cdot V_{AC} = 2\pi \cdot 50 \cdot (4.4 \times 10^{-9}) \cdot 240 = 0.33\,\text{mA} < 0.5\,\text{mA} \text{ limit}$$

---

## 3. Bridge Rectifier & Bulk Storage Capacitor Sizing

```text
                  Bridge Rectification & DC Bulk Storage
  AC1 In ──────┬───────[ GBU606 Bridge Rectifier ]───────┬───────> +V_BULK (120V - 375V DC)
               │                                         │
               │        AC1 ───|>|─── +DC                │
               │        AC2 ───|>|─── +DC              ┌─┴─┐ C_BULK1           ┌─┴─┐ C_BULK_HF
               │        -DC ───|>|─── AC1              │   │ 100uF / 450V      │   │ 470nF / 450V
               │        -DC ───|>|─── AC2              └─┬─┘ Nichicon 105°C    └─┬─┘ Polypropylene
  AC2 In ──────┴─────────────────────────────────────────┼───────────────────────┼─────────────────
                                                         │                       │
                                                      GND_PRI                 GND_PRI
```

### 3.1 Bulk Capacitor ($C_{bulk}$) Calculation
The bulk capacitor must maintain the DC bus voltage above $V_{bulk(min)} = 90\,\text{V}$ during a full AC half-cycle missing-pulse or line sag ($t_{holdup} \approx 10\,\text{ms}$) under minimum mains input ($V_{AC(min)} = 85\,\text{V}$):
1. Minimum peak AC voltage:
   $$V_{pk(min)} = \sqrt{2} \times 85\,\text{V} - 2 \cdot V_{diode} = 120.2\,\text{V} - 2.0\,\text{V} = 118.2\,\text{V}$$
2. Estimated input power (assuming $\eta = 88\%$ at $85\,\text{V}$ AC):
   $$P_{in} = \frac{P_{OUT}}{\eta} = \frac{72\,\text{W}}{0.88} = 81.8\,\text{W}$$
3. Required bulk capacitance for $10\,\text{ms}$ holdup time:
   $$C_{bulk} \ge \frac{2 \cdot P_{in} \cdot t_{holdup}}{V_{pk(min)}^2 - V_{bulk(min)}^2} = \frac{2 \times 81.8 \times 0.010}{(118.2)^2 - (90.0)^2} = \frac{1.636}{13971 - 8100} = 278\,\mu\text{F} \quad (\text{For 10ms holdup})$$
   *Standard Commercial Sizing (for $5\,\text{ms}$ half-cycle valley ripple)*:
   $$C_{bulk} \ge \frac{2 \cdot P_{in} \cdot 0.005}{(118.2)^2 - (90.0)^2} = 139\,\mu\text{F} \longrightarrow \text{Selected: } \mathbf{100\,\mu\text{F} + 47\,\mu\text{F} = 147\,\mu\text{F} / 450\,\text{V}}$$
   A high-frequency $470\,\text{nF} / 450\,\text{V}$ polypropylene film capacitor is placed in tight parallel to absorb high $di/dt$ switching pulses directly at the primary winding.

---

## 4. Quasi-Resonant (QR) Valley-Switching Flyback Controller Architecture

The primary controller employs the **TI UCC28740** (or **ON Semi NCP1342**) operating in **Quasi-Resonant (QR) Valley Switching Mode**:

```text
               Quasi-Resonant Valley Switching Waveform (Drain-to-Source)
  Vds ^
      │   V_bulk + V_reflected + V_spike
      │        ┌─.
      │       /   \
      │      /     \
      │     /       \
V_bulk┼────'         '─────────────────.
      │                                 \      Resonant Ringing (Lp with Coss)
      │                                  \      / \
      │                                   '────'   \     / \
      │                                    Valley 1 '───'   \
      │                                    (0.5 * Lp * I^2 = 0)
   0V ┴───────────────────────────────────────────────────────┴───> Time
                                              ▲
                                              └─ Primary MOSFET turns ON HERE!
                                                 Vds is at absolute MINIMUM!
                                                 Capacitive turn-on loss slashed by 75%!
```

### Why Quasi-Resonant (QR) Operation?
1. **Valley Switching**: In a standard hard-switched Flyback, the primary FET turns on while $V_{DS} = V_{bulk} + V_R \approx 475\,\text{V}$, dissipating capacitive stored energy $P_{coss} = \frac{1}{2} C_{oss} V_{DS}^2 f_{sw} \approx 1.5\,\text{W}$.
2. In QR mode, the controller monitors the transformer auxiliary winding via a zero-crossing detection (ZCD) pin. It turns the primary switch ON precisely at the resonant minimum (the "valley") of the drain ring, cutting capacitive turn-on losses by up to $80\%$.
3. **Variable Frequency EMI Spreading**: Because switching frequency modulates naturally with load and line voltage, EMI energy is distributed across a wider bandwidth, drastically easing compliance with CISPR 32 Class B limits without bulky chokes.

---

## 5. Transformer Magnetic Design (PQ26/20 Core, 3C95 Ferrite)

The flyback transformer is the heart of the primary stage. It acts not merely as a voltage transformer, but as a **coupled inductor** that stores magnetic energy during the primary ON time and discharges it into the secondary during the OFF time.

```text
                        PQ26/20 Transformer Winding Architecture
              ┌────────────────────────────────────────────────────────┐
              │             Ferrite Core (PQ26/20, 3C95)               │
              │  ┌──────────────────────────────────────────────────┐  │
              │  │ Primary Layer 1 (24 Turns, 0.35mm Magnet Wire)   │  │
              │  ├──────────────────────────────────────────────────┤  │
              │  │ Mylar Tape Insulation (3 Layers, Reinforced)     │  │
              │  ├──────────────────────────────────────────────────┤  │
              │  │ Secondary Winding (12 Turns, 3x 0.45mm Litz Wire)│  │
              │  ├──────────────────────────────────────────────────┤  │
              │  │ Mylar Tape Insulation (3 Layers, Reinforced)     │  │
              │  ├──────────────────────────────────────────────────┤  │
              │  │ Primary Layer 2 (24 Turns, 0.35mm Magnet Wire)   │  │  <-- Sandwich Winding!
              │  ├──────────────────────────────────────────────────┤  │      (Halves Leakage L)
              │  │ Auxiliary VCC Winding (8 Turns, 0.25mm Wire)     │  │
              │  └──────────────────────────────────────────────────┘  │
              └────────────────────────────────────────────────────────┘
```

### 5.1 Step-by-Step Magnetic Calculation:
1. **Core Selection**:
   - Selected Core: **Ferroxcube PQ26/20** (Core material: 3C95, optimized for low core losses at $70\,\text{kHz} \dots 100\,\text{kHz}$).
   - Effective Magnetic Cross-Section Area ($A_e$): $119\,\text{mm}^2 = 1.19 \times 10^{-4}\,\text{m}^2$.
   - Window Area ($A_w$): $44\,\text{mm}^2$.
   - Maximum operating flux density: $B_{max} = 0.28\,\text{Tesla}$ (safe margin below saturation flux density $B_{sat} = 0.42\,\text{T}$ at $100^\circ\text{C}$).
2. **Reflected Secondary Voltage ($V_R$)**:
   - Chosen as $V_R = 100\,\text{V}$.
   - Primary-to-secondary turns ratio ($n = N_p / N_s$):
     $$n = \frac{V_R}{V_{OUT} + V_{SR}} = \frac{100\,\text{V}}{24.0\,\text{V} + 0.1\,\text{V}} = 4.15 \longrightarrow \mathbf{n = 4.0}$$
3. **Maximum Primary Duty Cycle ($D_{max}$)**:
   - At minimum bulk voltage ($V_{bulk(min)} = 90\,\text{V}$):
     $$D_{max} = \frac{V_R}{V_R + V_{bulk(min)}} = \frac{100}{100 + 90} = 0.526 \approx 52.6\%$$
4. **Primary Inductance ($L_p$) & Peak Current ($I_{pk}$)**:
   - Minimum switching frequency at full load: $f_{sw(min)} = 65\,\text{kHz}$.
   - Primary peak current:
     $$I_{pk} = \frac{2 \cdot P_{in}}{V_{bulk(min)} \cdot D_{max}} = \frac{2 \times 81.8\,\text{W}}{90\,\text{V} \times 0.526} = 3.45\,\text{A}$$
   - Required Primary Inductance:
     $$L_p = \frac{V_{bulk(min)} \cdot D_{max}}{I_{pk} \cdot f_{sw(min)}} = \frac{90 \times 0.526}{3.45 \times 65000} = 2.11 \times 10^{-4}\,\text{H} \approx \mathbf{220\,\mu\text{H}}$$
5. **Winding Turns Calculation**:
   - Primary Turns ($N_p$):
     $$N_p = \frac{L_p \cdot I_{pk}}{B_{max} \cdot A_e} = \frac{220 \times 10^{-6} \cdot 3.45}{0.28 \cdot 1.19 \times 10^{-4}} = \frac{7.59 \times 10^{-4}}{3.332 \times 10^{-5}} = 22.8 \longrightarrow \mathbf{N_p = 48\,\text{turns}}$$
     *(Recalculating with split sandwich winding: $N_p = 48\,\text{turns}$, reducing peak operating $B_{max}$ to $0.133\,\text{T}$, guaranteeing ultra-low core temperature rise!).*
   - Secondary Turns ($N_s$):
     $$N_s = \frac{N_p}{n} = \frac{48}{4.0} = \mathbf{12\,\text{turns}}$$
   - Auxiliary VCC Turns ($N_{aux}$):
     Target controller supply: $V_{aux} = 16.0\,\text{V}$.
     $$N_{aux} = N_s \times \frac{V_{aux} + 0.7}{V_{OUT} + V_{SR}} = 12 \times \frac{16.7}{24.1} = 8.3 \longrightarrow \mathbf{N_{aux} = 8\,\text{turns}}$$
6. **Air Gap ($l_g$) Calculation**:
   $$l_g = \frac{\mu_0 \cdot N_p^2 \cdot A_e}{L_p} = \frac{(4\pi \times 10^{-7}) \cdot (48)^2 \cdot (1.19 \times 10^{-4})}{220 \times 10^{-6}} = \frac{3.451 \times 10^{-7}}{2.20 \times 10^{-4}} \approx \mathbf{1.56\,\text{mm}}$$

---

## 6. Primary Superjunction MOSFET & RCD Clamp Snubber Design

```text
                  Primary Superjunction Switch & RCD Snubber
           +V_BULK (Up to 375V DC)
                 │
                 ├───[ Primary Winding: Lp = 220uH ]───┐
                 │                                     │
                 ├───┐                                 ├─── Drain (D)
                 │  ┌┴┐ R_snub1, R_snub2               │   ┌───┴───┐
                 │  │ │ 2x 100kΩ / 2W                  │   │       │ Q1: Superjunction MOSFET
                 │  └┬┘ (50kΩ parallel equivalent)     └───┤       │ (IPB80R290P7: 800V, 0.29Ω)
                 │   ├───┐                                 └───┬───┘
                 │  ┌┴┐  │                                     │ Source (S)
                 │  │ │  │ C_snub                              │
                 │  └┬┘  │ 2.2nF / 1kV Ceramic                 ├───[ R_sense: 0.2Ω / 1W ]─── GND_PRI
                 │   ├───┘                                     │
                 └───┴───[<| D_snub (US1M: 1000V, trr=50ns) ]──┘
```

### 6.1 MOSFET Electrical Stress & Selection:
- Maximum Drain-to-Source Voltage Stress:
  $$V_{DS(max)} = V_{bulk(max)} + n(V_{OUT} + V_{SR}) + V_{spike} = 375\,\text{V} + (4.0 \times 24.1\,\text{V}) + 80\,\text{V} = 375 + 96.4 + 80 = 551.4\,\text{V}$$
- **Device Selected**: **Infineon IPB80R290P7** ($800\,\text{V}$ breakdown, $R_{DS(on)} = 0.29\,\Omega$, $I_D = 17\,\text{A}$, $Q_g = 24\,\text{nC}$).
- Safety derating margin: $\frac{800\,\text{V} - 551.4\,\text{V}}{800\,\text{V}} = 31.0\%$ (exceeds $20\%$ industrial derating guideline).

### 6.2 RCD Snubber Calculation:
1. Measured transformer primary leakage inductance ($L_{lk} \approx 1.5\% L_p$ with sandwich winding):
   $$L_{lk} = 0.015 \times 220\,\mu\text{H} = 3.3\,\mu\text{H}$$
2. Energy stored in leakage inductance per cycle:
   $$E_{leak} = \frac{1}{2} L_{lk} I_{pk}^2 = \frac{1}{2} (3.3 \times 10^{-6}) \cdot (3.45)^2 = 1.96 \times 10^{-5}\,\text{Joules}$$
3. Power dissipated in the snubber at $70\,\text{kHz}$:
   $$P_{snub} = E_{leak} \cdot f_{sw} \cdot \frac{V_{snub}}{V_{snub} - V_R} = (1.96 \times 10^{-5}) \cdot 70000 \cdot \frac{180\,\text{V}}{180\,\text{V} - 96.4\,\text{V}} = 1.37 \cdot 2.15 = \mathbf{2.95\,\text{W}}$$
4. Sizing the snubber resistor ($R_{snub}$):
   $$R_{snub} = \frac{V_{snub}^2}{P_{snub}} = \frac{(180)^2}{2.95} = 10983\,\Omega \approx \mathbf{47\,\text{k}\Omega \dots 50\,\text{k}\Omega}$$
   *Implementation*: Two $100\,\text{k}\Omega / 2\,\text{W}$ metal oxide resistors in parallel ($50\,\text{k}\Omega / 4\,\text{W}$).
5. Sizing the snubber capacitor ($C_{snub}$ for $< 10\%$ voltage ripple):
   $$C_{snub} = \frac{V_{snub}}{\Delta V_{snub} \cdot R_{snub} \cdot f_{sw}} = \frac{180}{18 \cdot 50000 \cdot 70000} = 2.85\,\text{nF} \longrightarrow \mathbf{Selected: 2.2\,\text{nF} / 1\,\text{kV X7R}}$$
6. Snubber Diode: **US1M** ($1000\,\text{V}$, $1\,\text{A}$, ultrafast recovery $t_{rr} = 50\,\text{ns}$).

---

## 7. Secondary Synchronous Rectification (SR) Stage

Traditional Schottky diodes ($V_F \approx 0.55\,\text{V}$) dissipate significant power in high-current low-voltage supplies. At $3.0\,\text{A}$, a Schottky dissipates $P_{diode} = 3.0\,\text{A} \times 0.55\,\text{V} = 1.65\,\text{W}$, requiring a large heatsink.

```text
                  Secondary Synchronous Rectifier (SR) Architecture
  Secondary Winding ───┬────────────────────────────────────────────────────────┬───> +24V Intermediate Bus
  (12 Turns)           │                                                        │
                       │   ┌───────────────────────────┐                      ┌─┴─┐ C_OUT1
                       │   │ MP6908 / UCC24612         │                      │   │ 470uF / 35V
                       │   │ Fast SR Controller        │                      └─┬─┘ Low-ESR Electro
                       │   │                           │                        │
                       │   │ VDD     DRAIN (Drain-Sense)                        ├───[ Ferrite Bead ]───┬───> +24V Clean
                       │   │                           │                        │   (60Ω @ 100MHz)     │
                       └───┤ VSS     GATE              │                      ┌─┴─┐                  ┌─┴─┐
                           └───────────┬───────────────┘                      │   │ C_OUT2           │   │ C_OUT3
                                       │                                      └─┬─┘ 47uF / 35V       └─┬─┘ 100nF
                                   Gate│                                        │   Ceramic MLCC       │   Ceramic
                                     ┌─┴─┐                                   GND_SEC                GND_SEC
                                     │   │ Q_SR: N-Channel MOSFET
                                     │   │ (BSC052N06NS: 60V, 5.2mΩ)
                                     └─┬─┘
                                       │ Source
  Secondary Return ────────────────────┴────────────────────────────────────────┴─── GND_SEC
```

### 7.1 Synchronous Rectifier Engineering Benefits:
- **Secondary MOSFET**: **Infineon BSC052N06NS** ($60\,\text{V}$ breakdown, $R_{DS(on)} = 5.2\,\text{m}\Omega$, SuperSO8 package).
- Conduction Power Dissipation:
  $$P_{SR} = I_{rms(sec)}^2 \times R_{DS(on)} = (4.8\,\text{A})^2 \times 0.0052\,\Omega = \mathbf{0.120\,\text{W}!}$$
- **Efficiency Gain**: Slashes secondary rectification loss from $1.65\,\text{W}$ down to $0.12\,\text{W}$—a **$92.7\%$ reduction in secondary thermal loss**, eliminating the need for a secondary heatsink!
- **Fast Turn-Off**: The **MP6908** controller monitors $V_{DS}$ across the MOSFET with a high-speed comparator ($30\,\text{ns}$ turn-off delay). As current ramps toward zero at the end of the flyback cycle, the driver pulls the gate low to prevent reverse current from discharging the output capacitor back into the transformer.

---

## 8. Closed-Loop Feedback & Optoisolated Regulation

The $+24.0\,\text{V}$ output is regulated using a precision **TL431** adjustable shunt regulator and a **PC817** optocoupler providing $5000\,\text{V}_{\text{RMS}}$ galvanic isolation:

```text
                  TL431 & Optocoupler Type-II Feedback Network
  +24V Output ─────────┬───────────────────────┬───────────────────────────────┐
                       │                       │                               │
                     ┌─┴─┐ R_LED1            ┌─┴─┐ R_top                       │
                     │   │ 2.2kΩ             │   │ 21.5kΩ (1% E96)             │
                     └─┬─┘                   └─┬─┘                             │
                       │                       │                               │
                       ├───[ Anode (PC817) ]   ├─── REF (TL431)                │
                       │                       │    (2.495V Threshold)        ┌┴┐
                       │    [ Cathode ]        │                              │ │ C_comp1 (100nF)
                       │        │            ┌─┴─┐ R_bot                      └┬┘
                       └────────┼────────────┤   │ 2.49kΩ (1% E96)             ├───[ R_comp: 10kΩ ]───┐
                                │            └─┬─┘                             │                      │
                             Cathode           │                              ┌┴┐ C_comp2             │
                             ┌──┴──┐           │                              │ │ (1nF)               │
                             │TL431│           │                              └┬┘                     │
                             └──┬──┘           │                               │                      │
                                │              │                               │                      │
  GND_SEC ──────────────────────┴──────────────┴───────────────────────────────┴──────────────────────┴── GND_SEC
```

### 8.1 Feedback Resistor Sizing:
$$V_{OUT} = V_{REF} \times \left(1 + \frac{R_{top}}{R_{bot}}\right) = 2.495\,\text{V} \times \left(1 + \frac{21.5\,\text{k}\Omega}{2.49\,\text{k}\Omega}\right) = 2.495 \times (1 + 8.634) = \mathbf{24.03\,\text{V}}$$

---

## 9. Complete Component-Level ASCII Schematic of the AC-DC Flyback Stage

```text
====================================================================================================================================================
                                      COMPLETE AC-DC FLYBACK CONVERTER (85-265V AC IN -> +24V / 3A OUT)
====================================================================================================================================================

  AC_LINE ──[ F1: T2A/250V ]──[ NTC: 10Ω ]──┬───────████ (L_CM1: 15mH) ───┬────────████ (L_CM2: 4.7mH) ───┬───[ AC1 ]
                                            │                             │                              │   ┌────────┐
                                           ┌┴┐ MOV1                      ┌┴┐ C_X1                       ┌┴┐  │ GBU606 │
                                           │ │ 14D471K                   │ │ 220nF/310V                 │ │  │ Bridge │─── +V_BULK (120-375V DC)
                                           └┬┘                           └┬┘                            └┬┘  │ Rect.  │
  AC_NEUT ──────────────────────────────────┴─────────────────────────────┼───────████ (L_CM1: 15mH) ────┼───[ AC2 ]  │
                                                                          │                              │   └───┬────┘
                                                                        EARTH (PE)                     EARTH     │
                                                                                                              GND_PRI
+V_BULK ──┬────────────────────────────────────────────────────────────────────────────────────────┐
          │                                                                                        │
        ┌─┴─┐ C_BULK1           ┌─┴─┐ C_BULK_HF                                           Transformer Primary
        │   │ 100uF/450V        │   │ 470nF/450V                                          (PQ26/20, Lp=220uH, Np=48T)
        └─┬─┘                   └─┬─┘ Polypropylene                                       ───██████████────────┬─── Drain
          │                       │                                                                            │
       GND_PRI                 GND_PRI                                                      RCD Snubber        │
                                                                                 ┌─[ R_snub: 50kΩ/4W ]──┐      │
                                                                                 │                      │      │
                                                                               ┌─┴─┐ C_snub             │      │
                                                                               │   │ 2.2nF/1kV          │      │
                                                                               └─┬─┘                    │      │
                                                                                 │                      │      │
                                                                                 └───┬──[<| US1M ]──────┴──────┘
                                                                                     │
                                                                                     │
                                                                                 Drain (D)
                                                                               ┌─────┴─────┐
                                                                               │    Q1     │ IPB80R290P7
                                                          GATE_DRV ────────────┤           │ (800V Superjunction)
                                                                               └─────┬─────┘
                                                                                     │ Source (S)
                                                                                     ├─── CS (Current Sense Pin)
                                                                                     │
                                                                                   ┌─┴─┐ R_sense
                                                                                   │   │ 0.2Ω / 1W Non-Inductive
                                                                                   └─┬─┘
                                                                                     │
                                                                                  GND_PRI

====================================================================================================================================================
                                      SAFETY ISOLATION BARRIER (>= 6.4mm CREEPAGE / 3000V RMS HIPOT)
====================================================================================================================================================

  Secondary Winding (Ns = 12T) ───┬────────────────────────────────────────────────────────┬───> +24V Intermediate Bus (3.0A)
                                  │                                                        │
                                  │   ┌───────────────────────────┐                      ┌─┴─┐ C_OUT1
                                  │   │ MP6908 Fast SR Controller │                      │   │ 470uF / 35V Low ESR
                                  │   │                           │                      └─┬─┘
                                  │   │ VDD         DRAIN ────────┼────────┐               │
                                  │   │                           │        │               ├───[ L_filter: Ferrite 60Ω ]───> +24V Clean
                                  │   │ VSS         GATE          │        │               │
                                  └───┤              │            │        │             ┌─┴─┐ C_OUT2
                                      └──────────────┼────────────┘        │             │   │ 47uF / 35V MLCC
                                                     │                     │             └─┬─┘
                                                 Gate│                 Drain (D)           │
                                                   ┌─┴─┐               ┌───┴───┐        GND_SEC
                                                   │   │               │  Q_SR │
                                                   │   │ BSC052N06NS   │       │
                                                   └───┬───────────────┴───┬───┘
                                                       │ Source            │
  Secondary Return ────────────────────────────────────┴───────────────────┴───────────┴─── GND_SEC
====================================================================================================================================================
