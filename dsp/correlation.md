# Correlation

### Correlation: An Intuitive Introduction

**Correlation** is a mathematical operation that measures the similarity between two signals. It tells us how much one signal resembles another, and it can also tell us if a signal resembles a time-shifted version of another signal.

**The Basic Idea: Shift, Multiply, and Sum**

Imagine you have two signals, `x(t)` and `y(t)`. To find the correlation between them, you perform the following steps for every possible time shift `τ`:

1.  **Shift:** You take one signal, say `y(t)`, and shift it in time by an amount `τ` to get `y(t - τ)`.
2.  **Multiply:** You multiply the first signal `x(t)` by the shifted second signal `y(t - τ)`.
3.  **Sum (Integrate):** You calculate the sum (or integral for continuous signals) of the products over all time.

The result of this process is the **correlation function**, `R_xy(τ)`. The value of this function at a particular time shift `τ` tells you how similar the signal `x(t)` is to the signal `y(t)` shifted by `τ`.

*   **High positive correlation:** If the signals are very similar at a given shift, the product `x(t) * y(t - τ)` will be large and positive for most `t`, resulting in a large positive value for `R_xy(τ)`.
*   **High negative correlation (anti-correlation):** If one signal is like an inverted version of the other at a given shift, the product will be large and negative, resulting in a large negative value for `R_xy(τ)`.
*   **Low correlation:** If the signals are unrelated, the product will be sometimes positive and sometimes negative, and the sum will tend to be small.

**A Graphical Example**

Imagine `x(t)` is a rectangular pulse from t=0 to t=1. Let `y(t)` be the same rectangular pulse.

*   If we don't shift `y(t)` (i.e., `τ=0`), then `x(t)` and `y(t)` are perfectly aligned. Their product is a rectangular pulse, and the integral (the area) is at its maximum.
*   If we shift `y(t)` by a small amount, the pulses will still overlap, and the correlation will be positive but smaller.
*   If we shift `y(t)` by more than the width of the pulse, they will no longer overlap, and the correlation will be zero.

*(A series of diagrams showing two rectangular pulses. The first diagram shows them perfectly aligned, with the product being a pulse of the same width. The next diagrams show one pulse shifting relative to the other, and the product (the overlapping area) decreasing.)*

This process of shifting and multiplying allows us to find out at which time shift the two signals are most similar.

## Cross-Correlation

**Cross-correlation** is the measure of similarity between two **different** signals as a function of the time lag applied to one of them. It is used to find the relationship between two signals.

#### Continuous-Time Cross-Correlation

For two continuous-time energy signals `x(t)` and `y(t)`, the cross-correlation function `R_xy(τ)` is defined as:

`R_xy(τ) = ∫(-∞ to ∞) x(t) * y(t - τ) dt`

where:
*   `τ` is the time lag or delay.
*   `y(t - τ)` is the time-shifted version of the signal `y(t)`.
*   The integral is over all time.

The order of the signals matters. `R_xy(τ)` is the correlation of `x(t)` with a shifted `y(t)`. The correlation of `y(t)` with a shifted `x(t)` is `R_yx(τ)`:

`R_yx(τ) = ∫(-∞ to ∞) y(t) * x(t - τ) dt`

#### Discrete-Time Cross-Correlation

For two discrete-time energy signals `x[n]` and `y[n]`, the cross-correlation sequence `R_xy[m]` is defined as:

`R_xy[m] = Σ(from n=-∞ to ∞) x[n] * y[n - m]`

where:
*   `m` is the time lag or delay in samples.
*   `y[n - m]` is the time-shifted version of the signal `y[n]`.
*   The summation is over all samples.

#### Normalized Cross-Correlation

The result of the correlation function depends on the amplitude of the signals. To make the correlation independent of the signal amplitudes, we can use the **normalized cross-correlation**, which is scaled to be between -1 and 1.

The normalized cross-correlation `ρ_xy(τ)` is defined as:

`ρ_xy(τ) = R_xy(τ) / sqrt(R_xx(0) * R_yy(0))`

where `R_xx(0)` and `R_yy(0)` are the auto-correlations of `x(t)` and `y(t)` at zero lag, which are equal to the energy of the signals.

*   `ρ_xy(τ) = 1` indicates perfect positive correlation at lag `τ`.
*   `ρ_xy(τ) = -1` indicates perfect negative correlation (anti-correlation) at lag `τ`.
*   `ρ_xy(τ) = 0` indicates no correlation at lag `τ`.

