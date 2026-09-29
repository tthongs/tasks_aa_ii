# Real-Time Efficiency Monitoring, Data Logging & SCPI Telemetry Subsystem

Welcome to the **VVDN Engineering Hub Technical Dossier on the Efficiency Monitoring, MicroSD Data Logging, and Digital Telemetry Subsystem** for the Smart Programmable Power Supply. This document delivers an exhaustive architectural and implementation analysis covering dual-domain AC/DC power metering, real-time efficiency computation ($\eta = P_{DC} / P_{AC}$), non-blocking FAT32 circular data logging, and industry-standard SCPI communication protocols.

---

## 1. Subsystem Executive Overview & Specifications

A core innovation of the Smart Programmable Power Supply is its ability to continuously measure **true grid AC input power** and **DC load output power** simultaneously across a reinforced isolation boundary, computing real-time conversion efficiency at $10\,\text{Hz}$ rates and streaming data to a MicroSD logger, local OLED display, and USB-C SCPI interface:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                    Dual-Domain Metering & Telemetry Specifications                │
├────────────────────────────┬─────────────────────────────┬────────────────────────┤
│ Parameter / Specification  │ Value / Unit                │ Implementation Detail  │
├────────────────────────────┼─────────────────────────────┼────────────────────────┤
│ **AC Voltage Sensing**     │ $85\,\text{V} \dots 265\,\text{V}$ AC RMS│ Isolated $\Delta\Sigma$ AMC1311│
│ **AC Current Sensing**     │ $0.05\,\text{A} \dots 2.0\,\text{A}$ RMS │ High-accuracy CT / Shunt│
│ **AC Power Measurement**   │ Real Active Power ($P_{AC}$ in W)│ Instantaneous $v(t) \cdot i(t)$│
│ **AC Power Factor ($\cos\phi$)│ $0.00 \dots 1.00$ True PF    │ Displacement & harmonic│
│ **DC Voltage Sensing**     │ $0.0\,\text{V} \dots 24.0\,\text{V}$ DC │ INA226 16-bit ADC      │
│ **DC Current Sensing**     │ $0.00\,\text{A} \dots 3.50\,\text{A}$ DC│ $10\,\text{m}\Omega$ Kelvin Shunt│
│ **DC Power Measurement**   │ $P_{DC} = V_{OUT} \times I_{OUT}$│ Hardware INA226 Mult.  │
│ **Real-Time Efficiency (η)**│ $0.0\% \dots 100.0\%$ ($\pm 0.5\%$)│ Computed at $10\,\text{Hz}$ rate│
│ **Data Logging Storage**   │ MicroSD Card (FAT32)        │ Timestamped CSV schema │
│ **Logging Sample Interval**│ $100\,\text{ms} \dots 10\,\text{s}$ Configurable│ Non-blocking FreeRTOS  │
│ **Local Display**          │ 1.3" $128\times 64$ Monochrome OLED│ I2C SSD1306/SH1106     │
│ **Remote Interface**       │ USB-C Virtual COM Port      │ Full SCPI Command Set  │
└────────────────────────────┴─────────────────────────────┴────────────────────────┘
```

---

## 2. Dual-Domain Power Metering Architecture

```text
  ================================ PRIMARY HIGH-VOLTAGE AC DOMAIN ================================
  85-265V AC Line
       │
       ├───[ 4x 1MΩ Resistor Divider ]───┐
       │                                 │
       │   Current Transformer (CT)      ├─── VINP (AMC1311 Isolated Amp)
       └───[ 1000:1 / Talema AC1005 ]───┐│
                                        │├─── VINN
                                        ││
                                      ┌─┴┴──────────────────────────────┐
                                      │ TI AMC1311 Isolated Modulator   │
                                      │ Reinforced Isolation (5kV RMS)  │
                                      └─┬───────────────────────────────┘
                                        │ Digital Differential Bitstream
  ================================ SAFETY ISOLATION BARRIER (>= 6.4mm) ===========================
                                        │
                                      ┌─┴───────────────────────────────┐
                                      │ Sinc3 Decimation Filter         │
                                      │ (Hardware peripheral inside     │
                                      │  STM32G474 Microcontroller)     │
                                      └─┬───────────────────────────────┘
                                        │ True V_AC_RMS, I_AC_RMS, P_AC (Watts)
                                        │
  ================================ SECONDARY LOW-VOLTAGE DC DOMAIN ===============================
  +V_OUT (5V - 20V) ───────────────────┬────────────────────────────────────────────────────────┐
                                       │                                                        │
                                     ┌─┴─┐ R_shunt                                            ┌─┴─┐ Load
                                     │   │ 10mΩ / 0.1% Kelvin                                 │   │ Terminal
                                     └─┬─┘                                                    └─┬─┘
                                       ├─── IN+ (INA226)                                        │
                                       │                                                     GND_SEC
                                       └─── IN- (INA226) ──── VBUS Sense
                                              │
                                            ┌─┴───────────────────────────────┐
                                            │ TI INA226 16-Bit Power Monitor  │
                                            │ 10µV Offset / 0.1% Gain Error   │
                                            └─┬───────────────────────────────┘
                                              │ I2C Bus (400 kHz)
                                              ▼
                                   ┌──────────────────────────────────┐
                                   │ STM32G474 / ESP32-S3 Central MCU │
                                   │ - Real-Time Efficiency Engine    │
                                   │ - CV/CC State Machine & DAC      │
                                   │ - MicroSD FAT32 Data Logger      │
                                   └──────────────────────────────────┘
