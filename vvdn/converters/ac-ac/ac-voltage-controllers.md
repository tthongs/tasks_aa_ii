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
| **AC_LINE_IN** | Input Terminal Block (L) | Fuse F_1 Input | 230V AC 50Hz utility input line | Time-lag ceramic fuse accommodates inrush current of inductive loads. |
| **AC_LINE_SW** | Fuse F_1 Output | T_1 Anode, T_2 Cathode, Snubber, MOV1 | Protected input AC rail | Direct input to the back-to-back anti-parallel SCR module. |
| **AC_CONTROLLED** | T_1 Cathode, T_2 Anode | Snubber, Load Terminal 1 | Phase-chopped AC output voltage | Waveform is sliced at firing angle α; fundamental voltage is continuously variable. |
| **GATE_TRIG** | MOC3052 Opto-TRIAC Pin 4 | T_1 / T_2 Gate Terminals | Optically isolated firing pulses | Zero-crossing or random-phase triggering depending on phase-angle vs burst mode. |
| **LOAD_RETURN** | Load Terminal 2 | AC Neutral Terminal Block (N) | AC mains neutral return path | Heavy-gauge line wiring sized for 16A continuous current. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **T_1, T_2** | Phase-Control Thyristor Pair | Vishay Semiconductors 25TTS12 | V_RRM = 1200 V, I_T(AV) = 16 A, I_GT = 45 mA, V_TM = 1.25 V | 1200 V rating ensures safe margins during inductive turn-off voltage kickback. |
| **R_snub, C_snub**| AC Power Snubber Network | TE Connectivity / KEMET | R = 47 Ω / 5 W Wirewound, C = 0.1 µF / 630 V Polypropylene | Essential for inductive loads (cos φ < 1); limits dv / dt < 200 V/µs at current zero-crossing. |
| **U_1 (Opto)** | Random-Phase Optoisolator | ON Semiconductor MOC3052M | V_DRM = 600 V, I_FT = 10 mA, V_ISO = 5000 V_RMS | Non-zero-crossing bilateral triac driver allows arbitrary firing angles α in [0°, 180°]. |
| **MOV_1** | Line Surge Varistor | Littelfuse V275LA20CP | V_RMS = 275 V, I_max = 6500 A, W_max = 120 J | Protects thyristors and optotriac driver against lightning and grid switching transients. |


### 1.1 Switching Devices:
- **Anti-Parallel Thyristor Pair (T_1, T_2)**: Dominates high-power industrial systems (> 1 kW ... 500 kW). Independent gate terminals allow asymmetric control and high dv/dt immunity.
- **TRIAC (Triode for Alternating Current)**: Integrated bidirectional semiconductor switch used in low-to-medium power consumer applications (< 2 kW, such as ceiling fan speed regulators and incandescent lamp dimmers).

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

In Phase Angle Control, gate pulses are delayed by firing angle α (0 <= α <= π) relative to the AC line zero crossings:

### 3.1 Resistive Load (R):
For a purely resistive load, the current waveform exactly matches the voltage waveform:
- Conduction angle per half-cycle: θ_cond = π - α.
- **RMS Output Voltage (V_o,rms)**:
  ```
V_o,rms = sqrt(1 / π Integral(α to π) ( V_m sin ω t )^2 d(ω t)) = V_in,rms * sqrt(1 / π ( π - α + sin(2α) / 2 ))
```
- **Output Power (P_o)**:
  ```
P_o = V_o,rms^2 / R = V_in,rms^2 / R * 1 / π ( π - α + sin(2α) / 2 )
```
- **Input Power Factor (PF)**:
  ```
PF = P_o / S = (V_o,rms * I_o,rms) / (V_in,rms * I_in,rms) = V_o,rms / V_in,rms = sqrt(1 / π ( π - α + sin(2α) / 2 ))
```

### 3.2 Inductive Load (R-L Load):
Inductive loads (such as induction motors) delay the current decay. The load impedance angle is:
```
φ = arctan((ω L) / R)
```
- When thyristor T_1 is fired at angle α, current continues to flow **past the voltage zero-crossing (π)** due to stored magnetic field energy in L:
  ```
i_o(ω t) = V_m / Z [ sin(ω t - φ) - sin(α - φ) * e^-R / (ω L) (ω t - α) ]
```
- Current terminates at the **Extinction Angle (β)**, where i_o(β) = 0:
  ```
sin(β - φ) = sin(α - φ) * e^-R / (ω L) (β - α)
```
- Total conduction angle is γ = β - α.

#### Critical Operational Rule for R-L Loads (α >= φ):
If the firing angle is chosen smaller than the load impedance angle (α < φ):
- The conducting thyristor does not turn off before the incoming anti-parallel thyristor receives its firing pulse.
- One thyristor stays permanently on, inducing asymmetric DC saturation in the supply transformer.
- *Strict Rule*: The firing angle must satisfy:
  ```
α >= φ
```

---

## 4. Integral Cycle (Burst Firing) Control

For heating loads with large thermal time constants (e.g., electric boilers, drying ovens), switching on every half-cycle causes unnecessary line harmonics. **Integral Cycle Control** delivers blocks of complete sinusoidal AC cycles:

- Number of conduction cycles: n
- Number of idle cycles: m
- Control Period: T_c = (n + m) * T_line
- Duty Cycle: k = n / (n + m)

### 4.1 Formulations:
- **RMS Output Voltage**:
  ```
V_o,rms = V_in,rms * sqrt(k) = V_in,rms * sqrt(n / (n + m))
```
- **Power Delivered**:
  ```
P = k * P_max = n / (n + m) * V_in,rms^2 / R
```
- **Input Power Factor**:
  ```
PF = sqrt(k) = sqrt(n / (n + m))
```

### 4.2 Major Engineering Advantage:
Thyristors are triggered and commutated exclusively at **zero line-voltage crossings (V = 0)**:
- dv/dt = 0 at turn-on => **Virtually zero radio frequency interference (RFI) / EMI**.
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
Direct-on-line (DOL) starting draws 6 ... 8 * rated full-load current (I_FLA) and induces severe mechanical shock torque.
1. The soft-starter ramps firing angle α smoothly from 120° down to 0° over 3 ... 30 seconds.
2. RMS voltage ramps smoothly from 30\% * V_line to 100\% * V_line.
3. Inrush current is restricted to 2.0 ... 3.0 * I_FLA, preventing substation voltage sags.
4. Once full speed is reached (α = 0°), an internal **Bypass Contactor** closes across the SCRs, eliminating thyristor conduction heat losses during normal operation.

### 5.2 Critical Snubber Protection:
- **dv/dt Snubber (R_s - C_s)**: Prevents rapid line transient spikes from capacitively charging the thyristor gate and causing false turn-on (dv/dt > 1000 V/µs).
  ```
C_s ≈ I_RMS / V_RMS * 10^-6, R_s = 2 * ζ sqrt(L_source / C_s)
```
- **di/dt Inductor**: Prevents localized silicon hot-spot destruction during the first microsecond of SCR turn-on (di/dt > 200 A/µs).
