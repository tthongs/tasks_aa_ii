# EVSE Hardware Schematics, Component Selection & Electrical Interfacing

This document provides a detailed circuit-level reference for the **Low Voltage Controller Board Schematics, Component Selection, Galvanic Isolation Barriers, EMC Protection, and Hardware Bring-Up**.

---

## 1. Schematic Sub-Circuits & Analog Signal Chains

Below are the detailed component-level schematic implementations for the core analog and digital circuits on the low-voltage controller board:

### 1.1 Control Pilot (CP) Bipolar $\pm 12\,\text{V}$ Driver & Peak Sampler

```text
                             +12V Supply Rail
                                    │
                                 ┌──┴──┐
       MCU 1 kHz PWM ──[ R_in ]──┤ +   │
       (0 to 3.3V)               │     ├───────[ R1: 1.0 kΩ, 1%, 0.5W ]──────┬────► CP Terminal
       MCU Bias DAC  ──[ R_fb ]──┤ -   │                                     │     (To Vehicle)
                                 └──┬──┘                                   ──┴──
                                    │                                      ▲ ▼ Dual Bi-directional TVS
                             -12V Supply Rail                              ──┬── (PESD12VS1UL - ±15 kV ESD)
                                                                             │
                                                                            GND
                                                                             │
                                   ┌─────────────────────────────────────────┘
                                   │
                                   ├──[ R_div1: 10 kΩ, 0.1% ]──┐
                                   │                           │
                                   │                         ┌─┴─┐
                                   │                         │   │ (ADC Buffer / Peak Detector)
                                   │                         └─┬─┘
                                   │                           │
                                   └──[ R_div2: 2.2 kΩ, 0.1% ]─┴─────► To MCU Precision ADC Channel
```

#### Circuit Theory & Component Selection:
1. **High-Voltage Rail-to-Rail Op-Amp (e.g., TI OPA2171 / Microchip MCP6022)**:
   - Operating across $+12\,\text{V}$ and $-12\,\text{V}$ supply rails ($24\,\text{V}$ total span).
   - High slew rate ($> 5\,\text{V}/\mu\text{s}$) to preserve sharp $< 2\,\mu\text{s}$ rise/fall edges on the $1.0\,\text{kHz}$ square wave.
   - High output current drive ($> 50\,\text{mA}$) to charge the parasitic capacitance of long ($> 5\text{--}7\,\text{meter}$) vehicle charging cables without rounding pulse corners.
2. **Output Resistor ($R_1$)**:
   - Exactly $1.00\,\text{k}\Omega$ with $1\%$ tolerance, rated for at least $0.5\,\text{W}$ to survive accidental short-circuits to chassis or ground.
3. **Synchronous Peak Sampling vs. Analog Peak Detector**:
   - **Method A (Digital Timer Triggered)**: The MCU timer generating the PWM triggers the ADC directly at the $50\%$ center point of the positive HIGH phase and the $50\%$ center point of the negative LOW phase. This eliminates analog diode drops and capacitor discharge droop.
   - **Method B (Hardware Peak Detector)**: A high-speed diode, low-leakage capacitor ($10\,\text{nF}$ C0G/NPO), and bleed resistor ($1\,\text{M}\Omega$) holding the DC peak voltage for slow MCU ADC polling.

---

### 1.2 Proximity Pilot (PP) Cable Detection Circuit

```text
                   +3.3V Analog Vref
                          │
                       [ R_pu: 330 Ω, 0.1% ]
                          │
   PP Terminal ───────────┼──────────────────[ R_filter: 1.0 kΩ ]───┬────► MCU ADC (PP Channel)
   (Type 2 Socket)        │                                         │
                        ──┴──                                     ──┴──
                        ▲ ▼ TVS Diode                             ──┬── C_filter: 100 nF (Noise rejection)
                        ──┬── (ESD5V0)                              │
                          │                                        GND
                         GND
```

#### Voltage Divider Equations at the MCU ADC Pin:
With $V_{REF} = 3.30\,\text{V}$ and $R_{PU} = 330\,\Omega$:
$$V_{ADC} = 3.30\,\text{V} \times \frac{R_c}{330\,\Omega + R_c}$$

