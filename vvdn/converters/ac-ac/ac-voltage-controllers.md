# AC Voltage Controllers: Phase Angle & Integral Cycle Control Mechanics

Welcome to the **VVDN Engineering Hub Technical Dossier on AC Voltage Controllers**. AC voltage controllers (also known as AC regulators) convert a fixed-voltage, fixed-frequency AC grid supply into a variable RMS AC voltage at the identical line frequency. 

Utilizing back-to-back (anti-parallel) Silicon Controlled Rectifiers (SCRs) or TRIACs, these controllers are standard in industrial induction motor soft-starters, furnace heating systems, light dimmers, and solid-state tap changers.

---

## 1. Operating Principle & Topologies

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: SINGLE-PHASE SOLID-STATE AC VOLTAGE CONTROLLER (230V AC RMS, 16A / 3.6kW)
========================================================================================================================

    AC LINE (230V RMS, 50Hz) ──[ F1: 20A Time-Lag ]──┬──────────────────────────────────────────────────┐
                                                     │                                                  │
                                                    ┌┴┐ MOV1: 275V RMS                                  │
                                                    │ │ Littelfuse V275LA20CP                           │
                                                    └┬┘ (Clamps Spikes > 4.5kA)                         │
                                                     │                                                  │
    AC NEUTRAL (Return) ─────────────────────────────┼────────────────────────────────────────────+     │
                                                     │                                            │     │
                                                     │        +---[ OPTO-TRIAC GATE DRIVER ]---+  │     │
                                                     │        |   Fairchild MOC3052 (600V)     |  │     │
                                                     │        |   [ Pin 6: Output Main Term ]  |  │     │
                                                     │        |        │                       |  │     │
                                                     │        |     [ R_lim: 330Ω / 1W ]       |  │     │
                                                     │        |        │                       |  │     │
                                                     │        |        +-----------------------|--|--+  │
                                                     │        |        │                       |  │  |  │
                                                     │        |   [ Pin 4: Output Trigger ]    |  │  |  │
                                                     │        |        │                       |  │  |  │
                                                     │        |        +-----------------------|--|--|--+
                                                     │        |                                |  │  |  │
                                                     │        |   [ Pin 1: LED Anode (+) ]     |  │  |  │
                                                     │        |   [ Pin 2: LED Cathode (-) ]   |  │  |  │
                                                     │        +--------+--------------+--------+  │  |  │
                                                     │                 |              |           │  |  │
                                                     │              PWM_TRIG        GND_ISO       │  |  │
                                                     │             (From MCU)                     │  |  │
                                                     │                                            │  |  │
                                                 Anode (A)      T1: FORWARD THYRISTOR             │  |  │
                                                ┌────┴──────────┐ (Vishay 25TTS12: 1200V/25A)     │  |  │
                                         +----->│               │<--------------------------------+  │  │
                                         |      └────┬──────────┘ (Gate 1)                           │  │
                                         |     Cath  │                                               │  │
                                         |           +================================+              │  │
                                         |           |                                |              │  │
                                         |       Cath│          T2: REVERSE THYRISTOR |              │  │
                                         |      ┌────┴──────────┐ (Anti-Parallel SCR) │              │  │
                                         |      │               │<--------------------+--------------+  │
                                         |      └────┬──────────┘ (Gate 2)            │                 │
                                         |     Anode │                                │                 │
                                         |           │                                │                 │
                                         +-----------+--[ R_snub: 47Ω / 5W Wirewound ]+                 │
                                                     |         │                                        │
                                                     |   [ C_snub: 0.1µF / 630V Film ]                  │
                                                     |         │                                        │
                                                     +---------+                                        │
                                                     │                                                  │
                                                     +=== PHASE-CONTROLLED AC OUTPUT (V_out)            │
                                                     │    (RMS Voltage: 0V to 230V Adjustable)          │
                                                     │                                                  │
                                                    ┌┴────────────────────────────────────────────────┐ │
                                                    │ AC MOTOR / HEATER LOAD (Z_L = R + jωL)          │ │
                                                    │ - Resistance: R = 15Ω                           │ │
                                                    │ - Inductance: L = 30mH                          │ │
                                                    └┬────────────────────────────────────────────────┘ │
                                                     │                                                  │
    AC NEUTRAL (Return) ─────────────────────────────┴──────────────────────────────────────────────────┴─── AC NEUTRAL
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **AC_LINE_IN** | Input Terminal Block (L) | Fuse $F_1$ Input | 230V AC 50Hz utility input line | Time-lag ceramic fuse accommodates inrush current of inductive loads. |
| **AC_LINE_SW** | Fuse $F_1$ Output | $T_1$ Anode, $T_2$ Cathode, Snubber, MOV1 | Protected input AC rail | Direct input to the back-to-back anti-parallel SCR module. |
| **AC_CONTROLLED** | $T_1$ Cathode, $T_2$ Anode | Snubber, Load Terminal 1 | Phase-chopped AC output voltage | Waveform is sliced at firing angle $\alpha$; fundamental voltage is continuously variable. |
| **GATE_TRIG** | MOC3052 Opto-TRIAC Pin 4 | $T_1 / T_2$ Gate Terminals | Optically isolated firing pulses | Zero-crossing or random-phase triggering depending on phase-angle vs burst mode. |
| **LOAD_RETURN** | Load Terminal 2 | AC Neutral Terminal Block (N) | AC mains neutral return path | Heavy-gauge line wiring sized for 16A continuous current. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **$T_1, T_2$** | Phase-Control Thyristor Pair | Vishay Semiconductors 25TTS12 | $V_{RRM} = 1200\,\text{V}, I_{T(AV)} = 16\,\text{A}, I_{GT} = 45\,\text{mA}, V_{TM} = 1.25\,\text{V}$ | $1200\,\text{V}$ rating ensures safe margins during inductive turn-off voltage kickback. |
| **$R_{snub}, C_{snub}$**| AC Power Snubber Network | TE Connectivity / KEMET | $R = 47\,\Omega / 5\,\text{W Wirewound}, C = 0.1\,\mu\text{F} / 630\,\text{V Polypropylene}$ | Essential for inductive loads ($\cos \phi < 1$); limits $\frac{dv}{dt} < 200\,\text{V}/\mu\text{s}$ at current zero-crossing. |
| **$U_1$ (Opto)** | Random-Phase Optoisolator | ON Semiconductor MOC3052M | $V_{DRM} = 600\,\text{V}, I_{FT} = 10\,\text{mA}, V_{ISO} = 5000\,\text{V}_{RMS}$ | Non-zero-crossing bilateral triac driver allows arbitrary firing angles $\alpha \in [0^\circ, 180^\circ]$. |
| **$MOV_1$** | Line Surge Varistor | Littelfuse V275LA20CP | $V_{RMS} = 275\,\text{V}, I_{max} = 6500\,\text{A}, W_{max} = 120\,\text{J}$ | Protects thyristors and optotriac driver against lightning and grid switching transients. |


