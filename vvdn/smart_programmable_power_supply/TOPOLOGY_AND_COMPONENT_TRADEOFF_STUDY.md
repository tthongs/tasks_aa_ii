# Engineering Deep-Dive: Comprehensive Topology & Component Trade-Off Study

Welcome to the **VVDN Engineering Hub Comprehensive Trade-Off Study** for the Smart Programmable Voltage Supply Module ($85\,\text{V} \dots 265\,\text{V}$ AC In $\rightarrow$ $5.0\,\text{V} \dots 20.0\,\text{V}$, $3.0\,\text{A}$ DC Out).

This guide is designed as an exhaustive, pedagogical engineering resource explaining **why each topology and component was chosen over its alternatives**, detailing the mathematical physics, efficiency impact, thermal constraints, and failure modes of each design choice.

---

## 1. System Architecture: Two-Stage Cascaded vs. Single-Stage Variable Flyback

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                 TWO-STAGE CASCADED VS SINGLE-STAGE VARIABLE FLYBACK COMPARISON                   │
├───────────────────────┬───────────────────────────┬──────────────────────────────────────────────┤
│ Design Dimension      │ Single-Stage Variable     │ Cascaded Two-Stage (Chosen)                  │
│                       │ Flyback (5V–20V Direct)   │ (QR Flyback 24V + Buck-Boost Post-Regulator) │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Auxiliary Bias VCC**│ **Collapses at 5V!**      │ **Rock-Solid Constant +16V**: Flyback always │
│                       │ (V_aux drops from 18V to  │ runs at fixed 24V output regardless of load. │
│                       │ 4V, triggering UVLO reset)│ Auxiliary bias winding never sags!           │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Transformer Design**│ Extreme primary turns vs  │ **Optimized for Single Operating Point**:    │
│                       │ saturation trade-off; poor│ PQ26/20 core operates at peak flux density   │
│                       │ magnetic utilization.     │ ($B_{max} = 0.133\,\text{T}$) across loads.  │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Output Ripple & BW**│ $100\,\text{Hz}$ mains    │ **Sub-25mV Ripple & Fast Step**: Buck-Boost  │
│                       │ ripple bleeds through;    │ post-regulator switches at $250\,\text{kHz}$,│
│                       │ slow optocoupler loop.    │ attenuating $100\,\text{Hz}$ line ripple.    │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Secondary Sensing** │ High-voltage isolation    │ **Secondary-Ground Referenced**: MCU manages │
│                       │ crossing required for DAC │ CV/CC locally on secondary ground.           │
│                       │ voltage adjustment.       │ No isolated DAC or high-voltage boundary!    │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Transient Response**│ Sluggish ($> 6\,\text{ms}$)│ **Ultra-Fast (< 120 µs)**: Post-regulator    │
│                       │ optocoupler bandwidth.    │ error amplifier responds immediately.        │
└───────────────────────┴───────────────────────────┴──────────────────────────────────────────────┘
```

### Why We Selected Cascaded Two-Stage:
1. **The 4:1 Auxiliary Bias Trap**: In a flyback transformer, auxiliary winding voltage tracks the secondary:
   $$V_{aux} \approx (V_{OUT} + V_{SR}) \cdot \left(\frac{N_{aux}}{N_s}\right) - V_D$$
   If sized for $V_{OUT} = 20\,\text{V}$ to give $V_{aux} = 18\,\text{V}$, then at $V_{OUT} = 5.0\,\text{V}$, $V_{aux}$ plunges down to $4.04\,\text{V}$. Because standard PWM controllers have an under-voltage lockout (UVLO) threshold of $V_{UVLO(off)} \approx 8.1\,\text{V} \dots 14\,\text{V}$, the supply continuously brownout-reboots! In our two-stage design, the Flyback output is fixed at $+24.0\,\text{V}$, so $V_{aux}$ stays rock-solid at $+16.0\,\text{V}$ under all load and output voltage settings.
2. **Dynamic Regulation Across Galvanic Barrier**: Regulating a programmable $5\text{V} \dots 20\text{V}$ output directly across an optocoupler introduces non-linear current transfer ratio (CTR) drift and severe loop phase lag, limiting bandwidth to $< 1.5\,\text{kHz}$. A secondary post-regulator allows the MCU to regulate voltage directly on the secondary ground plane with $35\,\text{kHz}$ bandwidth.

---

## 2. Post-Regulator Topology: 4-Switch Synchronous Buck-Boost vs. Alternatives

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   POST-REGULATOR TOPOLOGY COMPARISON                             │
├───────────────────────┬────────────┬──────────┬───────────┬──────────────┬───────────────────────┤
│ Topology Candidate    │ Efficiency │ Polarity │ Ripple    │ Switch Stress│ Why Chosen / Rejected │
├───────────────────────┼────────────┼──────────┼───────────┼──────────────┼───────────────────────┤
│ **4-Switch Sync BB    │ **96.8%    │ Positive │ < 25 mV   │ V_in (24V) / │ **CHOSEN**: Peak eff, │
│ (H-Bridge LM5176)**   │ (Peak)**   │ Non-Inv. │ pk-pk     │ V_out (20V)  │ multi-mode operation, │
│                       │            │          │           │              │ positive SELV ground. │
├───────────────────────┼────────────┼──────────┼───────────┼──────────────┼───────────────────────┤
│ **Traditional Single- │ 88.5%      │ Inverting│ > 45 mV   │ V_in + V_out │ **REJECTED**: Produces│
│ Switch Inverting BB** │            │ (-V_out) │ pk-pk     │ = 44V        │ negative output rail! │
├───────────────────────┼────────────┼──────────┼───────────┼──────────────┼───────────────────────┤
│ **Coupled-Inductor    │ 94.5%      │ Positive │ < 20 mV   │ V_in + V_out │ **REJECTED**: Series  │
│ SEPIC Converter**     │            │ Non-Inv. │ pk-pk     │ = 44V        │ cap C_sep carries 2.7A│
│                       │            │          │           │              │ RMS ripple; high loss.│
├───────────────────────┼────────────┼──────────┼───────────┼──────────────┼───────────────────────┤
│ **Synchronous Zeta    │ 95.1%      │ Positive │ < 12 mV   │ V_in + V_out │ **REJECTED**: Flying  │
│ Converter**           │            │ Non-Inv. │ pk-pk     │ = 44V        │ capacitor stress;     │
│                       │            │          │           │              │ complex gate drives.  │
├───────────────────────┼────────────┼──────────┼───────────┼──────────────┼───────────────────────┤
│ **Pure Synchronous    │ 97.5%      │ Positive │ < 18 mV   │ V_in (36V)   │ **REJECTED**: Requires│
│ Buck (Fixed 36V Bus)**│            │ Non-Inv. │ pk-pk     │              │ primary Flyback bus to│
│                       │            │          │           │              │ be raised to 36V.     │
└───────────────────────┴────────────┴──────────┴───────────┴──────────────┴───────────────────────┘
```

