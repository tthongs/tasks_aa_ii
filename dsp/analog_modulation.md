# Analog Modulation

## Amplitude Modulation (AM)

In AM, the amplitude of the carrier wave is varied in proportion to the message signal.

### Amplitude Modulation (AM): A Deeper Dive

Amplitude Modulation (AM) is a modulation technique where the amplitude of a high-frequency carrier signal is varied in proportion to the instantaneous amplitude of a lower-frequency message signal. The frequency and phase of the carrier remain constant.

**The Concept**

Imagine you have a message you want to send over a long distance, like your voice. Your voice signal has a relatively low frequency and can't travel far on its own. To send it over a long distance, you piggyback it onto a high-frequency radio wave, called the **carrier wave**.

In AM, the message signal "shapes" the amplitude of the carrier wave. When the message signal's amplitude is high, the carrier's amplitude is high. When the message signal's amplitude is low, the carrier's amplitude is low. The high-frequency carrier wave then carries this information to the receiver.

**AM Modulator**

A simple AM modulator can be implemented using a multiplier and an adder.

*(Block diagram of an AM modulator: A message signal m(t) is multiplied by a carrier signal cos(2πf_c*t), and the result is added to the carrier signal itself.)*

The message signal `m(t)` is first multiplied by the carrier signal `cos(2πf_c*t)`. This produces two sidebands. Then, the carrier signal is added back to create the final AM signal. This ensures that the carrier component is present in the output, which is important for simple demodulation.

**AM Demodulator (Envelope Detector)**

One of the main advantages of AM is the simplicity of its demodulation. A simple and effective demodulator is the **envelope detector**.

*(Block diagram of an envelope detector: An AM signal passes through a diode, which rectifies the signal. Then, a low-pass filter (a capacitor and a resistor) smooths out the high-frequency carrier, leaving the original message signal.)*

The envelope detector consists of:
1.  **A rectifier (diode):** This allows only the positive half of the AM signal to pass through.
2.  **A low-pass filter (capacitor and resistor):** The capacitor charges up on the positive peaks of the rectified signal and then discharges slowly through the resistor. This smooths out the high-frequency carrier wave, and the output voltage follows the "envelope" of the AM signal, which is the original message signal.

This type of demodulator is very cheap and simple to build, which is why AM radio receivers were so common and affordable.

### Derivation of the AM Signal Expression

Let the message signal be `m(t)` and the carrier signal be `c(t) = A_c * cos(2πf_c*t)`.

In amplitude modulation, the amplitude of the carrier is varied linearly by the message signal. The amplitude of the modulated signal, `A_mod(t)`, can be expressed as:

`A_mod(t) = A_c + k_a * m(t)`

Here, `A_c` is the unmodulated carrier amplitude and `k_a` is the modulator's amplitude sensitivity. The term `k_a * m(t)` represents the variation in amplitude caused by the message signal.

To ensure that the envelope of the modulated signal is always positive and follows the shape of `m(t)`, we can rewrite the expression as:

`A_mod(t) = A_c * [1 + (k_a / A_c) * m(t)]`

Let `μ = k_a * A_m / A_c` be the **modulation index**, where `A_m` is the peak amplitude of the message signal `m(t)`. If we normalize `m(t)` such that its peak amplitude is 1, we can simplify the expression for the modulation index to `μ = k_a / A_c`. Then we have:

`A_mod(t) = A_c * [1 + μ * m(t)]`

The complete AM signal `s(t)` is this time-varying amplitude multiplied by the carrier wave:

`s(t) = A_mod(t) * cos(2πf_c*t)`
`s(t) = A_c * [1 + μ * m(t)] * cos(2πf_c*t)`

This is the standard expression for a double-sideband full carrier (DSB-FC) AM signal.

**The Modulation Index (μ)**

The modulation index `μ` is a crucial parameter in AM. It determines the extent to which the carrier amplitude is varied by the message signal.

*   **μ < 1 (Undermodulation):** The carrier amplitude never drops to zero. The original message signal can be perfectly recovered by an envelope detector.
*   **μ = 1 (100% Modulation):** The carrier amplitude just drops to zero at the negative peaks of the message signal. This is the ideal case for maximum power efficiency with an envelope detector.
*   **μ > 1 (Overmodulation):** The carrier amplitude reverses its polarity at the negative peaks of the message signal. This causes distortion in the demodulated signal when using an envelope detector, as the envelope no longer follows the shape of the message signal.

