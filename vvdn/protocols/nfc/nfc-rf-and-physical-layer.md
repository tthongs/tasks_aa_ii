# NFC Physical Layer: RF Physics, Modulation, Antenna Design & Matching Networks

## 1. Electromagnetic Foundations of Near-Field Inductive Coupling

Unlike traditional UHF RFID (860–960 MHz) or Wi-Fi/Bluetooth (2.4 GHz) which communicate via **propagating electromagnetic radiative waves (Far-Field E-field)**, Near Field Communication operates at **13.56 MHz** and relies almost exclusively on **quasi-static magnetic inductive coupling (Near-Field H-field)**.

### 1.1 The Near-Field vs. Far-Field Boundary

The wavelength λ of an electromagnetic wave in free space is given by:

```
λ = c / f_c = (3 * 10^8 m/s) / (13.56 * 10^6 Hz) ≈ 22.12 meters
```

The transition boundary (radian distance r_boundary) between the reactive near-field and the radiative far-field is mathematically defined by:

```
r_boundary = λ / 2π = (22.12 m) / 2π ≈ 3.52 meters
```

- **Operating Region**: In all NFC applications, the physical distance d between reader and card is typically 1 to 4 cm (maximum 10 cm).
- **Physical Consequence**: Because d << 3.52 m, the electric field component E is negligible. The reader antenna does **not** radiate power into space like a dipole; instead, it behaves as the primary winding of an **air-core transformer**, creating an alternating magnetic flux density B(t) that penetrates the secondary coil (the tag).

```text
               Near-Field Region (d << lambda / 2*pi)
  +-------------------------------------------------------------+
  |                                                             |
  |  +--------------------+             +--------------------+  |
  |  |   PCD (Reader)     |   H-Field   |    PICC (Tag)      |  |
  |  |    Transceiver     |  Magnetic   |    Transponder     |  |
  |  |                    |    Flux     |                    |  |
  |  |  +--------------+  |  )  )  ) )  |  +--------------+  |  |
  |  |  | Primary Coil |==|============>|  |Secondary Coil|  |  |
  |  |  |     (L1)     |  |  )  )  ) )  |  |     (L2)     |  |  |
  |  |  +--------------+  |             |  +--------------+  |  |
  |  +--------------------+             +--------------------+  |
  |             \                          /                    |
  |              \--- Mutual Inductance --/                     |
  |                    M = k * sqrt(L1 * L2)                    |
  +-------------------------------------------------------------+
```

### 1.2 Biot-Savart Law and Magnetic Field Strength (H)

The magnetic field strength H(x) generated along the central normal axis x of a circular PCB loop antenna with radius r, turn count N, and peak current I is calculated using the Biot-Savart law:

```
H(x) = (I * N * r^2) / [ 2 * (r^2 + x^2)^(3/2) ]  [A/m]
```

Where:
- H(x): Magnetic field strength along the central coil axis at distance x (A/m)
- I: Current flowing through the loop antenna coil (A)
- N: Number of antenna coil conductor turns
- r: Radius of the circular antenna loop (m)
- x: Axial distance from the plane of the antenna (m)

For a rectangular planar antenna with dimensions a * b (width * height):

```
H(x) = (I * N * a * b) / (4π sqrt(x^2 + (a / 2)^2 + (b / 2)^2)) [ 1 / (x^2 + (a / 2)^2) + 1 / (x^2 + (b / 2)^2) ]
```

### 1.3 Magnetic Field Falloff Rate (1/x^3)

In the far field, radiated power decays according to the inverse-square law (1/r^2). In contrast, in the near-field inductive zone where x >> r:

```
H(x) proportional to 1 / x^3
```

This cubic drop-off provides an inherent physical security perimeter: eavesdropping becomes practically impossible beyond tens of centimeters without massive, highly visible inductive sniffing arrays.

### 1.4 Mutual Inductance (M) and Tag Power Harvesting

The voltage E_tag(t) induced in the tag antenna coil is governed by Faraday's law of electromagnetic induction:

```
E_tag(t) = -N_tag dΦ(t) / dt = -ω * M * I_reader * cos(ω t)
```

Where:
- ω = 2π f_c ≈ 85.2 * 10^6 rad/s (f_c = 13.56 MHz).
- M = k sqrt(L_reader * L_tag) is the mutual inductance.
- k is the inductive coupling coefficient (typically 0.01 <= k <= 0.15 in uncoupled/loosely coupled conditions).