```

---

## 3. AC Input Power Measurement & Calculations

Real active AC power ($P_{AC}$) cannot be calculated by simply multiplying RMS voltage by RMS current ($V_{RMS} \times I_{RMS}$), because non-linear rectifiers draw pulsed, distorted currents with a power factor ($\text{PF}$) significantly below unity ($\text{PF} \approx 0.55 \dots 0.65$ without active PFC).

### 3.1 Mathematical Active Power Formulation:
True active power is the average of instantaneous voltage and current products sampled at high frequency ($f_s \ge 10\,\text{kHz}$):

$$V_{RMS} = \sqrt{\frac{1}{N} \sum_{k=0}^{N-1} v_{AC}^2[k]}$$
$$I_{RMS} = \sqrt{\frac{1}{N} \sum_{k=0}^{N-1} i_{AC}^2[k]}$$
$$P_{AC(real)} = \frac{1}{N} \sum_{k=0}^{N-1} v_{AC}[k] \cdot i_{AC}[k]$$
$$\text{Apparent Power } S = V_{RMS} \times I_{RMS} \quad [\text{VA}]$$
$$\text{Power Factor } \text{PF} = \frac{P_{AC(real)}}{S} = \frac{P_{AC}}{V_{RMS} \times I_{RMS}}$$

### 3.2 Primary Sensing Hardware Design:
1. **Isolated Voltage Sensing**: An ultra-high-impedance resistor chain ($4\times 1.0\,\text{M}\Omega$ $1206$ resistors in series with a $2.0\,\text{k}\Omega$ precision $0.1\%$ shunt) scales $375\,\text{V}$ peak down to $187.5\,\text{mV}$, matching the linear $\pm 2.0\,\text{V}$ input range of the **TI AMC1311** reinforced isolation amplifier.
2. **Current Sensing**: A $1000:1$ toroidal current transformer (**Talema AC1005**) placed in series with the AC Line conductor steps down the $2\,\text{A}$ mains current to $2\,\text{mA}$. A $100\,\Omega$ burden resistor generates a clean $200\,\text{mV}_{\text{RMS}}$ secondary signal, routed into the secondary ADC with zero DC offset.

---

## 4. DC Output Power Measurement via INA226

The secondary load voltage and current are monitored using the **TI INA226**, an industry-standard 16-bit I2C power monitoring IC:

```text
                  INA226 Kelvin Current Shunt Interface
  From Inductor L ───┬────────────────────────────────────────────────────────┬───> +V_OUT Terminal
                     │                                                        │
                   ┌─┴─┐ R_shunt (10mΩ, 0.1%, 3W, 15ppm/°C)                   │
                   │   │ Bourns CSS2H-2512R-L010F                             │
                   └─┬─┘                                                      │
                     │ Kelvin Force 1                        Kelvin Force 2   │
                     ├─── Sense+                                   Sense- ────┤
                     │                                                        │
                   ┌─┴────────────────────────────────────────────────────────┴─┐
                   │ INA226 (16-Bit I2C Power Monitor)                          │
                   │                                                            │
                   │ IN+          IN-          VBUS          SDA         SCL    │
                   └─┬─────────────┬─────────────┬────────────┬───────────┬─────┘
                     │             │             │            │           │
                     └─────────────┴─────────────┘            └─────┬─────┘
                                                                I2C to MCU
