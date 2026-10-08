# Dossier 1: System Specifications & Topology Selection

Welcome to **Dossier 1** of the Step-by-Step 4-Switch Synchronous Buck-Boost Post-Regulator Design Guide. This document establishes the foundational design requirements, boundary operating conditions, topology trade-offs, and multi-mode operational state machine.

---

## Step 1: System Requirements & Parameter Envelopes

The post-regulator operates downstream of the isolated primary Quasi-Resonant (QR) Flyback converter ($+24.0\,\text{V} \pm 1.0\%$ DC bus). It provides a digitally programmable output voltage from **$5.0\,\text{V}$ to $20.0\,\text{V}$ DC** at continuous currents up to **$3.0\,\text{A}$** ($60.0\,\text{W}$ maximum continuous output power).

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      STEP 1: COMPREHENSIVE PARAMETER DESIGN ENVELOPE                             │
├────────────────────────────┬─────────────────────────────┬───────────────────────────────────────┤
│ Parameter / Specification  │ Value Range / Unit          │ Engineering Margin / Condition        │
├────────────────────────────┼─────────────────────────────┼───────────────────────────────────────┤
│ **Input Voltage ($V_{IN}$)**│ $+24.0\,\text{V}$ Nominal   │ Delivered by Isolated Primary Flyback │
│ **Input Voltage Tolerance**│ $22.0\,\text{V} \dots 26.0\,\text{V}$│ Dynamic tolerance under line/load sag │
│ **Output Voltage ($V_O$)** │ $5.0\,\text{V} \dots 20.0\,\text{V}$│ Digitally programmable (4:1 span)     │
│ **Voltage Programming Step│ $10\,\text{mV}$ Step Size   │ Commanded via MCU 12-bit DAC          │
│ **Continuous Current ($I_O$)│ $0.1\,\text{A} \dots 3.0\,\text{A}$│ Full rated current down to 5.0V out   │
│ **Current Limit Step**     │ $10\,\text{mA}$ Step Size   │ Hardware Constant Current (CC) clamp  │
│ **Maximum Output Power**   │ $60.0\,\text{W}$ Continuous │ Full-range load ($20\,\text{V} \times 3\,\text{A}$)   │
│ **Switching Frequency**    │ $250\,\text{kHz}$ Fixed PWM │ Optimized for inductor size vs loss   │
│ **Output Voltage Ripple**  │ $< 25\,\text{mV}_{\text{pk-pk}}$│ Full load $20\,\text{V} / 3\,\text{A}$, 20MHz BW  │
│ **Output Ripple at 5V/3A** │ $< 15\,\text{mV}_{\text{pk-pk}}$│ Pure buck mode operation              │
│ **Peak Conversion Eff.**   │ $\ge 96.5\%$ @ 15V / 3A     │ Synchronous rectification across FETs │
│ **Average Conversion Eff.**│ $> 94.5\%$ Across Range     │ Convection cooled, fanless enclosure  │
│ **Load Transient Recovery**│ $< 120\,\mu\text{s}$ to 1%  │ $50\% \rightarrow 100\%$ load step ($1.5A \rightarrow 3.0A$)│
│ **Load Transient Deviation**│ $< 250\,\text{mV}$ Peak     │ Under $1.5\,\text{A}/\mu\text{s}$ load slew rate     │
│ **Ambient Temperature**    │ $-20^\circ\text{C} \dots +70^\circ\text{C}$│ Industrial bench environment          │
│ **Target Junction Temp**   │ $T_j \le 100^\circ\text{C}$ │ Safe derating below $150^\circ\text{C}$ max limit│
└────────────────────────────┴─────────────────────────────┴───────────────────────────────────────┘
```

---

## Step 2: Topology Selection & Operating Principles

### 2.1 Why the 4-Switch Non-Inverting Synchronous Buck-Boost (H-Bridge)?
When an application requires an output voltage ($5.0\,\text{V} \dots 20.0\,\text{V}$) that can be both lower than and near the nominal input rail ($24.0\,\text{V}$), three classical topologies exist:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TOPOLOGY TRADE-OFF COMPARISON                                    │
├───────────────────────┬───────────────────────────┬──────────────────────────────────────────────┤
│ Topology Candidate    │ Key Advantages            │ Fatal Disadvantages / Elimination Rationale  │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Traditional Single- │ Simple, only 1 switch and │ **Negative Output Voltage**: Inverts polarity│
│ Switch Inverting BB** │ 1 diode.                  │ ($-5\text{V} \dots -20\text{V}$). Incompatible│
│                       │                           │ with common-ground bench test equipment!     │
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **Single-Ended Primary│ Non-inverting, 1 switch,  │ Series AC capacitor ($C_{sep}$) carries full │
│ Inductor (SEPIC)**    │ ground-referenced drive.  │ RMS load current ($2.74\,\text{A}_{\text{RMS}}$),│
│                       │                           │ causing high $I^2R$ ESR heating; eff $< 94\%$.│
├───────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ **4-Switch Synchronous│ **Positive non-inverting**│ Requires two high-side floating gate drivers.│
│ H-Bridge (CHOSEN)**   │ **output, peak eff >96.5%,│ *(Easily resolved using modern integrated    │
│                       │ pure buck mode efficiency,│  controllers such as TI LM5176).*            │
│                       │ sub-25mV ripple.**        │                                              │
└───────────────────────┴───────────────────────────┴──────────────────────────────────────────────┘
```

