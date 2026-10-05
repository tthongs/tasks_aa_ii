# Three-Phase DC-AC Inverters: 6-Switch VSI, THIPWM & Space Vector PWM (SVPWM)

Welcome to the **VVDN Engineering Hub Technical Dossier on Three-Phase DC-AC Inverters**. The three-phase Voltage Source Inverter (VSI) is the undisputed powerhouse of modern industrial motor drives (Variable Frequency Drives - VFD), Electric Vehicle (EV) traction inverters, high-power grid-connected solar farms, and wind power generation systems.

This guide provides an exhaustive mathematical and hardware analysis covering the two-level 6-switch VSI topology, six-step conduction modes, Third-Harmonic Injection PWM (THIPWM), and a masterclass deep dive into **Space Vector Pulse-Width Modulation (SVPWM)**.

---

## 1. Operating Principle & 6-Switch VSI Topology

The three-phase two-level VSI comprises three identical half-bridge phase legs (Leg U, Leg V, Leg W) connected across a common stiff DC link:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: THREE-PHASE TWO-LEVEL VOLTAGE SOURCE INVERTER (VSI) (800V DC -> 400V 3-PHASE, 50kW)
========================================================================================================================

    +VDC BUS (+800V Traction Battery / DC Link) ────────────────────────────────────────────────────────┐
        │                                                                                               │
       ┌┴─────────────────┐           PHASE LEG U                     PHASE LEG V           PHASE LEG W │
       │ C_LINK_BULK      │           Collector (C)                   Collector (C)         Collector(C)│
       │ 500µF / 900V     │          ┌────┴──────────┐               ┌────┴──────────┐     ┌────┴──────┐│
       │ Low-ESR Film     │          │ Q1: HS LEG U  │               │ Q3: HS LEG V  │     │ Q5: HS W  ││
       │ (Laminated Bus)  │   +----->│ Wolfspeed SiC │        +----->│ Wolfspeed SiC │  +->│ SiC MOSFET││
       └┬─────────────────┘   | Gate │ CAB016M12FM3  │        | Gate │ CAB016M12FM3  │  |  │ 1200V/16mΩ││
        │                     |      └────┬──────────┘        |      └────┬──────────┘  |  └────┬──────┘│
        │                     |    Emitter│                   |    Emitter│             |   Emit│       │
        │   ISOLATED DRIVER   |           │                   |           │             |       │       │
        │   UCC21750 (DESAT)  |           +=== PHASE U (U)    |           +=== PHASE V  |       +=== PH W
        │   OUT_U_HS ---------+           |    (0V to +800V)  |           |    (0V-800V)|       |    (0V-800V)
        │                                 |                   |           |             |       |       │
        │                             Collect(C)  +-----------+       Collect(C)        |   Collect(C)  │
        │                            ┌────┴───────┴──┐               ┌────┴──────────┐  |  ┌────┴──────┐│
        │                            │ Q2: LS LEG U  │               │ Q4: LS LEG V  │  |  │ Q6: LS W  ││
        │                     +----->│ CAB016M12FM3  │        +----->│ CAB016M12FM3  │  +->│ 1200V/16mΩ││
        │                     | Gate └────┬──────────┘        | Gate └────┬──────────┘     └────┬──────┘│
        │   OUT_U_LS ---------+    Emitter│             OUT_V-+    Emitter│             OUT_W--+Emit│   │
        │   (Low-Side Leg U)              │             (Leg V Drivers)   │             (Leg W Drivers) │
        │                                 │                               │                     │       │
    GND_DC ───────────────────────────────┴───────────────────────────────┴─────────────────────┴───────┴─── GND_DC
                                          │                               │                     │
                                          │     INLINE HALL SENSORS       │                     │
                                          ├──[ LEM CAB-500: Phase U ]─────┼─────────────────────┼───> TERMINAL U (Phase A)
                                          │  (Analog ADC -> TMS320F28379D)│                     │
                                          │                               ├──[ LEM CAB-500 ]────┼───> TERMINAL V (Phase B)
                                          │                               │  (Phase V Current)  │
                                          │                               │                     ├───> TERMINAL W (Phase C)
                                          │                               │                     │     │
                                          │  +----------------------------+---------------------+     │
                                          │  |   3-PHASE LC OUTPUT SINE FILTER (OPTIONAL FOR GRID-TIE) │
                                          │  |   - 3x Lf: 250µH / 100A Powder Core Chokes              │
                                          │  |   - 3x Cf: 22µF / 480VAC Delta-Connected Film Bank      │
                                          │  +----------------------------+---------------------+     │
                                          │                               │                     │     │
                                          +───────────────────────────────┼─────────────────────┼─────+
                                                                          │                     │
                                                                 +========+=====================+=======+
                                                                 |  3-PHASE PERMANENT MAGNET SYNCHRONOUS|
                                                                 |  MOTOR (PMSM) / INDUCTION MACHINE    |
                                                                 +======================================+
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VDC_BUS** | EV Battery / DC Busbar | C_link (+), Q_1, Q_3, Q_5 Collectors/Drains | Main 800V DC high-voltage rail | Symmetrical planar laminated copper busbar minimizes stray parasitic inductance (L_stray < 15 nH). |
| **PHASE_U (SW_U)** | Q_1 Emitter, Q_2 Collector | Current Transducer CT_U, Motor Terminal U | Phase U high-power switching node | Swings between 0 V and +800 V at PWM carrier frequency f_c = 16 kHz ... 20 kHz. |
| **PHASE_V (SW_V)** | Q_3 Emitter, Q_4 Collector | Current Transducer CT_V, Motor Terminal V | Phase V high-power switching node | Displaced 120° electrically from Phase U; high dv/dt edge rates (> 20 V/ns). |
| **PHASE_W (SW_W)** | Q_5 Emitter, Q_6 Collector | Current Transducer CT_W, Motor Terminal W | Phase W high-power switching node | Displaced 240° electrically from Phase U; monitored by inline current transducer. |
| **I_U / I_V / I_W** | LEM CAB-500 Analog Outputs | DSP ADC Inputs (ADCIN_A0, A1, A2) | Instantaneous phase current feedback | Closed-loop Field Oriented Control (FOC / Clarke-Park transforms) requires < 1 µs sampling latency. |
| **GND_DC** | Q_2, Q_4, Q_6 Emitters, C_link (-) | DC negative return busbar | High-current power return | Continuous return busbar; isolated from 12V automotive control chassis ground. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1 ... Q_6** | 3-Phase SiC Power Module | Wolfspeed CAB016M12FM3 | V_DS = 1200 V, I_D = 150 A, R_DS(on) = 16 mΩ | Half-bridge SiC module; ultra-fast body diode and low switching losses enable 98.8\% peak inverter efficiency. |
| **C_link** | DC Link Film Capacitor | KEMET C4AKJBW5500A3MJ | 500 µF, 900 V_DC, ESR = 1.2 mΩ, I_ripple = 85 A_rms | Handles severe triangular RMS ripple current drawn by 3-phase Space Vector PWM modulation. |
| **U_drv1-6** | Isolated Smart Gate Drivers | TI UCC21750DW | 5.7 kV_RMS isolation, 10 A sink/source, integrated DESAT & AMC | Fast Overcurrent Desaturation (DESAT) shutdown (< 200 ns) protects SiC switches during phase short-circuits. |
| **CT_U,V,W** | Automotive Hall Current Sensors | LEM CAB 500-C/SP5 | ± 500 A primary range, 0.5\% accuracy, CAN / analog output | High galvanic isolation; measures DC and AC phase currents without inserting series resistance into motor cables. |
| **U_ctrl** | Central Motor Control MCU | TI TMS320F28379D | Dual-Core 32-bit floating-point C28x DSP, Trigonometric Math Unit | Computes Space Vector PWM (SVPWM) switching vectors V_0 ... V_7 in real-time every 50 µs. |


