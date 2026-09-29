# Step-Up (Boost) DC-DC Converter: Right-Half-Plane Zero, CCM/DCM & Design

Welcome to the **VVDN Engineering Hub Technical Dossier on the Step-Up (Boost) DC-DC Converter**. The Boost converter is fundamental to battery-powered electronics, solar maximum power point tracking (MPPT), LED backlight drivers, and Active Power Factor Correction (PFC) pre-regulators. 

This document explores the magnetic physics of boost energy transfer, derives the infamous **Right-Half-Plane (RHP) Zero** stability limitation, details diode reverse-recovery phenomena, and provides practical component selection criteria.

---

## 1. Operating Principle & Boost Topology

The **Boost Converter** steps up an input DC voltage $V_{IN}$ to a higher DC output voltage $V_o$ by utilizing an inductor to store energy from the source and discharge it in series with the source into the load:

```text
                        Step-Up (Boost) DC-DC Converter
                      Inductor L
   +Vin DC ─────────────^^^^^^──────────────┬───────────────[>|] D1 (Boost Diode) ──┬───> +Vout
                                            │                                       │
                                        Drain (D)                                  ┌┴┐
                                        ┌───┴───┐ Q1 (Low-Side Switch)             │ │ C_out
                                        │  SW   │                                  └┬┘
                                        └───┬───┘                                   │
                                            │ Source (S)                            │
   GND ─────────────────────────────────────┴───────────────────────────────────────┴─── GND
```

### 1.1 Switching Intervals (CCM):
1. **Interval 1: Switch ON ($0 < t \le D \cdot T_s$)**:
   - MOSFET $Q_1$ conducts, connecting the switching node $SW$ to GND ($0\,\text{V}$).
   - Diode $D_1$ is reverse-biased ($V_{diode} = -V_o$).
   - Full input voltage $V_{IN}$ appears across inductor $L$. Current ramps up linearly:
     $$\frac{di_L}{dt} = \frac{V_{IN}}{L}$$
   - Energy is drawn from the input source and stored in $L$.
   - **Crucial Dynamic Observation**: During this interval, the output load is completely disconnected from the source and inductor; output current $I_o$ is supplied solely by the discharging output capacitor $C_{out}$.
2. **Interval 2: Switch OFF ($D \cdot T_s < t \le T_s$)**:
   - $Q_1$ turns OFF. The collapsing magnetic field forces the voltage across $L$ to reverse polarity.
   - Node $SW$ flies above $V_o$, forward-biasing diode $D_1$.
   - Voltage across $L$ is $V_L = V_{IN} - V_o < 0$. Current decays linearly:
     $$\frac{di_L}{dt} = \frac{V_{IN} - V_o}{L}$$
   - Energy stored in $L$, along with additional energy from input $V_{IN}$, flows into $C_{out}$ and the load.

---

## 2. Voltage and Current Waveforms

```text
                     Continuous Conduction Mode (CCM) Waveforms
   V_SW    ^
        Vo ┼──────────────┐                      ┌──────────────
           │              │                      │
        0V ┼──────────────┴──────────────────────┴──────────────> Time
           │◄─── D*Ts ───►│◄──── (1-D)*Ts ──────►│
   i_L     ^
           │              / \                    / \
     I_max ┼─────────────/   \──────────────────/   \───────────
     I_avg ┼─ ─ ─ ─ ─ ─ /─ ─ ─\─ ─ ─ ─ ─ ─ ─ ─ /─ ─ ─\─ ─ ─ ─ ─  (I_in = Io / (1-D))
     I_min ┼───────────/       \──────────────/       \─────────
           0────────────────────────────────────────────────────> Time
   i_Diode ^
     I_max ┼──────────────┐                      ┌──────────────
           │              │\                     │\
        0A ┼──────────────┴─\────────────────────┴─\────────────> Time
           │◄── Zero ────►│◄─ Pulsating Current ─►│
```

---

## 3. Mathematical Formulations & Component Sizing

### 3.1 Voltage Conversion Ratio:
Applying volt-second balance across inductor $L$:
$$\int_0^{T_s} v_L(t) \, dt = (V_{IN}) \cdot D \cdot T_s + (V_{IN} - V_o) \cdot (1 - D) \cdot T_s = 0$$
$$V_{IN} \cdot D + V_{IN} - V_o - V_{IN} \cdot D + V_o \cdot D = 0$$
$$V_{IN} = V_o (1 - D) \implies V_o = \frac{V_{IN}}{1 - D}$$
$$D = 1 - \frac{V_{IN}}{V_o}$$