### AM Spectrum and Bandwidth

To understand the frequency characteristics of an AM signal, we need to look at its spectrum. Let's start with the AM signal expression:

`s(t) = A_c * [1 + μ * m(t)] * cos(2πf_c*t)`
`s(t) = A_c * cos(2πf_c*t) + A_c * μ * m(t) * cos(2πf_c*t)`

This expression shows that the AM signal is composed of two parts:
1.  **The Carrier:** `A_c * cos(2πf_c*t)`
2.  **The Modulated Signal:** `A_c * μ * m(t) * cos(2πf_c*t)`

Let's find the Fourier transform of each part. Let `M(f)` be the Fourier transform of the message signal `m(t)`.

The Fourier transform of the carrier is a pair of impulses at `+f_c` and `-f_c`:

`F[A_c * cos(2πf_c*t)] = (A_c/2) * [δ(f - f_c) + δ(f + f_c)]`

The Fourier transform of the modulated signal is given by the modulation property of the Fourier transform:

`F[m(t) * cos(2πf_c*t)] = (1/2) * [M(f - f_c) + M(f + f_c)]`

So, the Fourier transform of the complete AM signal `s(t)` is:

`S(f) = (A_c/2) * [δ(f - f_c) + δ(f + f_c)] + (A_c*μ/2) * [M(f - f_c) + M(f + f_c)]`

**The AM Spectrum**

The spectrum of the AM signal consists of:
*   **A carrier component** at `f_c`.
*   **An upper sideband (USB)**, which is a shifted version of the message signal's spectrum, centered at `f_c`.
*   **A lower sideband (LSB)**, which is another shifted version of the message signal's spectrum, centered at `f_c`.

Let's assume the message signal `m(t)` is a single-tone sinusoid with frequency `f_m`: `m(t) = cos(2πf_m*t)`. Its spectrum `M(f)` consists of two impulses at `+f_m` and `-f_m`.

The AM spectrum will then have:
*   The carrier at `f_c`.
*   The upper sideband at `f_c + f_m` and `f_c - f_m`. But since `f_c > f_m`, `f_c - f_m` is positive.  Let's be more precise.
    `M(f-f_c)` will have impulses at `f-f_c = f_m` and `f-f_c = -f_m`, which means `f = f_c+f_m` and `f = f_c-f_m`.
    `M(f+f_c)` will have impulses at `f+f_c = f_m` and `f+f_c = -f_m`, which means `f = -f_c+f_m` and `f = -f_c-f_m`.
    So, for positive frequencies, the spectrum has components at `f_c`, `f_c + f_m`, and `f_c - f_m`.

*(A diagram showing the spectrum of a single-tone AM signal. It has a large carrier spike at f_c, and two smaller sideband spikes at f_c - f_m and f_c + f_m.)*

**Bandwidth of AM**

The bandwidth of the AM signal is the difference between the highest and lowest frequencies in its spectrum. From the diagram, we can see that the bandwidth is:

`BW = (f_c + f_m) - (f_c - f_m) = 2 * f_m`

If the message signal has a bandwidth of `W` (i.e., its frequencies range from 0 to `W`), then the AM signal will have a bandwidth of `2W`.

The AM signal occupies twice the bandwidth of the original message signal. This is one of the main disadvantages of standard AM.

### AM Power Efficiency

A major drawback of standard AM (DSB-FC) is its poor power efficiency. Much of the transmitted power is contained in the carrier, which carries no information.

Let's analyze the power distribution in an AM signal. The total power `P_t` is the sum of the carrier power `P_c` and the sideband power `P_sb`.

`P_t = P_c + P_sb`

The AM signal is `s(t) = A_c * cos(2πf_c*t) + A_c * μ * m(t) * cos(2πf_c*t)`.
Let's assume the message signal is a single tone `m(t) = cos(2πf_m*t)`.

`s(t) = A_c * cos(2πf_c*t) + A_c * μ * cos(2πf_m*t) * cos(2πf_c*t)`
`s(t) = A_c * cos(2πf_c*t) + (A_c*μ/2) * [cos(2π(f_c - f_m)t) + cos(2π(f_c + f_m)t)]`

This signal has three components: the carrier, the lower sideband, and the upper sideband. The power of a sinusoidal signal `A*cos(ωt)` is `A^2 / (2R)`. Assuming `R=1` for simplicity:

