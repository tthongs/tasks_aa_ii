# Digital Modulation

These are digital modulation techniques used to transmit digital data over an analog channel.

## ASK (Amplitude-Shift Keying)

The amplitude of the carrier wave is varied to represent digital data.
*   **Equation for binary ASK:**
    `s(t) = A_c * cos(2 * pi * f_c * t)` for binary 1
    `s(t) = 0` for binary 0

## FSK (Frequency-Shift Keying)

The frequency of the carrier wave is shifted to represent digital data.
*   **Equation for binary FSK:**
    `s(t) = A_c * cos(2 * pi * f_1 * t)` for binary 1
    `s(t) = A_c * cos(2 * pi * f_2 * t)` for binary 0

## PSK (Phase-Shift Keying)

The phase of the carrier wave is changed to represent digital data.
*   **Equation for BPSK (Binary PSK):**
    `s(t) = A_c * cos(2 * pi * f_c * t)` for binary 1
    `s(t) = A_c * cos(2 * pi * f_c * t + pi)` for binary 0

## QPSK (Quadrature Phase-Shift Keying)

A type of PSK that uses four different phase shifts to transmit two bits of data per symbol. The phases are typically 0, 90, 180, and 270 degrees.

## DM (Delta Modulation)

A technique for converting an analog signal into a digital signal by transmitting the difference between consecutive samples. It's a simpler form of Pulse Code Modulation (PCM).
