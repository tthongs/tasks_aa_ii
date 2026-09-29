# Uncontrolled Diode Rectifiers: 1-Phase & 3-Phase Bridge Physics & Filter Sizing

Welcome to the **VVDN Engineering Hub Technical Dossier on Uncontrolled Diode Rectifiers**. Uncontrolled rectifiers utilize passive semiconductor PN-junction or Schottky diodes to achieve AC-to-DC conversion without active gating signals. They are ubiquitous as input rectification stages in legacy linear power supplies, low-cost offline switched-mode power supplies (SMPS under $75\,\text{W}$), and industrial motor drive front-ends.

This guide explores single-phase and three-phase rectifier topologies, capacitor filtering physics, diode conduction angle contraction, crest factor, Peak Inverse Voltage (PIV) ratings, and inrush surge protection.

---

## 1. Operating Principle & Rectifier Architectures

### 1.1 Single-Phase Full-Wave Diode Bridge (Graetz Bridge):

```text
                     Single-Phase Full-Wave Diode Bridge
           AC Line ───┬───────────────────────────────┐
                      │                               │
                     ┌┴┐ D1                          ┌┴┐ D3
                     │>│                             │>│
                     └┬┘                             └┬┘
                      ├─── Node DC+ ──────────────────┼───────┬───[ NTC / Fuse ]───┬───> +Vdc
                      │                               │       │                    │
                     ┌┴┐ D4                          ┌┴┐ D2  ┌┴┐                  ┌┴┐
                     │>│                             │>│     │ │ C_bulk           │ │ R_load
                     └┬┘                             └┬┘     └┬┘                  └┬┘
                      │                               │       │                    │
                      ├─── Node DC- ──────────────────┼───────┴────────────────────┴───> -Vdc (GND)
                      │                               │
         AC Neutral ──┴───────────────────────────────┘
```

- **Positive Half-Cycle ($v_{ac} > 0$)**: Current flows from AC Line through diode $D_1$ into $C_{bulk}$ and returns through diode $D_2$ to AC Neutral.
- **Negative Half-Cycle ($v_{ac} < 0$)**: Current flows from AC Neutral through diode $D_3$ into $C_{bulk}$ and returns through diode $D_4$ to AC Line.
- **Diode Peak Inverse Voltage (PIV)**:
  $$V_{PIV} = V_{pk} = \sqrt{2} \cdot V_{ac,rms}$$
  *(For $230\,\text{V}_{rms}$ grid, $V_{PIV} = 325\,\text{V}$. Designers specify $600\,\text{V} \dots 800\,\text{V}$ rated bridge rectifiers to survive utility line surges).*

---

### 1.2 Three-Phase Six-Pulse Diode Bridge Rectifier:

```text
                     Three-Phase 6-Pulse Diode Bridge Rectifier
            Line L1 ───┬───────────────────────────────┐
            Line L2 ───┼───────────────┬───────────────┼───────────────┐
            Line L3 ───┼───────────────┼───────────────┼───────┬───────┼───────┐
                       │               │               │       │       │       │
                      ┌┴┐ D1          ┌┴┐ D3          ┌┴┐ D5   │       │       │
                      │>│             │>│             │>│      │       │       │
                      └┬┘             └┬┘             └┬┘      │       │       │
                       ├───────────────┼───────────────┼───────┴───────┼───────┼───> +Vdc
                       │               │               │               │       │     │
                      ┌┴┐ D4          ┌┴┐ D6          ┌┴┐ D2           │       │    ┌┴┐
                      │>│             │>│             │>│              │       │    │ │ C_bulk
                      └┬┘             └┬┘             └┬┘              │       │    └┬┘
                       ├───────────────┼───────────────┼───────────────┴───────┴───> -Vdc
                       │               │               │
```

- Top diodes ($D_1, D_3, D_5$) conduct whichever phase has the **highest positive potential**.
- Bottom diodes ($D_4, D_6, D_2$) conduct whichever phase has the **most negative potential**.
- Commutation occurs naturally every $60^\circ$ ($\frac{\pi}{3}$ radians).
- **Fundamental DC Output Ripple Frequency**:
  $$f_{ripple} = 6 \cdot f_{line} = 6 \cdot 50\,\text{Hz} = 300\,\text{Hz}$$
- **Average DC Voltage (without filter cap)**:
  $$V_{dc,avg} = \frac{3 \sqrt{3}}{\pi} \cdot \hat{V}_{phase} = \frac{3}{\pi} \cdot \hat{V}_{line-line} \approx 1.35 \cdot V_{LL,rms}$$
  *(For $400\,\text{V}_{rms}$ three-phase grid, $V_{dc,avg} \approx 540\,\text{V}$ DC).*

---

## 2. Capacitive Filter Physics & Diode Conduction Angle

When a bulk capacitor $C_{bulk}$ is connected across the rectifier output to smooth the DC rail, the diodes do not conduct for the full half-cycle ($180^\circ$):