- **13 A Cable ($R_c = 1500\,\Omega$)**: $V_{ADC} = 3.30 \times \frac{1500}{330 + 1500} = \mathbf{2.70\,\text{V}}$
- **20 A Cable ($R_c = 680\,\Omega$)**: $V_{ADC} = 3.30 \times \frac{680}{330 + 680} = \mathbf{2.22\,\text{V}}$
- **32 A Cable ($R_c = 220\,\Omega$)**: $V_{ADC} = 3.30 \times \frac{220}{330 + 220} = \mathbf{1.32\,\text{V}}$
- **63 A Cable ($R_c = 100\,\Omega$)**: $V_{ADC} = 3.30 \times \frac{100}{330 + 100} = \mathbf{0.77\,\text{V}}$
- **Cable Unplugged ($R_c = \infty$)**: $V_{ADC} = \mathbf{3.30\,\text{V}}$

---

### 1.3 Contactor Coil Driver with High-Efficiency Economizer

```text
                  +12V Aux Rail
                        │
                  ┌─────┴─────┐
                  │ Contactor │
                  │ Coil (12V)│
                  └─────┬─────┘
                        │
                        ├───────────────────┐
                        │                   │
                        │                 ┌─┴─┐
                        │                 │   │ Freewheeling Fast Diode (ES1J: 1A, 600V)
                        │                 └─┬─┘
                        │                   │
                        │                 ──┴── Zener / TVS Clamp (18V, SMAJ18A)
                        │                 ──┬── (Allows rapid magnetic field collapse)
                        │                   │
                        ├───────────────────┘
                        │
                      ──┴── Drain
       MCU PWM ──[Rg]─┤ NMOS (AO3400 / Si2302: 30V, 5.8A, Rds = 28mΩ)
                      ──┬── Source
                        │
                       GND
```

#### Why the TVS Clamp in Series with the Freewheeling Diode is Critical:
- A standard freewheeling diode recirculates coil current for a prolonged time ($> 50\text{--}100\,\text{ms}$), delaying contact opening.
- During a high-current short-circuit or $6\,\text{mA}$ DC residual fault, contacts must open in **$< 10\,\text{ms}$** to extinguish the arc before catastrophic damage.
- Placing an $18\,\text{V}$ TVS clamp in series with the diode forces the coil energy to dissipate across a higher voltage drop ($V_{clamp} = 18\,\text{V} + 0.7\,\text{V} = 18.7\,\text{V}$), collapsing the magnetic field and snapping the contactor open in **$< 8.5\,\text{ms}$**.

---

### 1.4 Motorized Cable Lock H-Bridge Driver

```text
                    +12V Supply Rail
                           │
                     ┌─────┴─────┐
                     │  DRV8871  │ (Integrated 3.6A H-Bridge with current limiting)
                     │ H-Bridge  │
  MCU Lock GPIO ────►│ IN1       │
  MCU Unlock GPIO ──►│ IN2   OUT1├───────[ Connector Lock DC Motor ]
                     │       OUT2├───────┘
                     │    ILIM   │
                     └─────┬─────┘
                           │
                          [R_ilim: 24 kΩ] (Clamps peak stall current to 1.5A)
                           │
                          GND
```

- When the plug is fully inserted, the MCU asserts `IN1=HIGH, IN2=LOW` for $300\,\text{ms}$ to drive the locking pin forward.
- If the pin stalls against an obstruction, the internal current limit trips safely without blowing fuses or overheating the gearmotor.
- Position microswitches on the actuator provide direct digital confirmation to MCU GPIO inputs.

---

## 2. Galvanic Isolation, Creepage & Clearance (IEC 60664-1 / IEC 61851-1)

To ensure user safety when handling charging plugs in wet outdoor conditions, strict physical isolation boundaries must be enforced across the printed circuit board:

```text
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
 ▒  HIGH VOLTAGE DOMAIN (230V / 400V AC Grid)                                         ▒
 ▒  L1, L2, L3, Neutral, Contactor High-Power Terminals                               ▒
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    │                                                                               │
    │◄─────────────── REINFORCED ISOLATION BARRIER (>= 6.3 to 8.0 mm) ─────────────►│
    │                                                                               │
    │  [Optical Isolation]          [Magnetic Isolation]      [Opto-Gate Drivers]   │
    │  PC817 / FOD817               Pulse Transformers        Silicon Labs Si823x   │
    │                                                                               │
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
 ▒  SELV CONTROLLER DOMAIN (+12V, +5V, +3.3V, -12V)                                   ▒
 ▒  MCU, IoT SoM, CP / PP Pins, RFID Reader, User Touchpoints                         ▒
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
```