### 2.2 4-Switch H-Bridge Power Stage Circuit:
The 4-switch topology consists of two half-bridges connected across a single power inductor ($L$):
* **Buck Half-Bridge**: Switch $Q_A$ (High-Side) and Synchronous Switch $Q_B$ (Low-Side) at node `SW1`.
* **Boost Half-Bridge**: Switch $Q_C$ (Low-Side) and Synchronous Switch $Q_D$ (High-Side) at node `SW2`.

```text
                                 4-Switch H-Bridge Topology
                    +24V DC Bus In
                         │
                     Drain (D)
                     ┌───┴───┐
                     │  Q_A  │ Buck High-Side Switch
            PWM_A ───┤       │ (BSC034N04LS: 40V, 3.4mΩ)
                     └───┬───┘
                         │ Source (S)
                         ├────── SW1 Node ──────[ Inductor L: 10µH ]────── SW2 Node ──────┬───> +V_OUT (5V-20V @ 3A)
                         │                                                                 │
                     Drain (D)                                                         Source (S)
                     ┌───┴───┐                                                         ┌───┴───┐
            PWM_B ───┤  Q_B  │ Buck Low-Side Sync                             PWM_D ───┤  Q_D  │ Boost High-Side Sync
                     └───┬───┘ (BSC034N04LS)                                           └───┬───┘ (BSC034N04LS)
                         │ Source (S)                                                      │ Drain (D)
                      PGND_SEC                                                         Drain (D)
                                                                                       ┌───┴───┐
                                                                              PWM_C ───┤  Q_C  │ Boost Low-Side Switch
                                                                                       └───┬───┘ (BSC034N04LS)
                                                                                           │ Source (S)
                                                                                        PGND_SEC
```

---

## 2.3 Multi-Mode Operational State Machine

