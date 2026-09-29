# Zeta DC-DC Converter: Inverse SEPIC Mechanics & Continuous Output Current

Welcome to the **VVDN Engineering Hub Technical Dossier on the Zeta (Inverse SEPIC) DC-DC Converter**. While the SEPIC converter offers continuous input current and a ground-referenced switch, its output current is discontinuous. The **Zeta Converter** flips this architecture: it features an **output inductor in series with the load (like a buck converter)**, delivering ultra-low output voltage ripple and continuous output current while maintaining non-inverting step-up/step-down capability.

This guide explores the Zeta topology, derives its voltage and current transfer functions, compares it against the SEPIC, and provides component sizing formulas.

---

## 1. Operating Principle & Zeta Topology

The **Zeta Converter** utilizes a high-side active switch ($Q_1$), a parallel inductor ($L_1$), a series flying coupling capacitor ($C_z$), a freewheeling diode ($D_1$), and an output filter inductor ($L_2$) connected directly to the output:

```text
                           Zeta DC-DC Converter Power Stage
   +Vin DC ────┬────────────── Drain (D)
               │               ┌───┴───┐ Q1 (High-Side Switch)
              ┌┴┐              │  SW   │
              │ │ C_in         └───┬───┘
              └┬┘                  │ Source (S)
               │                   ├── Node SW1 ────[   ] C_z ────┬── Node SW2 ───[ L2 ]──┬───> +Vout
               │                   │         (Flying Capacitor)   │ (Output Inductor)     │
               │                  ┌┴┐                            ┌┴┐                     ┌┴┐
               │                  │ │ Inductor L1                │ │ Diode D1            │ │ C_out
               │                  └┬┘ (To GND)                   └┬┘ (Anode to GND)      └┬┘
               │                   │                              │                       │
   GND ────────┴───────────────────┴──────────────────────────────┴───────────────────────┴─── GND
```

### 1.1 Conduction Intervals:
1. **Interval 1: Switch ON ($0 < t \le D \cdot T_s$)**:
   - High-side switch $Q_1$ conducts. Node $SW_1$ is pulled to $V_{IN}$.
   - Inductor $L_1$ is energized directly across $V_{IN}$ to GND:
     $$\frac{di_{L1}}{dt} = \frac{V_{IN}}{L_1}$$
   - The flying capacitor $C_z$ (precharged to $V_{out}$) pulls node $SW_2$ positive ($V_{SW2} = V_{IN} + V_{out}$), reverse-biasing diode $D_1$.
   - Inductor $L_2$ current ramps up, energized by $V_{IN} + V_{out} - V_{out} = V_{IN}$:
     $$\frac{di_{L2}}{dt} = \frac{V_{IN}}{L_2}$$
2. **Interval 2: Switch OFF ($D \cdot T_s < t \le T_s$)**:
   - $Q_1$ turns OFF. The collapsing fields of $L_1$ and $L_2$ pull nodes $SW_1$ and $SW_2$ negative.
   - Diode $D_1$ turns ON, clamping node $SW_2$ to GND ($0\,\text{V}$).
   - Inductor $L_1$ discharges its energy into flying capacitor $C_z$ through diode $D_1$.
   - Inductor $L_2$ freewheels through diode $D_1$ into the output capacitor $C_{out}$ and the load:
     $$\frac{di_{L2}}{dt} = \frac{-V_{out}}{L_2}$$

---

## 2. Voltage and Current Waveforms

```text
                          Zeta Key Operating Waveforms
   i_Cin   ^   Pulsating Input Current
           │   ┌──────┐                      ┌──────┐
           │   │      │                      │      │
        0A ┼───┴──────┴──────────────────────┴──────┴────────────────────> Time
           │◄─ D*Ts ─►│
   i_L2    ^   Continuous Output Current (Buck-Like!)
           │           / \                    / \
     I_out ┼─ ─ ─ ─ ─ /─ ─ ─\─ ─ ─ ─ ─ ─ ─ ─ /─ ─ ─\─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ 
           │         /       \              /       \
        0A ┼────────/─────────\────────────/─────────\───────────────────> Time
```

---

## 3. Mathematical Formulations & Component Sizing

### 3.1 Voltage Conversion Ratio:
Applying volt-second balance to output inductor $L_2$:
$$(V_{IN}) \cdot D \cdot T_s + (-V_{out}) \cdot (1 - D) \cdot T_s = 0$$
$$V_{out} = V_{IN} \cdot \frac{D}{1 - D}$$
The conversion ratio is identical to the SEPIC and classic buck-boost, delivering non-inverting positive output voltage.

### 3.2 Switch & Diode Voltage Stresses:
$$V_{DS,max} = V_{diode,rev} = V_{IN,max} + V_{out}$$

### 3.3 Continuous Output Filter Sizing:
Because output inductor $L_2$ feeds $C_{out}$ directly, the output ripple voltage formula is identical to a **Buck converter**:
$$\Delta V_{out} = \frac{\Delta I_{L2}}{8 \cdot f_s \cdot C_{out}}$$
*Huge Engineering Advantage*: Output voltage ripple in a Zeta converter is orders of magnitude lower than in a SEPIC or Boost converter for the same capacitor value!

### 3.4 Flying Capacitor Sizing ($C_z$):
The steady-state DC voltage across $C_z$ is equal to $V_{out}$:
$$V_{Cz} = V_{out}$$
To maintain capacitor voltage ripple $\Delta V_{Cz} \le 5\% \cdot V_{out}$:
$$C_z \ge \frac{I_{out} \cdot (1 - D)}{f_s \cdot \Delta V_{Cz}}$$

---

## 4. Head-to-Head Comparison: SEPIC vs. Zeta

| Engineering Parameter | SEPIC Converter | Zeta Converter (Inverse SEPIC) |
| :--- | :--- | :--- |
| **Output Polarity** | Positive (Non-inverting) | Positive (Non-inverting) |
| **Switch Gate Drive** | **Low-Side**: Referenced to GND (Simple standard driver) | **High-Side**: Floating switch (Requires bootstrap or P-FET) |
| **Input Current Waveform** | **Continuous**: Low input ripple, small input filter | **Pulsating**: High input ripple, requires larger $C_{in}$ |
| **Output Current Waveform** | **Pulsating**: High output ripple, requires large $C_{out}$ | **Continuous**: Ultra-low output ripple, small $C_{out}$ |
| **Shutdown Disconnect** | Yes (Series $C_{sep}$ blocks DC) | No (Diode and $L_2$ path) |
| **Optimal Application** | Battery-powered devices, automotive inputs | Low-noise analog sensor rails, instrumentation |