*   **Carrier Power:** `P_c = A_c^2 / 2`
*   **Lower Sideband Power:** `P_lsb = (A_c*μ/2)^2 / 2 = A_c^2 * μ^2 / 8`
*   **Upper Sideband Power:** `P_usb = (A_c*μ/2)^2 / 2 = A_c^2 * μ^2 / 8`

The total sideband power is:

`P_sb = P_lsb + P_usb = 2 * (A_c^2 * μ^2 / 8) = A_c^2 * μ^2 / 4`

We can also express the sideband power in terms of the carrier power:

`P_sb = (A_c^2 / 2) * (μ^2 / 2) = P_c * (μ^2 / 2)`

The total power is:

`P_t = P_c + P_sb = P_c + P_c * (μ^2 / 2) = P_c * (1 + μ^2 / 2)`

**Power Efficiency (η)**

The power efficiency `η` is the ratio of the useful sideband power to the total power:

`η = P_sb / P_t = [P_c * (μ^2 / 2)] / [P_c * (1 + μ^2 / 2)]`
`η = (μ^2 / 2) / (1 + μ^2 / 2) = μ^2 / (2 + μ^2)`

Let's look at the efficiency for different modulation indices:

*   For `μ = 0.5` (50% modulation), `η = 0.5^2 / (2 + 0.5^2) = 0.25 / 2.25 ≈ 11.1%`
*   For `μ = 1` (100% modulation), `η = 1^2 / (2 + 1^2) = 1 / 3 ≈ 33.3%`

Even at 100% modulation, only a third of the total power is in the information-carrying sidebands. The remaining two-thirds is in the carrier. This is why other forms of AM, such as Double-Sideband Suppressed Carrier (DSB-SC) and Single-Sideband (SSB) were developed to improve power efficiency by suppressing the carrier and one of the sidebands.

### AM: Advantages, Disadvantages, and Applications

#### Advantages of AM

*   **Simple Demodulation:** The main advantage of AM is the simplicity and low cost of its demodulators. The envelope detector is a very simple circuit, which made AM radios widely accessible.
*   **Narrow Bandwidth (compared to FM):** Standard AM has a bandwidth of twice the message signal's bandwidth. This is narrower than the bandwidth of an FM signal for a similar message.

#### Disadvantages of AM

*   **Poor Power Efficiency:** As we derived earlier, a large portion of the power is wasted in the carrier, which does not carry any information. This makes AM transmitters inefficient.
*   **Susceptibility to Noise:** AM is highly susceptible to noise. Noise from sources like lightning, electrical equipment, and other radio signals can add to the amplitude of the AM signal and be demodulated along with the original signal, leading to static and interference.
*   **Lower Audio Quality:** The bandwidth of AM radio broadcasts is typically limited to about 5 kHz to accommodate more stations in the AM band. This limits the audio quality, making it less suitable for high-fidelity music broadcasting compared to FM.

#### Applications of AM

*   **AM Radio Broadcasting:** This is the most well-known application of AM. The medium wave (MW) and short wave (SW) bands are used for AM broadcasting.
*   **Air-to-ground communication:** AM is used for VHF communication in aircraft. Its simplicity and reliability make it suitable for this application.
*   **Citizens Band (CB) radio:** AM is used in CB radios for short-distance communication.
*   **Quadrature Amplitude Modulation (QAM):** This is a more advanced form of AM where two carriers, 90 degrees out of phase, are modulated with two different message signals. QAM is a highly efficient modulation scheme used in many digital communication systems, such as modems and digital TV.

## Frequency Modulation (FM)

In FM, the frequency of the carrier wave is varied in proportion to the message signal.

### Frequency and Phase Modulation (FM & PM): A Deeper Dive

In **angle modulation**, the angle of the carrier wave is varied in proportion to the message signal. There are two types of angle modulation: Frequency Modulation (FM) and Phase Modulation (PM).

#### Frequency Modulation (FM)

In FM, the **instantaneous frequency** of the carrier wave is varied linearly by the message signal `m(t)`. The amplitude of the carrier remains constant.

The instantaneous frequency `f_i(t)` is given by:

`f_i(t) = f_c + k_f * m(t)`

where `f_c` is the carrier frequency and `k_f` is the frequency sensitivity of the modulator. The term `k_f * m(t)` represents the **frequency deviation**.

The phase of the FM signal is the integral of the instantaneous frequency:

`θ(t) = 2π ∫ f_i(τ) dτ = 2π ∫ (f_c + k_f * m(τ)) dτ`
`θ(t) = 2πf_c*t + 2πk_f ∫ m(τ) dτ`

The complete FM signal is:

`s_fm(t) = A_c * cos(θ(t)) = A_c * cos(2πf_c*t + 2πk_f ∫ m(τ) dτ)`

**FM Modulator (Voltage-Controlled Oscillator)**

A simple way to generate an FM signal is to use a **Voltage-Controlled Oscillator (VCO)**.

*(Block diagram of a direct FM modulator: A message signal m(t) is fed into a VCO, which produces the FM signal.)*

The VCO is a circuit that produces an oscillating signal whose frequency is proportional to an input voltage. When the message signal is applied to the VCO, it directly generates the FM signal.

#### Phase Modulation (PM)

In PM, the **instantaneous phase** of the carrier wave is varied linearly by the message signal `m(t)`. The amplitude of the carrier remains constant.

The instantaneous phase `θ(t)` is given by:

`θ(t) = 2πf_c*t + k_p * m(t)`

where `k_p` is the phase sensitivity of the modulator. The term `k_p * m(t)` represents the **phase deviation**.

The complete PM signal is:

`s_pm(t) = A_c * cos(2πf_c*t + k_p * m(t))`

**PM Modulator**

A PM signal can be generated by first differentiating the message signal and then using it to frequency modulate a carrier.

*(Block diagram of a PM modulator: A message signal m(t) is passed through a differentiator, and the output is fed into a VCO to produce the PM signal.)*

#### FM/PM Demodulator

Demodulating FM and PM signals is more complex than demodulating AM. A common method is to use a **differentiator followed by an envelope detector**.

*(Block diagram of an FM demodulator: An FM signal is passed through a differentiator. The output is an AM-like signal, which is then demodulated using an envelope detector.)*

The differentiator converts the frequency variations of the FM signal into amplitude variations. The resulting signal is a combination of AM and FM. An envelope detector can then be used to extract the original message signal.

More advanced FM demodulators, such as the **Phase-Locked Loop (PLL)**, provide better performance and noise immunity.

### The Relationship Between FM and PM

FM and PM are closely related forms of angle modulation. The key difference is how the message signal is incorporated into the carrier's angle.

Let's look at the instantaneous phase of FM and PM signals:

*   **FM:** `θ_fm(t) = 2πf_c*t + 2πk_f ∫ m(τ) dτ`
*   **PM:** `θ_pm(t) = 2πf_c*t + k_p * m(t)`

And the instantaneous frequency:

*   **FM:** `f_i_fm(t) = f_c + k_f * m(t)`
*   **PM:** `f_i_pm(t) = (1/2π) * d/dt [θ_pm(t)] = f_c + (k_p / 2π) * dm(t)/dt`

From these equations, we can see two important relationships:

1.  **Generating FM from PM:** If we first integrate the message signal `m(t)` and then use it to phase modulate a carrier, we will generate an FM signal.

    *(Block diagram showing a message signal m(t) passing through an integrator, then to a phase modulator to generate an FM signal.)*

2.  **Generating PM from FM:** If we first differentiate the message signal `m(t)` and then use it to frequency modulate a carrier, we will generate a PM signal.

    *(Block diagram showing a message signal m(t) passing through a differentiator, then to a frequency modulator to generate a PM signal.)*

This close relationship means that FM and PM have very similar characteristics. The main practical difference is in how they respond to the frequency content of the message signal.

*   In **FM**, the frequency deviation is proportional to the amplitude of the message signal, regardless of its frequency.
*   In **PM**, the frequency deviation is proportional to both the amplitude and the frequency of the message signal (because of the differentiation). This means that higher frequency components in the message signal will cause a larger frequency deviation in a PM signal.

Because of its more predictable and controlled bandwidth, FM is much more widely used than PM for analog communications, especially for broadcasting.

### FM and PM Signal Expressions

Let's look at the mathematical expressions for FM and PM signals in more detail, especially for the case of a single-tone message signal.

Let the message signal be a sinusoid: `m(t) = A_m * cos(2πf_m*t)`.

#### FM Signal Expression

The instantaneous frequency of the FM signal is:

`f_i(t) = f_c + k_f * m(t) = f_c + k_f * A_m * cos(2πf_m*t)`

The term `k_f * A_m` is the **peak frequency deviation**, denoted as `Δf`.

`Δf = k_f * A_m`