### Why 4-Switch Synchronous Buck-Boost:
1. **Positive Output Common Ground**: Traditional buck-boost converters invert voltage ($\frac{V_o}{V_i} = -\frac{D}{1-D}$), producing $-5\,\text{V} \dots -20\,\text{V}$. This makes USB-C connectivity, digital MCU monitoring, and standard bench ground referencing impossible without inverted logic and level-shifters. The 4-switch H-bridge provides a non-inverting positive output sharing a clean ground.
2. **Pure Buck Conduction Efficiency ($5\,\text{V} \dots 18\,\text{V}$)**: Because $24\,\text{V} > V_{OUT}$ for most of the operating range, the controller holds $Q_C$ OFF and $Q_D$ permanently ON. Only $Q_A$ and $Q_B$ toggle! This cuts switching losses in half, achieving up to **$96.8\%$ efficiency**.

---

## 3. Post-Regulator Control Modes: Multi-Mode State Machine vs. Continuous 4-Switch Toggling

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     MULTI-MODE OPERATION VS CONTINUOUS 4-SWITCH SWITCHING                        │
├───────────────────────┬───────────────────────────┬──────────────────────────────────────────────┤
│ Metric                │ Continuous 4-Switch PWM   │ Multi-Mode State Machine (Chosen)            │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Switches Active**   │ All 4 switches toggle on  │ **Only 2 switches toggle** during Buck mode  │
│                       │ EVERY switching cycle!    │ ($5\text{V} \dots 18\text{V}$ output).       │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Gate Drive Loss**   │ $4 \times Q_g V f_{sw}$   │ $2 \times Q_g V f_{sw}$                      │
│                       │ $\approx 160\,\text{mW}$  │ $\approx 80\,\text{mW}$ (50% reduction!)     │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Switching Loss**    │ High ($P_{sw}$ on 4 FETs) │ **Zero switching loss** on Boost switches!   │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Inductor Ripple**   │ Higher ripple current     │ Standard buck ripple ($\Delta I_L = 0.9A$).  │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Peak Efficiency**   │ $93.2\%$                  │ $\mathbf{96.8\%}$                            │
└───────────────────────┴───────────────────────────┴──────────────────────────────────────────────┘
```

### Why Multi-Mode State Machine:
* In a continuous 4-switch scheme, both switch nodes `SW1` and `SW2` slew violently at $250\,\text{kHz}$, creating excessive capacitive dump loss ($0.5 C_{oss} V^2 f_{sw}$) and doubling electromagnetic radiation.
* The **TI LM5176** multi-mode controller dynamically shifts between pure buck ($5\,\text{V} \dots 18\,\text{V}$), narrow buck-boost transition ($18\,\text{V} \dots 20\,\text{V}$), and pure boost (during bus dips), completely eliminating redundant switching transitions.

---

## 4. Primary Stage: Quasi-Resonant (QR) Valley Switching vs. Hard-Switched Flyback

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                   QUASI-RESONANT VALLEY SWITCHING VS HARD SWITCHING COMPARISON                   │
├───────────────────────┬───────────────────────────┬──────────────────────────────────────────────┤
│ Feature               │ Hard-Switched Fixed Freq  │ Quasi-Resonant Valley Switching (Chosen)     │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Turn-On Voltage**   │ Switch turns on at peak   │ **Switch turns on at resonant minimum valley**│
│                       │ $V_{DS} \approx 475V$     │ ($V_{DS} \approx 180V \dots 220V$).          │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Capacitive Loss**   │ $P = 0.5 C_{oss} V^2 f$   │ Slashed by **$\approx 75\%$**!               │
│                       │ $\approx 1.45\,\text{W}$  │ $\approx 0.35\,\text{W}$.                    │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **EMI Profile**       │ Fixed discrete spike peaks│ **Natural Frequency Jittering**: Valley ring │
│                       │ at fundamental & harmonics│ spreads EMI energy across wide spectrum.     │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Controller**        │ Standard UC3842           │ **TI UCC28740 / ON Semi NCP1342**            │
└───────────────────────┴───────────────────────────┴──────────────────────────────────────────────┘
```

