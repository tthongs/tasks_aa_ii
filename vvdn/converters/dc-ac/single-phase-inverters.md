# Single-Phase DC-AC Inverters: Topologies, Unipolar/Bipolar SPWM & Filter Design

Welcome to the **VVDN Engineering Hub Technical Dossier on Single-Phase DC-AC Inverters**. Single-phase inverters convert a DC source into a sinusoidal AC output voltage and form the core of residential solar micro-inverters, Uninterruptible Power Supplies (UPS), battery power backup systems, and mobile power inverters.

This guide provides a comprehensive hardware analysis covering Half-Bridge and Full-Bridge (H-Bridge) topologies, square-wave vs. quasi-square modulation, mathematical derivations of Bipolar and Unipolar Sinusoidal PWM (SPWM), carrier frequency harmonic cancellation, and LC output low-pass filter design.

---

## 1. Operating Principle & Inverter Architectures

### 1.1 Half-Bridge Inverter:
The Half-Bridge inverter employs two switches and a split DC bus capacitor divider:

```text
                        Half-Bridge Inverter Power Stage
   +Vdc ────┬─────────────────────────────┬─────────────────────────────────┐
            │                             │                                 │
        Drain (D)                         │                                 │
        ┌───┴───┐ S1                      │                                ┌┴┐
        │  Q1   │ High-Side Switch      ┌─┴─┐ C1                           │ │ C_bulk
        └───┬───┘                       │   │                              └┬┘
            │ Source (S)                └─┬─┘                               │
            ├─── Switching Leg A ─────────┼───[ Filter Lf ]───┬───> +VAC    │
            │                             ├─── Split Neutral ─┼─────> -VAC  │
        Drain (D)                         │    Point (0V)    ┌┴┐            │
        ┌───┴───┐ S2                    ┌─┴─┐ C2             │ │ Cf         │
        │  Q2   │ Low-Side Switch       │   │                └┬┘            │
        └───┬───┘                       └─┬─┘                 │             │
            │ Source (S)                  │                   │             │
   GND ─────┴─────────────────────────────┴───────────────────┴─────────────┴─── GND
```
- **Output Swing**: Node A swings between $+V_{dc}/2$ and $-V_{dc}/2$ relative to the neutral point.
- **Limitation**: The maximum peak fundamental AC voltage is $\hat{V}_{ac} = \frac{V_{dc}}{2}$. To generate $230\,\text{V}_{rms}$ ($325\,\text{V}_{peak}$), a DC bus of at least $650\,\text{V} \dots 700\,\text{V}$ is required.

---

### 1.2 Full-Bridge (H-Bridge) Inverter:
The Full-Bridge topology utilizes four switches in two bridge legs (Leg A and Leg B):

```text
                         Full-Bridge (H-Bridge) Inverter
   +Vdc ────┬───────────────────────┬───────────────────────────────────────┐
            │                       │                                       │
        Drain (D)               Drain (D)                                   │
        ┌───┴───┐ S1            ┌───┴───┐ S3                               ┌┴┐
        │  Q1   │ Leg A High    │  Q3   │ Leg B High                       │ │ C_bulk
        └───┬───┘               └───┬───┘                                  └┬┘
            │ Source (S)            │ Source (S)                            │
            ├─── Leg A Node ┐       ├─── Leg B Node ───┐                    │
            │               │       │                  │                    │
        Drain (D)           │   Drain (D)              │                    │
        ┌───┴───┐ S2        │   ┌───┴───┐ S4           │                    │
        │  Q2   │ Leg A Low │   │  Q4   │ Leg B Low    │                    │
        └───┬───┘           │   └───┬───┘              │                    │
            │ Source (S)    │       │ Source (S)       │                    │
   GND ─────┴───────────────┼───────┴──────────────────┼────────────────────┴─── GND
                            │                          │
                            ├───[ Filter Inductor Lf ]─┼───┐
                            │                          │  ┌┴┐
                            │                          └──┤ │ Filter Cap Cf
                            │                             └┬┘
                            │                              │
                            └──────────────────────────────┴───> AC Load (Vo = Va - Vb)
```
- **Output Swing**: Differential voltage $v_{AB} = v_A - v_B$ swings across three discrete levels: $+V_{dc}$, $0\,\text{V}$, and $-V_{dc}$.
- **Advantage**: Peak AC output voltage equals full $V_{dc}$ ($\hat{V}_{ac} = V_{dc}$), requiring only half the DC bus voltage of a half bridge ($V_{dc} \approx 350\,\text{V} \dots 400\,\text{V}$ for $230\,\text{V}_{rms}$).

