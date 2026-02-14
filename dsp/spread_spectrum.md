# Spread Spectrum

## FHSS (Frequency-Hopping Spread Spectrum)

A method of transmitting radio signals by rapidly switching a carrier among many frequency channels, using a pseudorandom sequence known to both transmitter and receiver. This makes the signal resistant to interference and eavesdropping.

*   **Dwell Time:** The time for which the transmitter stays on a particular frequency.

## DSSS (Direct-Sequence Spread Spectrum)

A spread spectrum technique where the original data signal is combined with a higher-rate bit sequence (chipping code) to spread the signal over a wider frequency band.

*   **Spreading:** The data signal `d(t)` is multiplied by a chipping sequence `c(t)` to get the transmitted signal `s(t) = d(t) * c(t)`.
*   **Processing Gain (PG):** The ratio of the chip rate to the data rate. A higher processing gain provides better interference rejection.
    `PG = (Chip Rate) / (Data Rate)`
