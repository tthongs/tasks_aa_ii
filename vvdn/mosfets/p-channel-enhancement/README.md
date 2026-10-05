# P-Channel Enhancement-Mode MOSFET (e-PMOS): Physics, Design & Applications

A **P-Channel Enhancement-Mode MOSFET** (**e-PMOS**) is a normally-off field-effect transistor where current conduction occurs through the flow of **holes** (h^+) across an induced p-type inversion layer within an n-type substrate. Because its source terminal is naturally connected to the most positive potential in a circuit, the e-PMOS is predominantly deployed in **high-side power switching**, **reverse battery polarity protection**, and complementary **CMOS** logic stages.

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
     │  Source (p+)                         Drain (p+)     │
  ───┤  ┌───────┐     P-Inversion Channel     ┌───────┐    ├───
 (S) │  │  p+   │  =========================  │  p+   │    │  (D)
     └──┴───────┴─────────────────────────────┴───────┴────┘
     │            Depletion Layer (Wdep)                   │
     │  - - - - - - - - - - - - - - - - - - - - - - - - -  │
     │                 n-type Substrate (or N-Well)        │
     │                                                     │
     └──────────────────────────┬──────────────────────────┘
                                │
                            Body (B) (Internally tied to Source)
```

### Physical Operation & Mobility Physics:
1. **Gate Drive Polarity (V_GS < 0 V)**:
   - For an enhancement PMOS, the threshold voltage is negative: V_TH(p) ≈ -1.0 V ... -3.5 V.
   - To turn the transistor ON, the Gate potential must be driven **more negative than the Source** (V_GS <= V_TH(p), or V_G < V_S - |V_TH|).
2. **The "Hole Mobility Penalty"**:
   - In crystalline Silicon, hole mobility (µ_p ≈ 450 cm^2/V*s) is approximately **2.5* to 3* lower** than electron mobility (µ_n ≈ 1350 cm^2/V*s).
   - Because R_DS(on) proportional to 1 / (µ C_ox (W/L)), achieving the same on-resistance in a PMOS requires roughly 2.5* to 3.0* larger die silicon area (and consequently proportional increases in gate charge Q_g and cost) compared to an NMOS of identical voltage and current ratings.

---

## 2. Circuit Topologies: High-Side Power Switching

Unlike an NMOS which requires a complex bootstrap circuit or charge pump to drive its gate above the positive supply rail in high-side configurations, a PMOS can be turned ON simply by pulling its gate down toward ground:

### 1. Direct Low-Voltage High-Side Switch (V_IN <= 12 V):
```text
           +V_IN (+5V / +12V Rail)
              │
              ├───┬───────────────────────────────┐
              │   │                               │
             [R1] │ Source (S)                    │
             100k └───┐                           │
              │       │                           │
              ├─── Gate (G)   PMOS                │
              │       │       [e.g. AO3401]       │
             [R2] ────┘                           │
             10k      └─── Drain (D)              │
              │               │                   │
         Collector            ▼ To Load           │
              │               │                   │
         ┌────┴────┐       [ LOAD ]               │
MCU ────┤ NPN BJT │           │                   │
GPIO    │ (2N3904)│          GND                  │
via 1k   └────┬────┘                              │
              │                                   │
             GND                                 GND
```

### 2. High-Voltage High-Side Switch with Zener Gate Clamp (V_IN > 20 V):
If V_IN = 24 V or 48 V, pulling the gate to ground would subject the gate oxide to V_GS = -24 V or -48 V, instantly destroying the oxide (since V_GS(max) = ± 20 V). A Zener clamp is mandatory:

```text
               +V_IN (+24V / +48V Bus)
                  │
                  ├───┬─────────────────────────┐
                  │   │                         │
                 [R1] │ Source (S)              │
                 10k  └───┐                     │
                  │       │                     │
                  ├──┬─ Gate (G) PMOS           │
                  │  │    │                     │
              [12V]  │    │                     │
             Zener ▲ │    │                     │
             Diode ──┘    └─── Drain (D)        │
                  │               │             │
                 [R2]             ▼ To Load     │
                 22k              │             │
                  │            [ LOAD ]         │
              Drain (D)           │             │
              ┌───┴───┐          GND            │
