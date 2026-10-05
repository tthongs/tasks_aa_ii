# Isolated Half-Bridge DC-DC Converter: Voltage-Divider Mechanics & Design

Welcome to the **VVDN Engineering Hub Technical Dossier on the Isolated Half-Bridge DC-DC Converter**. This guide delivers a comprehensive hardware engineering analysis of the Half-Bridge topology, exploring capacitive voltage division, transformer flux balancing, switch stress trade-offs, secondary LC rectification, and practical design for 100 W ... 500 W power conversion systems (such as industrial power modules and legacy ATX power supplies).

---

## 1. Operating Principle & Half-Bridge Architecture

The **Half-Bridge DC-DC Converter** replaces two switches of a full bridge with a pair of input divider capacitors (C_1, C_2), applying an alternating square-wave voltage of ± V_IN / 2 across the transformer primary winding:

```text
========================================================================================================================
     DETAILED HARDWARE SCHEMATIC: TWO-SWITCH ASYMMETRICAL/SYMMETRICAL HALF-BRIDGE CONVERTER (400V -> 12V/25A, 300W)
========================================================================================================================

                  +-----------------[ D_boot: DFLS1100 ]<------+ +VCC_DRV (+12V)
                  |                 [ 100V / 1A Schottky]      |
                  |                                           [R_boot: 2.2Ω]
                  |                                            |
                  |     +-----------[ C_boot: 0.1µF/50V X7R ]--+
                  |     |                                      |
                  |     |   +---[ HIGH-VOLTAGE HALF-BRIDGE DRIVER (e.g. UCC27282) ]---+
                  |     |   |                                                         |
                  +-------->| BOOT      [HO] Pin 8 ----[ R_g1: 4.7Ω ]----+             |
                        |   |                                            |             |
                        +-->| PHASE/HB  [LO] Pin 5 ----[ R_g2: 4.7Ω ]--+ |             |
                            |                                          | |             |
          PWM_IN ---------->| IN_HS/IN_LS    [VCC] Pin 2 <--- +12V     | |             |
                            | COM/GND_PRI    [COM] Pin 4 ---> GND_PRI  | |             |
                            +------------------------------------------|-|-------------+
                                                                       | |
    +V_BUS (+400V DC High-Voltage Rail) ──────┬────────────────────────|─|─────────────┬────────────────┐
        │                                     │                        │ │             │                │
       ┌┴─────────────────┐               Drain (D)                    │ │            ┌┴┐ C1            │
       │ C_BUS_BULK       │              ┌────┴──────────┐             │ │            │ │ 2.2µF / 450V ┌┴┐ R_bleed1
       │ 220µF / 450V     │              │ Q1: HS N-FET  │<------------+ │            └┬┘ Poly Film    │ │ 100kΩ / 1W
       │ Electrolytic     │              │ IPB60R099C7   │               │             │ (Divides Vin) └┬┘
       └┬─────────────────┘              │ (650V, 99mΩ)  │               │             │                │
        │                                └────┬──────────┘               │             +=== VIRTUAL NEUTRAL
        │                               Source│                          │             |    (Maintains +200V)
        │                                     │                          │             |
        │                                     +=== HALF-BRIDGE MID (HB)  │             |
        │                                     |    (Swings 0V to +400V)  │             |
        │                                     |                          │             |
        │                    +----------------+--[ C_b: 0.47µF / 630V ]--+             |
        │                    |                |   DC BLOCKING CAP        |             |
        │                    |                |   (Prevents Xfmr Sat)    |             |
        │                    |                |                          |             |
        │                    |                |       PRIMARY WINDING    |             |
        │                    |                |   +---[ Np: 24T ]--------+             |
        │                    |                |   |   * (Dot at HB)                    |
        │                    |                |   +------------------------------------+
        │                    |                |                                        │
        │                    |            Drain (D)                                   ┌┴┐ C2
        │                    |           ┌────┴──────────┐                            │ │ 2.2µF / 450V ┌┴┐ R_bleed2
        │                    |           │ Q2: LS N-FET  │<--------------+            └┬┘ Poly Film    │ │ 100kΩ / 1W
        │                    |           │ IPB60R099C7   │ (Gate)        │             │ (Divides Vin) └┬┘
        │                    |           └────┬──────────┘               │             │                │
        │                    |          Source│                          │             │                │
        │                    |                +---[ CS_PRI ]             │             │                │
        │                    |                │                          │             │                │
        │                    |               ┌┴┐ R_shunt: 0.10Ω / 3W     │             │                │
        │                    |               │ │ 1% Metal Strip          │             │                │
        │                    |               └┬┘ (Primary Current Sense) │             │                │
        │                    |                │                          │             │                │
    GND_PRI ─────────────────┴────────────────┴──────────────────────────┴─────────────┴────────────────┴─── GND_PRI
        │
       ┌┴┐ CY1: Safety Y1 Capacitor (2.2nF / 400VAC Across Galvanic Isolation Barrier)
       └┬┘
        │
   ============================================= ISOLATION BARRIER =====================================================
        │
    GND_SEC ──────────────────────────────────+─────────────────────────────────────────────────────────┬─── GND_SEC
        │                                     │                                                         │
        │                          SECONDARY CENTER-TAP                                                 │
        │                          (Ns1: 2T, Ns2: 2T)                                                   │
        │                                     │                                                         │
        │                       +-------------+-------------+                                           │
        │                       |                           |                                           │
        │                 SECONDARY WINDING 1         SECONDARY WINDING 2                               │
        │                 (Ns1: 2T)                   (Ns2: 2T)                                         │
        │                 * (Dot at Anode D1)         |                                                 │
        │                       |                     * (Dot at Center-Tap)                             │
        │                       +---[>|] D1           |                                                 │
        │                           MBR40200WT        +---[>|] D2 (MBR40200WT Schottky)                 │
        │                           [Cathode]             [Cathode]                                     │
        │                               │                     │                                         │
        │                               +==========+==========+=== NODE SEC_RECT                        │
        │                                          |               (Rectified +20V AC)                  │
        │                                          |                                                    │
        │                                          ├──[ R_snub_sec: 3.3Ω / 2W ]                         │
        │                                          │         │                                          │
        │                                          │   [ C_snub_sec: 2.2nF / 100V ]                     │
        │                                          │         │                                          │
        │                                          │      GND_SEC                                       │
        │                                          │                                                    │
        │                                          +---[ Lo: 4.7µH / 30A Choke ]───+=== +VOUT (+12V/25A)│
        │                                              Vishay IHLP-6767GZ-11       │                    │
        │                                              (DCR = 1.2mΩ, Isat = 36A)  ┌┴──────────────────┐ │
        │                                                                         │ COUT_BULK         │ │
        │                                                                        ┌┴┐ 4x 470µF/25V    ┌┴┐│ COUT_CER
        │                                                                        │ │ Poly (ESR=5mΩ)  │ ││ 6x 47µF/16V
        │                                                                        └┬┘                 └┬┘│ X7R 1210
        │                                                                         │                   │ │
    GND_SEC ──────────────────────────────────────────────────────────────────────┴───────────────────┴─┴─ GND_SEC
```

