# Signals and Systems

## LTI Systems (Linear Time-Invariant Systems)

An LTI system is a system where the output is linearly proportional to the input, and the system's behavior does not change over time.

*   **Impulse Response:** The output of an LTI system when the input is a unit impulse. It is denoted by `h(t)` for continuous-time systems and `h[n]` for discrete-time systems.
*   **Convolution:** The output `y(t)` or `y[n]` of an LTI system is the convolution of the input signal `x` with the impulse response `h`.
    *   Continuous-time: `y(t) = x(t) * h(t) = integral(x(τ)h(t-τ)dτ)`
    *   Discrete-time: `y[n] = x[n] * h[n] = Σ(x[k]h[n-k])`

## Fourier Series and Transform

*   **Fourier Series:** Represents a periodic signal as a sum of sinusoids. For a signal `x(t)` with period `T`:
    `x(t) = Σ(c_k * e^(j * 2 * pi * k * t / T))`
    where `c_k` are the Fourier series coefficients.
*   **Fourier Transform:** Represents a non-periodic signal in the frequency domain.
    `X(f) = integral(x(t) * e^(-j * 2 * pi * f * t) dt)`

## Z-Transform

The Z-transform is used for discrete-time signals.

*   **Definition:**
    `X(z) = Σ(x[n] * z^(-n))`
*   **Region of Convergence (ROC):** The set of values of `z` for which the Z-transform converges. The ROC is crucial for determining the stability and causality of a system.

## DFT (Discrete Fourier Transform) and FFT (Fast Fourier Transform)

*   **DFT:** Computes the frequency spectrum of a finite, discrete-time signal. For a signal `x[n]` of length `N`:
    `X[k] = Σ(x[n] * e^(-j * 2 * pi * k * n / N))` for `k = 0, 1, ..., N-1`
*   **FFT:** An efficient algorithm for computing the DFT. It reduces the computational complexity from O(N^2) to O(N log N).