MCU ──[100Ω]──┤  NMOS │                         │
GPIO          └───┬───┘                         │
                  │ Source (S)                  │
                 GND                           GND
```

---

## 3. Reverse Polarity (Reverse Battery) Protection

In automotive and industrial electronics, connecting battery leads in reverse will destroy downstream capacitors and ICs. A PMOS provides ideal reverse polarity protection with millivolt-level insertion loss compared to a classical series diode:

```text
       Battery Input (+)                                        Protected System Rail
       ──────────────────┬──────────────┬──────────────────────────────> (+V_SYS)
                         │              │
                         │          Drain (D)
                        [R1]            │
                        100k         ┌──┴──┐
                         │           │     │ PMOS
                         ├── Gate (G)┤     │ [Body diode cathode points to Vin!]
                         │           │     │
                      [15V]          └──┬──┘
                      Zener             │
                      Diode ▲        Source (S)
                         ├───┘          │
                         │              │
       Battery Input (-) ┴──────────────┴──────────────────────────────> (GND_SYS)
       ────────────────────────────────────────────────────────────────>
```

### Working Principle:
1. **Normal Connection (Correct Polarity)**:
   - Initial power application: Current flows through the PMOS **body diode** from Drain to Source, establishing a positive potential at the Source terminal.
   - The Gate is tied through R_1 to Ground. Therefore, V_GS = V_G - V_S ≈ 0 V - V_IN = -V_IN.
   - Once |V_GS| > |V_TH|, the PMOS channel turns fully ON. The low R_DS(on) shunts the body diode, reducing voltage drop across the switch to mere millivolts (V_drop = I_LOAD * R_DS(on)) with zero forward diode power dissipation.
2. **Reverse Connection (Battery Inverted)**:
   - The Source terminal is connected to the negative battery terminal, while the Gate is connected to the positive terminal through R_1.
   - Consequently, V_G > V_S, meaning V_GS > 0 V. The PMOS channel remains completely OFF.
   - The body diode is reverse-biased, completely blocking any reverse current flow and safeguarding all downstream circuits.

---

## 4. Key Datasheet Parameters & Traps

| Parameter | Symbol | Critical Significance | Rule of Thumb |
| :--- | :--- | :--- | :--- |
| **Drain-to-Source Breakdown** | V_(BR)DSS | Negative breakdown voltage between D and S | Must handle max positive rail plus inductive overshoot |
| **Gate-to-Source Limit** | V_GS(max) | Maximum gate dielectric stress (typically ± 20 V) | Clamp with 12 V - 15 V Zener in systems where V_IN > 12 V |
| **Threshold Voltage** | V_GS(th) | Gate voltage where conduction starts (typically -1.0 V ... -3.0 V) | Ensure drive voltage pulls gate well below V_TH (ideally -10 V) |
| **Static On-Resistance** | R_DS(on) | Channel on-resistance | Evaluate at specified V_GS (e.g. -4.5 V vs -10 V) |

---

## 5. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | -V_DS(max) | -I_D(max) | R_DS(on) (@-10V) | Typical Use-Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AO3401A** | Alpha & Omega | SOT-23 | 30 V | 4.0 A | 44 mΩ | Compact 3.3V/5V/12V load switches, battery cutoffs |
| **FDN340P** | onsemi / Fairchild | SOT-23 | 20 V | 2.0 A | 70 mΩ | Handheld power path management |
| **DMP3098L** | Diodes Inc | SOT-23 | 30 V | 3.8 A | 65 mΩ | Reverse battery protection in low-power microcontrollers |
| **IRF9540N** | Infineon (IR) | TO-220 | 100 V | 23 A | 117 mΩ | Industrial high-side actuator/relay switching |
| **SQJ407EP** | Vishay Siliconix | PowerPAK SO-8 | 40 V | 60 A | 7.2 mΩ | AEC-Q101 Automotive high-side power distribution |