### Properties of Cross-Correlation

The cross-correlation function has several important properties:

1.  **Commutativity:** Cross-correlation is not commutative in the same way as multiplication. Instead, it has a conjugate symmetry property:

    `R_xy(τ) = R_yx*(-τ)`

    For real-valued signals, this simplifies to:

    `R_xy(τ) = R_yx(-τ)`

    This means that `R_xy(τ)` and `R_yx(τ)` are mirror images of each other about the `τ=0` axis.

2.  **Time Shifting:** If one of the signals is shifted in time, the cross-correlation function is also shifted:

    If `z(t) = x(t - t_0)`, then `R_zy(τ) = R_xy(τ - t_0)`.

    This property is useful for determining the time delay between two signals.

3.  **Linearity:** The cross-correlation operator is linear. If we have three signals `x(t)`, `y(t)`, and `z(t)`, and two constants `a` and `b`, then:

    `R_{(ax+by)z}(τ) = a * R_xz(τ) + b * R_yz(τ)`

4.  **Cauchy-Schwarz Inequality:** The magnitude of the cross-correlation is always less than or equal to the geometric mean of the energies of the two signals:

    `|R_xy(τ)| <= sqrt(R_xx(0) * R_yy(0))`

    This is the basis for the normalized cross-correlation, which is always between -1 and 1. The equality holds only if `y(t) = c * x(t-τ)` for some constant `c`.

5.  **Relationship with the Frequency Domain:** The Fourier transform of the cross-correlation function is related to the Fourier transforms of the individual signals. This is a very important property that allows for efficient computation of correlation in the frequency domain.

    Let `X(f)` and `Y(f)` be the Fourier transforms of `x(t)` and `y(t)`. The Fourier transform of the cross-correlation `R_xy(τ)` is the **cross-spectral density** `S_xy(f)`:

    `F[R_xy(τ)] = S_xy(f) = X(f) * Y*(f)`

    where `Y*(f)` is the complex conjugate of `Y(f)`.

    This property means that we can compute the cross-correlation by:
    1.  Taking the Fourier transforms of the two signals.
    2.  Multiplying the first transform by the complex conjugate of the second.
    3.  Taking the inverse Fourier transform of the product.

    This is often much faster than computing the correlation directly in the time domain, especially for long signals (thanks to the Fast Fourier Transform algorithm).

### Relationship Between Cross-Correlation and Convolution

Cross-correlation and **convolution** are two fundamental operations in signal processing. They are very similar, but there is a key difference.

**Convolution** is defined as:

`x(t) * y(t) = ∫(-∞ to ∞) x(τ) * y(t - τ) dτ`

**Cross-correlation** is defined as:

`R_xy(t) = ∫(-∞ to ∞) x(τ) * y(τ - t) dτ`  (I'm using `t` as the shift variable here for easier comparison with convolution)

Let's compare the two operations:
*   **Convolution:** `∫ x(τ) * y(t - τ) dτ`
*   **Cross-correlation:** `∫ x(τ) * y(τ - t) dτ`

The only difference is in the second term inside the integral. In convolution, the second signal `y` is **flipped** (time-reversed) and then shifted. In cross-correlation, the second signal is just **shifted**.

**Deriving the Relationship**

We can express cross-correlation in terms of convolution.
`x(t) * y(-t) = ∫ x(τ) y(-(t-τ)) dτ = ∫ x(τ) y(τ-t) dτ`. This is exactly the cross-correlation `R_xy(t)`.

So, the cross-correlation of `x(t)` and `y(t)` is equivalent to the convolution of `x(t)` with the time-reversed version of `y(t)`.

`R_xy(t) = x(t) * y(-t)`

where `*` denotes convolution.

For complex signals, we also need to take the complex conjugate. The relationship is:

`R_xy(t) = x(t) * y*(-t)`

This relationship is very useful. It means that we can use convolution algorithms and hardware to compute cross-correlation. For example, in the frequency domain, we know that convolution becomes multiplication:

`F[x(t) * y(t)] = X(f) * Y(f)`

Using the relationship `R_xy(t) = x(t) * y*(-t)`, we can find the Fourier transform of the cross-correlation:

`F[R_xy(t)] = F[x(t) * y*(-t)] = F[x(t)] * F[y*(-t)]`

The Fourier transform of `y*(-t)` is `Y*(f)`. So, we get:

`F[R_xy(t)] = X(f) * Y*(f)`

This confirms the property we saw earlier.

**Summary of the Relationship**

| Operation        | Time Domain                               | Frequency Domain            |
| ---------------- | ----------------------------------------- | --------------------------- |
| **Convolution**  | `x(t) * y(t)` (flip, shift, multiply, sum)  | `X(f) * Y(f)`               |
| **Correlation**  | `R_xy(t)` (shift, multiply, sum)          | `X(f) * Y*(f)`              |

### Application: Signal Detection with Cross-Correlation (Matched Filtering)

One of the most important applications of cross-correlation is in **signal detection**. This is the process of finding a known signal, or "template", within a longer, noisy signal. This technique is often called **matched filtering**.

**The Scenario**

Imagine you are a radar system. You send out a specific pulse (the template signal, `p(t)`). This pulse travels, reflects off an object, and comes back to your receiver. The received signal, `r(t)`, is a noisy and time-delayed version of the original pulse. Your goal is to detect the presence of the reflected pulse and determine how long it took to come back (which tells you the distance to the object).

`r(t) = A * p(t - t_d) + n(t)`

where:
*   `A` is the amplitude of the reflected pulse.
*   `t_d` is the time delay.
*   `n(t)` is random noise.

**Using Cross-Correlation**

To find the pulse, you can compute the cross-correlation of the received signal `r(t)` with the known template pulse `p(t)`.

`R_rp(τ) = ∫ r(t) * p(t - τ) dt`

Let's see what happens when we substitute the expression for `r(t)`:

`R_rp(τ) = ∫ [A * p(t - t_d) + n(t)] * p(t - τ) dt`
`R_rp(τ) = A * ∫ p(t - t_d) * p(t - τ) dt + ∫ n(t) * p(t - τ) dt`

This expression has two parts:
1.  **The correlation of the pulse with itself (auto-correlation):** `A * ∫ p(t - t_d) * p(t - τ) dt`. This is the auto-correlation of the pulse `p(t)`, shifted by `t_d`. The auto-correlation function of a pulse-like signal has a strong peak at zero lag. So, this term will have a strong peak when `τ = t_d`.
2.  **The correlation of the noise with the pulse:** `∫ n(t) * p(t - τ) dt`. Since the noise `n(t)` is random and uncorrelated with the pulse `p(t)`, this term will be small for all values of `τ`.

**The Result**

The cross-correlation function `R_rp(τ)` will have a distinct peak at the time lag `τ` that corresponds to the delay `t_d` of the reflected pulse. By finding the location of this peak, we can determine the time delay and, therefore, the distance to the object.

*(A diagram showing a noisy signal with a hidden pulse. Below it, the cross-correlation of the noisy signal with the pulse template is shown. The correlation plot has a clear peak at the location of the pulse.)*

This technique is called a **matched filter** because the filter's impulse response is a "matched" (time-reversed) version of the signal we are looking for. In fact, the cross-correlation operation is equivalent to passing the signal through a filter whose impulse response is `p(-t)`.

## Auto-Correlation

**Auto-correlation** is a special case of cross-correlation where a signal is correlated with a time-shifted version of **itself**. It is a measure of how much a signal resembles a delayed version of itself.

Auto-correlation is used to find repeating patterns or periodicities in a signal. If a signal is periodic, its auto-correlation function will also be periodic, with peaks at time lags corresponding to the period of the signal.

#### Continuous-Time Auto-Correlation

For a continuous-time energy signal `x(t)`, the auto-correlation function `R_x(τ)` (or `R_xx(τ)`) is defined as:

`R_x(τ) = ∫(-∞ to ∞) x(t) * x(t - τ) dt`

where `τ` is the time lag.

#### Discrete-Time Auto-Correlation

For a discrete-time energy signal `x[n]`, the auto-correlation sequence `R_x[m]` (or `R_xx[m]`) is defined as:

`R_x[m] = Σ(from n=-∞ to ∞) x[n] * x[n - m]`

where `m` is the time lag in samples.

#### Normalized Auto-Correlation

Similar to cross-correlation, we can define a **normalized auto-correlation** function, `ρ_x(τ)`, which is scaled to be between -1 and 1.

`ρ_x(τ) = R_x(τ) / R_x(0)`

where `R_x(0)` is the auto-correlation at zero lag, which is the total energy of the signal.

The normalized auto-correlation is useful for comparing the periodicity of signals with different energies.

### Properties of Auto-Correlation

The auto-correlation function has several important properties that make it very useful for signal analysis:

1.  **Even Function:** The auto-correlation function is an even function for real-valued signals:

    `R_x(τ) = R_x(-τ)`

    This means the auto-correlation plot is symmetric about the `τ=0` axis.

2.  **Maximum at Zero Lag:** The auto-correlation function is maximum at zero lag (`τ=0`).

    `|R_x(τ)| <= R_x(0)`

    This is because a signal is most similar to itself when there is no time shift.

3.  **Relationship to Signal Energy:** At zero lag, the auto-correlation is equal to the total energy of the signal:

    `R_x(0) = ∫ |x(t)|^2 dt = E_x`

4.  **Periodicity:** If a signal is periodic with period `T`, its auto-correlation function is also periodic with the same period `T`. This property is the basis for using auto-correlation to find the fundamental frequency of a periodic signal.

5.  **The Wiener-Khinchin Theorem:** This is a very important theorem that relates the auto-correlation function to the **Power Spectral Density (PSD)** of the signal. The PSD, `S_x(f)`, describes how the power of a signal is distributed over different frequencies.

    The Wiener-Khinchin theorem states that the auto-correlation function and the power spectral density are a Fourier transform pair:

    `F[R_x(τ)] = S_x(f)`
    `S_x(f) = ∫ R_x(τ) * exp(-j2πτf) dτ`

    And conversely:

    `R_x(τ) = F^{-1}[S_x(f)]`

    From the cross-correlation property `F[R_xy(τ)] = X(f)Y*(f)`, we can see that for auto-correlation (`x=y`):

    `S_x(f) = F[R_x(τ)] = X(f)X*(f) = |X(f)|^2`

    So, the power spectral density is simply the squared magnitude of the signal's Fourier transform.

    **Why is this important?**

    The Wiener-Khinchin theorem gives us two ways to compute the power spectrum of a signal:
    1.  Directly, by taking the Fourier transform of the signal and squaring its magnitude.
    2.  Indirectly, by first computing the auto-correlation function and then taking its Fourier transform.

    The indirect method can be advantageous in some situations, especially when dealing with noisy signals or when a direct Fourier transform is difficult to compute.

### Derivation of Auto-Correlation Properties

Let's derive some of the key properties of the auto-correlation function.

#### 1. Even Function Property

We want to show that `R_x(τ) = R_x(-τ)` for a real-valued signal `x(t)`.

The definition of the auto-correlation function is:
`R_x(τ) = ∫(-∞ to ∞) x(t) * x(t - τ) dt`

Now let's look at `R_x(-τ)`:
`R_x(-τ) = ∫(-∞ to ∞) x(t) * x(t - (-τ)) dt = ∫(-∞ to ∞) x(t) * x(t + τ) dt`

Let's make a change of variable in the integral. Let `u = t + τ`. Then `t = u - τ` and `dt = du`. The limits of integration do not change.

`R_x(-τ) = ∫(-∞ to ∞) x(u - τ) * x(u) du`

Since the variable of integration is a dummy variable, we can replace `u` with `t`:

`R_x(-τ) = ∫(-∞ to ∞) x(t - τ) * x(t) dt = ∫(-∞ to ∞) x(t) * x(t - τ) dt`

This is exactly the definition of `R_x(τ)`. Therefore:

`R_x(τ) = R_x(-τ)`

The auto-correlation function is an even function.

#### 2. Maximum at Zero Lag Property

We want to show that `|R_x(τ)| <= R_x(0)`. This is a direct consequence of the Cauchy-Schwarz inequality, which we mentioned earlier for cross-correlation.

The Cauchy-Schwarz inequality for integrals states that:
`|∫ f(t)g(t) dt|^2 <= (∫ |f(t)|^2 dt) * (∫ |g(t)|^2 dt)`

Let `f(t) = x(t)` and `g(t) = x(t - τ)`.

Then the left side of the inequality is:
`|∫ x(t)x(t - τ) dt|^2 = |R_x(τ)|^2`

The right side of the inequality is:
`(∫ |x(t)|^2 dt) * (∫ |x(t - τ)|^2 dt)`

The integral `∫ |x(t)|^2 dt` is the energy of the signal, which is `R_x(0)`.
The integral `∫ |x(t - τ)|^2 dt` is the energy of the time-shifted signal. Since a time shift does not change the energy of a signal, this is also equal to `R_x(0)`.

So, the inequality becomes:

`|R_x(τ)|^2 <= R_x(0) * R_x(0) = [R_x(0)]^2`

Taking the square root of both sides, we get:

`|R_x(τ)| <= R_x(0)`

The magnitude of the auto-correlation at any lag `τ` is always less than or equal to the auto-correlation at zero lag.

### Application: Pitch Detection with Auto-Correlation

A classic application of auto-correlation is **pitch detection** in speech and audio signals. The pitch is the fundamental frequency of a periodic or semi-periodic signal, which we perceive as the "highness" or "lowness" of a sound.

**The Scenario**

Voiced sounds in human speech (like vowels) are produced by the periodic vibration of the vocal cords. This creates a periodic waveform, and the frequency of this repetition is the pitch of the voice. We want to determine this fundamental frequency.

**Using Auto-Correlation**

Since voiced speech is periodic, its auto-correlation function will also be periodic, with peaks at time lags corresponding to the period of the signal.

The process for pitch detection using auto-correlation is as follows:

1.  **Frame the Signal:** The speech signal is not stationary; its properties change over time. So, we first divide the signal into short, overlapping frames (typically 20-30 ms long). We assume that the pitch is constant within each frame.

2.  **Compute the Auto-Correlation:** For each frame, we compute the auto-correlation function.

3.  **Find the Peak:** We look for the highest peak in the auto-correlation function, excluding the peak at zero lag (which is always the maximum). The location of this peak, `τ_peak`, corresponds to the fundamental period of the signal.

4.  **Calculate the Pitch:** The pitch (fundamental frequency) `f_0` is the reciprocal of the period:

    `f_0 = 1 / τ_peak`

**Example**

Imagine a person speaking the vowel "a". The waveform will be a repeating pattern.

*(A diagram showing a short segment of a periodic speech waveform. Below it, the auto-correlation of this waveform is shown. The auto-correlation has a large peak at τ=0, and another significant peak at a lag τ corresponding to the period of the waveform.)*

The auto-correlation plot will show a strong peak at a certain lag, which is the period of the vowel sound. By finding this peak, we can calculate the pitch of the speaker's voice.

**Challenges**

While auto-correlation is a powerful tool for pitch detection, it has some challenges:
*   **Noise:** Noise can obscure the peaks in the auto-correlation function.
*   **Formants:** The vocal tract creates resonances called formants, which can sometimes create peaks in the auto-correlation function that are not related to the pitch. This can lead to "pitch-halving" or "pitch-doubling" errors.

Despite these challenges, auto-correlation-based methods are still widely used and form the basis for many more advanced pitch detection algorithms.

### Expanded Applications of Correlation

Correlation is a powerful and versatile tool with applications in many diverse fields.

#### Cross-Correlation Applications

*   **Radar and Sonar:** As discussed, used to detect the time delay of reflected signals to measure distance.
*   **Wireless Communications:** Used in receivers to synchronize with the incoming signal and to estimate the channel characteristics.
*   **Image Processing:** Used for template matching, where you search for a small template image within a larger image. This is used in object recognition and industrial inspection.
*   **Cryptography:** Used to analyze the properties of pseudo-random number generators.
*   **Neuroscience:** Used to analyze the firing patterns of neurons to understand how they are connected and how they communicate.
*   **Geophysics:** Used to analyze seismic data to locate the epicenter of an earthquake or to map underground geological structures.
*   **Finance:** Used to measure the correlation between the prices of different financial assets, which is crucial for portfolio management and risk assessment.

#### Auto-Correlation Applications

*   **Pitch Detection:** As discussed, used to find the fundamental frequency of speech and music signals.
*   **Power Spectral Density Estimation:** The Wiener-Khinchin theorem shows that the auto-correlation can be used to estimate the power spectral density of a signal, which is useful for analyzing the frequency content of signals.
*   **Communications:** Used to detect and remove echoes in a communication channel.
*   **Astronomy:** Used to analyze the light from stars to detect the presence of exoplanets (by looking for periodic dimming of the starlight).
*   **Fluid Dynamics:** Used to analyze turbulent flows to understand their structure and behavior.
*   **Economics:** Used to analyze time series data (like stock prices or GDP) to identify trends and periodicities.