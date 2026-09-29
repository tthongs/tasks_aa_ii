# P-Channel Enhancement-Mode MOSFET (e-PMOS): Physics, Design & Applications

A **P-Channel Enhancement-Mode MOSFET** (**e-PMOS**) is a normally-off field-effect transistor where current conduction occurs through the flow of **holes** ($h^+$) across an induced p-type inversion layer within an n-type substrate. Because its source terminal is naturally connected to the most positive potential in a circuit, the e-PMOS is predominantly deployed in **high-side power switching**, **reverse battery polarity protection**, and complementary **CMOS** logic stages.

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
1. **Gate Drive Polarity ($V_{GS} < 0\,\text{V}$)**:
   - For an enhancement PMOS, the threshold voltage is negative: $V_{TH(p)} \approx -1.0\,\text{V} \dots -3.5\,\text{V}$.
   - To turn the transistor ON, the Gate potential must be driven **more negative than the Source** ($V_{GS} \le V_{TH(p)}$, or $V_G < V_S - |V_{TH}|$).
2. **The "Hole Mobility Penalty"**:
   - In crystalline Silicon, hole mobility ($\mu_p \approx 450\,\text{cm}^2/\text{V}\cdot\text{s}$) is approximately **$2.5\times$ to $3\times$ lower** than electron mobility ($\mu_n \approx 1350\,\text{cm}^2/\text{V}\cdot\text{s}$).
   - Because $R_{DS(on)} \propto \frac{1}{\mu C_{ox} (W/L)}$, achieving the same on-resistance in a PMOS requires roughly $2.5\times$ to $3.0\times$ larger die silicon area (and consequently proportional increases in gate charge $Q_g$ and cost) compared to an NMOS of identical voltage and current ratings.

---

## 2. Circuit Topologies: High-Side Power Switching

Unlike an NMOS which requires a complex bootstrap circuit or charge pump to drive its gate above the positive supply rail in high-side configurations, a PMOS can be turned ON simply by pulling its gate down toward ground:

### 1. Direct Low-Voltage High-Side Switch ($V_{IN} \le 12\,\text{V}$):
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

### 2. High-Voltage High-Side Switch with Zener Gate Clamp ($V_{IN} > 20\,\text{V}$):
If $V_{IN} = 24\,\text{V}$ or $48\,\text{V}$, pulling the gate to ground would subject the gate oxide to $V_{GS} = -24\,\text{V}$ or $-48\,\text{V}$, instantly destroying the oxide (since $V_{GS(max)} = \pm 20\,\text{V}$). A Zener clamp is mandatory:

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
   - The Gate is tied through $R_1$ to Ground. Therefore, $V_{GS} = V_G - V_S \approx 0\,\text{V} - V_{IN} = -V_{IN}$.
   - Once $|V_{GS}| > |V_{TH}|$, the PMOS channel turns fully ON. The low $R_{DS(on)}$ shunts the body diode, reducing voltage drop across the switch to mere millivolts ($V_{drop} = I_{LOAD} \cdot R_{DS(on)}$) with zero forward diode power dissipation.
2. **Reverse Connection (Battery Inverted)**:
   - The Source terminal is connected to the negative battery terminal, while the Gate is connected to the positive terminal through $R_1$.
   - Consequently, $V_G > V_S$, meaning $V_{GS} > 0\,\text{V}$. The PMOS channel remains completely OFF.
   - The body diode is reverse-biased, completely blocking any reverse current flow and safeguarding all downstream circuits.

---

## 4. Key Datasheet Parameters & Traps

| Parameter | Symbol | Critical Significance | Rule of Thumb |
| :--- | :--- | :--- | :--- |
| **Drain-to-Source Breakdown** | $V_{(BR)DSS}$ | Negative breakdown voltage between D and S | Must handle max positive rail plus inductive overshoot |
| **Gate-to-Source Limit** | $V_{GS(max)}$ | Maximum gate dielectric stress (typically $\pm 20\,\text{V}$) | Clamp with $12\,\text{V} - 15\,\text{V}$ Zener in systems where $V_{IN} > 12\,\text{V}$ |
| **Threshold Voltage** | $V_{GS(th)}$ | Gate voltage where conduction starts (typically $-1.0\,\text{V} \dots -3.0\,\text{V}$) | Ensure drive voltage pulls gate well below $V_{TH}$ (ideally $-10\,\text{V}$) |
| **Static On-Resistance** | $R_{DS(on)}$ | Channel on-resistance | Evaluate at specified $V_{GS}$ (e.g. $-4.5\,\text{V}$ vs $-10\,\text{V}$) |

---

## 5. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | $-V_{DS(max)}$ | $-I_{D(max)}$ | $R_{DS(on)}$ (@-10V) | Typical Use-Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AO3401A** | Alpha & Omega | SOT-23 | $30\,\text{V}$ | $4.0\,\text{A}$ | $44\,\text{m}\Omega$ | Compact 3.3V/5V/12V load switches, battery cutoffs |
| **FDN340P** | onsemi / Fairchild | SOT-23 | $20\,\text{V}$ | $2.0\,\text{A}$ | $70\,\text{m}\Omega$ | Handheld power path management |
| **DMP3098L** | Diodes Inc | SOT-23 | $30\,\text{V}$ | $3.8\,\text{A}$ | $65\,\text{m}\Omega$ | Reverse battery protection in low-power microcontrollers |
| **IRF9540N** | Infineon (IR) | TO-220 | $100\,\text{V}$ | $23\,\text{A}$ | $117\,\text{m}\Omega$ | Industrial high-side actuator/relay switching |
| **SQJ407EP** | Vishay Siliconix | PowerPAK SO-8 | $40\,\text{V}$ | $60\,\text{A}$ | $7.2\,\text{m}\Omega$ | AEC-Q101 Automotive high-side power distribution |