### Why Quasi-Resonant Valley Switching:
* In standard flyback converters, when the primary switch turns on, the energy stored in the parasitic output capacitance $C_{oss}$ is dumped as heat into the MOSFET channel:
  $$P_{coss} = \frac{1}{2} C_{oss} V_{DS}^2 f_{sw}$$
  Because $V_{DS} \approx 475\,\text{V}$, the squared voltage term ($475^2 = 225,625\,\text{V}^2$) creates severe dissipation.
* The **UCC28740** detects the demagnetization of the transformer via an auxiliary zero-crossing detection (ZCD) pin. It waits until the resonance between primary inductance $L_p$ and $C_{oss}$ reaches its absolute lowest voltage valley before triggering the gate, slashing turn-on loss by $75\%$ and running substantially cooler.

---

## 5. Secondary Rectification: Synchronous MOSFET vs. Schottky Diode

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      SECONDARY SYNCHRONOUS RECTIFICATION VS SCHOTTKY DIODE                       │
├───────────────────────┬───────────────────────────┬──────────────────────────────────────────────┤
│ Metric                │ Schottky Diode (e.g. MBR1060)│ Synchronous MOSFET (Infineon BSC052N06NS) │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Conduction Voltage**│ $V_F \approx 0.55\,\text{V}$│ $V_{DS} = I_{rms} \times R_{DS(on)} = 0.025V$│
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Thermal Dissipation**│ $P = 3.0\,\text{A} \times 0.55\,\text{V}$│ $P = (4.8\,\text{A}_{\text{RMS}})^2 \times 0.0052\,\Omega$│
│                       │ $\mathbf{= 1.65\,\text{W}}$│ $\mathbf{= 0.120\,\text{W}}$ (92.7% reduction!)│
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Heatsink Required?**│ **Yes**: Bulky aluminum   │ **No**: SMT copper polygon cooling is enough.│
│                       │ heatsink mandatory.       │                                              │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Stage Efficiency**  │ $\approx 88.5\%$          │ $\mathbf{> 91.5\%}$                          │
└───────────────────────┴───────────────────────────┴──────────────────────────────────────────────┘
```

### Why Synchronous Rectification:
* At $3.0\,\text{A}$ continuous secondary current, a Schottky diode with $0.55\,\text{V}$ forward drop dissipates $1.65\,\text{W}$. In a fanless enclosed bench supply, this produces a local temperature rise of $\Delta T > 50^\circ\text{C}$.
* Using an **MP6908 fast SR controller** driving a $5.2\,\text{m}\Omega$ MOSFET drops dissipation to **$0.12\,\text{W}$**, eliminating the secondary heatsink entirely and boosting stage efficiency by **$3.0\%$**.

---

## 6. Digital Voltage Programming: DAC Feedback Injection vs. Alternatives

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           VOLTAGE PROGRAMMING IMPLEMENTATION COMPARISON                          │
├───────────────────────┬────────────┬───────────┬──────────────┬──────────────────────────────────┤
│ Method                │ Resolution │ Bandwidth │ Linearity    │ Engineering Failure Mode         │
├───────────────────────┼────────────┼───────────┼──────────────┼──────────────────────────────────┤
│ **DAC Summing Node    │ **3.65 mV/ │ > 35 kHz  │ **Strictly   │ **CHOSEN**: Pure analog summing, │
│ Current Injection**   │ LSB (12b)**│ (Instant) │ Linear KCL** │ no noise, instant response.      │
├───────────────────────┼────────────┼───────────┼──────────────┼──────────────────────────────────┤
│ **Digital Potentiometer│ ~60 mV /  │ < 5 kHz   │ Non-linear   │ **REJECTED**: Terminal voltage   │
│ (e.g. AD5290)**       │ Step (8b)  │ (I2C lag) │ wiper resist.│ limited to 5V; wiper parasitics. │
├───────────────────────┼────────────┼───────────┼──────────────┼──────────────────────────────────┤
│ **Filtered PWM +      │ Variable   │ < 100 Hz  │ Requires RC  │ **REJECTED**: Massive RC filter  │
│ Resistor Injection**  │ (Noise)    │ (Sluggish)│ filter ripple│ delay; PWM ripple bleeds into FB.│
└───────────────────────┴────────────┴───────────┴──────────────┴──────────────────────────────────┘
```