### 1.1 Switching Logic & Pole Voltages:
Each leg switch state can be defined by a binary variable S_x in {0, 1} (where x in {u, v, w}):
- S_x = 1: High-side switch Q_high is ON; leg terminal voltage v_xN = V_dc.
- S_x = 0: Low-side switch Q_low is ON; leg terminal voltage v_xN = 0 V.

---

## 2. Six-Step (180° & 120°) Conduction Modes

```text
                     180-Degree Conduction Mode Phase Voltages
   Switch States:
   Q1 (Phase U) ───────┐                       ┌───────────────────┐
                       └───────────────────────┘                   └───────────────────
   Q3 (Phase V) ───────────────┐                       ┌───────────────────┐
                               └───────────────────────┘                   └───────────
   Q5 (Phase W) ───────────────────────┐                       ┌───────────────────┐
                ───────────────────────┘                       └───────────────────┘
   v_UN (Pole)  +Vdc ──┐                       ┌───────────────────┐
                  0V ──┴───────────────────────┴───────────────────┴───────────────────
   v_UV (Line)  +Vdc ──────┐               ┌───
                  0V ──────┴───────┐       │
                -Vdc ──────────────┴───────┴───────────────────────────────────────────
                       │◄─ 60° ─►│ Six-Step Output (Severe 5th and 7th Harmonics!)
```