The tag's integrated circuit rectifies this induced alternating voltage through an internal Schottky or CMOS bridge rectifier, charging an internal reservoir capacitor to power its internal state machine, memory, and cryptographic logic.

---

## 2. Downlink Modulation: Reader to Card (PCD -> PICC)

The reader transmits data to the tag by modulating the 13.56 MHz carrier. Three primary modulation schemes are standardized across ISO/IEC 14443 and ISO/IEC 18092.

```text
ISO 14443 Type A (100% ASK, Modified Miller)
  Carrier: 13.56 MHz
  RF Envelope:
  High -----------------+         +-----------------+         +-------
                        |         |                 |         |
  Low                   +---------+                 +---------+
                        |<--t1--->|
                        (Pause: 2 - 3 us)

ISO 14443 Type B / FeliCa (10% ASK, NRZ-L / Manchester)
  RF Envelope:
  High -----------------+         +-----------------+         +-------
                        |  m~10%  |                 |  m~10%  |
  Low                   +---------+                 +---------+
                        Residual Carrier maintained for continuous tag power!
```

### 2.1 ISO/IEC 14443 Type A: 100% ASK with Modified Miller Coding

At the base bitrate of **106 kbps**, Type A utilizes **100% Amplitude Shift Keying (ASK)**, also referred to as On-Off Keying (OOK) or carrier blanking.
- **Elementary Time Unit (1 etu)**: 1 etu = 128 / f_c ≈ 9.44\ µs.
- **Carrier Pause (t_1)**: The RF field is dropped to near-zero amplitude for a duration of t_1 = 2.0 to 3.0\ µs (27 to 40 carrier cycles).
- **Modified Miller Encoding Rules**:
  - **Bit '1'**: A pause occurs in the **middle** of the bit interval (4.72\ µs from the start).
  - **Bit '0'**:
    - If preceded by a '0': A pause occurs at the **start** of the bit interval.
    - If preceded by a '1': **No pause** occurs throughout the entire bit interval.
  - **Start of Frame (SOF)**: Encoded as a bit '0' with a mandatory initial pause.
  - **End of Frame (EOF)**: Logic level '0' without pauses for 1 etu.

> [!NOTE]
> **Why Modified Miller?** Standard Miller coding or NRZ could result in prolonged periods of zero RF power during long sequences of zeros. The Modified Miller rules guarantee that the carrier is never interrupted for more than 3.0\ µs, ensuring the passive card's power supply does not collapse.

### 2.2 ISO/IEC 14443 Type B: 10% ASK with NRZ-L Coding

Type B was designed for high-security applications (passports, national ID cards, banking) where constant tag power supply is critical:
- **Modulation Index (m)**:
  ```
m = (A - B) / (A + B) * 100\% (8\% <= m <= 14\%)
```
  Where A is the unmodulated carrier amplitude and B is the modulated lower amplitude.
- **Coding**: Non-Return-to-Zero Level (**NRZ-L**).
  - High carrier amplitude (A) represents logic **1**.
  - Lower carrier amplitude (B) represents logic **0**.
- **Bit Rates**: Standardized at **106, 212, 424, and 848 kbps**.
- **SOF / EOF**:
  - SOF: 10 to 11 low bits (logic 0) followed by 2 to 3 high bits (logic 1).
  - EOF: 10 to 11 low bits.

### 2.3 JIS X 6319-4 / FeliCa: 10% ASK with Manchester Coding

Used widely in Japanese mass transit (Suica, Pasmo) and NFC Forum Type 3 Tags:
- Operates natively at **212 kbps** and **424 kbps**.
- Uses **Manchester Coding**:
  - Logic **0**: Negative edge in the center of the bit (High-to-Low transition).
  - Logic **1**: Positive edge in the center of the bit (Low-to-High transition).
- Guaranteed edge transition in every bit simplifies clock recovery in high-noise environments.

---

## 3. Uplink Modulation: Card to Reader (PICC -> PCD)

A passive tag contains no battery and no active 13.56 MHz oscillator. It cannot transmit a radio signal back to the reader. Instead, it utilizes **Load Modulation**.

