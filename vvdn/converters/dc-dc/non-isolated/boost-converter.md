# Step-Up (Boost) DC-DC Converter: Right-Half-Plane Zero, CCM/DCM & Design

Welcome to the **VVDN Engineering Hub Technical Dossier on the Step-Up (Boost) DC-DC Converter**. The Boost converter is fundamental to battery-powered electronics, solar maximum power point tracking (MPPT), LED backlight drivers, and Active Power Factor Correction (PFC) pre-regulators. 

This document explores the magnetic physics of boost energy transfer, derives the infamous **Right-Half-Plane (RHP) Zero** stability limitation, details diode reverse-recovery phenomena, and provides practical component selection criteria.

---

## 1. Operating Principle & Boost Topology

The **Boost Converter** steps up an input DC voltage $V_{IN}$ to a higher DC output voltage $V_o$ by utilizing an inductor to store energy from the source and discharge it in series with the source into the load:

```text
========================================================================================
         DETAILED HARDWARE SCHEMATIC: STEP-UP (BOOST) DC-DC CONVERTER (12V -> 24V/5A)
========================================================================================

    +VIN (+12V DC) ─────────────────────────────────────────────────────────────┐
        │                                                                       │
       [F1: 10A Fuse]                                                           │
        │                                                                       │
       ┌┴─────────────────┐                                                     │
       │ CIN_BULK         │                                                     │
      ┌┴┐ 220µF/25V Poly ┌┴┐ CIN_CER                                            │
      │ │ (Low-ESR 12mΩ) │ │ 2x 10µF/25V X7R                                    │
      └┬┘                └┬┘                                                    │
       │                  │                                                     │
       │                  │        BOOST POWER INDUCTOR                         │
       │                  │    +---[ L1: 15µH / 12A Shielded ]---+              │
       │                  │    |   Vishay IHLP-5050FD-01         |              │
       │                  │    |   (DCR = 9.5mΩ, Isat = 14A)     |              │
       │                  │    |                                 |              │
       │                  │    +---------------------------------+              │
       │                  │                                      │              │
       │                  │                                      +=== SWITCHING NODE (SW)
       │                  │                                      |    (0V to +24.7V pulse)
       │                  │                                      |
       │                  │          +---[ R_snub: 4.7Ω / 1W ]---+
       │                  │          |
       │                  │         ┌┴┐ C_snub: 470pF / 100V C0G
       │                  │         └┬┘ (Suppresses high dv/dt overshoot)
       │                  │          |
       │                  │         PGND
       │                  │          |
       │                  │          │ Drain (D)             BOOST RECTIFIER DIODE
       │                  │         ┌┴──────────────┐        +---[ D1: SiC Schottky ]---+
       │                  │         │ Q1: N-MOSFET  │        |   Wolfspeed C3D04060A    |
       │                  │         │ IPP045N10N5   │        |   (600V, 4A, Qrr = 0)    |
       │                  │  +----->│ (100V, 4.5mΩ) │        +---[ Anode  ->|  Cath ]---+
       │                  │  | Gate └┬──────────────┘                               │
       │                  │  |       │ Source (S)                                   │
       │                  │  |       │                                              +=== +VOUT (+24V/5A)
       │                  │  |       +---[ Kelvin Sense CS+ ]                       │
       │                  │  |       │                                             ┌┴──────────────────┐
       │                  │  |      ┌┴┐ R_shunt: 5.0mΩ / 2W 1%                     │ COUT_BULK         │
       │                  │  |      │ │ Metal Strip Shunt                         ┌┴┐ 2x 330µF/35V Poly ┌┴┐ COUT_CER
       │                  │  |      └┬┘ (Current Sense)                           │ │ (ESR = 10mΩ)     │ │ 3x 10µF/50V
       │                  │  |       │                                            └┬┘                  └┬┘ X7R 1210
       │                  │  |       +---[ Kelvin Sense CS- ]                      │                    │
       │                  │  |       │                                             │       +VOUT        │
       │                  │  |      PGND                                           │         │          │
       │                  │  |                                                     │      [ R_fb1: 28.7kΩ, 0.1% ]
       │                  │  |  +---[ GATE DRIVER & CONTROLLER INTERFACE ]---+     │         │
       │                  │  |  |                                            |     │         +---> V_FB (To Controller)
       │                  │  +--+--[ R_g: 4.7Ω ]<-- OUT (Pin 7: UCC27517)    |     │         │     (V_ref = 1.000V)
       │                  │     |                   VDD (Pin 6) <-- +12V_DRV |     │      [ R_fb2: 1.24kΩ, 0.1% ]
       │                  │     |                   IN+ (Pin 2) <-- PWM_IN   |     │         │
       │                  │     |                   GND (Pin 3) ---> PGND    |     │        AGND (Quiet Ground)
       │                  │     +--------------------------------------------+     │         │
       │                  │                                                        │      (Single Star Point)
   PGND┴──────────────────┴────────────────────────────────────────────────────────┴─────────+────────> GND (Return)
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VIN_FILT** | Fuse $F_1$ Output | $C_{in}$ bank (+), Inductor $L_1$ Terminal 1 | Filtered DC input supply bus | Solid copper pour rated for 12A continuous current. |
| **SW (Switching Node)** | Inductor $L_1$ Pin 2, $Q_1$ Drain (Tab) | Diode $D_1$ Anode, Snubber $R_{snub}$ Pin 1 | Pulsating square-wave voltage node | Keep trace short and wide; place diode $D_1$ anode directly abutting $Q_1$ drain tab. |
| **GATE_DRV** | Driver OUT (UCC27517 Pin 7) | Resistor $R_g$ Pin 1 -> $Q_1$ Gate (Pin 1) | High-speed gate charging output | Minimize loop area between GATE_DRV and PGND return to avoid spurious turn-on. |
| **CS_P / CS_N** | $R_{shunt}$ Top / Bottom Kelvin Pads | PWM Controller Current Sense Pins | Peak current & overcurrent monitor | Route as balanced shielded twisted-pair trace directly to controller sense pins. |
| **+VOUT** | Diode $D_1$ Cathode | $C_{out}$ bank (+), Feedback $R_{fb1}$, Load (+) | Stepped-up regulated +24V rail | Wide copper plane; output caps must absorb high pulsating reverse diode current ($I_{D,rms}$). |
| **V_FB** | Divider $R_{fb1}/R_{fb2}$ Node | Controller FB Inverting Input | Output voltage regulation feedback | Place $R_{fb1}/R_{fb2}$ adjacent to controller IC; route sense line away from $L_1$ magnetic core. |
| **PGND** | $C_{in}$ (-), $R_{shunt}$ (-), $C_{out}$ (-) | High-current power return plane | Power circulating loop ground | Continuous ground plane on internal PCB Layer 2. |
| **AGND** | Controller Reference, $R_{fb2}$ (-) | Star Ground Tie at $C_{out}$ GND pad | Low-noise analog signal reference | Connects to PGND at exactly one quiet point to prevent ground-bounce jitter. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **$Q_1$** | Low-Side N-MOSFET | Infineon IPP045N10N5 | $V_{DS} = 100\,\text{V}, I_D = 120\,\text{A}, R_{DS(on)} = 4.5\,\text{m}\Omega, Q_g = 44\,\text{nC}$ | $100\,\text{V}$ breakdown margin protects against inductive voltage spikes above $+24\,\text{V}$ rail. |
| **$D_1$** | Boost Rectifier Diode | Wolfspeed C3D04060A | $V_{RRM} = 600\,\text{V}, I_F = 4\,\text{A}, V_F = 1.5\,\text{V}, Q_{rr} \approx 0\,\text{nC}$ | Silicon Carbide (SiC) eliminates reverse recovery current spike, eliminating diode turn-off losses. |
| **$L_1$** | Boost Inductor | Vishay IHLP-5050FD-01 | $L = 15\,\mu\text{H}, I_{sat} = 14\,\text{A}, I_{rms} = 12\,\text{A}, DCR = 9.5\,\text{m}\Omega$ | Powdered composite core prevents thermal runaway saturation under high peak input current ($I_{in} \approx 11\,\text{A}$). |
| **$C_{in,bulk}$**| Input Bulk Cap | Panasonic 25SVPF220M | $220\,\mu\text{F}, 25\,\text{V}, \text{OS-CON Polymer}, ESR = 12\,\text{m}\Omega$ | Smooths source ripple current; provides low input source impedance. |
| **$C_{out,bulk}$**| Output Bulk Cap | Panasonic 35SVPF330M | $2 \times 330\,\mu\text{F}, 35\,\text{V}, \text{Polymer}, ESR = 10\,\text{m}\Omega$ | Absorbs full pulsating load current; specifies $I_{ripple,rms} \ge 6.5\,\text{A}$. |
| **$C_{out,cer}$**| Output Ceramic MLCC | TDK C3225X7R1H106M | $3 \times 10\,\mu\text{F}, 50\,\text{V}, \text{X7R}, 1210$ package | Shunts high-frequency switching edges ($t_{fall} < 20\,\text{ns}$). |
| **$R_{shunt}$**| Current Sense Resistor | Susumu KRL6432E-M-R005-F | $5.0\,\text{m}\Omega, 2.0\,\text{W}, 1\%, 4\text{-terminal Kelvin}$ | Ultra-low inductance metal foil construction for accurate sub-microsecond current trip. |
| **$R_{snub}$ / $C_{snub}$** | SW RC Snubber Network | Vishay CRCW1206 / TDK C0G | $R = 4.7\,\Omega / 1\,\text{W}, C = 470\,\text{pF} / 100\,\text{V C0G}$ | Restricts ringing frequency to $< 50\,\text{MHz}$ for CISPR 32 Class B EMC compliance. |


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