```

### 4.1 Calibration & Resolution Register Configuration:
- **Shunt Resistor**: $R_{shunt} = 10.0\,\text{m}\Omega = 0.010\,\Omega$.
- **Maximum Expected Current**: $I_{max} = 3.50\,\text{A}$.
- **Current LSB Calculation**:
  $$\text{Current\_LSB} = \frac{I_{max}}{2^{15}} = \frac{3.50}{32768} = 106.8\,\mu\text{A/bit} \longrightarrow \text{Selected: } \mathbf{100\,\mu\text{A/LSB} = 0.1\,\text{mA/LSB}}$$
- **Calibration Register Value ($CAL$)**:
  $$CAL = \text{trunc}\left(\frac{0.00512}{\text{Current\_LSB} \times R_{shunt}}\right) = \text{trunc}\left(\frac{0.00512}{0.000100 \times 0.010}\right) = \mathbf{5120} \quad (\text{0x1400})$$
- **Power LSB**:
  $$\text{Power\_LSB} = 25 \times \text{Current\_LSB} = 25 \times 0.000100\,\text{A} = \mathbf{2.5\,\text{mW/LSB}}$$

---

## 5. Real-Time Efficiency Engine ($\eta$) & Digital Filtering

At a steady $10\,\text{Hz}$ rate ($100\,\text{ms}$ timer interrupt), the microcontroller fetches the latest $P_{AC}$ and $P_{DC}$ values to calculate efficiency:

$$\eta[n] = \frac{P_{DC}[n]}{P_{AC}[n]} \times 100\%$$

```text
                         Efficiency Engine Signal Processing Chain
  Raw P_AC (from AC Metering) ───┐
                                 ▼
                          [ Sanity Check ] ──> If P_AC < 0.5W: Clamp η = 0.0% (Standby State)
                                 │
  Raw P_DC (from INA226) ────────┤
                                 ▼
                         [ Division Unit ] ──> η_raw = (P_DC / P_AC) * 100%
                                 │
                                 ▼
                      [ Low-Pass EMA Filter ] ──> η_filt[n] = 0.2 * η_raw + 0.8 * η_filt[n-1]
                                 │
                                 ├───> 1.3" OLED Display (Efficiency Gauge)
                                 ├───> MicroSD Data Logger Task (CSV Record)
                                 └───> SCPI Telemetry Parser (:MEAS:EFF?)
