# Buck-Boost DC-DC Converters: Inverting vs 4-Switch Non-Inverting Architecture

Welcome to the **VVDN Engineering Hub Technical Dossier on Buck-Boost DC-DC Converters**. When the input DC voltage can be higher, equal to, or lower than the desired regulated output rail—such as automotive battery cranking ($6\,\text{V} \dots 28\,\text{V}$ to $12\,\text{V}$), lithium-ion battery discharge profiles ($2.7\,\text{V} \dots 4.2\,\text{V}$ to $3.3\,\text{V}$), or USB Power Delivery ($5\,\text{V} \dots 20\,\text{V}$)—the Buck-Boost topology is mandatory.

This guide provides an exhaustive hardware analysis of the classic **Inverting Buck-Boost Converter** and the modern industrial workhorse: the **4-Switch Synchronous Non-Inverting Buck-Boost Converter (FSBB)**.

---

## 1. Classic Inverting Buck-Boost Converter

The classic single-switch Buck-Boost converter produces an output voltage whose polarity is inverted with respect to the input source ground:

```text
                      Classic Inverting Buck-Boost Converter
   +Vin DC ────┬────────────────── Drain (D)
               │                   ┌───┴───┐ Q1 (High-Side Switch)
              ┌┴┐                  │  SW   │
              │ │ C_in             └───┬───┘
              └┬┘                      │ Source (S)
               │                       ├─── Switching Node (SW) ───[|<] D1 (Diode) ──┬───> -Vout
               │                       │                                             │
               │                      ┌┴┐                                           ┌┴┐
               │                      │ │ Inductor L                                │ │ C_out
               │                      └┬┘                                           └┬┘
               │                       │                                             │
   GND ────────┴───────────────────────┴─────────────────────────────────────────────┴─── GND
```

### 1.1 Operating Mechanism:
1. **Switch ON ($0 < t \le D \cdot T_s$)**:
   - $Q_1$ is ON; Diode $D_1$ is reverse-biased by $-V_o$ and $V_{IN}$.
   - Inductor $L$ is connected directly between $V_{IN}$ and GND. Inductor current ramps up:
     $$\frac{di_L}{dt} = \frac{V_{IN}}{L}$$
   - Energy is stored in inductor $L$. Capacitor $C_{out}$ independently supplies the load.
2. **Switch OFF ($D \cdot T_s < t \le T_s$)**:
   - $Q_1$ turns OFF. The inductor forces node $SW$ negative to maintain continuous current flow.
   - Diode $D_1$ is forward-biased, pulling current out of the negative output rail through the inductor to GND.
   - Inductor current decays:
     $$\frac{di_L}{dt} = \frac{-|V_o|}{L}$$
   - Output voltage is **strictly negative** with respect to GND.

### 1.2 Transfer Function & Volt-Second Balance:
$$\int_0^{T_s} v_L(t) \, dt = V_{IN} \cdot D \cdot T_s + (-|V_o|) \cdot (1 - D) \cdot T_s = 0$$
$$|V_o| = V_{IN} \cdot \frac{D}{1 - D} \implies V_o = -V_{IN} \cdot \frac{D}{1 - D}$$
- When $D < 0.5 \implies |V_o| < V_{IN}$ (Step-Down / Buck Mode)
- When $D = 0.5 \implies |V_o| = V_{IN}$ (Unity Gain)
- When $D > 0.5 \implies |V_o| > V_{IN}$ (Step-Up / Boost Mode)

### 1.3 Severe Switch Stress:
Both the switch $Q_1$ and the diode $D_1$ see a peak reverse voltage equal to the **sum of input and output voltages**:
$$V_{stress} = V_{IN} + |V_o|$$
*Engineering Drawback*: The negative output polarity and severe switch voltage stress make the classic topology inconvenient for standard single-rail consumer and automotive electronics.

---

## 2. Four-Switch Synchronous Non-Inverting Buck-Boost (FSBB)

The **4-Switch Buck-Boost (FSBB)** combines a synchronous buck leg and a synchronous boost leg connected via a single central power inductor:

