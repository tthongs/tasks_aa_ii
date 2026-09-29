# Three-Phase DC-AC Inverters: 6-Switch VSI, THIPWM & Space Vector PWM (SVPWM)

Welcome to the **VVDN Engineering Hub Technical Dossier on Three-Phase DC-AC Inverters**. The three-phase Voltage Source Inverter (VSI) is the undisputed powerhouse of modern industrial motor drives (Variable Frequency Drives - VFD), Electric Vehicle (EV) traction inverters, high-power grid-connected solar farms, and wind power generation systems.

This guide provides an exhaustive mathematical and hardware analysis covering the two-level 6-switch VSI topology, six-step conduction modes, Third-Harmonic Injection PWM (THIPWM), and a masterclass deep dive into **Space Vector Pulse-Width Modulation (SVPWM)**.

---

## 1. Operating Principle & 6-Switch VSI Topology

The three-phase two-level VSI comprises three identical half-bridge phase legs (Leg U, Leg V, Leg W) connected across a common stiff DC link:

```text
                        Three-Phase Two-Level Voltage Source Inverter (VSI)
   +Vdc ────┬───────────────────────┬───────────────────────┬───────────────────────────────────┐
            │                       │                       │                                   │
        Drain (D)               Drain (D)               Drain (D)                               │
        ┌───┴───┐ S1            ┌───┴───┐ S3            ┌───┴───┐ S5                           ┌┴┐
        │  Q1   │ Leg U High    │  Q3   │ Leg V High    │  Q5   │ Leg W High                   │ │ C_dc
        └───┬───┘               └───┬───┘               └───┬───┘                              └┬┘
            │ Source (S)            │ Source (S)            │ Source (S)                        │
            ├─── Phase U (A) ───────┼───────────────────────┼───────────────────┐               │
            │                       ├─── Phase V (B) ───────┼───────────────┐   │               │
            │                       │                       ├─── Phase W (C)┼───┼───────────┐   │
            │                       │                       │               │   │           │   │
        Drain (D)               Drain (D)               Drain (D)           │   │           │   │
        ┌───┴───┐ S2            ┌───┴───┐ S4            ┌───┴───┐ S6        │   │           │   │
        │  Q2   │ Leg U Low     │  Q4   │ Leg V Low     │  Q6   │ Leg W Low │   │           │   │
        └───┬───┘               └───┬───┘               └───┬───┘           │   │           │   │
            │ Source (S)            │ Source (S)            │ Source (S)    │   │           │   │
   GND ─────┴───────────────────────┴───────────────────────┴───────────────┼───┼───────────┼───┴─── GND
                                                                            │   │           │
                                                                   ┌────────┴───┴───────────┴────────┐
                                                                   │ 3-Phase AC Motor / Grid (U,V,W) │
                                                                   └─────────────────────────────────┘
```

### 1.1 Switching Logic & Pole Voltages:
Each leg switch state can be defined by a binary variable $S_x \in \{0, 1\}$ (where $x \in \{u, v, w\}$):
- $S_x = 1$: High-side switch $Q_{high}$ is ON; leg terminal voltage $v_{xN} = V_{dc}$.
- $S_x = 0$: Low-side switch $Q_{low}$ is ON; leg terminal voltage $v_{xN} = 0\,\text{V}$.

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

- **$180^\circ$ Conduction Mode**: Exactly 3 switches are ON at any given instant. While generating maximum fundamental power, the output is a stepped six-step waveform with large low-order harmonics ($5th, 7th, 11th$), causing severe motor torque ripple and thermal losses.
- **Modern Drive Requirement**: Variable frequency drives (VFD) and EV traction systems require high-frequency PWM to eliminate low-order harmonics.

---

## 3. Sinusoidal PWM vs. Third-Harmonic Injection (THIPWM)

### 3.1 Standard SPWM Limitation:
In standard SPWM, three sinusoidal reference waves shifted by $120^\circ$ are compared against a common triangular carrier:
- Linear modulation limit: $m_a \le 1.0$.
- The maximum fundamental peak phase-to-neutral voltage is $\hat{V}_{ph} = \frac{V_{dc}}{2}$.
- The maximum RMS line-to-line voltage is:
  $$V_{LL,rms} = \frac{\sqrt{3} \cdot \hat{V}_{ph}}{\sqrt{2}} = \frac{\sqrt{3} \cdot V_{dc}}{2 \sqrt{2}} \approx 0.612 \cdot V_{dc}$$
- *Problem*: Almost $39\%$ of the available DC-bus voltage capability is wasted!

