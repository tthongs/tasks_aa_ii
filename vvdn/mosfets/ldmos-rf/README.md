# Lateral Double-Diffused MOSFETs (LDMOS): RF Power & High-Frequency Amplifiers

A **Lateral Double-Diffused MOSFET** (**LDMOS**) is a specialized power field-effect transistor engineered specifically for high-power, high-gain radio frequency (RF) and microwave amplification across the $1\,\text{MHz} \dots 3.8\,\text{GHz}$ frequency spectrum. By utilizing a lateral conduction profile coupled with an integrated backside grounded substrate flange, LDMOS delivers extreme breakdown voltage ($> 100\,\text{V}$), negligible feedback capacitance ($C_{rss}$), and unmatched VSWR mismatch ruggedness across **4G/5G cellular base stations**, **broadcast transmitters**, **avionics radar**, and **industrial ISM generators**.

---

## 1. Semiconductor Physics & Device Cross-Section

```text
       Source Metal                 Gate (Poly-Si)            Drain Metal
       ┌──────────┐                  ┌──────────┐             ┌──────────┐
       │    Al    │                  │  GATE    │             │  DRAIN   │
       ├───┬──────┴──────────────────┴────┬─────┴─────────────┴───┬──────┤
       │n+ │ p-Body (Channel)   SiO2 Oxide│  n- Drift Extension   │ n+   │
       └───┴───────────────┐              │  (Drift Region)       │──────┘
              p+ Sink      │              └───────────────────────┘
              (Low-Z Plug) │
       ────────────────────┴──────────────────────────────────────────────
       │                    p+ Highly Doped Substrate                    │
       ──────────────────────────────────────────────────────────────────
       │              Backside Flange (Bolted Directly to RF Ground)     │
```

### Key Structural Innovations:
1. **Backside Grounded Flange (Zero Common-Lead Inductance)**:
   - In RF power amplification, common-source parasitic inductance ($L_S$) is the primary destroyer of RF power gain:
     $$G_{max} \propto \frac{1}{\omega^2 \cdot L_S}$$
   - LDMOS connects the top $n^+$ source to the $p^+$ substrate through a low-resistance vertical diffusion plug (the **p+ sink**). The metallic package flange serves simultaneously as the RF ground, DC ground return, and physical heat dissipation mounting surface. Parasitic source inductance is effectively reduced to near zero.
2. **Extended Lateral $n^-$ Drift Region**:
   - To withstand high drain supply voltages ($28\,\text{V} \dots 65\,\text{V}$ DC bus with RF peak swings $> 150\,\text{V}$), an extended lateral $n^-$ drift region is placed between the channel and the drain contact.
   - Stepped field oxide plates over the drift region spread the electric field evenly, preventing localized dielectric breakdown.
3. **Ultra-Low Feedback Miller Capacitance ($C_{rss} = C_{gd}$)**:
   - The lateral separation between the gate and the drain contact slashes $C_{rss}$ to less than $1\,\text{pF}$ even in multi-hundred-watt transistors. Low $C_{rss}$ prevents parasitic self-oscillation and yields immense power gain ($18\,\text{dB} \dots 26\,\text{dB}$) in a single stage.

---

## 2. RF Power Amplifier Topologies: The Doherty Architecture

In modern cellular base stations (4G LTE / 5G NR), signals have extreme Peak-to-Average Power Ratios (PAPR $\approx 7 - 10\,\text{dB}$). Standard Class-AB amplifiers suffer abysmal efficiency at back-off. LDMOS is the core technology powering **Doherty Power Amplifiers**:

```text
                               ┌───[ Main Carrier Amp (Class AB) ]───[ λ/4 Line ]───┐
                               │     (Biased to conduct continuously)               │
    RF Input ──[ 90° Hybrid ]──┤                                                    ├──> RF Out (50Ω)
               Splitter        │                                                    │
                               └───[ Peak / Peaking Amp (Class C) ]─────────────────┘
                                     (Turns ON only during high power crests)
```

### Working Principle:
- **Average Signal Power (Back-off)**: The Main (Carrier) amplifier operates close to saturation (peak efficiency), while the Peaking amplifier is biased in Class C and remains completely OFF.
- **Peak Signal Power (Crest)**: As the RF envelope exceeds average power, the Peaking amplifier turns ON and delivers current, actively pulling down the apparent load impedance seen by the Main amplifier via active load modulation ($\lambda/4$ transmission line).
- **Result**: Peak power efficiency of $> 55\%$ is maintained across the entire modulation envelope.

---

## 3. Ruggedness & Extreme VSWR Survival ($> 65:1$)

In industrial RF applications (CO2 laser excitation, RF plasma chambers, magnetic resonance imaging), antenna disconnection or load arcing creates a total reflection of RF power back into the transistor ($|\Gamma| = 1$).

### Modern "XR" (Extreme Ruggedness) LDMOS:
- Devices such as NXP **BLF188XR** and NXP **MRFX1K80H** integrate monolithic protection diodes and internal capacitive ballasting.
- They withstand a **$65:1$ Voltage Standing Wave Ratio (VSWR)** at all phase angles with zero degradation, surviving conditions that would instantly vaporize standard power MOSFETs.

---

## 4. Commercial Part Catalog & Selection

| Part Number | Manufacturer | Package | Supply ($V_{DD}$) | Frequency Range | Pout (P1dB / Sat) | Power Gain | Primary Application |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AFT09MS007N** | NXP Semiconductor | SOT-89 | $7.5\,\text{V} - 13.6\,\text{V}$ | $136 - 941\,\text{MHz}$ | $7\,\text{W}$ | $20\,\text{dB}$ | Handheld two-way radio, L-band telemetry |
| **BLF188XR** | Ampleon | SOT539A | $50\,\text{V}$ | $10 - 600\,\text{MHz}$ | $1400\,\text{W}$ | $28\,\text{dB}$ | FM broadcast (88-108 MHz), CO2 Laser, MRI |
| **MRFX1K80H** | NXP Semiconductor | NI-1230-4 | $65\,\text{V}$ | $1.8 - 400\,\text{MHz}$ | $1800\,\text{W}$ | $26\,\text{dB}$ | 65:1 VSWR Industrial heating, Avionics radar |
| **MRFE6VP61K25H**| Freescale / NXP | NI-1230 | $50\,\text{V}$ | $1.8 - 600\,\text{MHz}$ | $1250\,\text{W}$ | $24\,\text{dB}$ | High-power pulsed radar, particle accelerators |
