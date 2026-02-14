# Windowing and Stability

## Window Methods

In DSP, windowing is used to reduce spectral leakage when analyzing a finite portion of a signal.

*   **Rectangular Window:** Equivalent to no window. Has good frequency resolution but poor dynamic range.
*   **Hanning Window:** Good for general purpose use, with a good trade-off between resolution and dynamic range.
*   **Hamming Window:** Similar to Hanning but with better side-lobe suppression.
*   **Blackman Window:** Excellent side-lobe suppression, but wider main lobe (poorer resolution).
*   **Kaiser Window:** A flexible window with a parameter that allows trading off between main-lobe width and side-lobe level.

## Stability

A crucial property of a DSP system. A system is **BIBO (Bounded-Input, Bounded-Output) stable** if its output remains bounded for any bounded input.

*   **For LTI systems:** Stability is guaranteed if the impulse response `h[n]` is absolutely summable: `Σ|h[n]| < ∞`.
*   **In the Z-domain:** A system is stable if and only if all the poles of its transfer function lie inside the unit circle.

## Linear Phase

A property of a filter where the phase response is a linear function of frequency. This is important for preserving the shape of the signal.

*   **Group Delay:** A measure of the time delay of the signal as a function of frequency. For a linear phase filter, the group delay is constant.
*   **FIR filters** can be designed to have exact linear phase. **IIR filters** generally cannot.