### 3.2 Third-Harmonic Injection (THIPWM):
By injecting a third harmonic with an amplitude of $\frac{1}{6}$ of the fundamental into each phase reference:
$$v_{ref,u}(t) = \hat{V}_1 \sin(\omega t) + \frac{1}{6} \hat{V}_1 \sin(3\omega t)$$

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
- Because the three phases are identical, the third-harmonic components cancel out completely in the line-to-line differential voltages ($v_{uv} = v_u - v_v$).
- **The Result**: Maximum modulation index increases from $m_a = 1.0$ to $m_a = \frac{2}{\sqrt{3}} \approx 1.155$ without entering non-linear overmodulation, boosting AC output voltage by **$15.5\%$**!

---

## 4. Space Vector PWM (SVPWM) Masterclass

**Space Vector PWM (SVPWM)** is the mathematical and industrial pinnacle of inverter modulation, providing optimal harmonic cancellation and maximizing DC bus utilization.

### 4.1 Clarke Transformation to the Stationary $\alpha-\beta$ Frame:
The three instantaneous phase voltages are mapped onto a two-dimensional orthogonal complex plane:
$$\begin{bmatrix} v_\alpha \\ v_\beta \end{bmatrix} = \frac{2}{3} \begin{bmatrix} 1 & -\frac{1}{2} & -\frac{1}{2} \\ 0 & \frac{\sqrt{3}}{2} & -\frac{\sqrt{3}}{2} \end{bmatrix} \begin{bmatrix} v_u \\ v_v \\ v_w \end{bmatrix}$$

### 4.2 The Eight Voltage Space Vectors:
With 3 switch legs and 2 states per leg ($S_u, S_v, S_w$), there are $2^3 = 8$ possible switching combinations:

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

1. **Six Active Vectors ($V_1 \dots V_6$)**:
   Each vector has a magnitude of $\frac{2}{3} V_{dc}$ and is separated from its neighbors by $60^\circ$, forming the vertices of a regular hexagon.
   - $V_1(100): \theta = 0^\circ$
   - $V_2(110): \theta = 60^\circ$
   - $V_3(010): \theta = 120^\circ$
   - $V_4(011): \theta = 180^\circ$
   - $V_5(001): \theta = 240^\circ$
   - $V_6(101): \theta = 300^\circ$
2. **Two Zero Vectors ($V_0, V_7$)**:
   - $V_0(000)$: All three low-side switches are ON; phase terminals shorted to GND.
   - $V_7(111)$: All three high-side switches are ON; phase terminals shorted to $+V_{dc}$.
   - Magnitude is identically **0 Volts**.

---

## 5. Dwell Time Formulations & Symmetric Switching

To synthesize an arbitrary rotating reference voltage vector $\vec{V}_{ref}$ at angle $\theta$ inside **Sector 1** ($0 \le \theta \le 60^\circ$), the inverter time-averages the two adjacent active vectors ($V_1, V_2$) and the zero vectors ($V_0, V_7$) over switching period $T_s$:

$$\vec{V}_{ref} \cdot T_s = \vec{V}_1 \cdot T_1 + \vec{V}_2 \cdot T_2 + \vec{V}_z \cdot T_0$$

### 5.1 Dwell Time Equations for Sector 1:
$$T_1 = \sqrt{3} \cdot T_s \cdot \frac{|\vec{V}_{ref}|}{V_{dc}} \cdot \sin\left(\frac{\pi}{3} - \theta\right)$$
$$T_2 = \sqrt{3} \cdot T_s \cdot \frac{|\vec{V}_{ref}|}{V_{dc}} \cdot \sin(\theta)$$
$$T_0 = T_s - T_1 - T_2$$
*(Where $T_0$ is divided equally between zero states $V_0$ and $V_7$: $T_{V0} = T_{V7} = \frac{T_0}{2}$.)*

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
1. **Single-Leg Toggling**: At every state transition, **only one phase leg changes state** ($0 \rightarrow 1$ or $1 \rightarrow 0$), minimizing switching losses.
2. **Maximum Linear AC Output**: The maximum radius of the reference vector corresponds to the inscribed circle of the hexagon:
   $$|\vec{V}_{ref,max}| = \frac{2}{3} V_{dc} \cdot \cos(30^\circ) = \frac{V_{dc}}{\sqrt{3}} \approx 0.577 \cdot V_{dc}$$
   The resulting maximum fundamental line-to-line RMS voltage is:
   $$V_{LL,rms} = \frac{\sqrt{3} \cdot |\vec{V}_{ref,max}|}{\sqrt{2}} = \frac{V_{dc}}{\sqrt{2}} \approx 0.707 \cdot V_{dc}$$
   **SVPWM achieves a full $15.5\%$ increase in AC output voltage over standard sinusoidal SPWM ($0.707$ vs. $0.612$)!**
3. **Harmonic Cancellation**: Center-aligned symmetric PWM eliminates all even harmonics and significantly reduces total harmonic distortion (THD).