### Why DAC Current Injection Summing Node:
1. **Mathematical Linearity**: By tying a precision resistor ($R_{DAC} = 11.0\,\text{k}\Omega$) between the 12-bit DAC and the error amplifier feedback junction (held at virtual-fixed reference $V_{REF} = 1.20\,\text{V}$), the output voltage follows a strictly linear equation:
   $$V_{OUT} = V_{OUT(max)} - \left(\frac{R_{top}}{R_{DAC}}\right) \cdot V_{DAC}$$
2. **Instant Response**: Unlike a filtered PWM network which introduces an RC filter delay of $> 10\,\text{ms}$, DAC voltage updates take effect in microseconds with zero injected switching noise.

---

## 7. Constant-Current (CC) Protection: Fast Analog Clamp vs. MCU Software Loop

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    ANALOG HARDWARE CC CLAMP VS MCU SOFTWARE ADC INTERRUPT                        │
├───────────────────────┬───────────────────────────┬──────────────────────────────────────────────┤
│ Metric                │ MCU Software ADC Loop     │ Hardware Analog Clamp (Chosen)               │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Sense Element**     │ INA226 (I2C Bus)          │ **INA240A2 (Continuous Analog 50 V/V)**      │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Response Latency**  │ $1.0\,\text{ms} \dots 5.0\,\text{ms}$│ **< 5 µs (Sub-cycle hardware clamp)**     │
│                       │ (ADC conversion + I2C)    │ (TLV3501 comparator propagation = 4.5ns)     │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Dead-Short Outcome**│ **MOSFET Destructive Failure**│ **Immediate Current Limiting**: Duty cycle   │
│                       │ Inductor saturates and    │ collapses safely; output folds back without  │
│                       │ silicon blows before MCU! │ stress.                                      │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **MCU Crash Immunity**│ Fails if firmware crashes.│ **100% Autonomous Hardware Protection**.     │
└───────────────────────┴───────────────────────────┴──────────────────────────────────────────────┘
```

### Why Hardware Analog Clamp:
* A dead short circuit applied to the output terminals causes current to rise at a rate of:
  $$\frac{di}{dt} = \frac{V_{IN}}{L} = \frac{24.0\,\text{V}}{10\,\mu\text{H}} = 2.4\,\text{A}/\mu\text{s}$$
* Within $5\,\mu\text{s}$, the current will exceed $12\,\text{A}$, driving the inductor into hard saturation and destroying the power MOSFETs before an MCU could ever read an I2C register or execute an interrupt!
* The **INA240A2 + TLV3501 + BAT54** clamp operates autonomously in analog hardware, pulling down the `COMP` pin in **$< 5\,\mu\text{s}$** and protecting the system 100% of the time.

---

## 8. Power Inductor: Flat-Wire Shielded vs. Standard Wirewound

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      FLAT-WIRE SHIELDED INDUCTOR VS STANDARD WIREWOUND                           │
├───────────────────────┬───────────────────────────┬──────────────────────────────────────────────┤
│ Metric                │ Standard Wirewound Inductor│ Wurth WE-HCC Flat-Wire (7443321000, Chosen)  │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Conductor Profile** │ Round magnet wire         │ **Flat rectangular copper strip**            │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Skin Effect Loss**  │ High AC resistance at     │ **Ultra-low AC resistance**: High surface    │
│                       │ $250\,\text{kHz}$.        │ area minimizes high-frequency skin depth loss│
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **DC Resistance (DCR)│ $24\,\text{m}\Omega \dots 32\,\text{m}\Omega$│ **11.8 mΩ** (50% reduction in copper loss!)  │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Magnetic Shielding**│ Unshielded / Semi-shielded│ **Full magnetic shielding**: Suppresses      │
│                       │ radiates flux into traces.│ radiated flux into sensitive feedback traces.│
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Saturation Behavior**│ Abrupt saturation cliff   │ **Soft saturation**: Handles current spikes. │
└───────────────────────┴───────────────────────────┴──────────────────────────────────────────────┘
```