### 1.1 Switching Devices:
- **Anti-Parallel Thyristor Pair ($T_1, T_2$)**: Dominates high-power industrial systems ($> 1\,\text{kW} \dots 500\,\text{kW}$). Independent gate terminals allow asymmetric control and high $dv/dt$ immunity.
- **TRIAC (Triode for Alternating Current)**: Integrated bidirectional semiconductor switch used in low-to-medium power consumer applications ($< 2\,\text{kW}$, such as ceiling fan speed regulators and incandescent lamp dimmers).

---

## 2. Control Methodologies: Phase Angle vs. Integral Cycle

```text
                       Waveforms: Phase Angle vs. Integral Cycle
   PHASE ANGLE CONTROL:
   v_in  ^    /\        /\
         │   /  \      /  \
      0V ┼──/────\────/────\─────────────────────────────────────────────> Time
         │ /      \  /      \
         │/        \/        \
   v_out ^
         │     ┌─\       ┌─\
      0V ┼─────┴──\──────┴──\───────────────────────────────────────────> Time
         │◄-α-►│   \         \
         │ Firing   '─────────'
           Angle
   INTEGRAL CYCLE / BURST FIRING CONTROL:
   v_out ^  n = 3 Full Cycles ON (Zero Crossings Only)      m = 2 Cycles OFF
         │   /\    /\    /\
         │  /  \  /  \  /  \                                  /\    /\
      0V ┼─/────\/────\/────\────────────────────────────────/──\──/──\─> Time
         │/      \/    \/    \                              /    \/    \
         │◄───────── Ton ──────────►│◄────── Toff ────────►│
```

---

## 3. Phase Angle Control: Derivations & R-L Load Dynamics

In Phase Angle Control, gate pulses are delayed by firing angle $\alpha$ ($0 \le \alpha \le \pi$) relative to the AC line zero crossings:

### 3.1 Resistive Load ($R$):
For a purely resistive load, the current waveform exactly matches the voltage waveform:
- Conduction angle per half-cycle: $\theta_{cond} = \pi - \alpha$.
- **RMS Output Voltage ($V_{o,rms}$)**:
  $$V_{o,rms} = \sqrt{\frac{1}{\pi} \int_{\alpha}^{\pi} \left( V_m \sin \omega t \right)^2 d(\omega t)} = V_{in,rms} \cdot \sqrt{\frac{1}{\pi} \left( \pi - \alpha + \frac{\sin(2\alpha)}{2} \right)}$$
- **Output Power ($P_o$)**:
  $$P_o = \frac{V_{o,rms}^2}{R} = \frac{V_{in,rms}^2}{R} \cdot \frac{1}{\pi} \left( \pi - \alpha + \frac{\sin(2\alpha)}{2} \right)$$