### 1.1 Detailed Component Connection Netlist & Terminal Details:

| Net Name | Source (Pin / Terminal) | Destination (Pin / Terminal) | Electrical Function | Hardware Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **+V_BUS** | PFC Output (+400V) | C_bus (+), Q_1 Drain, Divider Cap C_1 Pin 1 | High-voltage stiff DC bus | Trace layout must respect IEC 62368-1 high-voltage creepage rules (>= 2.5 mm). |
| **HB_MID** | Q_1 Source, Q_2 Drain | Driver PHASE (Pin 7), DC Blocking Cap C_b Pin 1 | High-voltage half-bridge switching node | Swings between 0 V and +400 V at switching frequency f_s; minimize copper area. |
| **VIRTUAL_NEUTRAL** | Divider Caps C_1 / C_2 Junction | Transformer Primary N_p Pin 2, Bleeders | Midpoint reference rail (V_BUS/2 = 200 V) | Balanced by polypropylene film capacitors C_1, C_2; bleeder resistors prevent DC drift. |
| **PRI_XFMR_AC** | DC Blocking Cap C_b Pin 2 | Transformer Primary N_p Pin 1 | AC-coupled primary excitation | Capacitor C_b blocks any DC imbalance current, preventing staircase transformer saturation. |
| **SEC_RECT** | Diodes D_1, D_2 Common Cathodes | Output Choke L_o Pin 1, Secondary Snubber | Full-wave rectified low-voltage AC node | Delivers smooth continuous inductor charging current; double switching frequency ripple. |
| **+VOUT** | Output Choke L_o Pin 2 | C_out bank (+), Feedback network, Load (+) | High-current regulated +12V DC rail | Wide power copper plane; handles 25A continuous load current. |
| **GND_SEC** | Transformer Secondary Center-Tap | C_out bank (-), Secondary Return | Secondary isolated power ground | Carries total load return current (25 A). |

