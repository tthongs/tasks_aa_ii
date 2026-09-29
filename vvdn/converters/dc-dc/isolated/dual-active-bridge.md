# Dual Active Bridge (DAB) DC-DC Converter: Bidirectional Physics, Modulation & ZVS

Welcome to the **VVDN Engineering Hub Technical Dossier on the Dual Active Bridge (DAB) Converter**. This guide provides an advanced mathematical and hardware analysis of the DAB topology—the premier isolated bidirectional DC-DC architecture for Electric Vehicle (EV) onboard chargers, Vehicle-to-Grid (V2G) systems, battery energy storage systems (BESS), and solid-state transformers (SST).

---

## 1. Operating Principle & Bidirectional Architecture

The **Dual Active Bridge (DAB)** converter comprises two active full-bridge (H-bridge) switching stages coupled across a high-frequency isolation transformer with an energy-transfer power inductance ($L$):

```text
                           Dual Active Bridge (DAB) Power Stage
  ========== PRIMARY BRIDGE (PORT 1: V1) ==========       ========== SECONDARY BRIDGE (PORT 2: V2) ==========
  +V1 DC ────┬──────────────────┬─────────────────┐        +V2 DC ────┬──────────────────┬─────────────────┐
             │                  │                 │                   │                  │                 │
         Drain (D)          Drain (D)             │               Drain (D)          Drain (D)             │
         ┌───┴───┐          ┌───┴───┐             │               ┌───┴───┐          ┌───┴───┐             │
         │  S1   │          │  S3   │           ┌─┴─┐ C1          │  S5   │          │  S7   │           ┌─┴─┐ C2
         └───┬───┘          └───┬───┘           │   │             └───┬───┘          └───┬───┘           │   │
             │ Source (S)       │ Source (S)    └─┬─┘                 │ Source (S)       │ Source (S)    └─┬─┘
             ├─── Leg A ──┐     ├─── Leg B ─┐     │                   ├─── Leg C ──┐     ├─── Leg D ─┐     │
             │            │     │           │     │                   │            │     │           │     │
         Drain (D)        │ Drain (D)       │     │               Drain (D)        │ Drain (D)       │     │
         ┌───┴───┐        │ ┌───┴───┐       │     │               ┌───┴───┐        │ ┌───┴───┐       │     │
         │  S2   │        │ │  S4   │       │     │               │  S6   │        │ │  S8   │       │     │
         └───┬───┘        │ └───┬───┘       │     │               └───┬───┘        │ └───┬───┘       │     │
             │ Source (S) │     │ Source (S)│     │                   │ Source (S) │     │ Source (S)│     │
          GND_1 ──────────┴─────┴───────────┴─────┴── GND_1        GND_2 ──────────┴─────┴───────────┴─────┴── GND_2
                          │                 │                                      │                 │
                          ├───[ Inductor L ]┼───[ Transformer Primary: N1 ]───┐    │                 │
                          │   (Energy Trans)│             ││                  │    │                 │
                          │                 └─────────────┼───────────────────┘    │                 │
                          │                               ││                       │                 │
                          │                     [ Transformer Secondary: N2 ]──────┴─────────────────┘
                          │                               ││
```

### 1.1 Core Energy Transfer Mechanism:
1. Both primary and secondary bridges generate high-frequency AC square-wave voltages ($v_{ac1}$ and $v_{ac2}$) with $50\%$ duty cycle at frequency $f_s$ ($50\,\text{kHz} \dots 200\,\text{kHz}$).
2. Power transfer is **not** controlled by varying duty cycle or frequency; instead, it is governed by the **Phase-Shift Angle ($\phi$)** between the primary AC square wave and the secondary AC square wave across the energy-transfer inductor ($L$):
   - **Forward Power Flow ($P_{1 \rightarrow 2}$)**: Primary leads Secondary ($\phi > 0$).
   - **Reverse Power Flow ($P_{2 \rightarrow 1}$)**: Secondary leads Primary ($\phi < 0$).
   - **Zero Power Flow ($P = 0$)**: Bridges are in exact phase synchronization ($\phi = 0$).

---

## 2. Mathematical Formulations & Phase-Shift Modulation

```text
                  Single Phase Shift (SPS) Key Waveforms
  v_ac1 ^        +V1
        │   ┌──────────────┐              ┌──────────────┐
        └───┘              └──────────────┘              └───────> Time
                           -V1
  v_ac2 ^               +V2' (Reflected)
        │         ┌──────────────┐              ┌──────────────┐
        └─────────┘              └──────────────┘              ──> Time
            │◄─φ─►│
            Phase Shift Angle
  i_L   ^           I_pk
        │          / \                           / \
        │         /   \                         /   \
     0A ┼────────/─────\───────────────────────/─────\───────────> Time
        │       /       \                     /       \
        │      /         \-I_pk              /         \-I_pk
```

### 2.1 Transferred Power Equation (Single Phase Shift - SPS):
Defining the normalized phase-shift ratio $d = \frac{\phi}{\pi}$ (where $-1 \le d \le 1$):