- **180° Conduction Mode**: Exactly 3 switches are ON at any given instant. While generating maximum fundamental power, the output is a stepped six-step waveform with large low-order harmonics (5th, 7th, 11th), causing severe motor torque ripple and thermal losses.
- **Modern Drive Requirement**: Variable frequency drives (VFD) and EV traction systems require high-frequency PWM to eliminate low-order harmonics.

---

## 3. Sinusoidal PWM vs. Third-Harmonic Injection (THIPWM)

### 3.1 Standard SPWM Limitation:
In standard SPWM, three sinusoidal reference waves shifted by 120° are compared against a common triangular carrier:
- Linear modulation limit: m_a <= 1.0.
- The maximum fundamental peak phase-to-neutral voltage is V_pk_ph = V_dc / 2.
- The maximum RMS line-to-line voltage is:
  ```
V_LL,rms = (sqrt(3) * V_pk_ph) / sqrt(2) = (sqrt(3) * V_dc) / (2 sqrt(2)) ≈ 0.612 * V_dc
```
- *Problem*: Almost 39\% of the available DC-bus voltage capability is wasted!

### 3.2 Third-Harmonic Injection (THIPWM):
By injecting a third harmonic with an amplitude of 1 / 6 of the fundamental into each phase reference:
```
v_ref,u(t) = V_pk_1 sin(ω t) + 1 / 6 V_pk_1 sin(3ω t)
```

```text
                  Third-Harmonic "Saddle" Waveform & DC Expansion
   v_ref ^
         │        Saddle Shape (Peak Voltage Reduced by 15.5%!)
         │           .-'""'-.       .-'""'-.
         │          /        \     /        \
      0V ┼─────────/──────────\───/──────────\──────────────────────────> Time
         │                     '-'            '-'
         │◄──────────────── Third-Harmonic Injected ────────────────►│
```
- The third harmonic flattens the crest of the sinusoidal reference wave ("saddle shape"), preventing the peak from touching the triangular carrier limits.
- Because the three phases are identical, the third-harmonic components cancel out completely in the line-to-line differential voltages (v_uv = v_u - v_v).
- **The Result**: Maximum modulation index increases from m_a = 1.0 to m_a = 2 / sqrt(3) ≈ 1.155 without entering non-linear overmodulation, boosting AC output voltage by **15.5\%**!

---

## 4. Space Vector PWM (SVPWM) Masterclass

**Space Vector PWM (SVPWM)** is the mathematical and industrial pinnacle of inverter modulation, providing optimal harmonic cancellation and maximizing DC bus utilization.

### 4.1 Clarke Transformation to the Stationary α-β Frame:
The three instantaneous phase voltages are mapped onto a two-dimensional orthogonal complex plane:
```
begin{bmatrix} v_α \\ v_β end{bmatrix} = 2 / 3 begin{bmatrix} 1 & -1 / 2 & -1 / 2 \\ 0 & sqrt(3) / 2 & -sqrt(3) / 2 end{bmatrix} begin{bmatrix} v_u \\ v_v \\ v_w end{bmatrix}
```

### 4.2 The Eight Voltage Space Vectors:
With 3 switch legs and 2 states per leg (S_u, S_v, S_w), there are 2^3 = 8 possible switching combinations:

```text
                         The SVPWM Hexagon and 8 Space Vectors
                                     +V_beta ^
                                             │
                             V3 (010)        │        V2 (110)
                                 \           │           /
                                  \   SEC 2  │  SEC 1   /
                                   \         │         /
                                    \        │  V_ref /  Angle θ
                                     \       │   .---'
                                      \      │  /   /
                       V4 (011) ───────\─────┼─────/─────── V1 (100) ───> +V_alpha
                                       /     │     \        Magnitude = (2/3)*Vdc
                                      /      │      \
                                     / SEC 3 │ SEC 6 \
                                    /        │        \
                                   /  SEC 4  │  SEC 5  \
                                 /           │           \
                             V5 (001)        │        V6 (101)
                                             │
                              Zero Vectors: V0 (000) & V7 (111) at origin
```

