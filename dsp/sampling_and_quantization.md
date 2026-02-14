# Sampling and Quantization

## Nyquist Sampling Theorem

This fundamental theorem of digital signal processing states that to accurately reconstruct a continuous-time signal from its samples, the sampling rate (`f_s`) must be at least twice the highest frequency component (`f_max`) in the signal.

*   **Nyquist Rate:** `2 * f_max`
*   **Nyquist-Shannon Sampling Theorem:** `f_s >= 2 * f_max`

Sampling below the Nyquist rate leads to a form of distortion called **aliasing**, where high frequencies in the original signal are incorrectly interpreted as lower frequencies.

## Quantization

The process of converting a continuous range of values into a finite range of discrete values.

*   **Resolution (n):** The number of bits used for quantization.
*   **Number of Levels (L):** `L = 2^n`
*   **Quantization Step Size (Δ):** The difference between adjacent quantization levels.
*   **Quantization Error:** The difference between the original analog value and the quantized digital value. The error is in the range `[-Δ/2, Δ/2]`.
*   **Signal-to-Quantization-Noise Ratio (SQNR):** A measure of the quality of the quantization. For a full-scale sine wave:
    `SQNR (dB) = 6.02n + 1.76`
