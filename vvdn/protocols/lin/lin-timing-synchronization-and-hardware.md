# LIN Protocol: Timing Calculations, Synchronization & Hardware Engineering

## 1. Bit Timing & Frame Duration Calculations

LIN operates at standardized serial bitrates capped at a maximum of **20.0 kbps** (with standard industry implementations operating at **19,200 bps**, **9,600 bps**, and **2,400 bps**). The 20 kbps ceiling is an intentional electromagnetic compatibility (EMC) design constraint: by limiting the bitrate and enforcing controlled slew rates, LIN eliminates radiated RF emissions without requiring expensive shielded twisted-pair cabling.

---

### 1.1 Bit Period & Frame Duration Formulas

Given a configured baud rate (BR):

#### Step 1: Nominal Bit Time (T_bit)
```
T_bit = 1 / BR
```

Where:
- T_bit: Nominal bit time duration (s)
- BR: LIN communication baud rate (typically 19200 bps or 9600 bps) (bps)
- At **19,200 bps**: T_bit = 1 / 19200 ≈ 52.08 µs
- At **9,600 bps**: T_bit = 1 / 9600 ≈ 104.17 µs

#### Step 2: Nominal Header Duration (T_header_nom)
The Master Header consists of:
- Synch Break: 13 dominant bits + 1 recessive delimiter bit = **14 bits**
- Synch Byte (`0x55`): 1 Start + 8 Data + 1 Stop = **10 bits**
- Protected ID (PID): 1 Start + 8 Data + 1 Stop = **10 bits**
```
T_header_nom = 34 * T_bit
```

#### Step 3: Nominal Response Duration (T_response_nom)
For an N-byte payload (N in {1 ... 8}) plus 1 Checksum byte:
```
T_response_nom = 10 * (N + 1) * T_bit
```

#### Step 4: Total Nominal Frame Duration (T_frame_nom)
```
T_frame_nom = T_header_nom + T_response_nom = ( 34 + 10 * (N + 1) ) * T_bit
```

#### Step 5: Maximum Allowable Frame Slot Budget (T_frame_max)
Because slaves may have internal processing latency, inter-byte delays, and clock frequency drift, the LIN specification defines an official **1.4* slot multiplier**:
```
T_frame_max = 1.4 * T_frame_nom
```

### 1.2 LIN Frame Timing Reference Table (at 19,200 bps)

| Payload (N) | Header Bits | Response Bits | Total Bits | Nominal Time (T_nom) | Max Slot Budget (T_max) | Max Frames / Sec |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Byte** | 34 | 20 | **54 bits** | 2.81 ms | **3.94 ms** | 253.9 fps |
| **2 Bytes** | 34 | 30 | **64 bits** | 3.33 ms | **4.67 ms** | 214.2 fps |
| **4 Bytes** | 34 | 50 | **84 bits** | 4.38 ms | **6.12 ms** | 163.3 fps |
| **8 Bytes** | 34 | 90 | **124 bits** | 6.46 ms | **9.04 ms** | 110.6 fps |

> [!TIP]
> When designing Master Schedule Tables, set the slot duration to at least T_frame_max (e.g., allocate a **10.0 ms** schedule slot for an 8-byte frame at 19.2 kbps) to prevent header truncation.

---

## 2. Slave Auto-Baud Clock Synchronization Mathematics

A core economic pillar of LIN is allowing high-volume slave microcontrollers to run without external quartz crystals or ceramic resonators. Instead, slaves operate from low-cost internal on-chip RC oscillators that exhibit up to **± 14\% uncalibrated frequency drift** across automotive temperature extremes (-40°C ... +125°C).

### 2.1 The 8-Bit Sync Window Measurement

The Master initiates every frame with a precise crystal-derived **Synch Byte (`0x55`)**.
Because `0x55` equals `01010101b`, it generates 5 distinct falling edges on the UART line:

```text
 Edge 1          Edge 2          Edge 3          Edge 4          Edge 5
   │               │               │               │               │
 ──┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───────
   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘
   |<- 2T ->|<- 2T ->|<- 2T ->|<- 2T ->|
   |<--------------------- Sync Window = Exactly 8 T_bit ---------------------->|
```

1. **Timer Capture**: An internal MCU hardware timer configured for Input Capture records the timestamp of Edge 1 (t_1) and Edge 5 (t_5).
2. **Elapsed Quanta**:
   ```
Δ T = t_5 - t_1 = 8 * T_bit_master
```
3. **Derived Bit Period (T_bit)**:
   ```
T_bit = (Δ T) / 8
```
4. **Hardware UART Baud Rate Register Reload**:
   Given an internal slave timer clock frequency f_timer:
   ```
Baud Divisor (BRR) = (Δ T_timer ticks) / 8
```