```text
               TRANSCEIVER RX DEMODULATOR                  TAG LOAD MODULATOR
               +--------------------------+                +-------------------------+
               | Primary Coil (L1)        |                | Secondary Coil (L2)     |
13.56 MHz =====|==========================|== Mutual M ===>|==========+==============|
Carrier Source | V_coil = V0 +- Delta_V   |                |          |              |
               +--------------------------+                |      +---+---+          |
                            |                              |      |  FET  | (Switch) |
                     Envelope Detector                     |      +---+---+          |
                     & Bandpass Filter                     |          |              |
                     (Tuned to 848 kHz)                    |      [R_mod / C_mod]    |
                            |                              |          |              |
                     Data to SPI FIFO                      |         GND             |
                                                           +-------------------------+
```

### 3.1 Physics of Inductive Load Modulation

The reader antenna coil has an uncoupled input impedance Z_in = R_1 + jω L_1.
When a tag is coupled with mutual inductance M, the **reflected impedance** Δ Z seen at the reader's primary terminals is:

```
Δ Z = (ω^2 M^2) / Z_tag
```

Where Z_tag = R_tag + j(ω L_2 - 1 / (ω C_2)).

When the tag turns on an internal MOSFET switch, connecting an extra load resistor (R_mod) or tuning capacitor (C_mod) across its antenna coil:
1. The tag's impedance Z_tag changes abruptly.
2. The reflected impedance Δ Z changes proportionally.
3. This creates a tiny voltage variation Δ V across the reader's primary antenna coil (V_coil = V_0 ± Δ V).
4. The reader's analog front-end (AFE) detects and demodulates this small voltage fluctuation (Δ V ≈ 10 mV to 100 mV riding on a 10 V to 20 V carrier).

### 3.2 The 848 kHz Subcarrier

If the tag modulated the carrier directly at 106 kbps, the sidebands would fall at 13.56 MHz ± 106 kHz. At these offsets, the phase noise, amplitude flicker noise (1/f noise), and carrier leakage from the high-power reader transmitter overwhelm the minute load-modulation signal.

To solve this, ISO/IEC 14443 introduces an **848 kHz subcarrier**:

```
f_s = f_c / 16 = (13.56 MHz) / 16 = 847.5 kHz ≈ 848 kHz
```

- The tag modulates the 848 kHz subcarrier with its digital data.
- The subcarrier then load-modulates the 13.56 MHz carrier.
- This translates the card signal into two distinct spectral sidebands located well outside the reader's phase noise floor:
  - **Lower Sideband (LSB)**: 13.56 MHz - 848 kHz = 12.712 MHz
  - **Upper Sideband (USB)**: 13.56 MHz + 848 kHz = 14.408 MHz

```text
               13.56 MHz Carrier
                     |
                     |
                  |  |  |
                  |  |  |  <- Reader Phase Noise
               +--+--+--+--+
               |  |  |  |  |
               |  |  |  |  |
     LSB       |  |  |  |  |       USB
  12.712 MHz   |  |  |  |  |    14.408 MHz
      |        |  |  |  |  |        |
    +---+      |  |  |  |  |      +---+
    |   |      |  |  |  |  |      |   |
----+---+------+--+--+--+--+------+---+---- Frequency
    |<--- 848 kHz --->|<--- 848 kHz --->|
```

### 3.3 Uplink Encoding Schemes

| Protocol / Bitrate | Subcarrier Used? | Subcarrier Modulation | Data Bit Coding |
| :--- | :--- | :--- | :--- |
| **ISO 14443A (106 kbps)** | **Yes (848 kHz)** | On/Off Subcarrier Keying | **Manchester Coding** on subcarrier |
| **ISO 14443B (106 kbps)** | **Yes (848 kHz)** | **BPSK** (Δθ = 180°) | **NRZ-L** |
| **ISO 14443A/B (212/424/848 kbps)** | **No** (Direct) | Direct Load Modulation | **BPSK or Manchester** |
| **FeliCa (212 / 424 kbps)** | **No** (Direct) | Direct Load Modulation | **Manchester** |
| **ISO 15693 (26.48 kbps)** | **Yes (424 or 484 kHz)**| Single or Dual Subcarrier | **Manchester** |

---

## 4. Reader Antenna Design & Circuit Modeling