```text
               4-Switch Synchronous Non-Inverting Buck-Boost (FSBB)
   +Vin ───┬───────────────┐                               ┌───────────────┬───> +Vout
           │               │                               │               │
       Drain (D)       Drain (D)                       Drain (D)       Drain (D)
       ┌───┴───┐ QA    ┌───┴───┐ QB                    ┌───┴───┐ QC    ┌───┴───┐ QD
       │  HS1  │       │  LS1  │                       │  LS2  │       │  HS2  │
       └───┬───┘       └───┬───┘                       └───┬───┘       └───┬───┘
           │ Source        │ Source                        │ Source        │ Source
           ├── Node SW1 ───┴─────[ Central Inductor L ]────┴── Node SW2 ───┤
          ┌┴┐                                                             ┌┴┐
      Cin │ │                                                         Cout│ │
          └┬┘                                                             └┬┘
   GND ────┴───────────────────────────────────────────────────────────────┴─── GND
```

### 2.1 The Three Control Regimes:

To maximize efficiency ($> 98\%$), modern FSBB controllers (e.g., LM5176, LT8390, TPS55288) do not switch all 4 FETs simultaneously. Instead, they dynamically switch between three operating regions:

```text
               FSBB Operating Modes Across Input Voltage Sweep
      Efficiency
         100% ┼──────────.                 .──────────
              │           '.             .'
          95% ┼             '-----------'
              │              (4-Switch Region)
              0─────────────────────────────────────────> Vin
                  Vin < Vo        Vin ≈ Vo        Vin > Vo
                [Pure Boost]    [Buck-Boost]    [Pure Buck]
```

1. **Pure Buck Mode ($V_{IN} > 1.15 \cdot V_o$)**:
   - $Q_D$ is held continuously **ON** ($100\%$ duty cycle).
   - $Q_C$ is held continuously **OFF**.
   - $Q_A$ and $Q_B$ switch as a standard synchronous buck converter.
   - Only 2 switches toggle; switching losses are minimal.
2. **Pure Boost Mode ($V_{IN} < 0.85 \cdot V_o$)**:
   - $Q_A$ is held continuously **ON** ($100\%$ duty cycle).
   - $Q_B$ is held continuously **OFF**.
   - $Q_C$ and $Q_D$ switch as a standard synchronous boost converter.
3. **Buck-Boost Mode ($0.85 \cdot V_o \le V_{IN} \le 1.15 \cdot V_o$)**:
   - Both legs switch to provide seamless, monotonic output voltage regulation across the transition boundary without control loop instability or output voltage glitching.

---

## 3. Mathematical Formulations & Component Sizing

### 3.1 Inductor Sizing Formula:
The worst-case inductor ripple occurs in Boost mode at minimum input voltage:
$$L \ge \frac{V_{IN,min}^2 \cdot (V_o - V_{IN,min})}{f_s \cdot \Delta I_L \cdot V_o^2}$$
Choosing ripple current ratio $r = 0.3 \dots 0.4$ relative to maximum average inductor current:
$$I_{L,max} = \frac{V_o \cdot I_{o,max}}{\eta \cdot V_{IN,min}}$$
$$L = \frac{V_{IN,min} \cdot (V_o - V_{IN,min})}{f_s \cdot (r \cdot I_{L,max}) \cdot V_o}$$

### 3.2 Output Capacitor Sizing:
In boost and buck-boost modes, output current is discontinuous. $C_{out}$ must support the load current during switch ON time:
$$C_{out} \ge \frac{I_{o,max} \cdot D_{boost}}{f_s \cdot \Delta V_{o,allowable}}$$

---

## 4. Hardware Engineering Trade-Offs

| Parameter | Inverting Buck-Boost | 4-Switch Synchronous Buck-Boost (FSBB) |
| :--- | :--- | :--- |
| **Output Polarity** | Negative (Inverted) | Positive (Common Ground) |
| **Component Count** | 1 Switch, 1 Diode, 1 Inductor | 4 MOSFETs, 1 Inductor, Dual Drivers |
| **Switch Voltage Stress** | $V_{IN} + |V_o|$ | $\max(V_{IN}, V_o)$ |
| **Peak Efficiency** | $82\% \dots 88\%$ | $96\% \dots 98.5\%$ |
| **Primary Applications** | Low-cost negative bias rails (Op-Amps, LCDs) | USB-PD (5-20V), Automotive Infotainment, Drone ESCs |