To maximize efficiency and eliminate unnecessary switching losses, the controller ([TI LM5176](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply/mcu-buck-boost-post-regulator.md#L222)) operates in **three distinct operational modes** based on the relationship between $V_{IN}$ and $V_{OUT}$:

```text
                             MULTI-MODE CONTROL REGIME MAP
  Output Voltage (V_OUT)
    ^
20V ┼────────────────────────────────────────────────────────── [ BUCK-BOOST TRANSITION MODE ]
    │                                                           - Alternating Buck & Boost cycles
18V ┼────────────────────────────────────────────────────────── - All 4 switches active (smooth transition)
    │
    │
    │                                                           [ PURE BUCK MODE ]
    │                                                           - Q_C is OFF (0% duty cycle)
    │                                                           - Q_D is ON (100% continuous conduction)
    │                                                           - Only Q_A and Q_B switch at 250 kHz!
    │                                                           - D_buck = V_OUT / V_IN (20.8% to 75.0%)
    │                                                           - Slashing switching loss by 50%!
    │
 5V ┼──────────────────────────────────────────────────────────
    └─────────────────────────────────────────────────────────> Time
```

### 1. Pure Buck Mode ($V_{OUT} < 0.85 \times V_{IN}$, i.e., $V_{OUT} = 5.0\,\text{V} \dots 18.0\,\text{V}$):
* **Switch States**:
  * $Q_C$ is held **permanently OFF** ($0\%$ duty cycle).
  * $Q_D$ is held **permanently ON** ($100\%$ duty cycle, acting as a low-resistance $3.4\,\text{m}\Omega$ pass transistor).
  * $Q_A$ and $Q_B$ switch synchronously at $250\,\text{kHz}$:
    $$D_{buck} = \frac{V_{OUT}}{V_{IN}} = \frac{5.0\,\text{V}}{24.0\,\text{V}} = 20.8\% \dots \frac{18.0\,\text{V}}{24.0\,\text{V}} = 75.0\%$$
* **Efficiency Impact**: Only two switches toggle! Boost switching losses and inductor reverse ringing are **zero**, enabling peak efficiencies of **$96.8\%$**.

### 2. Buck-Boost Transition Mode ($0.85 \times V_{IN} \le V_{OUT} \le 1.15 \times V_{IN}$, i.e., $V_{OUT} = 18.0\,\text{V} \dots 20.0\,\text{V}$):
* When $V_{OUT}$ approaches $V_{IN}$ ($20.0\,\text{V} \approx 24.0\,\text{V}$), pure buck mode requires $D \approx 83\%$, where narrow off-times cause pulse-skipping or erratic jitter.
* The controller engages an **interleaved buck-boost switching cycle**:
  * Cycle 1: Buck pulse (induces energy into $L$).
  * Cycle 2: Boost pulse (steps up energy from $L$ into $C_{OUT}$).
* This ensures seamless, monotonic voltage control with zero subharmonic oscillation or output ripple bursts.

### 3. Pure Boost Mode (when $V_{IN} < 0.85 \times V_{OUT}$, e.g., input sag to $18\,\text{V}$):
* $Q_A$ is held **permanently ON** ($100\%$ duty cycle).
* $Q_B$ is held **permanently OFF**.
* $Q_C$ and $Q_D$ switch synchronously at $250\,\text{kHz}$:
  $$D_{boost} = 1 - \frac{V_{IN}}{V_{OUT}} = 1 - \frac{18.0\,\text{V}}{20.0\,\text{V}} = 10.0\%$$

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             SWITCH OPERATING STATES ACROSS REGIMES                               │
├───────────────────────┬──────────────┬──────────────┬──────────────┬─────────────────────────────┤
│ Switch Identifier     │ Pure Buck    │ Buck-Boost   │ Pure Boost   │ Function / Implementation   │
├───────────────────────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│ **Q_A (Buck High)**   │ Switching    │ Switching    │ ON (100%)    │ High-side floating drive    │
│ **Q_B (Buck Low)**    │ Switching    │ Switching    │ OFF (0%)     │ Ground-referenced sync rect │
│ **Q_C (Boost Low)**   │ OFF (0%)     │ Switching    │ Switching    │ Ground-referenced switch    │
│ **Q_D (Boost High)**  │ ON (100%)    │ Switching    │ Switching    │ High-side floating sync rect│
└───────────────────────┴──────────────┴──────────────┴──────────────┴─────────────────────────────┘
```
