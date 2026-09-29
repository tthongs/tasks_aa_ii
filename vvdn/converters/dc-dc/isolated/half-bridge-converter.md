# Isolated Half-Bridge DC-DC Converter: Voltage-Divider Mechanics & Design

Welcome to the **VVDN Engineering Hub Technical Dossier on the Isolated Half-Bridge DC-DC Converter**. This guide delivers a comprehensive hardware engineering analysis of the Half-Bridge topology, exploring capacitive voltage division, transformer flux balancing, switch stress trade-offs, secondary LC rectification, and practical design for $100\,\text{W} \dots 500\,\text{W}$ power conversion systems (such as industrial power modules and legacy ATX power supplies).

---

## 1. Operating Principle & Half-Bridge Architecture

The **Half-Bridge DC-DC Converter** replaces two switches of a full bridge with a pair of input divider capacitors ($C_1, C_2$), applying an alternating square-wave voltage of $\pm \frac{V_{IN}}{2}$ across the transformer primary winding:

```text
                      Symmetrical Half-Bridge Converter Power Stage
   +Vin DC ────┬─────────────────────────────┬───────────────────────────────────────────┐
               │                             │                                           │
           Drain (D)                         │                                           │
           ┌───┴───┐ Q1                      │                                           │
           │  S1   │ High-Side Switch      ┌─┴─┐ C1 (Bulk Divider Cap)                  ┌┴┐
           └───┬───┘                       │   │ (Maintains Vin/2)                      │ │ C_in
               │ Source (S)                └─┬─┘                                        └┬┘
               ├──────────────────┐          ├─── Virtual Neutral Point (Vin/2)          │
               │                  │          │                                           │
           Drain (D)              ├──[ Np ]──┤                                           │
           ┌───┴───┐ Q2           │    ││    │                                           │
           │  S2   │ Low-Side     │    ││  ┌─┴─┐ C2 (Bulk Divider Cap)                  │
           └───┬───┘ Switch       │    ││  │   │ (Maintains Vin/2)                      │
               │ Source (S)       │    ││  └─┬─┘                                         │
   GND_PRI ────┴──────────────────┼────┼─────┴───────────────────────────────────────────┴─── GND_PRI
                                  │    ││
   ============================== │ == │ ================== ISOLATION BARRIER ==================
                                  │    ││
                                  │    ││ Secondary Center-Tap
                                  │    └───[ Ns1 ]───[>|] D1 ──┬───[ Inductor Lo ]──┬───> +Vout
                                  │          ││                │                    │
                                  └──────────┼─────────────────┤                   ┌┴┐
                                             ││                │                   │ │ Co
                                           [ Ns2 ]───[>|] D2 ──┘                   └┬┘
                                             ││                                     │
                                  GND_SEC ───┴──────────────────────────────────────┴─── GND_SEC
```

### 1.1 Core Operating Phases:
1. **Phase 1: High-Side Conduction ($Q_1$ ON, $0 < t \le D \cdot T_s$)**:
   - $Q_1$ turns ON while $Q_2$ remains OFF.
   - Primary winding voltage is clamped to $V_p = V_{IN} - \frac{V_{IN}}{2} = +\frac{V_{IN}}{2}$.
   - Secondary winding $N_{s1}$ forward-biases diode $D_1$, driving power into output inductor $L_o$ and capacitor $C_o$. Secondary voltage is $V_s = +\frac{V_{IN}}{2} \cdot \left(\frac{N_s}{N_p}\right)$.
2. **Phase 2: Dead-Time ($Q_1, Q_2$ OFF, $D \cdot T_s < t \le 0.5 T_s$)**:
   - Both switches are OFF. Primary current ceases or circulates through parasitic paths.
   - Secondary diodes $D_1$ and $D_2$ both conduct simultaneously, freewheeling output inductor current $I_{Lo}$ and clamping secondary voltage to $\approx 0\,\text{V}$.
3. **Phase 3: Low-Side Conduction ($Q_2$ ON, $0.5 T_s < t \le (0.5 + D) \cdot T_s$)**:
   - $Q_2$ turns ON while $Q_1$ remains OFF.
   - Primary winding is connected between GND and the virtual neutral $\frac{V_{IN}}{2}$, applying $V_p = -\frac{V_{IN}}{2}$.
   - Secondary winding $N_{s2}$ forward-biases diode $D_2$, driving load power with reversed transformer polarity.
4. **Phase 4: Dead-Time ($Q_1, Q_2$ OFF, $(0.5 + D) \cdot T_s < t \le T_s$)**:
   - Secondary diodes freewheel again until the next cycle begins.

---

## 2. Voltage and Current Waveforms