---

## 2. Modulation Techniques: Bipolar vs. Unipolar SPWM

In **Sinusoidal Pulse-Width Modulation (SPWM)**, a high-frequency triangular carrier wave $v_{tri}(t)$ at switching frequency $f_c$ is compared against a low-frequency reference sine wave $v_{ref}(t)$ at grid frequency $f_m$ ($50\,\text{Hz}$):
- Amplitude Modulation Index: $m_a = \frac{\hat{V}_{ref}}{\hat{V}_{tri}} \quad (0 \le m_a \le 1)$
- Frequency Modulation Ratio: $m_f = \frac{f_c}{f_m}$

```text
                  Bipolar SPWM vs. Unipolar SPWM Output Waveforms
   BIPOLAR SPWM (2-Level Differential Output):
   v_AB  ^
   +Vdc  ┼──┐  ┌┐ ┌──┐ ┌───┐ ┌──┐ ┌┐  ┌──
         │  │  ││ │  │ │   │ │  │ ││  │
   -Vdc  ┼──┴──┴┴─┴──┴─┴───┴─┴──┴─┴┴──┴──> Time (Switches between +Vdc and -Vdc)
         │ First harmonic cluster appears at CARRIER FREQUENCY: f_c
   
   UNIPOLAR SPWM (3-Level Differential Output):
   v_AB  ^
   +Vdc  ┼──┐  ┌┐ ┌──┐ ┌───┐ ┌──┐ ┌┐  ┌──
         │  │  ││ │  │ │   │ │  │ ││  │
     0V  ┼──┴──┴┴─┴──┴─┴───┴─┴──┴─┴┴──┴───────────────
         │                                  ┌┐ ┌──┐ ┌───┐
   -Vdc  ┼──────────────────────────────────┴┴─┴──┴─┴───┴──> Time
         │ First harmonic cluster appears at DOUBLE CARRIER: 2 * f_c !
```

### 2.1 Bipolar SPWM:
- Diagonal switch pairs are driven simultaneously: $(S_1, S_4)$ ON together, or $(S_2, S_3)$ ON together.
- Output voltage $v_{AB}$ switches violently between $+V_{dc}$ and $-V_{dc}$.
- The dominant harmonic cluster appears around **carrier frequency $f_c$**.
- High $dv/dt$ stress and requires a large output filter inductor.

### 2.2 Unipolar SPWM (The Modern Standard):
- Bridge legs are modulated with two $180^\circ$ phase-opposed reference waves:
  - Leg A compares $v_{ref}(t)$ with $v_{tri}(t)$.
  - Leg B compares $-v_{ref}(t)$ with $v_{tri}(t)$.
- During the positive AC half-cycle, $v_{AB}$ alternates smoothly between **$+V_{dc}$ and $0\,\text{V}$**.
- During the negative AC half-cycle, $v_{AB}$ alternates smoothly between **$0\,\text{V}$ and $-V_{dc}$**.
- **Harmonic Doubling Feature**: The switching frequency ripple in Leg A and Leg B cancels differentially. The first major harmonic band appears at **$2 \cdot f_c$**!
  - For a $20\,\text{kHz}$ MOSFET switching frequency, the output filter only needs to attenuate ripple starting at **$40\,\text{kHz}$**, dramatically reducing inductor size and core losses.

---

## 3. Mathematical Formulations & Harmonic Spectrum

### 3.1 Fundamental Output Voltage:
In the linear modulation range ($m_a \le 1.0$):
$$\hat{V}_{fund} = m_a \cdot V_{dc} \implies V_{rms,fund} = \frac{m_a \cdot V_{dc}}{\sqrt{2}} \approx 0.707 \cdot m_a \cdot V_{dc}$$

### 3.2 Total Harmonic Distortion (THD) Standards:
$$\text{THD}_v = \frac{\sqrt{\sum_{h=2}^{\infty} V_h^2}}{V_1} \times 100\%$$
- Grid-tied standards (**IEEE 519 / IEC 61000-3-2**) mandate:
  - Individual voltage harmonics: $\le 3\%$
  - Total Voltage THD: $\le 5\%$