```

### Edge-Case Handling:
1. **Zero-Load / Standby Mode**: When the output is enabled but no load is connected ($I_{OUT} = 0\,\text{A}$), the primary stage draws standby quiescent power ($P_{AC} \approx 180\,\text{mW}$). Because $P_{DC} = 0\,\text{W}$, the efficiency is mathematically $0.0\%$. The algorithm clamps efficiency to $0.0\%$ to avoid spurious division or noisy fluctuating readings.
2. **Exponential Moving Average (EMA)**: Mitigates visual jitter on the OLED display caused by line-cycle ripple:
   $$\eta_{filt}[n] = \alpha \cdot \eta_{raw}[n] + (1 - \alpha) \cdot \eta_{filt}[n-1] \quad (\alpha = 0.20)$$

---

## 6. MicroSD Data Logging Engine & FAT32 File Format

Data logging is implemented as an independent, low-priority FreeRTOS worker task. A **lock-free circular ring buffer** decouples the high-speed metering engine from flash memory write latencies:

```text
                  Non-Blocking MicroSD Data Logging Architecture
  10Hz Metering ISR / Task
             │
             ├─── Creates Telemetry Record struct
             │    { timestamp, Vac, Iac, Pac, PF, Vdc, Idc, Pdc, eff, T_pri, T_sec }
             ▼
     ┌────────────────────────────────────────────────────────┐
     │ Lock-Free Circular Ring Buffer (RAM: 64 Records)        │
     │ [Rec 0] [Rec 1] [Rec 2] ... [Rec 63]                   │
     └──────────────────────────┬─────────────────────────────┘
                                │ FreeRTOS Queue Notification
                                ▼
     ┌────────────────────────────────────────────────────────┐
     │ MicroSD Logging Task (Low Priority FreeRTOS Task)       │
     │ - Batches 10 records into a 512-byte sector buffer     │
     │ - Writes via FatFs `f_write()` in single sector bursts │
     │ - Flushes to physical Flash via `f_sync()` every 5 sec │
     └──────────────────────────┬─────────────────────────────┘
                                │ SPI / SDIO Bus (25 MHz)
                                ▼
     ┌────────────────────────────────────────────────────────┐
     │ MicroSD Flash Memory Card (FAT32 File System)           │
     │ File: `/LOGS/SPPS_20260929_001.CSV`                     │
     └────────────────────────────────────────────────────────┘
```

### 6.1 CSV File Schema Specification:
Every session creates a new file numbered sequentially (`SPPS_YYYYMMDD_NNN.CSV`):

```csv
timestamp_ms,vac_rms,iac_rms,pac_w,pf,vdc_out,idc_out,pdc_w,eff_pct,temp_pri_c,temp_sec_c,mode
1000,230.4,0.125,18.42,0.64,12.012,1.250,15.015,81.51,42.3,38.7,CV
1100,230.3,0.126,18.45,0.64,12.011,1.251,15.026,81.44,42.4,38.7,CV
1200,230.5,0.125,18.40,0.64,12.012,1.250,15.015,81.60,42.5,38.8,CV
```

---

## 7. SCPI Command Parser & Telemetry Protocol

The module supports the IEEE 488.2 **Standard Commands for Programmable Instruments (SCPI)** protocol via USB-CDC (Virtual COM Port, $115200\,\text{baud}$, 8N1):

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          Supported SCPI Command Dictionary                        │
├───────────────────────┬───────────────────────────┬───────────────────────────────┤
│ SCPI Command          │ Parameter / Type          │ Description / Response        │
├───────────────────────┼───────────────────────────┼───────────────────────────────┤
│ `*IDN?`               │ None                      │ `VVDN,SPPS-60W,SN2026-09,V1.0`│
│ `*RST`                │ None                      │ Resets supply to 5.0V / 0.5A  │
│ `:VOLT <value>`       │ Float ($5.0 \dots 20.0$)  │ Sets output voltage setpoint  │
│ `:VOLT?`              │ None                      │ Queries voltage setpoint      │
│ `:CURR <value>`       │ Float ($0.1 \dots 3.0$)   │ Sets current limit threshold  │
│ `:CURR?`              │ None                      │ Queries current limit         │
│ `:OUTP <ON|OFF>`      │ Boolean (`1` or `0`)      │ Enables/disables power stage  │
│ `:OUTP?`              │ None                      │ Queries output state (1 or 0) │
│ `:MEAS:VOLT?`         │ None                      │ Measures DC output voltage    │
│ `:MEAS:CURR?`         │ None                      │ Measures DC output current    │
│ `:MEAS:POW?`          │ None                      │ Measures DC output power (W)  │
│ `:MEAS:AC:VOLT?`      │ None                      │ Measures RMS AC mains voltage │
│ `:MEAS:AC:POW?`       │ None                      │ Measures real active AC power │
│ `:MEAS:EFF?`          │ None                      │ Queries real-time efficiency  │
│ `:LOG:START`          │ None                      │ Starts MicroSD CSV data log   │
│ `:LOG:STOP`           │ None                      │ Stops logging and closes file │
│ `:SYST:ERR?`          │ None                      │ `0,"No error"` or error code  │
└───────────────────────┴───────────────────────────┴───────────────────────────────┘
```