So, `f_i(t) = f_c + Δf * cos(2πf_m*t)`.

The phase of the FM signal is the integral of the instantaneous frequency:

`θ(t) = 2π ∫ (f_c + Δf * cos(2πf_m*τ)) dτ`
`θ(t) = 2πf_c*t + (2πΔf / 2πf_m) * sin(2πf_m*t)`
`θ(t) = 2πf_c*t + (Δf / f_m) * sin(2πf_m*t)`

The ratio `Δf / f_m` is the **modulation index**, denoted by `β`.

`β = Δf / f_m`

So, the phase is `θ(t) = 2πf_c*t + β * sin(2πf_m*t)`.

And the complete FM signal is:

`s_fm(t) = A_c * cos(2πf_c*t + β * sin(2πf_m*t))`

#### PM Signal Expression

The instantaneous phase of the PM signal is:

`θ(t) = 2πf_c*t + k_p * m(t) = 2πf_c*t + k_p * A_m * cos(2πf_m*t)`

The term `k_p * A_m` is the **peak phase deviation**, which is also the modulation index `β` for PM.

`β = k_p * A_m`

So, the phase is `θ(t) = 2πf_c*t + β * cos(2πf_m*t)`.

And the complete PM signal is:

`s_pm(t) = A_c * cos(2πf_c*t + β * cos(2πf_m*t))`

As you can see, for a sinusoidal message signal, the FM and PM signal expressions are very similar. The only difference is the phase of the modulating term (`sin` for FM, `cos` for PM).

### FM Spectrum and Bessel Functions

The spectrum of an FM signal is much more complex than that of an AM signal. It consists of a carrier and an infinite number of sidebands. The amplitudes of these components are described by **Bessel functions of the first kind**.

Let's start with the single-tone FM signal:

`s_fm(t) = A_c * cos(2πf_c*t + β * sin(2πf_m*t))`

Using the trigonometric identity `cos(A+B) = cos(A)cos(B) - sin(A)sin(B)`, we get:

`s_fm(t) = A_c * [cos(2πf_c*t)cos(βsin(2πf_m*t)) - sin(2πf_c*t)sin(βsin(2πf_m*t))]`

The terms `cos(βsin(2πf_m*t))` and `sin(βsin(2πf_m*t))` can be expanded into a Fourier series, which involves Bessel functions `J_n(β)`:

*   `cos(βsin(θ)) = J_0(β) + 2 * Σ (from n=1 to ∞) J_{2n}(β) * cos(2nθ)`
*   `sin(βsin(θ)) = 2 * Σ (from n=0 to ∞) J_{2n+1}(β) * sin((2n+1)θ)`

Substituting these expansions into the FM signal expression (with `θ = 2πf_m*t`) and after some trigonometric manipulation, we get the following expression for the FM signal:

`s_fm(t) = A_c * Σ (from n=-∞ to ∞) J_n(β) * cos(2π(f_c + nf_m)t)`

**The FM Spectrum**

This expression shows that the FM signal consists of:
*   A carrier component at `f_c` with amplitude `A_c * J_0(β)`.
*   An infinite number of sidebands at frequencies `f_c ± nf_m` (where `n = 1, 2, 3, ...`) with amplitudes `A_c * J_n(β)`.

**Bessel Functions and the Modulation Index (β)**

The values of the Bessel functions `J_n(β)` depend on the modulation index `β`.

*(A plot showing the values of J_n(β) for different n and β. The plot shows that for a given β, the values of J_n(β) decrease as n increases.)*

*   **Small β (Narrowband FM):** When `β` is small (typically `β < 0.2`), only `J_0(β)` and `J_1(β)` are significant. The spectrum consists of the carrier and the first pair of sidebands at `f_c ± f_m`. The bandwidth is approximately `2 * f_m`, similar to AM.
*   **Large β (Wideband FM):** When `β` is large, there are many significant sidebands. The number of significant sidebands increases with `β`.

**Key Properties of the FM Spectrum:**

*   **Constant Power:** The total power of the FM signal is `A_c^2 / 2` and is independent of the modulation index `β`. The power is simply redistributed among the carrier and the sidebands.
*   **Carrier Vanishing:** For certain values of `β`, `J_0(β) = 0`. At these points, the carrier component disappears completely, and all the power is in the sidebands. This is a useful property for measuring the modulation index.

### FM Bandwidth and Carson's Rule

