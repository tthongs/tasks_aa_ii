# Zeta DC-DC Converter: Inverse SEPIC Mechanics & Continuous Output Current

Welcome to the **VVDN Engineering Hub Technical Dossier on the Zeta (Inverse SEPIC) DC-DC Converter**. While the SEPIC converter offers continuous input current and a ground-referenced switch, its output current is discontinuous. The **Zeta Converter** flips this architecture: it features an **output inductor in series with the load (like a buck converter)**, delivering ultra-low output voltage ripple and continuous output current while maintaining non-inverting step-up/step-down capability.

This guide explores the Zeta topology, derives its voltage and current transfer functions, compares it against the SEPIC, and provides component sizing formulas.

---

## 1. Operating Principle & Zeta Topology

The **Zeta Converter** utilizes a high-side active switch ($Q_1$), a parallel inductor ($L_1$), a series flying coupling capacitor ($C_z$), a freewheeling diode ($D_1$), and an output filter inductor ($L_2$) connected directly to the output:

```text
========================================================================================================================
       DETAILED HARDWARE SCHEMATIC: NON-INVERTING ZETA DC-DC CONVERTER (9V-18V IN -> 12V/4A OUT)
========================================================================================================================

                  +-----------------[ D_boot: DFLS1100 ]<------+ +V_DRV (+12V)
                  |                 [ 100V / 1A Schottky]      |
                  |                                           [R_boot: 2.2Ω]
                  |                                            |
                  |     +-----------[ C_boot: 0.1µF/50V X7R ]--+
                  |     |                                      |
                  |     |   +---[ HIGH-SIDE GATE DRIVER (e.g. UCC27282 / LM5113) ]---+
                  |     |   |                                                        |
                  +-------->| BOOT      [HO] Pin 8 ----[ R_g: 2.2Ω ]----+            |
                        |   |                                           |            |
                        +-->| PHASE/SW1 [VCC] Pin 2 <--- +V_DRV         |            |
                            |                                           |            |
          PWM_IN ---------->| IN_HS     [COM] Pin 4 ---> PGND           |            |
                            +-------------------------------------------|------------+
                                                                        |
    +VIN (9V-18V DC) ───────────────────────────────────────────┐       |
        │                                                       │       |
       [F1: 8A Fuse]                                            │       |
        │                                                       │       |
       ┌┴─────────────────┐                                     │       |
       │ CIN_BULK         │                                     │ Drain |
      ┌┴┐ 220µF/35V Poly ┌┴┐ CIN_CER                           ┌┴───────┴──────┐
      │ │ (Low-ESR 12mΩ) │ │ 2x 10µF/35V X7R                   │ Q1: N-MOSFET  │<----+
      └┬┘                └┬┘                                   │ BSC035N10NS5  │ (Gate)
       │                  │                                    │ (100V, 3.5mΩ) │
       │                  │                                    └┬──────────────┘
       │                  │                                     │ Source (S)
       │                  │                                     │
       │                  │                                     +=== NODE SW1 (Switch Node 1)
       │                  │                                     |    (0V to +18V pulse)
       │                  │                                     |
       │                  │            FLYING CAPACITOR         ├──[ R_snub: 3.3Ω / 1W ]
       │                  │     +------[ Cz: 10µF / 50V ]-------+         │
       │                  │     |      TDK C3225X7R1H106M       |   [ C_snub: 470pF ]
       │                  │     |      (Precharged to Vout)     |         │
       │                  │     |                               |        PGND
       │                  │     |      PRIMARY INDUCTOR         |
       │                  │     |   +--[ L1: 22µH / 6.0A ]------+
       │                  │     |   |  Coilcraft MSD1278-223    |
       │                  │     |   |  (DCR = 32mΩ)             |
       │                  │     |   +-------------+-------------+
       │                  │     |                 │
       │                  │     |                PGND (Ground Return)
       │                  │     |
       │                  │     +=== NODE SW2 (Diode / Inductor Node)
       │                  │     |    (0V to +30V pulse)
       │                  │     |
       │                  │     +---[ D1: Schottky Diode (Cathode) ]
       │                  │     |   V30100P (100V / 30A Trench)
       │                  │     |   [ Anode to PGND ]
       │                  │     |         │
       │                  │     |        PGND
       │                  │     |
       │                  │     |        OUTPUT FILTER INDUCTOR
       │                  │     +---[ L2: 22µH / 6.0A Shielded ]---+
       │                  │         Coilcraft MSD1278-223          |
       │                  │         (DCR = 32mΩ, Isat = 6.8A)      |
       │                  │                                        |
       │                  │                                        +=== +VOUT (+12V/4A Regulated)
       │                  │                                        │
       │                  │                                       ┌┴──────────────────┐
       │                  │                                       │ COUT_BULK         │
       │                  │                                      ┌┴┐ 2x 270µF/25V    ┌┴┐ COUT_CER
       │                  │                                      │ │ Poly (ESR=10mΩ) │ │ 3x 22µF/25V
       │                  │                                      └┬┘                 └┬┘ X7R 1210
       │                  │                                       │                   │
       │                  │                                       │      +VOUT        │
       │                  │                                       │        │          │
       │                  │                                       │     [ R_fb1: 90.9kΩ, 0.1% ]
       │                  │                                       │        │
       │                  │                                       │        +---> V_FB (To Controller)
       │                  │                                       │        │     (V_ref = 1.200V)
       │                  │                                       │     [ R_fb2: 10.0kΩ, 0.1% ]
       │                  │                                       │        │
       │                  │                                       │       AGND (Quiet Ground)
       │                  │                                       │        │
       │                  │                                       │     (Single Star Point)
   PGND┴──────────────────┴───────────────────────────────────────┴────────+───────────────────┴─── PGND (0V Rail)
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+VIN_FILT** | Fuse $F_1$ Output | $C_{in}$ bank (+), $Q_1$ Drain (Pins 5-8) | Filtered positive DC input bus | High-side N-channel MOSFET drain connected directly to input rail. |
| **SW1 (Switch Node 1)** | $Q_1$ Source (Pins 1-3) | Inductor $L_1$ Pin 1, Flying Cap $C_z$ Pin 1, Driver PHASE | High-side pulsating switching node | Requires bootstrap gate driver referenced to SW1; swings between $0\,\text{V}$ and $+V_{IN}$. |
| **SW2 (Switch Node 2)** | Flying Cap $C_z$ Pin 2 | Diode $D_1$ Cathode, Output Inductor $L_2$ Pin 1 | Secondary pulsating node | Swings between $0\,\text{V}$ (when $D_1$ conducts) and $V_{IN} + V_o$ (when $Q_1$ conducts). |
| **+VOUT** | Inductor $L_2$ Pin 2 | $C_{out}$ bank (+), Feedback $R_{fb1}$, Load (+) | Non-inverting continuous-current output | Output inductor $L_2$ provides continuous DC current, resulting in very low output voltage ripple. |
| **PGND** | $C_{in}$ (-), Inductor $L_1$ Pin 2, Diode $D_1$ Anode, $C_{out}$ (-) | System power ground return | Common zero-volt power ground | Continuous ground plane; carries circulating inductor and diode currents. |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **$Q_1$** | High-Side N-MOSFET | Infineon BSC035N10NS5 | $V_{DS} = 100\,\text{V}, I_D = 100\,\text{A}, R_{DS(on)} = 3.5\,\text{m}\Omega, Q_g = 28\,\text{nC}$ | Requires floating bootstrap driver circuit ($D_{boot}, C_{boot}$) to bias gate above $V_{IN}$. |
| **$D_1$** | Freewheeling Diode | Vishay V30100P | $V_{RRM} = 100\,\text{V}, I_F = 30\,\text{A}, V_F = 0.52\,\text{V}, t_{rr} < 20\,\text{ns}$ | Anode to ground, cathode to SW2. Sees peak reverse voltage $V_{R} = V_{IN} + V_o$. |
| **$C_z$** | Flying Energy Capacitor | TDK C3225X7R1H106M | $10\,\mu\text{F}, 50\,\text{V}, \text{X7R Ceramic}, 1210$ package | Steady-state DC voltage across $C_z$ equals $V_o$; handles high AC ripple current. |
| **$L_1, L_2$** | Coupled / Dual Inductors | Coilcraft MSD1278-223MLD | $2 \times 22\,\mu\text{H}, I_{sat} = 6.8\,\text{A}, DCR = 32\,\text{m}\Omega$ | $L_2$ placed at output creates low-noise output spectrum identical to a standard Buck converter. |
| **$C_{out,bulk}$** | Output Bulk Capacitor | Panasonic 25SVPF270M | $2 \times 270\,\mu\text{F}, 25\,\text{V}, \text{OS-CON Polymer}, ESR = 10\,\text{m}\Omega$ | Smooths residual inductor ripple current; low ESR ensures $< 20\,\text{mV}$ ripple. |


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