---

## 4. LC Output Low-Pass Filter Design

To transform the high-frequency pulsed PWM waveform into a clean $50\,\text{Hz}$ sine wave with $\text{THD} < 2\%$, a second-order LC low-pass filter is required:

```text
                             LC Low-Pass Filter Topology
                  Lf (Filter Inductor)
   Node A ────────────^^^^^^^^──────────┬──────────────────> Grid / Load L
                                        │
                                       ┌┴┐
                                       │ │ Cf (Film Capacitor)
                                       └┬┘
                                        │
   Node B ──────────────────────────────┴──────────────────> Grid / Load N
```

### 4.1 Filter Cutoff Frequency Selection:
The corner frequency $f_{cut}$ must be positioned comfortably between the fundamental line frequency ($f_m$) and the effective switching frequency ($f_{sw,eff} = 2 f_c$ for unipolar):
$$10 \cdot f_m \le f_{cut} \le \frac{1}{5} \cdot f_{sw,eff}$$
$$f_{cut} = \frac{1}{2\pi \sqrt{L_f \cdot C_f}}$$

### 4.2 Inductor Sizing ($L_f$):
The filter inductor limits the high-frequency ripple current. To restrict peak-to-peak ripple $\Delta I_L$ to $20\% \dots 30\%$ of rated peak load current $I_{pk}$:
$$L_f \ge \frac{V_{dc}}{8 \cdot f_{sw,eff} \cdot \Delta I_L}$$

### 4.3 Capacitor Sizing ($C_f$):
The capacitor must attenuate switching frequency harmonics without drawing excessive reactive VAR current at the fundamental frequency ($Q_{cap} \le 5\% \cdot S_{rated}$):
$$C_f \le \frac{0.05 \cdot P_{rated}}{2\pi \cdot f_m \cdot V_{ac,rms}^2}$$
And satisfies the corner frequency requirement:
$$C_f = \frac{1}{(2\pi f_{cut})^2 \cdot L_f}$$
*Component Rule*: Always specify low-dissipation-factor Metalized Polypropylene (MKP) film capacitors rated for continuous AC voltage (X2 / Snubber grade).

---

## 5. Practical Design Example: 3 kW 230V/50Hz Solar Inverter

- **DC Bus Voltage**: $V_{dc} = 400\,\text{V}$
- **Output Rating**: $V_o = 230\,\text{V}_{rms}$, $50\,\text{Hz}$, $P_o = 3000\,\text{W}$ ($I_{rms} = 13.04\,\text{A}$, $I_{pk} = 18.44\,\text{A}$)
- **Switching Frequency**: $f_c = 25\,\text{kHz}$ (Unipolar SPWM $\implies f_{sw,eff} = 50\,\text{kHz}$)
- **Modulation Index**:
  $$m_a = \frac{\sqrt{2} \cdot 230\,\text{V}}{400\,\text{V}} = \frac{325.3\,\text{V}}{400\,\text{V}} \approx 0.813$$
- **Inductor Sizing ($\Delta I_L = 20\% \cdot I_{pk} = 3.69\,\text{A}$)**:
  $$L_f = \frac{400\,\text{V}}{8 \cdot 50\,000\,\text{Hz} \cdot 3.69\,\text{A}} \approx 0.271\,\text{mH} \implies \text{Select } 0.33\,\text{mH}$$
- **Corner Frequency Selection**:
  $$f_{cut} = 2.5\,\text{kHz} \quad (10 \cdot 50\,\text{Hz} \ll 2.5\,\text{kHz} \ll 50\,\text{kHz})$$
- **Capacitor Sizing**:
  $$C_f = \frac{1}{(2\pi \cdot 2500)^2 \cdot 0.33 \cdot 10^{-3}} \approx 12.3\,\mu\text{F} \implies \text{Select } 10\,\mu\text{F / 300VAC MKP}$$
- **Reactive VAR Verification**:
  $$Q_c = 2\pi \cdot 50 \cdot 10\,\mu\text{F} \cdot (230\,\text{V})^2 \approx 166\,\text{VAR} \quad \left(\frac{166}{3000} \approx 5.5\% \text{ of rated power - fully compliant}\right)$$