---

## 8. Embedded C Firmware Architecture: Core Telemetry Loop

Below is the production-grade C implementation of the 10Hz dual-domain power metering and efficiency logging task:

```c
/**
 * @file spps_telemetry.c
 * @brief Real-Time Dual-Domain Power & Efficiency Metering Task
 * @company VVDN Technologies
 */

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include "spps_telemetry.h"
#include "ina226.h"
#include "ac_metering.h"
#include "fatfs.h"

#define EMA_ALPHA           0.20f   /* Filter smoothing coefficient */
#define MIN_STANDBY_POWER   0.50f   /* Power threshold below which eff = 0 */

typedef struct {
    uint32_t timestamp_ms;
    float vac_rms;
    float iac_rms;
    float pac_watts;
    float power_factor;
    float vdc_out;
    float idc_out;
    float pdc_watts;
    float eff_percent;
    float temp_primary;
    float temp_secondary;
    char mode[4];
} TelemetryData_t;

static TelemetryData_t current_data;
static float filtered_efficiency = 0.0f;
static FIL log_file;
static bool logging_active = false;

void SPPS_Telemetry_Task(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(100); /* 100ms = 10Hz */

    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xFrequency);

        /* 1. Acquire Primary AC Measurements */
        AC_Metering_Read(&current_data.vac_rms, 
                         &current_data.iac_rms, 
                         &current_data.pac_watts, 
                         &current_data.power_factor);

        /* 2. Acquire Secondary DC Measurements via INA226 */
        INA226_Read_VBUS(&current_data.vdc_out);
        INA226_Read_Current(&current_data.idc_out);
        current_data.pdc_watts = current_data.vdc_out * current_data.idc_out;

        /* 3. Compute Real-Time Conversion Efficiency */
        if (current_data.pac_watts > MIN_STANDBY_POWER && current_data.pdc_watts > 0.05f) {
            float raw_eff = (current_data.pdc_watts / current_data.pac_watts) * 100.0f;
            if (raw_eff > 100.0f) raw_eff = 100.0f; /* Physical sanity clamp */
            
            /* Apply Exponential Moving Average */
            filtered_efficiency = (EMA_ALPHA * raw_eff) + ((1.0f - EMA_ALPHA) * filtered_efficiency);
        } else {
            filtered_efficiency = 0.0f; /* Zero-load or standby state */
        }
        current_data.eff_percent = filtered_efficiency;

        /* 4. Write CSV Record to MicroSD if Logging is Active */
        if (logging_active) {
            char csv_buffer[128];
            int len = snprintf(csv_buffer, sizeof(csv_buffer),
                "%lu,%.1f,%.3f,%.2f,%.2f,%.3f,%.3f,%.3f,%.2f,%.1f,%.1f,%s\n",
                xTaskGetTickCount() * portTICK_PERIOD_MS,
                current_data.vac_rms, current_data.iac_rms, current_data.pac_watts, current_data.power_factor,
                current_data.vdc_out, current_data.idc_out, current_data.pdc_watts, current_data.eff_percent,
                current_data.temp_primary, current_data.temp_secondary, current_data.mode);

            UINT bytes_written;
            f_write(&log_file, csv_buffer, len, &bytes_written);
        }
    }
}
```