An NFC reader antenna is an inductive loop fabricated directly onto PCB copper layers (FR-4) or flex-PCB.

```text
Equivalent Electrical Model of a Planar PCB Loop Antenna:
             R_ant                L_ant
     +-------\/\/\/---------------+---UUUUU---+
     |        (Ohmic)             | (Loop L)  |
     |                            |           |
    ===                          ===          |
    --- C_p                      --- C_p      |
     |  (Parasitic Capacitance)   |           |
     +----------------------------+-----------+
```

### 4.1 Planar Rectangular Antenna Inductance Calculation

For a rectangular loop antenna on PCB with N turns, conductor width w, conductor thickness t, track spacing s, outer dimensions a_out * b_out, and inner dimensions a_in * b_in:

```
L_ant = (µ_0 µ_r) / π [ -2(a + b) + 2sqrt(a^2 + b^2) - a * ln((a + sqrt(a^2 + b^2)) / b) - b * ln((b + sqrt(a^2 + b^2)) / a) + a * ln(2a / (w+t)) + b * ln(2b / (w+t)) ] * N^1.8
```

Where:
- µ_0 = 4π * 10^-7 H/m.
- a = (a_out + a_in) / 2 (mean length).
- b = (b_out + b_in) / 2 (mean width).

**Rule of Thumb for Bring-up**:
A typical 4-turn rectangular PCB antenna of dimensions 45 mm * 35 mm with 0.5 mm track width yields:
```
L_ant ≈ 1.5\ µH to 2.5\ µH, R_ant ≈ 0.8\ Ω to 1.5\ Ω, C_p ≈ 2 pF to 5 pF
```

### 4.2 Antenna Quality Factor (Q) and Bandwidth Trade-Off

The Quality Factor (Q) of the antenna loop defines the ratio of stored energy to dissipated energy per cycle:

```
Q = (ω * L_ant) / R_total = (2π * (13.56 * 10^6) * L_ant) / (R_ant + R_Q)
```

The -3 dB RF operational bandwidth BW is inversely proportional to Q:

```
BW = f_c / Q = (13.56 MHz) / Q
```

#### The Fundamental NFC Design Dilemma:

```text
High Q (Q > 35):
  [+] High magnetic field H (long operating range).
  [-] Narrow Bandwidth (BW < 380 kHz).
  [-] Severe attenuation of 848 kHz subcarrier sidebands (12.71 MHz & 14.41 MHz).
  [-] Heavy ringing during 100% ASK carrier pauses -> Violates ISO 14443A pulse shapes!

Low Q (Q < 10):
  [+] Wide Bandwidth (BW > 1.35 MHz) -> Crisp pulses, excellent high-bitrate performance.
  [-] Low H-field strength -> Drastically reduced reading range (< 1 cm).
```

**Recommended Industry Design Targets**:
- **Standard ISO 14443 Type A (106 kbps)**: Q = 20 to 30 (BW ≈ 450 to 680 kHz).
- **High-speed NFC (212, 424, 848 kbps) & Type B**: Q = 10 to 15 (BW ≈ 900 kHz to 1.35 MHz).

To lower an antenna's natural Q to the target value, hardware designers add dedicated **damping resistors (R_Q)** in series with the antenna coil.

---

## 5. Complete RF Analog Front-End Matching Network

NFC transceivers (PN532, MFRC522, ST25R3916) feature differential push-pull output drivers (`TX1` and `TX2`) operating from 3.3V or 5V supplies.
The differential output is a square wave. The analog front-end circuit must perform three distinct functions:
1. **EMC Harmonic Filtering**: Suppress 2nd (27.12 MHz), 3rd (40.68 MHz), and higher harmonics to comply with FCC / CE RED regulations.
2. **Impedance Matching**: Transform the low-impedance inductive antenna (Z_ant) to match the target driver output load (R_load ≈ 20\ Ω to 50\ Ω).
3. **Receive Demodulation Path**: Tap the antenna voltage into the `RX` pin through a capacitive voltage divider and high-pass envelope network.