- **Input Power Factor ($\text{PF}$)**:
  $$\text{PF} = \frac{P_o}{S} = \frac{V_{o,rms} \cdot I_{o,rms}}{V_{in,rms} \cdot I_{in,rms}} = \frac{V_{o,rms}}{V_{in,rms}} = \sqrt{\frac{1}{\pi} \left( \pi - \alpha + \frac{\sin(2\alpha)}{2} \right)}$$

### 3.2 Inductive Load ($R-L$ Load):
Inductive loads (such as induction motors) delay the current decay. The load impedance angle is:
$$\phi = \arctan\left(\frac{\omega L}{R}\right)$$
- When thyristor $T_1$ is fired at angle $\alpha$, current continues to flow **past the voltage zero-crossing ($\pi$)** due to stored magnetic field energy in $L$:
  $$i_o(\omega t) = \frac{V_m}{Z} \left[ \sin(\omega t - \phi) - \sin(\alpha - \phi) \cdot e^{-\frac{R}{\omega L} (\omega t - \alpha)} \right]$$
- Current terminates at the **Extinction Angle ($\beta$)**, where $i_o(\beta) = 0$:
  $$\sin(\beta - \phi) = \sin(\alpha - \phi) \cdot e^{-\frac{R}{\omega L} (\beta - \alpha)}$$
- Total conduction angle is $\gamma = \beta - \alpha$.

#### Critical Operational Rule for R-L Loads ($\alpha \ge \phi$):
If the firing angle is chosen smaller than the load impedance angle ($\alpha < \phi$):
- The conducting thyristor does not turn off before the incoming anti-parallel thyristor receives its firing pulse.
- One thyristor stays permanently on, inducing asymmetric DC saturation in the supply transformer.
- *Strict Rule*: The firing angle must satisfy:
  $$\alpha \ge \phi$$

---

## 4. Integral Cycle (Burst Firing) Control

For heating loads with large thermal time constants (e.g., electric boilers, drying ovens), switching on every half-cycle causes unnecessary line harmonics. **Integral Cycle Control** delivers blocks of complete sinusoidal AC cycles:

- Number of conduction cycles: $n$
- Number of idle cycles: $m$
- Control Period: $T_c = (n + m) \cdot T_{line}$
- Duty Cycle: $k = \frac{n}{n + m}$

### 4.1 Formulations:
- **RMS Output Voltage**:
  $$V_{o,rms} = V_{in,rms} \cdot \sqrt{k} = V_{in,rms} \cdot \sqrt{\frac{n}{n + m}}$$
- **Power Delivered**:
  $$P = k \cdot P_{max} = \frac{n}{n + m} \cdot \frac{V_{in,rms}^2}{R}$$
- **Input Power Factor**:
  $$\text{PF} = \sqrt{k} = \sqrt{\frac{n}{n + m}}$$

### 4.2 Major Engineering Advantage:
Thyristors are triggered and commutated exclusively at **zero line-voltage crossings ($V = 0$)**:
- $dv/dt = 0$ at turn-on $\implies$ **Virtually zero radio frequency interference (RFI) / EMI**.
- No acoustic switching noise or line notch distortions.

---

## 5. Hardware Implementation: Snubbers & Motor Soft-Starters

```text
               Three-Phase Soft-Starter for Induction Motor
      Line L1 ───┬───[ T1 / T2 ]───┬─── Motor Phase U
                 │                 │
                 ├──[ Rs ]──[ Cs ]─┤ (RC Snubber Network)
                 │                 │
      Line L2 ───┴───[ T3 / T4 ]───┴─── Motor Phase V
      Line L3 ───────[ T5 / T6 ]─────── Motor Phase W
```

### 5.1 Induction Motor Soft-Starting Principle:
Direct-on-line (DOL) starting draws $6 \dots 8 \times$ rated full-load current ($I_{FLA}$) and induces severe mechanical shock torque.
1. The soft-starter ramps firing angle $\alpha$ smoothly from $120^\circ$ down to $0^\circ$ over $3 \dots 30\,\text{seconds}$.
2. RMS voltage ramps smoothly from $30\% \cdot V_{line}$ to $100\% \cdot V_{line}$.
3. Inrush current is restricted to $2.0 \dots 3.0 \times I_{FLA}$, preventing substation voltage sags.
4. Once full speed is reached ($\alpha = 0^\circ$), an internal **Bypass Contactor** closes across the SCRs, eliminating thyristor conduction heat losses during normal operation.

### 5.2 Critical Snubber Protection:
- **$dv/dt$ Snubber ($R_s - C_s$)**: Prevents rapid line transient spikes from capacitively charging the thyristor gate and causing false turn-on ($dv/dt > 1000\,\text{V}/\mu\text{s}$).
  $$C_s \approx \frac{I_{RMS}}{V_{RMS}} \cdot 10^{-6}, \quad R_s = 2 \cdot \zeta \sqrt{\frac{L_{source}}{C_s}}$$
- **$di/dt$ Inductor**: Prevents localized silicon hot-spot destruction during the first microsecond of SCR turn-on ($di/dt > 200\,\text{A}/\mu\text{s}$).