```text
               Diode Conduction Interval & Pulsed Current Spikes
   Voltage ^
       Vpk ┼───────.             .───────.             .───────
           │      / \           / \     / \           / \
           │     /   '-._______.-' \   /   '-._______.-' \
           │    /   Capacitor Ripple\ /                   \
        0V ┼───/─────────────────────v─────────────────────\───────────> Time
   Current ^
           │      |               |     |               |
      I_pk ┼──────|───────────────|─────|───────────────|──────────────
           │     / \             / \   / \             / \
        0A ┼────'───'───────────'───'─'───'───────────'───'────────────> Time
           │◄-θc-►│ Conduction Angle (Narrow Pulsed Spike!)
```

### 2.1 The Physics of Narrow Conduction Angles ($\theta_c$):
- The diodes can only conduct when the input AC voltage exceeds the capacitor voltage: $v_{ac}(t) > v_{cap}(t)$.
- As the capacitor discharges slowly into the load, the diode stays reverse-biased during most of the cycle.
- Near the voltage crest, the diode turns ON for a brief interval $\theta_c \approx 30^\circ \dots 60^\circ$.
- **Consequence**: The entire charge needed to supply the load for a full half-cycle ($10\,\text{ms}$) must be delivered in just $1.5 \dots 3\,\text{ms}$!
- The diode peak current $I_{pk}$ spikes to **$5 \dots 10 \times$ the average load current**, producing:
  - Severe crest factor: $\text{CF} = \frac{I_{pk}}{I_{rms}} \ge 3.0$
  - High total harmonic distortion: $\text{THD}_i \ge 80\% \dots 120\%$
  - Poor power factor: $\text{PF} \approx 0.55 \dots 0.65$ lagging.

---

## 3. Mathematical Formulations & Component Sizing

### 3.1 Bulk Capacitor Sizing for Specified Ripple ($\Delta V_{ripple}$):
Assuming the capacitor discharges into load $P_o$ during the discharge time $t_{dis} \approx \frac{1}{2 f_{line}}$:
$$C_{bulk} \ge \frac{P_o}{2 \cdot f_{line} \cdot V_{dc,pk} \cdot \Delta V_{ripple}} = \frac{I_{dc,load}}{2 \cdot f_{line} \cdot \Delta V_{ripple}}$$
Where:
- $f_{line} = 50\,\text{Hz}$ or $60\,\text{Hz}$
- $V_{dc,pk} = \sqrt{2} \cdot V_{ac,rms}$
- $\Delta V_{ripple}$ is the allowable peak-to-peak DC ripple voltage (typically $5\% \dots 10\% \cdot V_{dc,pk}$).

### 3.2 Diode Peak & RMS Current Stresses:
$$I_{diode,pk} \approx I_{dc} \cdot \frac{\pi}{\theta_c}$$
$$I_{diode,rms} \approx I_{dc} \cdot \sqrt{\frac{\pi}{2 \theta_c}}$$
*Component Selection Rule*: Specify diodes whose non-repetitive peak forward surge current rating ($I_{FSM}$) is at least $10 \dots 20 \times$ rated DC load current.

---

## 4. Inrush Current & Thermal Protection

```text
               Inrush Current Limiting: NTC vs. Relay Pre-Charge
   SCHEME A (Low Cost, < 100W):                  SCHEME B (High Reliability, > 100W):
   AC ───[ Fuse ]───[ NTC Thermistor ]─── Bridge  AC ───[ Fuse ]───┬───[ Power Resistor R_pre ]───┬─── Bridge
                                                                   │                              │
                                                                   └───[ Bypass Relay Contact ]───┘
```

1. **Cold Inrush Surge**: When first plugged into AC mains at peak voltage ($v_{ac} = 325\,\text{V}$), the uncharged bulk capacitor looks like an absolute short circuit ($Z_{cap} \approx 0\,\Omega$). Inrush current is limited only by line impedance, easily exceeding $100\,\text{A} \dots 200\,\text{A}$, which can weld switch contacts and trip circuit breakers.
2. **NTC Thermistor (Scheme A)**: A Negative Temperature Coefficient thermistor has high resistance when cold ($5 \dots 10\,\Omega$), limiting inrush to $I_{inrush} = \frac{325\,\text{V}}{10\,\Omega} = 32.5\,\text{A}$. Once running, load current heats the NTC, dropping its resistance to $< 0.5\,\Omega$.
   - *Failure Mode*: If power drops out for 1 second and immediately returns, the NTC is still hot and provides **zero protection**!
3. **Relay-Bypassed Power Resistor (Scheme B)**: Mandatory for industrial power electronics. A ceramic wirewound resistor ($20 \dots 50\,\Omega$) limits initial charging. Once $C_{bulk}$ reaches $80\% \dots 90\%$ of peak voltage, a microcontroller or analog timer closes an electromechanical relay across the resistor, eliminating continuous resistor power dissipation.