### 1.2 Component Bill of Materials & Parametric Specifications:

| RefDes | Component Description | Manufacturer & Part Number | Key Electrical Specifications | Critical Design Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Q_1, Q_2** | High-Voltage N-MOSFETs | Infineon IPB60R099C7 | V_DS = 650 V, I_D = 24 A, R_DS(on) = 99 mΩ, Q_g = 32 nC | CoolMOS C7 technology minimizes switching and gate charge losses at 100 kHz. |
| **C_1, C_2** | Voltage Divider Film Caps | KEMET R46KR422000M1M | 2.2 µF, 450 V_DC, Metallized Polypropylene Film | Handles high continuous AC ripple current (I_rms ≈ 2.5 A); film dielectric avoids capacitance drift. |
| **C_b** | DC Blocking Capacitor | TDK B32652A6474J000 | 0.47 µF, 630 V_DC, High-Pulse Film | Eliminates any steady-state DC magnetization current through transformer primary winding. |
| **T_1** | Main Power Transformer | Custom ETD44 Core (3C95) | Turns: 24:(2+2), L_m = 1.8 mH, L_lk < 2.5 µH | Split primary/secondary sandwich construction to minimize leakage inductance and proximity losses. |
| **D_1, D_2** | Secondary Dual Schottky | ON Semi MBR40200WT | V_RRM = 200 V, I_F = 40 A, V_F = 0.72 V | Common-cathode TO-247 Schottky diode mounted on secondary high-performance heatsink. |
| **L_o** | Output Filter Inductor | Vishay IHLP-6767GZ-11 | L = 4.7 µH, I_sat = 36 A, I_rms = 30 A, DCR = 1.2 mΩ | Low-loss molded powder choke rated for > 30 A continuous saturation. |
| **C_out,bulk** | Output Bulk Capacitor | Panasonic 25SVPF470M | 4 * 470 µF, 25 V, OS-CON Polymer, ESR = 5 mΩ | Paralleled bank yields total ESR of 1.25 mΩ for ultra-low output ripple (< 15 mV). |
| **U_1 (Driver)** | Half-Bridge Gate Driver | TI UCC27282DR | 120 V / 650 V bootstrap, 3 A sink / source, robust dv/dt | Withstands negative transient swings on HB pin down to -5 V. |


### 1.1 Core Operating Phases:
1. **Phase 1: High-Side Conduction (Q_1 ON, 0 < t <= D * T_s)**:
   - Q_1 turns ON while Q_2 remains OFF.
   - Primary winding voltage is clamped to V_p = V_IN - V_IN / 2 = +V_IN / 2.
   - Secondary winding N_s1 forward-biases diode D_1, driving power into output inductor L_o and capacitor C_o. Secondary voltage is V_s = +V_IN / 2 * (N_s / N_p).
2. **Phase 2: Dead-Time (Q_1, Q_2 OFF, D * T_s < t <= 0.5 T_s)**:
   - Both switches are OFF. Primary current ceases or circulates through parasitic paths.
   - Secondary diodes D_1 and D_2 both conduct simultaneously, freewheeling output inductor current I_Lo and clamping secondary voltage to ≈ 0 V.