```text
                            DIFFERENTIAL MATCHING NETWORK SCHEMATIC
                EMC Low-Pass Filter       Matching Network
                +--- L0 ---+             +--- C_series ---+
TX1 >-----------+          +-------------+                +---+
                |          |             |                |   |
               === C0     === C_parallel ===             [RQ] |
               ---        ---            ---              |   |
                |          |              |               +---+
               GND        GND            GND                  |
                                                              +--- L_ant (Antenna Coil)
                                                              |
                                                              +---+
                |          |              |                   |   |
               GND        GND            GND                 [RQ] |
                |          |              |                   |   |
               === C0     === C_parallel ===                  |   |
                |          |             |                +---+
TX2 >-----------+          +-------------+                +---+
                +--- L0 ---+             +--- C_series ---+

                                         C_rx1 (10-22 pF)
Antenna Tap >---------------------------------+---||---> RX Pin on Transceiver
                                              |
                                             [R_rx] (1k - 2.2k)
                                              |
                                            VMID (Internal Bias Reference)
```

### 5.1 EMC Low-Pass Filter Calculation

The EMC filter is a 2nd-order LC low-pass filter with cutoff frequency f_EMC selected between **17 MHz and 22 MHz**:

```
f_EMC = 1 / (2π sqrt(L_0 * C_0)) ≈ 20 MHz
```

Standard component values:
- L_0 = 470 nH or 560 nH (Shielded, high-current, low-R_DC RF inductors).
- C_0:
  ```
C_0 = 1 / (4π^2 f_EMC^2 L_0) ≈ 1 / (4π^2 (20 * 10^6)^2 (560 * 10^-9)) ≈ 113 pF (Use 100 pF to 120 pF COG/NPO)
```

### 5.2 Series (C_series) and Parallel (C_parallel) Matching Capacitors

Given antenna inductance L_ant, target quality factor Q_target, and driver differential load resistance R_L:

1. Calculate the required damping resistance R_total:
   ```
R_total = (ω * L_ant) / Q_target => R_Q = (R_total - R_ant) / 2
```
2. Calculate the parallel matching capacitance C_parallel:
   ```
C_parallel ≈ 1 / (ω^2 L_ant) * (1 - R_total / R_L)
```
3. Calculate the series matching capacitance C_series:
   ```
C_series ≈ 1 / (ω sqrt(R_L * R_total))
```

> [!TIP]
> **Component Selection**: All matching capacitors (C_0, C_series, C_parallel) **must** be **C0G/NP0 dielectric ceramic capacitors** with ± 1\% or ± 2\% tolerance and rated for >= 50V. Standard X7R or X5R dielectrics have severe voltage-dependent capacitance drops and thermal drift that will detune the 13.56 MHz resonance.

---

## 6. Metal Proximity, Ferrite Shielding & Tuning in Enclosures

When an NFC antenna is mounted inside a product enclosure near batteries, copper ground planes, aluminum shielding, or display panels:

```text
WITHOUT FERRITE SHIELDING (Broken):
  +---------------------------------------------+
  | NFC Coil (AC Magnetic Flux B)               |
  +---------------------------------------------+
           |           |           |
           v           v           v
  ===============================================  <- Metal Enclosure / LiPo Battery
     Eddy Currents (I_eddy) induced in metal
     generate opposing counter-flux (Lenz's Law)
  ===============================================
  Result: Total H-field canceled; L_ant drops by 30-50%;
  Resonance shifts from 13.56 MHz to 17+ MHz; Reader FAILS.

WITH SINTERED FERRITE ABSORBER SHEET (Working):
  +---------------------------------------------+
  | NFC Coil                                    |
  +---------------------------------------------+
  ===============================================  <- Sintered Ferrite Sheet (mu_r' > 120)
     Flux lines channeled horizontally through
     high-permeability ferrite material.
  ===============================================
  ===============================================  <- Metal Enclosure / LiPo Battery
     ZERO eddy currents in metal! Field preserved.
```

### Engineering Guidelines for Metal Environments:
1. **Apply Sintered Ferrite Sheet**: Place a high-permeability sheet (e.g. 3M AB5000, Würth WE-FSFS) between the PCB coil and the metal surface.
2. **Ferrite Specifications at 13.56 MHz**:
   - Real permeability: µ_r' >= 100 to 150 (channels magnetic flux).
   - Imaginary loss factor: µ_r'' < 3 to 5 (minimizes RF energy absorption).
3. **Always Retune In-Situ**: Measure L_ant and tune C_series, C_parallel with the antenna mounted in its final mechanical enclosure with all screws, battery, and displays installed.
