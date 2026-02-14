# Digital Filters

Digital filters are algorithms that operate on a digital signal to remove unwanted components or enhance desired ones. They are categorized into two main types:

## FIR (Finite Impulse Response) Filter

An FIR filter's output is a weighted sum of the current and a finite number of past input samples.

*   **Difference Equation:**
    `y[n] = Σ(b_i * x[n-i])` for `i = 0 to N`
    where `b_i` are the filter coefficients and `N` is the filter order.
*   **Properties:**
    *   Always stable.
    *   Can be designed to have a linear phase response.
    *   Generally require a higher order than IIR filters for the same frequency response.

## IIR (Infinite Impulse Response) Filter

An IIR filter's output depends on both current and past input samples, as well as past output samples (feedback).

*   **Difference Equation:**
    `Σ(a_k * y[n-k]) = Σ(b_j * x[n-j])`
    where `a_k` and `b_j` are the filter coefficients.
*   **Properties:**
    *   More computationally efficient than FIR filters.
    *   Can be unstable if not designed carefully (poles must be inside the unit circle).
    *   Generally do not have a linear phase response.