```text
                     Half-Bridge Key Operating Waveforms
   Gate Q1  ───┐        ┌──────────────┐
               └────────┘              └─────────────────────────────
   Gate Q2  ───────────────────────────┐        ┌──────────────┐
            ───────────────────────────┘        └──────────────┘
               │◄─ D ─►│
   V_primary   +Vin/2
            ┌──────────┐
            │          │
         ───┴──────────┴────────────────────────┐          ┌─────────
                                                │          │
                                                └──────────┘ -Vin/2
   I_Lo         / \                      / \                      / \
            ───/   \────────────────────/   \────────────────────/   \
   V_rect   ┌──────────┐             ┌──────────┐             ┌──────
            │          │             │          │             │
         ───┴──────────┴─────────────┴──────────┴─────────────┴──────
```

---

## 3. Mathematical Formulations & Component Sizing

### 3.1 Voltage Conversion Ratio:
Because each half-cycle applies only $\frac{V_{IN}}{2}$ to the primary winding:
$$V_{out} = \frac{N_s}{N_p} \cdot V_{IN} \cdot D$$
Where $D = \frac{t_{on}}{T_s}$ is the duty cycle per switch ($0 \le D < 0.5$, practically $D_{max} \approx 0.42 \dots 0.45$).

### 3.2 Switch Stress Analysis:
- **Peak Drain-to-Source Voltage**:
  $$V_{DS,max} = V_{IN,max}$$
  *(A massive advantage over Push-Pull, which sees $2 \cdot V_{IN}$.)*
- **Primary Current Stress**:
  Because primary voltage is halved ($\frac{V_{IN}}{2}$), primary RMS current is doubled compared to full-bridge for identical power:
  $$I_{pri,pk} \approx \frac{N_s}{N_p} \cdot I_o = \frac{V_o \cdot I_o}{\frac{V_{IN}}{2} \cdot 2 D} = \frac{P_{out}}{\eta \cdot V_{IN} \cdot D}$$
  $$I_{pri,rms} \approx I_{pri,pk} \cdot \sqrt{2 D}$$

### 3.3 Capacitive Divider Sizing:
Capacitors $C_1$ and $C_2$ carry high AC ripple current. The AC ripple voltage across each capacitor must be restricted to $\Delta V_C \le 5\% \dots 10\% \cdot \frac{V_{IN}}{2}$:
$$C_1 = C_2 \ge \frac{I_{pri,pk} \cdot D_{max}}{2 \cdot f_s \cdot \Delta V_C}$$

### 3.4 Inherent Core Saturation Immunity:
A premier engineering feature of the capacitive half-bridge is **automatic DC flux balancing**. If a duty cycle asymmetry occurs ($\Delta D = D_1 - D_2 \ne 0$), a net DC current flows into the midpoint. The capacitor voltages drift ($V_{C1} \ne V_{C2}$) until the volt-second integral across the transformer primary perfectly balances to zero:
$$\int_0^{T_s} v_p(t) \, dt = V_{C1} \cdot D_1 \cdot T_s - V_{C2} \cdot D_2 \cdot T_s = 0$$
Thus, the half-bridge core **cannot walk into DC saturation**, eliminating the need for complex flux-balancing control loops.

---

## 4. Hardware Engineering Trade-Offs

| Parameter | Half-Bridge | Full-Bridge | Push-Pull |
| :--- | :--- | :--- | :--- |
| **Number of Primary Switches** | 2 | 4 | 2 |
| **Switch Voltage Rating** | $V_{IN}$ | $V_{IN}$ | $2 \cdot V_{IN}$ |
| **Primary Current Rating** | $2 \times$ | $1 \times$ | $1 \times$ |
| **Transformer Utilization** | Excellent (Bidirectional $\pm B$) | Excellent (Bidirectional $\pm B$) | Excellent (Bidirectional $\pm B$) |
| **Gate Drive Complexity** | 1 High-Side + 1 Low-Side Driver | 2 High-Side + 2 Low-Side Drivers | 2 Ground-Referenced Low-Side Drivers |
| **DC Core Walking Risk** | None (Capacitor Balances) | High (Requires blocking cap) | Severe (Flux walking risk) |
| **Typical Power Range** | $100\,\text{W} \dots 500\,\text{W}$ | $500\,\text{W} \dots 10\,\text{kW}+$ | $50\,\text{W} \dots 500\,\text{W}$ (Low $V_{IN}$) |

---

## 5. Practical Design Rules & PCB Layout Guidelines

1. **Capacitor Selection**: Use low-ESR, high-ripple-current metalized polypropylene (MKP) film capacitors or ceramic arrays in parallel with bulk electrolytics for $C_1, C_2$. Electrolytic capacitors alone cannot handle high-frequency charging pulses without excessive heating.
2. **High-Side Bootstrapping**: Implement a bootstrap diode with ultra-fast reverse recovery ($t_{rr} < 25\,\text{ns}$) and a high-voltage gate driver IC (e.g., UCC27712, IR2110) or pulse transformer drive.
3. **Midpoint Parasitic Inductance**: Minimize loop area between switch midpoint node, transformer primary, and the capacitor divider junction to limit high-frequency $dv/dt$ radiated EMI.