3. **Phase 3: Low-Side Conduction (Q_2 ON, 0.5 T_s < t <= (0.5 + D) * T_s)**:
   - Q_2 turns ON while Q_1 remains OFF.
   - Primary winding is connected between GND and the virtual neutral V_IN / 2, applying V_p = -V_IN / 2.
   - Secondary winding N_s2 forward-biases diode D_2, driving load power with reversed transformer polarity.
4. **Phase 4: Dead-Time (Q_1, Q_2 OFF, (0.5 + D) * T_s < t <= T_s)**:
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
Because each half-cycle applies only V_IN / 2 to the primary winding:
```
V_out = N_s / N_p * V_IN * D
```
Where D = t_on / T_s is the duty cycle per switch (0 <= D < 0.5, practically D_max ≈ 0.42 ... 0.45).

### 3.2 Switch Stress Analysis:
- **Peak Drain-to-Source Voltage**:
  ```
V_DS,max = V_IN,max
```
  *(A massive advantage over Push-Pull, which sees 2 * V_IN.)*
- **Primary Current Stress**:
  Because primary voltage is halved (V_IN / 2), primary RMS current is doubled compared to full-bridge for identical power:
  ```
I_pri,pk ≈ N_s / N_p * I_o = (V_o * I_o) / (V_IN / 2 * 2 D) = P_out / (η * V_IN * D)
```
  ```
I_pri,rms ≈ I_pri,pk * sqrt(2 D)
```

### 3.3 Capacitive Divider Sizing:
Capacitors C_1 and C_2 carry high AC ripple current. The AC ripple voltage across each capacitor must be restricted to Δ V_C <= 5\% ... 10\% * V_IN / 2:
```
C_1 = C_2 >= (I_pri,pk * D_max) / (2 * f_s * Δ V_C)
```

### 3.4 Inherent Core Saturation Immunity:
A premier engineering feature of the capacitive half-bridge is **automatic DC flux balancing**. If a duty cycle asymmetry occurs (Δ D = D_1 - D_2 != 0), a net DC current flows into the midpoint. The capacitor voltages drift (V_C1 != V_C2) until the volt-second integral across the transformer primary perfectly balances to zero:
```
int_0^T_s v_p(t) dt = V_C1 * D_1 * T_s - V_C2 * D_2 * T_s = 0
```
Thus, the half-bridge core **cannot walk into DC saturation**, eliminating the need for complex flux-balancing control loops.

---

## 4. Hardware Engineering Trade-Offs

| Parameter | Half-Bridge | Full-Bridge | Push-Pull |
| :--- | :--- | :--- | :--- |
| **Number of Primary Switches** | 2 | 4 | 2 |
| **Switch Voltage Rating** | V_IN | V_IN | 2 * V_IN |
| **Primary Current Rating** | 2 * | 1 * | 1 * |
| **Transformer Utilization** | Excellent (Bidirectional ± B) | Excellent (Bidirectional ± B) | Excellent (Bidirectional ± B) |
| **Gate Drive Complexity** | 1 High-Side + 1 Low-Side Driver | 2 High-Side + 2 Low-Side Drivers | 2 Ground-Referenced Low-Side Drivers |
| **DC Core Walking Risk** | None (Capacitor Balances) | High (Requires blocking cap) | Severe (Flux walking risk) |
| **Typical Power Range** | 100 W ... 500 W | 500 W ... 10 kW+ | 50 W ... 500 W (Low V_IN) |

---

## 5. Practical Design Rules & PCB Layout Guidelines

1. **Capacitor Selection**: Use low-ESR, high-ripple-current metalized polypropylene (MKP) film capacitors or ceramic arrays in parallel with bulk electrolytics for C_1, C_2. Electrolytic capacitors alone cannot handle high-frequency charging pulses without excessive heating.
2. **High-Side Bootstrapping**: Implement a bootstrap diode with ultra-fast reverse recovery (t_rr < 25 ns) and a high-voltage gate driver IC (e.g., UCC27712, IR2110) or pulse transformer drive.
3. **Midpoint Parasitic Inductance**: Minimize loop area between switch midpoint node, transformer primary, and the capacitor divider junction to limit high-frequency dv/dt radiated EMI.