```c
/* lin_autobaud_isr.c - Production Slave Auto-Baud Input Capture ISR */
#include <stdint.h>

volatile uint32_t edge_timestamps[5];
volatile uint8_t edge_count = 0;
volatile uint16_t measured_bit_ticks = 0;

void TIM2_IRQHandler(void) {
    if (TIM2->SR & TIM_SR_CC1IF) {
        /* Read captured timer counter */
        uint32_t current_tick = TIM2->CCR1;
        
        if (edge_count < 5) {
            edge_timestamps[edge_count++] = current_tick;
        }

        if (edge_count == 5) {
            /* Delta between Edge 1 and Edge 5 spans exactly 8 bit periods */
            uint32_t delta_ticks = edge_timestamps[4] - edge_timestamps[0];
            measured_bit_ticks = (uint16_t)(delta_ticks / 8);

            /* Reload hardware UART Baud Rate Register (USART_BRR) */
            USART1->BRR = measured_bit_ticks;

            /* Switch pin from Timer Input Capture mode to UART RX mode */
            reconfigure_pin_to_uart();
            edge_count = 0;
        }
    }
}
```

### 2.2 Oscillator Clock Tolerance Requirements (ISO 17987)

To ensure reliable data sampling without framing errors across all 8 data bytes:

| Node Type | Oscillator Requirement | Max Permissible Clock Drift |
| :--- | :--- | :--- |
| **Master Node** | Quartz Crystal or High-Precision Oscillator | **<= ± 0.5\%** |
| **Slave Node (Resonator)**| Ceramic Resonator (No auto-baud calibration required) | **<= ± 1.5\%** |
| **Slave Node (On-Chip RC)**| Internal RC Oscillator (Prior to Synch Byte capture) | **<= ± 14.0\%** |
| **Slave Node (On-Chip RC)**| Internal RC Oscillator (Calibrated post-Synch capture) | **<= ± 1.5\%** across the entire frame |

---

## 3. Electrical Characteristics & Duty Cycle Timing Budgets

To guarantee reliable threshold detection across varying battery voltages, ISO 17987-4 specifies transmitter and receiver duty cycles across standardized voltage thresholds:

```text
 12V (VBAT)
  0.744 VBAT ─────── / ─────────────┬───────────── \ ─────── TH_rec(max) = 0.744 VBAT
                     /              │              \
  0.581 VBAT ───────/─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─\─ ─ ─  TH_dom(max) = 0.581 VBAT
                   /                │                \
  0.422 VBAT ─────/─ ─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─\───  TH_rec(min) = 0.422 VBAT
                 /                  │                  \
  0.284 VBAT ───/───────────────────┴───────────────────\─── TH_dom(min) = 0.284 VBAT
 GND (0V)
                |<------------- t_bus_dom -------------->|
```

### 3.1 Transmitter Duty Cycle Equations

The physical transmitter must ensure that the generated dominant pulse duration (t_bus_dom) satisfies two formal duty cycle limits:

```
Duty Cycle 1 (D1) = t_bus_rec(min) / (2 * T_bit) >= 0.396
```
```
Duty Cycle 2 (D2) = t_bus_rec(max) / (2 * T_bit) <= 0.581
```

*(where t_bus_rec is the recessive interval measured across the standardized receiver threshold levels at 19.2 kbps).*

---

## 4. Circuit Design, Protection & PCB Layout

```text
                +12V Battery Supply (VBAT)
                   │
                  ─┴─ Reverse Polarity Diode (e.g., BAS21 / 1N4007)
                  ▲─┬
                    │
                   [ ] Master Pull-up: 1.0 kΩ (1%)  [Slave: 30 kΩ]
                    │
      LIN Pin ──────┼──────────────────────────────┬───────────────────> LIN Bus
                    │                              │
                   ─┴─ Bus Capacitor              ─┴─ Bidirectional TVS
                   ─┬─ 1.0 nF (Master) / 220 pF   ─┬─ (e.g., PESD1LIN)
                    │   (Slave)                    │
                   GND                            GND
```

