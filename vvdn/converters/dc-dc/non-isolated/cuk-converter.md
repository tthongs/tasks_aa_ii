# Ćuk DC-DC Converter: Capacitive Energy Transfer & Zero-Ripple Physics

Welcome to the **VVDN Engineering Hub Technical Dossier on the Ćuk DC-DC Converter**. Invented by Dr. Slobodan Ćuk at Caltech, this topology is unique among switched-mode power converters: it uses an intermediate capacitor for energy transfer rather than an inductor's magnetic field, and features **continuous current at both input and output ports**, resulting in exceptionally low electromagnetic interference (EMI).

This document explores the circuit topology, derives the volt-second and charge-balance equations, examines switch stresses, and details the **Coupled-Inductor Zero-Ripple Phenomenon**.

---

## 1. Operating Principle & Ćuk Topology

The **Ćuk Converter** comprises two inductors ($L_1, L_2$), an active switch ($Q_1$), a diode ($D_1$), an energy-transfer coupling capacitor ($C_1$), and an output filter capacitor ($C_o$):

```text
                           Classic Inverting Ćuk Converter
              Inductor L1                      Capacitor C1              Inductor L2
   +Vin DC ─────^^^^^^──────────────┬──────────────[   ]─────────────┬─────^^^^^^───────┬───> -Vout
                                    │      (Energy Transfer Cap)     │                  │
                                Drain (D)                            │                 ┌┴┐
                                ┌───┴───┐ Q1                        ┌┴┐ D1 (Diode)     │ │ C_out
                                │  SW   │                           │ │ (Anode to Vo)  └┬┘
                                └───┬───┘                           └┬┘                 │
                                    │ Source (S)                     │                  │
   GND ─────────────────────────────┴────────────────────────────────┴──────────────────┴─── GND
```

### 1.1 Conduction Intervals:
1. **Interval 1: Switch OFF ($D \cdot T_s < t \le T_s$)**:
   - Switch $Q_1$ is OFF. Diode $D_1$ is forward-biased.
   - Input inductor $L_1$ charges coupling capacitor $C_1$ via diode $D_1$.
   - Output inductor $L_2$ delivers stored energy through diode $D_1$ into output capacitor $C_{out}$ and the load.
   - The voltage across $C_1$ in steady state settles to:
     $$V_{C1} = V_{IN} + |V_o|$$
2. **Interval 2: Switch ON ($0 < t \le D \cdot T_s$)**:
   - Switch $Q_1$ turns ON, pulling the left terminal of $C_1$ to GND ($0\,\text{V}$).
   - The right terminal of $C_1$ drops to $-(V_{IN} + |V_o|)$, reverse-biasing diode $D_1$.
   - Energy stored in $C_1$ is transferred directly into output inductor $L_2$ and the load.
   - Concurrently, input inductor $L_1$ draws energy directly from $V_{IN}$ to GND.

---

## 2. Voltage and Current Waveforms

```text
                          Ćuk Converter Key Waveforms
   i_L1    ^   Continuous Input Current
           │           / \                    / \
           │──────────/   \──────────────────/   \───────────────────> Time
   i_L2    ^   Continuous Output Current
           │           / \                    / \
           │──────────/   \──────────────────/   \───────────────────> Time
   V_Q1    ^
   Vin+|Vo|┼──────────────┐                      ┌──────────────┐
           │              │                      │              │
        0V ┼──────────────┴──────────────────────┴──────────────┴────> Time
           │◄─── D*Ts ───►│◄──── (1-D)*Ts ──────►│
```

---

## 3. Mathematical Formulations & Transfer Function

### 3.1 Voltage Conversion Ratio:
Applying volt-second balance to input inductor $L_1$:
$$V_{IN} \cdot D + (V_{IN} - V_{C1}) \cdot (1 - D) = 0 \implies V_{C1} = \frac{V_{IN}}{1 - D}$$

Applying volt-second balance to output inductor $L_2$:
$$(V_{C1} - |V_o|) \cdot D + (-|V_o|) \cdot (1 - D) = 0 \implies V_{C1} \cdot D - |V_o| = 0 \implies |V_o| = D \cdot V_{C1}$$

Substituting $V_{C1}$:
$$|V_o| = V_{IN} \cdot \frac{D}{1 - D} \implies V_o = -V_{IN} \cdot \frac{D}{1 - D}$$

### 3.2 Component Sizing Equations:
1. **Input Inductor ($L_1$)**:
   $$L_1 = \frac{V_{IN} \cdot D}{f_s \cdot \Delta I_{L1}}$$
2. **Output Inductor ($L_2$)**:
   $$L_2 = \frac{|V_o| \cdot (1 - D)}{f_s \cdot \Delta I_{L2}}$$
3. **Energy Transfer Capacitor ($C_1$)**:
   $C_1$ carries the full load current during switch ON time. To restrict capacitor ripple to $\Delta V_{C1}$:
   $$C_1 = \frac{I_o \cdot D}{f_s \cdot \Delta V_{C1}}$$
4. **Switch & Diode Stresses**:
   Both the MOSFET $Q_1$ and diode $D_1$ must withstand the combined rail voltage:
   $$V_{DS,max} = V_{diode,rev} = V_{IN} + |V_o|$$

---

## 4. The Coupled-Inductor Zero-Ripple Phenomenon

Because both inductors $L_1$ and $L_2$ experience identical AC voltage waveforms across their terminals ($(V_{IN} - V_{C1})$ and $-|V_o|$), they can be **wound onto a single magnetic core**:

```text
                     Coupled-Inductor Ćuk Configuration
                     L1 (Primary)            C1             L2 (Secondary)
   +Vin ─────────────^^^^^^──────┬──────────[  ]─────────┬───^^^^^^─────────┬───> -Vout
                       ││        │                       │     ││           │
                       ││ M      │                       │     ││ M        ┌┴┐
                       ││        │                       │     ││          │ │ Co
   GND  ─────────────────────────┴───────────────────────┴─────────────────┴─── GND
```

### 4.1 Ripple Steering Mechanism:
With mutual inductance $M = k \sqrt{L_1 L_2}$ between the two windings:
$$\frac{di_{L1}}{dt} = \frac{v_1 \cdot (L_2 - M)}{L_1 L_2 - M^2}, \quad \frac{di_{L2}}{dt} = \frac{v_2 \cdot (L_1 - M)}{L_1 L_2 - M^2}$$
If the turns ratio is selected such that:
$$M = L_2 \implies k \sqrt{\frac{L_1}{L_2}} = 1 \implies \frac{N_1}{N_2} = \frac{1}{k}$$
The AC ripple current in inductor $L_2$ is **driven identically to zero ($\Delta i_{L2} = 0$)**!
All AC switching ripple is "steered" into the input inductor $L_1$, yielding **completely DC, ripple-free current at the output** without requiring a massive electrolytic capacitor!

---

## 5. Engineering Trade-Offs & Application Domain

| Advantage | Engineering Challenge |
| :--- | :--- |
| **Continuous currents at both input and output** (ultra-low conducted EMI). | Inverted output voltage polarity. |
| **Zero output ripple** achievable via magnetic coupling. | High component count: 2 inductors + 2 capacitors. |
| Non-pulsating currents extend battery and capacitor lifetime. | High voltage stress ($V_{IN} + |V_o|$) on semiconductor switches. |
| Ideal for ultra-low noise instrumentation, audio amplifiers, RF PA bias. | Coupling capacitor $C_1$ carries high AC RMS ripple current ($I_{C1,rms} \approx I_o \sqrt{D}$). |
