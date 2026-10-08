# Dossier 6: Bring-Up, Calibration & Bench Testing

Welcome to **Dossier 6** of the Step-by-Step 4-Switch Synchronous Buck-Boost Post-Regulator Design Guide. This document provides the hardware bring-up checklist, digital calibration algorithms, dynamic load step testing procedures, and the bench troubleshooting matrix.

---

## Step 14: Step-by-Step Bring-Up Procedure

Follow this rigorous multi-stage procedure when powering up and verifying prototype hardware for the first time:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   HARDWARE BRING-UP CHECKLIST                                    │
├──────┬──────────────────────┬────────────────────────────────────────────────────────────────────┤
│ Step │ Verification Phase   │ Test Description & Expected Pass Criterion                         │
├──────┼──────────────────────┼────────────────────────────────────────────────────────────────────┤
│ **1**│ Cold Impedance Check │ Before applying power, verify with a calibrated DMM:               │
│      │                      │ - Resistance across $+V_{IN}$ to PGND: $> 100\,\text{k}\Omega$.    │
│      │                      │ - Resistance across $+V_{OUT}$ to PGND: $> 50\,\text{k}\Omega$.   │
│      │                      │ - Gate-to-Source resistance on all 4 FETs: $> 100\,\text{k}\Omega$.│
│      │                      │ - Ensure no solder bridges across SuperSO8 MOSFET pins.            │
├──────┼──────────────────────┼────────────────────────────────────────────────────────────────────┤
│ **2**│ Low-Voltage Auxiliary│ Connect current-limited $+12.0\,\text{V}$ bench supply to $V_{IN}$ │
│      │ Verification         │ with current compliance limit set to $150\,\text{mA}$.             │
│      │                      │ - Verify internal VCC regulator outputs $+5.0\,\text{V} \pm 2\%$.  │
│      │                      │ - Measure oscillator frequency: $250\,\text{kHz} \pm 5\%$.         │
│      │                      │ - Check quiescent standby current: $< 25\,\text{mA}$.              │
├──────┼──────────────────────┼────────────────────────────────────────────────────────────────────┤
│ **3**│ Gate Drive & Deadtime│ Probe high-side and low-side gate pins with high-speed scope:      │
│      │ Inspection           │ - Confirm clean square waves with rise/fall times $< 15\,\text{ns}$.│
│      │                      │ - Verify non-overlapping dead-time: $t_{dead} \approx 25\,\text{ns}$│
│      │                      │ - Confirm zero shoot-through cross-conduction current spikes.      │
├──────┼──────────────────────┼────────────────────────────────────────────────────────────────────┤
│ **4**│ Nominal $+24.0V$ Ramp│ Increase bench supply to $+24.0\,\text{V}$ nominal.                │
│      │                      │ - Verify default output voltage stabilizes at $20.0\,\text{V}$.    │
│      │                      │ - Measure no-load output ripple: $< 10\,\text{mV}_{\text{pk-pk}}$. │
├──────┼──────────────────────┼────────────────────────────────────────────────────────────────────┤
│ **5**│ DAC Voltage Sweep    │ Execute MCU DAC test firmware sweep:                               │
│      │                      │ - Command $V_{DAC} = 0.00\,\text{V} \longrightarrow V_O = 20.00\,\text{V}$ │
│      │                      │ - Command $V_{DAC} = 1.65\,\text{V} \longrightarrow V_O = 12.50\,\text{V}$ │
│      │                      │ - Command $V_{DAC} = 3.30\,\text{V} \longrightarrow V_O = 5.00\,\text{V}$  │
│      │                      │ - Verify monotonic transition across the entire 4:1 voltage span.  │
├──────┼──────────────────────┼────────────────────────────────────────────────────────────────────┤
│ **6**│ Full Load Soak       │ Connect programmable electronic load. Gradually increment current  │
│      │                      │ from $0.5\,\text{A} \rightarrow 1.5\,\text{A} \rightarrow 3.0\,\text{A}$.│
│      │                      │ - Verify output ripple remains $< 25\,\text{mV}_{\text{pk-pk}}$.   │
│      │                      │ - Confirm conversion efficiency $\ge 96.5\%$ at $15\,\text{V}/3A$. │
└──────┴──────────────────────┴────────────────────────────────────────────────────────────────────┘
```

---

## Step 15: Calibration & Accuracy Verification

Due to component tolerances in $R_{top}, R_{DAC}, R_{bot}$ and the MCU DAC reference, a **2-point linear software calibration** guarantees sub-$10\,\text{mV}$ absolute accuracy:

```text
                           2-POINT LINEAR CALIBRATION MATRIX
  Measured Voltage (V_OUT)
    ^
20V ┼───────────────────────────────────────────────────────────── [ Cal Point 2: DAC = 0.0V ]
    │                                                              - Target: 20.000 V
    │                                                              - Measured: V_meas_high
    │
    │                              Linear Fit: V_meas = m * V_prog + b
    │
 5V ┼────────────────────────────── [ Cal Point 1: DAC = 3.3V ]
    │                               - Target: 5.000 V
    │                               - Measured: V_meas_low
    └────────────────────────────────────────────────────────────> Commanded Voltage