1. **Six Active Vectors (V_1 ... V_6)**:
   Each vector has a magnitude of 2 / 3 V_dc and is separated from its neighbors by 60°, forming the vertices of a regular hexagon.
   - V_1(100): θ = 0°
   - V_2(110): θ = 60°
   - V_3(010): θ = 120°
   - V_4(011): θ = 180°
   - V_5(001): θ = 240°
   - V_6(101): θ = 300°
2. **Two Zero Vectors (V_0, V_7)**:
   - V_0(000): All three low-side switches are ON; phase terminals shorted to GND.
   - V_7(111): All three high-side switches are ON; phase terminals shorted to +V_dc.
   - Magnitude is identically **0 Volts**.

---

## 5. Dwell Time Formulations & Symmetric Switching

To synthesize an arbitrary rotating reference voltage vector vec{V}_ref at angle θ inside **Sector 1** (0 <= θ <= 60°), the inverter time-averages the two adjacent active vectors (V_1, V_2) and the zero vectors (V_0, V_7) over switching period T_s:

```
vec{V}_ref * T_s = vec{V}_1 * T_1 + vec{V}_2 * T_2 + vec{V}_z * T_0
```

### 5.1 Dwell Time Equations for Sector 1:
```
T_1 = sqrt(3) * T_s * |vec{V}_ref| / V_dc * sin(π / 3 - θ)
```
```
T_2 = sqrt(3) * T_s * |vec{V}_ref| / V_dc * sin(θ)
```
```
T_0 = T_s - T_1 - T_2
```
*(Where T_0 is divided equally between zero states V_0 and V_7: T_V0 = T_V7 = T_0 / 2.)*

---

### 5.2 Symmetric 7-Segment Switching Sequence:
To minimize semiconductor switching losses and generate zero-crossing odd harmonic cancellation, the switching sequence in Sector 1 is structured symmetrically:

```text
                  Symmetric 7-Segment Switching Pattern (Sector 1)
   State: │  V0 (000)  │  V1 (100)  │  V2 (110)  │  V7 (111)  │  V2 (110)  │  V1 (100)  │  V0 (000)  │
          │◄─ T0/4 ───►│◄─── T1/2 ─►│◄─── T2/2 ─►│◄─── T0/2 ─►│◄─── T2/2 ─►│◄─── T1/2 ─►│◄─ T0/4 ───►│
   Leg U: ─────────────────┌────────────────────────────────────────────────────────┐─────────────────
   (Su)   ─────────────────┘                                                        └─────────────────
   Leg V: ──────────────────────────────┌──────────────────────────────┐──────────────────────────────
   (Sv)   ──────────────────────────────┘                              └──────────────────────────────
   Leg W: ───────────────────────────────────────────┌────┐───────────────────────────────────────────
   (Sw)   ───────────────────────────────────────────┘    └───────────────────────────────────────────
          │◄──────────────────────────────── Switching Period Ts ────────────────────────────────────►│
```

### Key Engineering Features of 7-Segment SVPWM:
1. **Single-Leg Toggling**: At every state transition, **only one phase leg changes state** (0 -> 1 or 1 -> 0), minimizing switching losses.
2. **Maximum Linear AC Output**: The maximum radius of the reference vector corresponds to the inscribed circle of the hexagon:
   ```
|vec{V}_ref,max| = 2 / 3 V_dc * cos(30°) = V_dc / sqrt(3) ≈ 0.577 * V_dc
```
   The resulting maximum fundamental line-to-line RMS voltage is:
   ```
V_LL,rms = (sqrt(3) * |vec{V}_ref,max|) / sqrt(2) = V_dc / sqrt(2) ≈ 0.707 * V_dc
```
   **SVPWM achieves a full 15.5\% increase in AC output voltage over standard sinusoidal SPWM (0.707 vs. 0.612)!**
3. **Harmonic Cancellation**: Center-aligned symmetric PWM eliminates all even harmonics and significantly reduces total harmonic distortion (THD).
