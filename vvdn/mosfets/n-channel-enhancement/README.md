# N-Channel Enhancement-Mode MOSFET (e-NMOS): Physics, Design & Applications

An **N-Channel Enhancement-Mode MOSFET** (commonly designated **e-NMOS**) is the most ubiquitous discrete transistor and integrated circuit building block in electronics. Being a **normally-off** device, no conduction channel exists at zero gate bias ($V_{GS} = 0\,\text{V}$). It relies on an applied positive gate potential ($V_{GS} > V_{TH}$) to electrostatically induce an electron inversion layer in a p-type substrate.

---

## 1. Semiconductor Physics & Device Structure

```text
                             Gate (G)
                                │
                          ┌─────┴─────┐ Poly-Si / Metal Gate
                          │   GATE    │
                     ┌────┴───────────┴────┐
                     │  Gate Oxide (SiO2)  │  (tox: 10nm - 50nm)
     ┌───────────────┴─────────────────────┴───────────────┐
     │  Source (n+)                         Drain (n+)     │
  ───┤  ┌───────┐      Inversion Channel      ┌───────┐    ├───
 (S) │  │  n+   │  =========================  │  n+   │    │  (D)
     └──┴───────┴─────────────────────────────┴───────┴────┘
     │            Depletion Layer (Wdep)                   │
     │  - - - - - - - - - - - - - - - - - - - - - - - - -  │
     │                 p-type Substrate                    │
     │                                                     │
     └──────────────────────────┬──────────────────────────┘
                                │
                            Body (B) (Internally tied to Source)
```

### Physical Working Steps:
1. **Zero Gate Bias ($V_{GS} = 0\,\text{V}$)**:
   - The $n^+$ Source, $p$ Substrate, and $n^+$ Drain form two back-to-back $p-n$ diodes ($n^+-p$ and $p-n^+$).
   - Any voltage applied across Drain-to-Source ($V_{DS} > 0$) reverse-biases the Drain-to-Body junction. Only tiny reverse leakage current ($I_{DSS} \approx \text{nA}$) flows.
2. **Threshold Formation ($V_{GS} = V_{TH}$)**:
   - A positive voltage on the gate creates a vertical downward electric field ($E_{vert}$).
   - Mobile holes ($h^+$) in the p-substrate are repelled away from the $\text{Si-SiO}_2$ interface, uncovering negatively charged immobile acceptor ions ($N_A^-$) to form a depletion region.
   - When $V_{GS}$ reaches the **Threshold Voltage ($V_{TH} \approx 1.5\,\text{V} - 4.0\,\text{V}$)**, the conduction band bends below the Fermi level at the surface, pulling in free minority electrons ($e^-$). This forms an $n$-type **surface inversion channel**.
3. **Channel Conduction ($V_{GS} > V_{TH}$)**:
   - Because electrons are the majority carriers in the channel, they possess high drift mobility ($\mu_n \approx 1350 - 1450\,\text{cm}^2/\text{V}\cdot\text{s}$ in bulk Silicon), enabling very low on-resistance per unit die area compared to PMOS.

---

## 2. Terminal Characteristic Curves & Mathematical Models

```text
       Drain Current (Id) vs Drain-to-Source Voltage (Vds)
  Id ^
     │                              Vgs = 10V (Deep Triode & Saturation)
     │                         .------------------------
     │                     .---
     │                 .---         Vgs = 7V
     │             .---        .------------------------
     │         .---        .---
     │     .---        .---         Vgs = 5V
     │  .-'        .---        .------------------------
     │ /       .---        .---
     │/    .---        .---         Vgs = 3V
     │ .---        .---        .------------------------
     │/        .---
     │     .---                     Vgs < Vth (Cutoff: Id ~ 0)
     └───────────────────────────────────────────────────> Vds
        Linear / Triode          Saturation (Active)
        (Vds < Vgs - Vth)        (Vds >= Vgs - Vth)
```

### Characteristic Mathematical Equations:
- **Triode (Linear / Ohmic) Regime** ($V_{DS} < V_{GS} - V_{TH}$):
  $$I_D = \mu_n C_{ox} \left(\frac{W}{L}\right) \left[ (V_{GS} - V_{TH}) V_{DS} - \frac{1}{2} V_{DS}^2 \right]$$
  For small $V_{DS}$, channel resistance $R_{DS(on)}$ is purely ohmic:
  $$R_{DS(on)} = \frac{1}{\mu_n C_{ox} (W/L) (V_{GS} - V_{TH})}$$
- **Saturation Regime** ($V_{DS} \ge V_{GS} - V_{TH}$):
  $$I_{D(sat)} = \frac{1}{2} \mu_n C_{ox} \left(\frac{W}{L}\right) (V_{GS} - V_{TH})^2 (1 + \lambda V_{DS})$$
  Where $\lambda$ is channel length modulation ($1/V_A$).