$$P = \frac{V_1 \cdot V_2'}{2\pi f_s L} \cdot \phi \left(1 - \frac{|\phi|}{\pi}\right) = \frac{V_1 \cdot (n V_2)}{2 f_s L} \cdot d (1 - |d|)$$
where:
- $V_1$: DC voltage of Port 1
- $V_2' = n \cdot V_2$: DC voltage of Port 2 reflected to primary ($n = N_1 / N_2$)
- $L = L_{ext} + L_{leakage}$: Total series energy-transfer inductance
- $f_s$: Switching frequency ($\text{Hz}$)

### 2.2 Maximum Transferred Power:
The power parabolic curve peaks at a phase shift of **$90^\circ$ ($\phi = \pi/2$, or $d = 0.5$)**:
$$P_{max} = \frac{V_1 \cdot V_2'}{8 f_s L}$$
*Engineering Design Guideline*: Normal operating power is sized at $d_{nom} \approx 0.2 \dots 0.35$ ($\phi \approx 36^\circ \dots 63^\circ$) to reserve dynamic margin and maintain high efficiency.

---

## 3. Zero-Voltage Switching (ZVS) Soft-Switching Boundaries

The DAB topology achieves ultra-high efficiency ($> 97.5\%$) by operating with **Zero-Voltage Switching (ZVS)** on all 8 switches:
- Before each MOSFET turns on, the circulating inductive current $i_L(t)$ discharges the output capacitance ($C_{oss}$) of the incoming switch and charges $C_{oss}$ of the outgoing switch.
- When $V_{DS}$ drops to zero, the anti-parallel body diode clamps the switch to zero volts, allowing lossless turn-on ($P_{sw(on)} = 0$).

```text
               ZVS Operating Range as a Function of Voltage Ratio (M)
   Phase Shift (d) ^
               0.5 ┼─────────────────────────────────────────────┐
                   │               FULL ZVS REGION               │
                   │           (All 8 switches achieve           │
                   │            Zero-Voltage Switching)          │
                   │                 .─────────.                 │
                   │             .──'           '──.             │
                   │         .──'                   '──.         │
                   │     .──'                           '──.     │
               0.0 ┴────'───────────────────────────────────'────┴───> Voltage Ratio M
                   0.0                 1.0                 2.0        (M = n*V2 / V1)
```

### ZVS Condition Formulations:
Defining the voltage conversion ratio $M = \frac{n V_2}{V_1}$:
1. **Primary Bridge ZVS Condition**:
   $$d \ge \frac{M - 1}{2 M} \quad (\text{For } M > 1)$$
2. **Secondary Bridge ZVS Condition**:
   $$d \ge \frac{1 - M}{2} \quad (\text{For } M < 1)$$
- When $M = 1.0$ (perfectly matched transformer ratio), **ZVS is maintained down to virtually zero load**!
- When $M \neq 1.0$ at light loads, inductive energy is insufficient to completely discharge $C_{oss}$, causing loss of ZVS and increased switching dissipation.

---

## 4. Advanced Modulation Strategies

To extend the soft-switching ZVS boundary and eliminate reactive circulating currents during light-load operation, advanced multi-variable modulation techniques are employed:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          DAB Modulation Strategies Comparison                     │
├─────────────────────┬───────────────────┬─────────────────────────────────────────┤
│ Modulation Strategy │ Control Degrees   │ Engineering Advantages                  │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Single Phase Shift│ 1 Degree of       │ Simplest control implementation;        │
│ (SPS)**             │ Freedom ($\phi$)  │ high circulating current at light load. │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Extended Phase    │ 2 Degrees         │ Introduces inner duty cycle on primary  │
│ Shift (EPS)**       │ ($\phi, D_1$)     │ bridge; expands ZVS down to 20% load.   │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Dual Phase Shift  │ 2 Degrees         │ Synchronized inner duty cycles          │
│ (DPS)**             │ ($\phi, D_1=D_2$) │ ($D_1 = D_2$); slashes reactive power.  │
├─────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ **Triple Phase Shift│ 3 Degrees         │ Independent control of $\phi, D_1, D_2$;│
│ (TPS)**             │ ($\phi, D_1, D_2$)│ Global minimum RMS current optimization.│
└─────────────────────┴───────────────────┴─────────────────────────────────────────┘
```

---

## 5. Industrial Design Example: 10 kW EV Fast-Charging DAB Stage

- **Port 1 (DC Bus)**: $V_1 = 400\,\text{V}$ DC
- **Port 2 (EV Battery)**: $V_2 = 300\,\text{V} \dots 450\,\text{V}$ DC (Nominal $400\,\text{V}$)
- **Target Power**: $P = 10.0\,\text{kW}$
- **Switching Frequency**: $f_s = 100\,\text{kHz}$
- **Transformer Ratio**: $n = N_1 / N_2 = 1.0$
- **Nominal Phase Shift**: $d = 0.25$ ($\phi = 45^\circ$)

### Energy-Transfer Inductor Sizing ($L$):
$$L = \frac{V_1 \cdot (n V_2)}{2 f_s \cdot P} \cdot d(1 - d) = \frac{400 \times 400}{2 \cdot 100000 \cdot 10000} \cdot 0.25(1 - 0.25) = \frac{160000}{2 \times 10^9} \cdot 0.1875 = \mathbf{15.0\,\mu\text{H}}$$
*Inductor Realization*: High-frequency low-loss Sendust / Nanocrystalline distributed-gap toroidal inductor carrying $35\,\text{A}_{\text{RMS}}$ AC current.
