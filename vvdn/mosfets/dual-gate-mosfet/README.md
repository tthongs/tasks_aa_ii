# Dual-Gate MOSFETs (Tetrode FET): RF Mixers & Automatic Gain Control

A **Dual-Gate MOSFET** (often referred to as a **MOSFET Tetrode**) is a multi-electrode field-effect transistor featuring two separate, independently biased control gates (**Gate 1** and **Gate 2**) arranged in series over a single shared conduction channel between Source and Drain. By monolithically integrating a **cascode amplifier topology** onto a single silicon die, dual-gate MOSFETs achieve an ultra-low reverse transfer (Miller) capacitance (C_rss < 0.02 pF), wide dynamic **Automatic Gain Control (AGC)** range, and superior intermodulation performance across VHF, UHF, and microwave communications.

---

## 1. Semiconductor Physics & Monolithic Cascode Equivalence

```text
       Source (S)           Gate 1 (G1)          Gate 2 (G2)           Drain (D)
       ┌────────┐            ┌────────┐           ┌────────┐           ┌────────┐
       │   Al   │            │ Poly-Si│           │ Poly-Si│           │   Al   │
       ├───┬────┴────────────┴───┬────┴───────────┴───┬────┴───────────┴───┬────┤
       │n+ │  SiO2 Gate 1 Oxide  │ n-Island (Virtual) │ SiO2 Gate 2 Oxide  │ n+ │
       └───┴─────────────────────┴────────────────────┴────────────────────┴────┘
                    p-Substrate (Internally connected to Source)
```

### Monolithic Cascode Equivalence:
A dual-gate MOSFET behaves electrically as two distinct transistors connected in series:
1. **Lower Transistor (M_1)**: A **Common-Source (CS)** amplifier whose gate is Gate 1.
2. **Upper Transistor (M_2)**: A **Common-Gate (CG)** amplifier whose gate is Gate 2.

```text
                         Drain (D)
                            │
                         ┌──┴──┐
       Gate 2 (G2) ──────┤ M2  │ (Common-Gate Stage: Low input impedance, high output Z)
       (AGC / LO)        └──┬──┘
                            │ (Virtual Internal Node)
                         ┌──┴──┐
       Gate 1 (G1) ──────┤ M1  │ (Common-Source Stage: High input impedance)
       (RF Input)        └──┬──┘
                            │
                         Source (S) (Tied to RF Ground)
```

### Elimination of Miller Capacitance & Unconditional Stability:
- In conventional single-gate RF amplifiers, the Drain-to-Gate capacitance (C_gd ≈ 1 - 5 pF) feeds inverted high-voltage RF output back to the input gate. At high frequencies, this negative conductance causes self-oscillation unless complex, band-limited neutralization transformers are added.
- In a Dual-Gate MOSFET, **Gate 2 is bypassed to AC ground** via a decoupling capacitor (10 nF).
- Gate 2 acts as a grounded electrostatic Faraday shield interposed between the drain and Gate 1.
- Reverse feedback capacitance is slashed to **C_rss <= 0.02 pF**, ensuring unconditional high-frequency stability up to 1 GHz without neutralization!

---

## 2. RF Circuit Topologies: AGC Amplifiers & Active Mixers

### 1. Low-Noise RF Amplifier with Automatic Gain Control (AGC):
In communication receivers (FM, VHF maritime, SDR front-ends), incoming signal strength varies over orders of magnitude (1 µV ... 100 mV). A dual-gate MOSFET provides clean dynamic gain adjustment:

```text
           +V_DD Supply (+9V / +12V)
                 │
               [ L1 ] RF Choke / LC Tuned Tank
                 │
                 ├───[ Cout ]───> RF Output
                 │
              Drain (D)
                 │
              ┌──┴──┐
AGC Bias ─────┤ G2  │ Dual-Gate FET (e.g. BF998)
Control       │     │
(0V to +4V)   └──┬──┘
                 │
              ┌──┴──┐
RF Signal ────┤ G1  │
Input (50Ω)   └──┬──┘
                 │
              Source (S) ──┬──[ Rs: 270Ω ]──┬── GND
                           │                │
                           └──[ Cs: 10nF ]──┘
```

#### How AGC Operates Without Detuning the Front-End:
- Varying the DC voltage on **Gate 2** (0 V ... +4 V) modulates the drain-to-source voltage of the lower transistor M_1, dynamically adjusting overall transconductance g_m over a **> 40 dB attenuation range**.
- Crucially, changing V_G2 has **virtually zero influence on the input capacitance at Gate 1** (C_iss(G1)). The tuned RF input filter remains precisely centered on the desired RF channel without frequency pulling or bandwidth distortion!

---

### 2. Active Dual-Gate RF Mixer:
By injecting two distinct frequencies into Gate 1 and Gate 2, the non-linear cross-multiplication across the shared channel acts as a high-performance active mixer:
- **Gate 1 (G_1)**: Driven by weak received RF antenna signal (f_RF).
- **Gate 2 (G_2)**: Driven by local oscillator (f_LO).
- **Drain (D)**: Connected to an intermediate frequency (IF) tuned tank (f_IF = |f_RF - f_LO|).
- High isolation between G_1 and G_2 (> 30 dB) prevents local oscillator radiation from leaking back into the antenna.

---

## 3. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | V_DS(max) | I_D(max) | Forward Transfer g_fs | C_rss (Typ) | Target Application |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BF998** | NXP / Vishay | SOT-143 | 12 V | 30 mA | 24 mS | **0.015 pF** | VHF/UHF TV tuners, wideband SDR front-ends |
| **BF992** | NXP Semiconductor| SOT-143 | 20 V | 30 mA | 20 mS | 0.020 pF | Low-noise RF preamplifiers, 433/868 MHz ISM |
| **3SK294** | Toshiba | S-Mini (4-pin) | 10 V | 20 mA | 28 mS | 0.012 pF | UHF wireless microphones, cellular LNA |
| **CF750** | Siemens / Infineon| SOT-143 | 12 V | 25 mA | 22 mS | 0.018 pF | Low-noise FM broadcast front-ends |