---

## 9. Output Filtering: Hybrid Ceramic + Polymer Bank vs. Single Capacitor Types

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT FILTER BANK CAPACITOR COMPARISON                             │
├───────────────────────┬───────────────────────────┬──────────────────────────────────────────────┤
│ Configuration         │ Advantages                │ Drawbacks / Engineering Failure Mode         │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Pure Standard       │ Inexpensive bulk capacity.│ **High ESR ($> 150\,\text{m}\Omega$)**:      │
│ Electrolytic Bank**   │                           │ Generates $\Delta V = 180\,\text{mV}$ ripple;│
│                       │                           │ dries out over time at elevated temp.        │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Pure Ceramic        │ Ultra-low ESR, compact.   │ **Severe DC Bias Derating**: Loses $55\%$    │
│ MLCC Bank**           │                           │ capacitance at 20V DC. Causes loop           │
│                       │                           │ instability during 3A dynamic load steps.    │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Hybrid Bank:        │ **Best of Both Worlds**:  │ Slightly higher BOM item count (2 lines).    │
│ Ceramic + Polymer     │ - Ceramic handles 250kHz  │ *(Fully justified by sub-8mV ripple and      │
│ (CHOSEN)**            │   switching ripple ($3m\Omega$).│  rock-solid 120µs transient response).*      │
│                       │ - Polymer provides 100µF  │                                              │
│                       │   non-derating bulk.      │                                              │
└───────────────────────┴───────────────────────────┴──────────────────────────────────────────────┘
```

---

## 10. Summary Matrix of Design Decisions

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MASTER ENGINEERING DECISION MATRIX                               │
├────────────────────────────┬─────────────────────────────┬───────────────────────────────────────┤
│ Functional Subsystem       │ Selected Implementation     │ Core Justification / Failure Avoided  │
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Overall Architecture**   │ Two-Stage Cascaded          │ Prevents Flyback aux VCC collapse;    │
│                            │ (Flyback + Buck-Boost)      │ enables secondary-ground referenced MCU│
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Post-Regulator**         │ 4-Switch Synchronous BB     │ Delivers positive non-inverting rail; │
│                            │ (TI LM5176)                 │ operates at 96.8% eff in pure buck.   │
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Primary Controller**     │ Quasi-Resonant (UCC28740)   │ Valley switching slashes Coss loss 75%│
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Secondary Rectifier**    │ Sync MOSFET (BSC052N06NS)   │ Cuts thermal loss from 1.65W to 0.12W │
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Voltage Programming**    │ 12-Bit DAC Current Injection│ Instant analog summing; 3.65mV step   │
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Current Limiting**       │ Analog Clamp (TLV3501)      │ Sub-5µs response protects against dead│
│                            │                             │ short circuits without MCU latency.   │
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Inductor**               │ Flat-Wire Shielded (WE-HCC) │ 11.8mΩ DCR; 11.5A saturation current  │
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Output Capacitors**      │ 4x MLCC + 1x Polymer        │ Sub-8mV ripple; immune to bias droop  │
└────────────────────────────┴─────────────────────────────┴───────────────────────────────────────┘
```