### 3.2 Inductor Ripple & Value Calculation:
$$\Delta I_L = \frac{V_{IN} \cdot D}{f_s \cdot L}$$
Average inductor current equals average input current:
$$I_{L,avg} = I_{IN} = \frac{I_o}{1 - D} = \frac{V_o \cdot I_o}{\eta \cdot V_{IN}}$$
Choosing ripple ratio $r = \frac{\Delta I_L}{I_{L,avg}} \approx 0.2 \dots 0.4$:
$$L = \frac{V_{IN} \cdot (V_o - V_{IN})}{f_s \cdot \Delta I_L \cdot V_o} = \frac{V_{IN} \cdot D}{f_s \cdot (r \cdot I_{IN})}$$

### 3.3 Output Capacitor Sizing & RMS Ripple Stress:
Because diode current is discontinuous, $C_{out}$ must support the entire load current $I_o$ during switch ON-time:
$$\Delta V_{o,cap} = \frac{I_o \cdot D}{f_s \cdot C_{out}} \implies C_{out} \ge \frac{I_o \cdot D}{f_s \cdot \Delta V_{o,allowable}}$$
The RMS ripple current through $C_{out}$ is exceptionally severe:
$$I_{Cout,rms} = I_o \cdot \sqrt{\frac{D}{1 - D}}$$
*Engineering Implication*: Always verify that the chosen capacitor's RMS ripple current rating exceeds $I_{Cout,rms}$ to prevent thermal degradation.

---

## 4. The Right-Half-Plane (RHP) Zero Hazard & Stability

The Boost converter possesses an intrinsic non-minimum phase zero in its small-signal control-to-output transfer function, known as the **Right-Half-Plane (RHP) Zero**:

$$\omega_{RHPZ} = \frac{R_{load} \cdot (1 - D)^2}{L} \quad (\text{rad/s}) \implies f_{RHPZ} = \frac{R_{load} \cdot (1 - D)^2}{2\pi \cdot L} \quad (\text{Hz})$$

```text
                  Transient Response to a Step Increase in Duty Cycle
   Duty Cycle D ^
                │       Step increase in D (Load asks for more Vo)
                ├───────┌───────────────────────────────────────────────> Time
   Output Vo    ^
                │           Vo initially DIPS!
                │       - - ┐                  .------------------------
                │            \                /
                │             '--------------' (Takes time for L to charge)
                0───────────────────────────────────────────────────────> Time
```

### 4.1 Physical Explanation of the RHP Zero:
1. When load increases, the controller increases duty cycle $D$ to boost output voltage.
2. An increased $D$ means the switch stays ON longer, which **reduces the diode conduction time ($1-D$)**.
3. Consequently, less energy is delivered to the output during the immediate next switching cycles while inductor current is ramping up!
4. The output voltage **drops initially** before rising to its target.
5. In the frequency domain, an RHP zero provides **$+20\,\text{dB/decade}$ gain boost but $-90^\circ$ phase lag**—a toxic combination for closed-loop stability.

### 4.2 Control Bandwidth Restriction:
To ensure stable feedback and avoid $180^\circ$ phase margin collapse, the crossover frequency ($f_c$) of the voltage control loop must be capped at:
$$f_c \le \frac{1}{3} \dots \frac{1}{5} \cdot f_{RHPZ}$$
*Worst-case operating condition*: Minimum input voltage $V_{IN,min}$ and maximum load current $I_{o,max}$ (minimum $R_{load}$ and highest $D$).

---

## 5. Diode Reverse Recovery & Synchronous Boost

In CCM, when switch $Q_1$ turns ON, diode $D_1$ is conducting full inductor current.
- Standard silicon PN diodes take $t_{rr} = 30 \dots 100\,\text{ns}$ to clear reverse minority carriers.
- During $t_{rr}$, the diode conducts reverse current directly from $V_o$ through $Q_1$ to GND, creating a massive current spike ($I_{spike} = I_L + I_{rr,pk}$) and severe turn-on losses in $Q_1$.
- **Hardware Solutions**:
  1. Use **Silicon Carbide (SiC) Schottky Diodes** ($Q_{rr} \approx 0$).
  2. Implement **Synchronous Boost**: Replace diode with an active N-channel or P-channel MOSFET with body-diode anti-parallel conduction and dead-time management.