### 4.1 Bus Capacitance & Passive Rise Time Budget
- The total lumped bus capacitance (C_bus) comprises the capacitance of all connected nodes plus the physical wiring harness (C_wire ≈ 100 pF/meter):
  ```
C_bus = C_master + Sum(i=1 to N) C_slave_i + (L_cable * C_wire) <= 10.0 nF
```
- **Passive RC Rise Time (t_r)**:
  The transition from Dominant (0V) back to Recessive (12V) is driven purely by the passive pull-up resistors:
  ```
τ = R_bus_eq * C_bus
```
  ```
t_r ≈ 2.2 * τ = 2.2 * R_bus_eq * C_bus
```
  For R_bus_eq = 789.5 Ω and C_bus = 4.7 nF:
  ```
t_r = 2.2 * 789.5 Ω * 4.7 * 10^-9 F ≈ 8.16 µs
```
  Since T_bit = 52.08 µs at 19.2 kbps, an 8.16 µs rise time represents 15.6\% of the bit period, comfortably within the 20\% maximum limit.

### 4.2 Automotive Transient & Surge Protection (ISO 7637-2)
Vehicle 12V electrical rails routinely experience high-energy voltage transients:
- **Pulse 1 (Inductive load disconnect)**: -100 V to -150 V negative spike.
- **Pulse 2a (Harness inductance)**: +37 V to +55 V positive spike.
- **Pulse 3a/3b (Switch arcing & relay chatter)**: ± 150 V high-frequency bursts.
- **Pulse 5b (Alternator Load Dump)**: +35 V ... +40 V clamped surge lasting up to 400 ms.

#### Hardware Mitigation:
1. Protect the LIN bus pin with an automotive-grade TVS diode (e.g., Nexperia `PESD1LIN` or Bourns `CDSOT23-T24CAN`) rated for V_WM >= 24 V and breakdown voltage V_BR >= 27 V.
2. Insert a series blocking diode (e.g., `BAS21`) in series with the pull-up resistor to block reverse battery and negative inductive transients from reaching the microcontroller.

---

## 5. Root Cause Analysis (RCA) Troubleshooting Matrix

When troubleshooting LIN networks in the laboratory or on production vehicles, use this structured diagnosis table:

| Observed Symptom | Oscilloscope / Logic Analyzer Signature | Probable Root Cause | Verification & Corrective Action |
| :--- | :--- | :--- | :--- |
| **Slaves ignore all Master headers; no response on the bus.** | Oscilloscope shows Break field pulse duration is only 9 ... 10 bit times instead of >= 13 bits. | **UART peripheral framing error**: Master firmware is transmitting standard `0x00` instead of a genuine Hardware LIN Break. | Configure UART peripheral in true LIN Mode (e.g., STM32 `HAL_LIN_SendBreak()`) to generate an uncorrupted 13-bit dominant break. |
| **Communication works for early data bytes, but 7th and 8th bytes corrupt with framing errors.** | Bit edges drift progressively away from sample instants across the frame. | **Slave RC oscillator frequency drift** exceeding ± 1.5\% across the frame duration. | Verify slave auto-baud timer capture logic. Ensure timer clock resolution is >= 1 MHz. If operating over extreme temperature ranges, consider tuning the RC oscillator trims or selecting a ceramic resonator. |
| **Master flags Checksum Error on diagnostic frames (`0x3C`/`0x3D`).** | Header and payload bytes appear valid on logic analyzer, but Master rejects response. | **Checksum Mode Mismatch**: Slave calculated Enhanced Checksum instead of **Classic Checksum**. | By ISO 17987 standard, diagnostic frames (`0x3C` and `0x3D`) **must always use Classic Checksum** (data bytes only, excluding PID). |
| **Bus line is permanently pinned Dominant (0.8V); no communication possible.** | LIN bus remains at 0.8 V constantly; no node can pull the bus high. | **Transceiver TXD pin shorted to Ground** or slave firmware crash holding TXD LOW on a transceiver lacking dominant timeout. | Disconnect slave nodes one by one until bus releases to 12 V. Replace old transceivers with modern ICs featuring internal TXD Dominant Clamping (e.g., `TJA1021`). |
| **Rising edges are heavily rounded; bits fail to reach 0.8 VBAT at 19.2 kbps.** | Exponential RC rise curve with t_r > 15 µs; high bits truncated. | **Excessive bus capacitance** (C_bus > 10 nF) or missing Master 1 kΩ pull-up resistor. | Check master termination resistor (1 kΩ to V_BAT). If cable harness is excessively long, reduce node filter capacitors from 1 nF to 220 pF. |
| **Slaves fail to wake up from Sleep Mode when button pressed.** | Dominant wake-up pulse on bus is only 50 µs wide. | **Wake-up pulse too short**: Transceiver filters require at least 150 µs ... 250 µs dominant pulse. | Increase GPIO pull-down duration in firmware to 500 µs ... 1.0 ms to ensure all sleeping transceivers reliably detect the wake-up event. |