### 2.1 Isolation Design Parameters

| Parameter | Standard Rule | Value for $400\,\text{V}$ AC RMS Grid | Design Implementation |
| :--- | :--- | :--- | :--- |
| **Clearance** | Line-of-sight distance through air | $\ge 4.0\text{--}5.5\,\text{mm}$ | Physical component spacing and routing keep-out zones. |
| **Creepage Distance** | Surface path distance over PCB FR4 | $\ge 6.3\text{--}8.0\,\text{mm}$ (Pollution Degree 2, Material Group IIIa) | Routed isolation slots (air routing cutouts) under optocouplers. |
| **Dielectric Withstand** | Hi-Pot electrical test voltage | $3.75\,\text{kV} \text{ AC for } 60\,\text{seconds}$ | Factory 100% production line isolation test. |
| **Touch Current** | Maximum allowable leakage to ground | $< 0.25\,\text{mA}$ | High-impedance isolation between SELV common and chassis. |

---

## 3. EMC, Surge & Transient Protection (IEC 61000-4-x)

EVSEs are connected permanently to the building's electrical service entrance and are exposed to external lightning strikes, inductive motor switching spikes, and electrostatic discharge from human users.

```text
       AC Mains Line In (L1..L3)
                │
                ├───[ Gas Discharge Tube (GDT: 600V, 10kA) ]───┐
                │                                              │
                ├───[ Metal Oxide Varistor (MOV: 14D471K) ]────┼───► Earth Ground (PE)
                │                                              │
                ├───[ Differential Common-Mode Choke ]─────────┘
                │
                └───► Main Contactor & Internal SMPS
```

### 3.1 Transient Protection Matrix

| Threat Category | Applied Standard | Test Severity Level | Hardware Protection Solution |
| :--- | :--- | :--- | :--- |
| **Lightning Surge** | IEC 61000-4-5 | $\pm 4.0\,\text{kV}$ (Common Mode), $\pm 2.0\,\text{kV}$ (Diff) | Coordinated GDT + MOV hybrid network at AC mains inlet. |
| **Electrical Fast Transient (EFT / Burst)** | IEC 61000-4-4 | $\pm 2.0\,\text{kV} \text{ @ } 5\,\text{kHz}$ on power, $\pm 1.0\,\text{kV}$ on signal | Common-mode chokes and RC snubber networks on relay lines. |
| **Electrostatic Discharge (ESD)** | IEC 61000-4-2 | $\pm 8\,\text{kV}$ Contact, $\pm 15\,\text{kV}$ Air Discharge | Low-capacitance TVS arrays ($< 3\,\text{pF}$) on CP, PP, and RFID. |
| **Conducted RF Immunity**| IEC 61000-4-6 | $10\,\text{V} \text{ RMS (150 kHz to 80 MHz)}$ | Pi-filter ($C\text{-}L\text{-}C$) on all DC supply rails. |

---

## 4. Hardware Bring-Up & Test Procedure

Follow this disciplined bench bring-up procedure when powering a new revision of the Low Voltage Controller Board for the first time:

```text
  Phase 1: Cold Impedance Verification (Unpowered DMM checks)
     │
     ▼
  Phase 2: Auxiliary Power Rail Ramp-Up (+12V, +5V, +3.3V, -12V checks)
     │
     ▼
  Phase 3: Control Pilot Signal Integrity (12V DC State A, 1 kHz PWM shape)
     │
     ▼
  Phase 4: Simulated Vehicle Handshake (States A -> B -> C -> D)
     │
     ▼
  Phase 5: Contactor Pull-in & Economizer PWM Verification
     │
     ▼
  Phase 6: 6mA DC / 30mA AC Fault Trip Injection Calibration
     │
     ▼
  Phase 7: IoT Gateway Boot & OCPP Central System Handshake
```

### Step-by-Step Bring-Up Instructions:
1. **Cold Board Impedance Check**:
   - Measure resistance to Ground on all primary rails ($+12\,\text{V}, +5\,\text{V}, +3.3\,\text{V}, -12\,\text{V}$). Ensure no rail exhibits $< 50\,\Omega$ impedance.
