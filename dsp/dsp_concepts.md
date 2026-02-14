# DSP Concepts

## Digital Communication

The transmission of information digitally. This involves several steps:
1.  **Source Coding:** Compressing the data to reduce redundancy.
2.  **Channel Coding:** Adding redundancy to detect and correct errors.
3.  **Modulation:** Converting the digital data into a signal suitable for the channel.
4.  **Transmission:** Sending the signal over the channel.
5.  **Reception:** Receiving the signal.
6.  **Demodulation:** Converting the received signal back to digital data.
7.  **Channel Decoding:** Correcting errors.
8.  **Source Decoding:** Decompressing the data.

## Convolution

A mathematical operation that describes the effect of a linear time-invariant (LTI) system on a signal.

*   **Convolution Integral (Continuous-time):**
    `y(t) = integral(x(τ) * h(t - τ) dτ)`
*   **Convolution Sum (Discrete-time):**
    `y[n] = Σ(x[k] * h[n - k])`

Convolution is used for filtering, system analysis, and many other DSP applications.