---

## 3. Circuit Implementation: Low-Side Switch Architecture

In automotive ECUs, microcontroller peripherals, and motor drivers, the e-NMOS is the gold standard for **low-side switching**:

```text
                +V_LOAD (+12V / +24V Rail)
                      │
                      ├───┐
                      │   │
                     [ LOAD ] (Solenoid / Relay / Motor / LED string)
                      │   │
                      ├───┴─── [Freewheeling Diode: 1N4007 / SS34]
                      │
                   Drain (D)
                      │
                   ┌──┴──┐
       R_gate      │     │
MCU ───[ 100Ω ]───┤  NMOS│
GPIO              │     │
             ┌────┴──┬───┘
             │       │
            [10k]    │ Source (S)
            R_pd     │
             │       │
            GND     GND (Common Ground Return)
```

### Hardware Design Rules:
1. **Pull-Down Resistor ($R_{pd} \approx 10\,\text{k}\Omega - 100\,\text{k}\Omega$)**:
   - Placed directly between Gate and Source.
   - Prevents the high-impedance gate from floating during MCU reset, bootloader execution, or high-Z uninitialized GPIO states, which would cause parasitic turn-on and burn out the transistor.
2. **Series Gate Resistor ($R_{gate} \approx 10\,\Omega - 100\,\Omega$)**:
   - Damps LC ringing formed between trace parasitic inductance ($L_{gate}$) and MOSFET input capacitance ($C_{iss}$).
   - Limits the peak transient sourcing/sinking current pulled from the MCU GPIO.
3. **Freewheeling Diode**:
   - Required for inductive loads. When the NMOS abruptly turns off, inductor current cannot instantaneously drop to zero ($\Delta V = -L \frac{di}{dt}$), causing a positive voltage spike at the Drain that will exceed $V_{(BR)DSS}$ and destroy the device if not clamped.

---

## 4. Key Datasheet Parameters & Electrical Traps

| Datasheet Parameter | Symbol | Critical Significance | Design Rule of Thumb |
| :--- | :--- | :--- | :--- |
| **Drain-Source Breakdown Voltage** | $V_{(BR)DSS}$ | Maximum voltage across D-S before avalanche occurs | Select with $\ge 20\% - 50\%$ margin above supply bus |
| **Gate-Source Voltage Limit** | $V_{GS(max)}$ | Dielectric breakdown rating of thin $\text{SiO}_2$ (typically $\pm 20\,\text{V}$) | Clamp with $15\,\text{V} - 18\,\text{V}$ TVS / Zener if transients exist |
| **Threshold Voltage** | $V_{GS(th)}$ | Gate voltage where $I_D \approx 250\,\mu\text{A}$ begins conduction | Must NOT be confused with fully enhanced drive voltage ($V_{GS} \ge 10\,\text{V}$) |
| **Static Drain-Source On-Resistance**| $R_{DS(on)}$ | Internal resistance when fully ON at specified $V_{GS}$ and $T_j$ | Derate by $1.5\times - 2.0\times$ for $T_j = 125^\circ\text{C}$ operation |
| **Total Gate Charge** | $Q_g$ | Total charge needed to raise $V_{GS}$ to operating level | Determines driver current requirements: $I_{drive} = Q_g / t_{target}$ |
| **Reverse Recovery Charge** | $Q_{rr}$ | Body diode recovery charge during commutation | Causes shoot-through and ringing in half-bridge converters |

---

## 5. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | $V_{DS(max)}$ | $I_{D(max)}$ | $R_{DS(on)}$ (@10V) | Typical Use-Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2N7002** | onsemi / Diodes Inc | SOT-23 | $60\,\text{V}$ | $300\,\text{mA}$ | $5.0\,\Omega$ | Small-signal level shifting, LED drive, logic gates |
| **BSS138** | onsemi / Fairchild | SOT-23 | $50\,\text{V}$ | $220\,\text{mA}$ | $3.5\,\Omega$ | $I^2C$ bidirectional level translator |
| **IRLZ44N** | Infineon (IR) | TO-220 | $55\,\text{V}$ | $47\,\text{A}$ | $22\,\text{m}\Omega$ | 5V Logic-level hobbyist/industrial load switching |
| **IRF540N** | Infineon (IR) | TO-220 | $100\,\text{V}$ | $33\,\text{A}$ | $44\,\text{m}\Omega$ | Classical power switching, audio amplifier, solenoids |
| **BSC030N04NS** | Infineon | TDSON-8 (SuperSO8)| $40\,\text{V}$ | $100\,\text{A}$ | $3.0\,\text{m}\Omega$ | Automotive synchronous buck, high-efficiency PoL |