```

### Calibration Formulation in Firmware:
1. **Calibration Slope ($m$)**:
   $$m = \frac{V_{meas,high} - V_{meas,low}}{V_{target,high} - V_{target,low}} = \frac{V_{meas}(0\text{V}) - V_{meas}(3.3\text{V})}{20.000 - 5.000}$$
2. **Calibration Offset ($b$)**:
   $$b = V_{meas,low} - (m \times 5.000)$$
3. **Calibrated DAC Command**:
   $$V_{DAC,cal} = \frac{V_{OUT,target} - b}{m}$$
Stored in the MCU internal Flash EEPROM emulation sector, this eliminates resistor initial tolerance error and guarantees $< 0.1\%$ absolute voltage accuracy!

---

## Step 16: Dynamic Load Transient & Thermal Stress Testing

```text
                       DYNAMIC LOAD STEP RESPONSE (1.5A -> 3.0A -> 1.5A)
  Output Current (I_OUT)
  3.0A ┼               ┌───────────────────────────────┐
       │               │                               │
  1.5A ┼───────────────┘                               └───────────────────────────────
       │
  Output Voltage (V_OUT)
       │    Steady-State
  20.0V┼───.               .───────────────────────.               .───────────────────
       │    \             /                         \             /
       │     \           / < 120µs Recovery          \           / Overshoot < 180mV
       │      '─────────'                             '─────────'
       │      Droop < 220mV
       └──────────────────────────────────────────────────────────────────────────────> Time
```

### 16.1 Oscilloscope Probe Technique for Ripple Measurement:
> [!IMPORTANT]
> Never use standard 6-inch alligator ground leads to measure switching ripple! The loop inductance picks up radiated magnetic noise from the inductor, showing artificial $150\,\text{mV}$ spikes.
> * Always use the **tip-and-barrel** or **coaxial pig-tail** probe connection directly across output capacitor $C_{OUT}$.
> * Set oscilloscope channel bandwidth limit to **$20\,\text{MHz}$**.

---

## Step 17: Bench Root Cause Analysis (RCA) Troubleshooting Matrix

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           BENCH ROOT CAUSE ANALYSIS (RCA) MATRIX                                         │
├────────────────────────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────┤
│ Observed Fault Symptom     │ Probable Root Cause                       │ Diagnostic & Corrective Action                  │
├────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ **Output oscillates or     │ 1. Phase margin degraded by insufficient  │ 1. Increase feedforward capacitor $C_{FF}$ from │
│ hunts at 5 kHz – 10 kHz**  │    lead compensation across $R_{top}$.    │    $47\,\text{pF}$ to $100\,\text{pF}$.         │
│                            │ 2. Excessive ESR on output capacitor bank.│ 2. Verify ceramic MLCCs are soldered cleanly;   │
│                            │ 3. Digital noise injected via DAC trace.  │    add $100\,\text{pF}$ bypass cap at DAC pin.  │
├────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ **Excessive output ripple  │ 1. Ceramic MLCCs suffering extreme DC     │ 1. Ensure rated voltage of MLCCs is $\ge 25V$;  │
│ voltage (> 50 mV pk-pk)**  │    voltage bias derating (> 70% loss).    │    verify $100\,\mu\text{F}$ polymer cap is populated│
│                            │ 2. Measurement artifact from probe loop.  │ 2. Use tip-and-barrel ground spring probe.      │
├────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ **MOSFET runs excessively  │ 1. Insufficient gate drive voltage        │ 1. Measure BOOT-to-SW voltage; ensure it stays  │
│ hot (> 90°C) at light load│    causing MOSFET to operate in linear    │    above $4.5\,\text{V}$. Replace bootstrap cap │
│                            │    resistive region.                      │    with $0.22\,\mu\text{F} / 50\,\text{V}$ X7R. │
│                            │ 2. Cross-conduction shoot-through.        │ 2. Increase series gate resistor to $4.7\,\Omega$.│
├────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ **Constant Current (CC)    │ 1. Kelvin sense traces picking up switch  │ 1. Reroute Kelvin traces as a tight differential│
│ mode chatters or falsely   │    node SW1/SW2 capacitive displacement   │    pair on Layer 4 shielded by ground plane.    │
│ trips below limit**        │    currents ($dV/dt$).                    │ 2. Add $100\,\Omega + 1\,\text{nF}$ low-pass    │
│                            │ 2. INA240 input filter missing.           │    RC differential filter at INA240 inputs.     │
├────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ **Output voltage collapses │ 1. Hardware CC clamp comparator threshold  │ 1. Verify MCU DAC2 output voltage $V_{ISET}$;   │
│ prematurely under load**   │    set too low.                           │    ensure $V_{ISET} \ge 1.50\,\text{V}$ for 3A. │
│                            │ 2. Controller inductor peak current limit │ 2. Verify current sense resistor $R_S$ between  │
│                            │    resistor ($R_{S}$) tripping early.     │    `CS` and `CSG` pins matches datasheet spec.  │
└────────────────────────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────┘
```