Theoretically, the bandwidth of an FM signal is infinite because it has an infinite number of sidebands. However, in practice, the sidebands with very small amplitudes can be neglected. We need a rule to estimate the **practical bandwidth** of an FM signal.

**Carson's Rule**

Carson's Rule is a widely used rule of thumb to estimate the bandwidth of an FM signal. It states that approximately 98% of the total power in an FM signal is contained within a bandwidth of:

`BW ≈ 2 * (Δf + f_m)`

where:
*   `Δf` is the peak frequency deviation.
*   `f_m` is the highest frequency in the message signal.

We can also express this in terms of the modulation index `β = Δf / f_m`:

`BW ≈ 2 * (β*f_m + f_m) = 2 * f_m * (β + 1)`

**Derivation and Intuition**

Carson's Rule is an empirical rule, and not a strict mathematical derivation. It provides a good approximation for a wide range of modulation indices.

*   **For Narrowband FM (small β):** When `β` is small, `Δf` is small compared to `f_m`. Carson's Rule gives `BW ≈ 2 * f_m`, which is consistent with our observation that NBFM has a bandwidth similar to AM.
*   **For Wideband FM (large β):** When `β` is large, `Δf` is large compared to `f_m`. Carson's Rule gives `BW ≈ 2 * Δf`. This makes sense, as the spectrum is spread over a wide range of frequencies around the carrier, determined by the peak frequency deviation.

Carson's rule provides a bridge between these two extremes. It essentially says that the bandwidth is the sum of the bandwidth of the two sidebands in NBFM (`2*f_m`) and the bandwidth occupied by the frequency sweep in WBFM (`2*Δf`), but this is just an intuitive way to remember the formula. The rule is based on observations of the Bessel functions and the power contained in the sidebands.

**Example: FM Radio**

For a commercial FM radio station in the US:
*   The maximum frequency deviation is `Δf = 75 kHz`.
*   The maximum message frequency (for high-fidelity audio) is `f_m = 15 kHz`.

The modulation index is `β = Δf / f_m = 75 / 15 = 5`.
Using Carson's Rule, the bandwidth is:

`BW ≈ 2 * (75 kHz + 15 kHz) = 2 * 90 kHz = 180 kHz`

This is why FM radio stations are allocated a channel bandwidth of 200 kHz, which includes a guard band to prevent interference with adjacent channels.

### FM/PM: Advantages, Disadvantages, and Applications

#### Advantages of FM/PM

*   **Superior Noise Immunity:** This is the biggest advantage of FM over AM. Noise primarily affects the amplitude of a radio signal. Since the information in an FM signal is carried in its frequency variations, not its amplitude, FM is much more resilient to noise. An amplitude limiter circuit in an FM receiver can remove most of the noise before demodulation.
*   **Higher Audio Quality:** FM broadcasting allows for a wider bandwidth than AM, which results in higher fidelity audio. This is why FM is the preferred standard for music broadcasting.
*   **Constant Power:** The total power of an FM signal is constant, regardless of the modulation index. This makes the design of power amplifiers for FM transmitters simpler than for AM transmitters.

#### Disadvantages of FM/PM

*   **Wider Bandwidth:** FM signals occupy a much wider bandwidth than AM signals. This means that fewer FM stations can be accommodated in a given frequency band.
*   **More Complex Modulators and Demodulators:** FM modulators (VCOs) and demodulators (PLLs, differentiators) are more complex and expensive to implement than their AM counterparts.
*   **Threshold Effect:** In FM, there is a phenomenon called the **threshold effect**. If the signal-to-noise ratio (SNR) at the receiver drops below a certain threshold, the performance of the FM demodulator degrades rapidly, and the output becomes very noisy. AM does not have such a sharp threshold.

#### Applications of FM/PM

*   **FM Radio Broadcasting:** This is the most common application of FM, used for high-quality audio broadcasting in the VHF band (88-108 MHz).
*   **Analog Television Sound:** The audio portion of analog TV signals is transmitted using FM.
*   **Two-way Radio:** FM is widely used in two-way radio systems, such as police, fire, and taxi radios, because of its good noise immunity.
*   **Satellite Communications:** FM is used in some satellite communication links.
*   **Magnetic Tape Recording:** FM is used to record the luminance (black and white) component of a video signal onto magnetic tape, as it is insensitive to the amplitude variations of the tape playback.
*   **Phase modulation (PM)** is less common in analog transmission, but it is the basis for many digital modulation schemes, such as Phase-Shift Keying (PSK).