2. **DC Voltage Rail Verification**:
   - Power board with current-limited bench supply ($12.0\,\text{V}, 500\,\text{mA}$).
   - Verify $+5.0\,\text{V} \pm 2\%$, $+3.3\,\text{V} \pm 1\%$, and verify that the inverting charge pump produces $-12.0\,\text{V} \pm 5\%$.
3. **Control Pilot Waveform Verification (Oscilloscope)**:
   - In State A (unconnected), probe CP with high-impedance $10\text{X}$ probe. Verify steady $+12.0\,\text{V} \pm 0.4\,\text{V}$ DC.
   - Attach EVSE test simulator with $R_2 = 2.74\,\text{k}\Omega$. Verify signal drops to $+9.0\,\text{V}$ and immediately starts outputting $1.000\,\text{kHz} \pm 5\,\text{Hz}$ square wave.
   - Verify negative peak drops to **$-12.0\,\text{V} \pm 0.5\,\text{V}$** (confirming diode check circuit operates).
4. **State C Transition & Contactor Actuation**:
   - Switch in parallel resistor $R_3 = 1.3\,\text{k}\Omega$ on simulator.
   - Verify CP positive peak drops to $+6.0\,\text{V} \pm 0.3\,\text{V}$.
   - Probe contactor gate. Verify gate driver delivers $100\%$ duty cycle for $100\,\text{ms}$, followed by clean transition to $35\text{--}40\%$ economizer PWM at $25\,\text{kHz}$.
5. **RCM Trip Injection**:
   - Inject calibrated $6.0\,\text{mA}$ DC fault using precision current calibrator.
   - Verify comparator trips in $< 10.0\,\text{s}$ and de-asserts contactor gate immediately.

---

## 5. Bench RCA Troubleshooting Matrix

| Symptom / Anomaly | Root Cause | Underlying Electrical Physics | Corrective Bench Action |
| :--- | :--- | :--- | :--- |
| **CP voltage stuck at +12V; EV not detected** | Defective $R_1$, blown op-amp, or open CP line | Op-amp output disconnected from physical terminal. | 1. Measure resistance of $R_1$ ($1.0\,\text{k}\Omega$).<br>2. Check op-amp supply rails ($+12\,\text{V}$ and $-12\,\text{V}$). |
| **Negative CP voltage reads 0V instead of -12V** | Negative charge pump failed; $V_{EE}$ pin at $0\,\text{V}$ | Op-amp cannot pull below its negative supply rail. | Verify $-12\,\text{V}$ charge pump output; replace charge pump IC or flyback diode. |
| **Rounded CP edges; frequency drift $> 20\,\text{Hz}$** | Op-amp slew rate too low or excessive cable capacitance | $RC$ filter formed by op-amp output impedance and cable capacitance. | Upgrade to higher slew rate op-amp ($> 10\,\text{V}/\mu\text{s}$) or reduce output filtering capacitance. |
| **Contactor buzzes / chatters continuously** | Economizer PWM frequency too low or hold voltage too weak | Hold voltage drops below contactor dropout threshold ($V_{drop} \approx 4.0\,\text{V}$). | Increase economizer PWM duty cycle from $35\%$ to $45\text{--}50\%$, or raise PWM frequency to $> 20\,\text{kHz}$. |
| **Nuisance 6mA DC RCM trips during vehicle plug-in** | Ground bounce or high inrush current through common ground | Fluxgate sensor saturated by unbalanced capacitive inrush. | Add $20\text{--}50\,\text{ms}$ software trip debounce or improve ground plane partitioning. |
| **PP voltage reads 3.3V despite 32A cable attached** | Broken PP pin or missing $R_c$ inside cable plug | Resistor divider floating without bottom leg resistor. | Inspect socket PP pin mechanical contact tension; measure $R_{PP}$ with DMM ($220\,\Omega$ expected). |
| **OCPP WebSocket connection rejected (`401 Unauthorized`)** | Wrong `chargePointId` or invalid TLS client certificate | CSMS rejects registration due to authorization failure. | Check `BootNotification` payload JSON and verify provisioned X.509 client certificate expiration. |
