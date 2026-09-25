# NFC Embedded Firmware Architecture, Linux Driver Integration & Debugging Guide

## 1. Embedded Firmware Driver Architecture

To achieve clean portability across microcontroller platforms (STM32, ESP32, NXP LPC/i.MX RT, Nordic nRF), the NFC software stack is structured into four decoupled layers:

```text
+-----------------------------------------------------------------------------------+
|                           APPLICATION LAYER                                       |
|        (NDEF URI Launcher, Access Control Gate, Transit HCE Payment)             |
+-----------------------------------------------------------------------------------+
                                          |
+-----------------------------------------------------------------------------------+
|                           PROTOCOL ENGINE LAYER                                   |
|   (ISO/IEC 14443-3 Poller & Anti-collision, ISO 14443-4 T=CL, ISO 7816-4 APDU)    |
+-----------------------------------------------------------------------------------+
                                          |
+-----------------------------------------------------------------------------------+
|                         DEVICE DRIVER / AFE LAYER                                 |
|  (Register Maps, FIFO Push/Pull, BitFraming Control, CRC16_A Engine, RF Power)     |
+-----------------------------------------------------------------------------------+
                                          |
+-----------------------------------------------------------------------------------+
|                     HARDWARE ABSTRACTION LAYER (HAL)                              |
|       (SPI_Transfer, GPIO_CS_Assert, GPIO_CS_Deassert, IRQ_ISR, Timer_Delay_ms)    |
+-----------------------------------------------------------------------------------+
```

---

## 2. Production-Grade Embedded C Driver Implementation

Below is a complete, modular, production-ready implementation in C demonstrating SPI HAL abstraction, register access, FIFO burst transfers, RF field control, 7-bit REQA framing, and the complete ISO 14443-3 anti-collision loop.

### 2.1 Hardware Abstraction Layer Header (`nfc_hal.h`)

```c
#ifndef NFC_HAL_H
#define NFC_HAL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @brief Initialize SPI peripheral, CS pin, Reset pin, and IRQ line.
 */
void nfc_hal_init(void);

/**
 * @brief Assert Chip Select (drive CS# LOW).
 */
void nfc_hal_cs_low(void);

/**
 * @brief Deassert Chip Select (drive CS# HIGH).
 */
void nfc_hal_cs_high(void);

/**
 * @brief Full-duplex synchronous SPI byte transfer.
 * @param tx_byte Byte to transmit onto MOSI.
 * @return Byte clocked in from MISO.
 */
uint8_t nfc_hal_spi_transfer_byte(uint8_t tx_byte);

/**
 * @brief Synchronous multi-byte SPI transfer (burst mode).
 * @param tx_buf Buffer to send (can be NULL if only reading).
 * @param rx_buf Buffer to receive (can be NULL if only writing).
 * @param length Total number of bytes to transfer.
 */
void nfc_hal_spi_transfer(const uint8_t *tx_buf, uint8_t *rx_buf, size_t length);

/**
 * @brief Blocking millisecond delay.
 */
void nfc_hal_delay_ms(uint32_t ms);

/**
 * @brief Blocking microsecond delay.
 */
void nfc_hal_delay_us(uint32_t us);

/**
 * @brief Drive hardware reset pin.
 * @param state true = assert reset (LOW), false = release reset (HIGH).
 */
void nfc_hal_reset_pin(bool state);

#endif /* NFC_HAL_H */
```

### 2.2 Transceiver Driver Implementation (`nfc_transceiver.c`)

```c
#include "nfc_hal.h"
#include <string.h>

/* Standard MFRC522 / Register-Driven Transceiver Register Addresses */
#define REG_COMMAND           0x01
#define REG_COMIEN            0x02
#define REG_COMIRQ            0x04
#define REG_ERROR             0x06
#define REG_STATUS2           0x08
#define REG_FIFO_DATA         0x09
#define REG_FIFO_LEVEL        0x0A
#define REG_WATER_LEVEL       0x0B
#define REG_CONTROL           0x0C
#define REG_BIT_FRAMING       0x0D
#define REG_COLL              0x0E
#define REG_MODE              0x11
#define REG_TX_CONTROL        0x14
#define REG_TX_ASK            0x15
#define REG_CRC_RESULT_HIGH   0x21
#define REG_CRC_RESULT_LOW    0x22
#define REG_T_MODE            0x2A
#define REG_T_PRESCALER       0x2B
#define REG_T_RELOAD_HIGH     0x2C
#define REG_T_RELOAD_LOW      0x2D

/* Command Codes */
#define CMD_IDLE              0x00
#define CMD_MEM               0x01
#define CMD_GEN_RANDOM_ID     0x02
#define CMD_CALC_CRC          0x03
#define CMD_TRANSMIT          0x04
#define CMD_NO_CMD_CHANGE     0x07
#define CMD_RECEIVE           0x08
#define CMD_TRANSCEIVE        0x0C
#define CMD_MF_AUTHENT        0x0E
#define CMD_SOFT_RESET        0x0F

/* Status Codes */
typedef enum {
    NFC_STATUS_OK = 0,
    NFC_STATUS_TIMEOUT,
    NFC_STATUS_COLLISION,
    NFC_STATUS_CRC_ERROR,
    NFC_STATUS_FIFO_OVERFLOW,
    NFC_STATUS_PROTOCOL_ERROR
} nfc_status_t;

/* Tag UID Structure */
typedef struct {
    uint8_t uid_bytes[10];
    uint8_t uid_length;      /* 4 (Single), 7 (Double), or 10 (Triple) */
    uint8_t sak;             /* Select Acknowledge byte */
} nfc_tag_t;

/* ========================================================================== */
/* Register Read / Write Helpers over SPI                                      */
/* ========================================================================== */

void nfc_write_reg(uint8_t reg_addr, uint8_t value) {
    nfc_hal_cs_low();
    /* Format: Bit 7 = 0 (Write), Bits 6..1 = Address, Bit 0 = 0 */
    nfc_hal_spi_transfer_byte((reg_addr << 1) & 0x7E);
    nfc_hal_spi_transfer_byte(value);
    nfc_hal_cs_high();
}

uint8_t nfc_read_reg(uint8_t reg_addr) {
    uint8_t value;
    nfc_hal_cs_low();
    /* Format: Bit 7 = 1 (Read), Bits 6..1 = Address, Bit 0 = 0 */
    nfc_hal_spi_transfer_byte(((reg_addr << 1) & 0x7E) | 0x80);
    value = nfc_hal_spi_transfer_byte(0x00); /* Clock in data */
    nfc_hal_cs_high();
    return value;
}

void nfc_set_bit_mask(uint8_t reg, uint8_t mask) {
    uint8_t current = nfc_read_reg(reg);
    nfc_write_reg(reg, current | mask);
}

void nfc_clear_bit_mask(uint8_t reg, uint8_t mask) {
    uint8_t current = nfc_read_reg(reg);
    nfc_write_reg(reg, current & (~mask));
}

/* ========================================================================== */
/* RF Field Control & Initialization                                          */
/* ========================================================================== */

void nfc_rf_field_on(void) {
    uint8_t current = nfc_read_reg(REG_TX_CONTROL);
    if ((current & 0x03) != 0x03) {
        /* Set bits 0 and 1 to enable TX1 and TX2 push-pull drivers */
        nfc_write_reg(REG_TX_CONTROL, current | 0x03);
        /* MANDATORY ISO 14443-3 Section 5.1 Guard Delay */
        nfc_hal_delay_ms(5);
    }
}

void nfc_rf_field_off(void) {
    nfc_clear_bit_mask(REG_TX_CONTROL, 0x03);
}

void nfc_init(void) {
    nfc_hal_init();
    
    /* Hard reset cycle */
    nfc_hal_reset_pin(true);
    nfc_hal_delay_ms(2);
    nfc_hal_reset_pin(false);
    nfc_hal_delay_ms(10);
    
    /* Soft reset via SPI command */
    nfc_write_reg(REG_COMMAND, CMD_SOFT_RESET);
    nfc_hal_delay_ms(50);
    
    /* Configure internal timers for ISO 14443A timeout detection */
    nfc_write_reg(REG_T_MODE, 0x8D);
    nfc_write_reg(REG_T_PRESCALER, 0x3E);
    nfc_write_reg(REG_T_RELOAD_HIGH, 0x00);
    nfc_write_reg(REG_T_RELOAD_LOW, 0x1E);
    
    /* Force 100% ASK modulation */
    nfc_write_reg(REG_TX_ASK, 0x40);
    /* Set Mode register to standard 6363h CRC coprocessor */
    nfc_write_reg(REG_MODE, 0x3D);
    
    /* Turn on RF carrier */
    nfc_rf_field_on();
}

/* ========================================================================== */
/* ISO/IEC 14443-A CRC-16 Calculation (Polynomial 0x1021, Preset 0x6363)      */
/* ========================================================================== */

void nfc_calculate_crc_a(const uint8_t *data, size_t length, uint8_t *crc_out) {
    uint32_t wcrc = 0x6363; /* ISO 14443-A standard initial seed */
    for (size_t i = 0; i < length; i++) {
        uint8_t byte = data[i];
        byte ^= (uint8_t)(wcrc & 0x00FF);
        byte ^= (byte << 4);
        wcrc = (wcrc >> 8) ^ ((uint32_t)byte << 8) ^ ((uint32_t)byte << 3) ^ ((uint32_t)byte >> 4);
    }
    crc_out[0] = (uint8_t)(wcrc & 0xFF);         /* Low byte first */
    crc_out[1] = (uint8_t)((wcrc >> 8) & 0xFF);  /* High byte second */
}

/* ========================================================================== */
/* Transceive Engine: Sends FIFO, waits for tag load-modulation response      */
/* ========================================================================== */

nfc_status_t nfc_transceive(const uint8_t *send_data, size_t send_len,
                           uint8_t *recv_data, size_t *recv_len,
                           uint8_t *valid_bits, uint8_t rx_align) {
    uint8_t wait_irq = 0x30; /* RxIRQ and IdleIRQ */
    uint8_t bit_framing = (rx_align << 4) | (valid_bits ? *valid_bits : 0);
    
    nfc_write_reg(REG_COMMAND, CMD_IDLE);
    nfc_write_reg(REG_COMIRQ, 0x7F);        /* Clear all pending interrupts */
    nfc_set_bit_mask(REG_FIFO_LEVEL, 0x80); /* Flush FIFO */
    
    /* Write payload to FIFO */
    for (size_t i = 0; i < send_len; i++) {
        nfc_write_reg(REG_FIFO_DATA, send_data[i]);
    }
    
    nfc_write_reg(REG_BIT_FRAMING, bit_framing);
    nfc_write_reg(REG_COMMAND, CMD_TRANSCEIVE);
    nfc_set_bit_mask(REG_BIT_FRAMING, 0x80); /* Set StartSend bit */
    
    /* Await completion or timeout (max 25 ms) */
    uint32_t timeout_counter = 2000;
    uint8_t irq_val = 0;
    while (timeout_counter--) {
        irq_val = nfc_read_reg(REG_COMIRQ);
        if (irq_val & wait_irq) break;
        if (irq_val & 0x01) return NFC_STATUS_TIMEOUT; /* TimerIRQ */
        nfc_hal_delay_us(10);
    }
    if (timeout_counter == 0) return NFC_STATUS_TIMEOUT;
    
    /* Check for hardware collision or error flags */
    uint8_t err_val = nfc_read_reg(REG_ERROR);
    if (err_val & 0x08) return NFC_STATUS_COLLISION;     /* CollErr */
    if (err_val & 0x04) return NFC_STATUS_CRC_ERROR;     /* Parity / CRC */
    if (err_val & 0x10) return NFC_STATUS_FIFO_OVERFLOW; /* BufferOvfl */
    
    /* Read received response from FIFO */
    uint8_t bytes_in_fifo = nfc_read_reg(REG_FIFO_LEVEL);
    if (recv_len) {
        if (bytes_in_fifo > *recv_len) bytes_in_fifo = (uint8_t)*recv_len;
        *recv_len = bytes_in_fifo;
        for (uint8_t i = 0; i < bytes_in_fifo; i++) {
            recv_data[i] = nfc_read_reg(REG_FIFO_DATA);
        }
    }
    
    if (valid_bits) {
        *valid_bits = nfc_read_reg(REG_CONTROL) & 0x07;
    }
    
    return NFC_STATUS_OK;
}

/* ========================================================================== */
/* REQA / WUPA Polling: Transmits 7-Bit Short Frame                           */
/* ========================================================================== */

nfc_status_t nfc_poll_reqa(uint8_t *atqa_out) {
    uint8_t reqa_cmd = 0x26; /* REQA opcode */
    size_t rx_len = 2;
    uint8_t valid_bits = 7;  /* MANDATORY: exactly 7 bits */
    
    /* Clear parity/CRC bits for short frames */
    nfc_clear_bit_mask(REG_COLL, 0x80);
    
    nfc_status_t status = nfc_transceive(&reqa_cmd, 1, atqa_out, &rx_len, &valid_bits, 0);
    if (status != NFC_STATUS_OK) return status;
    if (rx_len != 2 || valid_bits != 0) return NFC_STATUS_PROTOCOL_ERROR;
    
    return NFC_STATUS_OK;
}

/* ========================================================================== */
/* Complete Cascade Anti-Collision & Selection Loop                           */
/* ========================================================================== */

nfc_status_t nfc_select_tag(nfc_tag_t *tag) {
    uint8_t atqa[2];
    nfc_status_t status = nfc_poll_reqa(atqa);
    if (status != NFC_STATUS_OK) return status;
    
    uint8_t cascade_levels[] = {0x93, 0x95, 0x97};
    uint8_t uid_offset = 0;
    
    for (uint8_t cl = 0; cl < 3; cl++) {
        uint8_t sel_cmd = cascade_levels[cl];
        uint8_t buffer[9];
        buffer[0] = sel_cmd;
        buffer[1] = 0x20; /* NVB = 0x20 (2 bytes known: SEL + NVB) */
        
        size_t rx_len = sizeof(buffer) - 2;
        status = nfc_transceive(buffer, 2, &buffer[2], &rx_len, NULL, 0);
        if (status != NFC_STATUS_OK) return status;
        
        /* Verify BCC (Block Check Character = XOR of 4 bytes) */
        uint8_t bcc = buffer[2] ^ buffer[3] ^ buffer[4] ^ buffer[5];
        if (bcc != buffer[6]) return NFC_STATUS_CRC_ERROR;
        
        /* Select card (NVB = 0x70) */
        buffer[1] = 0x70;
        nfc_calculate_crc_a(buffer, 7, &buffer[7]); /* Append 2-byte CRC_A */
        
        uint8_t sak_resp[3];
        rx_len = sizeof(sak_resp);
        status = nfc_transceive(buffer, 9, sak_resp, &rx_len, NULL, 0);
        if (status != NFC_STATUS_OK) return status;
        
        tag->sak = sak_resp[0];
        
        /* Check if UID contains Cascade Tag (0x88) */
        if (buffer[2] == 0x88) {
            /* Double or Triple UID: copy 3 real UID bytes, advance to next cascade */
            memcpy(&tag->uid_bytes[uid_offset], &buffer[3], 3);
            uid_offset += 3;
        } else {
            /* Final cascade level: copy 4 UID bytes */
            memcpy(&tag->uid_bytes[uid_offset], &buffer[2], 4);
            uid_offset += 4;
            tag->uid_length = uid_offset;
            break;
        }
    }
    
    return NFC_STATUS_OK;
}
```

---

## 3. Linux Kernel Subsystem & Driver Integration

In embedded Linux environments (e.g. NXP i.MX8, TI AM62x, Raspberry Pi CM4), NFC transceivers can be integrated via the **native Linux NFC Subsystem (`net/nfc`)** or through **`spidev`** with user-space libraries.

```text
+-----------------------------------------------------------------------------------+
|                        User-Space Applications                                    |
|             (neard daemon, nfctool, libnfc, Android Open Source Project)         |
+-----------------------------------------------------------------------------------+
                                          |
                               [AF_NFC / Netlink Sockets]
                                          |
+-----------------------------------------------------------------------------------+
|                     Linux Kernel NFC Core (net/nfc)                               |
|              (Digital Layer, LLCP Engine, NCI Core, Raw Sockets)                  |
+-----------------------------------------------------------------------------------+
                                          |
+-----------------------------------------------------------------------------------+
|                     Kernel Transceiver Drivers (drivers/nfc/)                     |
|           (pn533_spi.c, st25r3916_spi.c, trf7970a.c, nxp-pn544.c)                |
+-----------------------------------------------------------------------------------+
                                          |
                             [Linux SPI Bus Framework]
                                          |
+-----------------------------------------------------------------------------------+
|                       SoC Hardware SPI Controller                                 |
+-----------------------------------------------------------------------------------+
```

### 3.1 Device Tree Configuration (DTS)

To bind an SPI-based NFC transceiver (e.g. PN532 or ST25R3916) in the Linux Device Tree:

```dts
&spi1 {
    status = "okay";
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_spi1>;

    nfc@0 {
        compatible = "nxp,pn532";
        reg = <0>;                         /* Chip Select index (CS0) */
        spi-max-frequency = <5000000>;      /* 5 MHz max clock */
        
        interrupt-parent = <&gpio1>;
        interrupts = <18 IRQ_TYPE_EDGE_FALLING>;
        
        reset-gpios = <&gpio1 19 GPIO_ACTIVE_LOW>;
        
        /* Optional: Power-down GPIO */
        enable-gpios = <&gpio1 20 GPIO_ACTIVE_HIGH>;
        
        status = "okay";
    };
};
```

### 3.2 User-Space `libnfc` Integration over SPI

If using `libnfc` via user-space `/dev/spidev0.0`, configure `/etc/nfc/devices.d/pn532_spi.conf`:

```ini
name = "PN532 over SPI"
connstring = "pn532_spi:/dev/spidev0.0:5000000"
allow_intrusive_scan = true
```

Test hardware bring-up from the Linux shell:
```bash
# Scan for connected NFC transceivers
nfc-scan-device -v

# Continuously poll for tags and print UID/SAK/ATQA
nfc-poll
```

---

## 4. Hardware Bring-Up & Signal Integrity Verification

Bring-up must follow a structured 4-step physical verification process:

```text
+-------------------+      +--------------------+      +--------------------+      +--------------------+
|  STEP 1: SPI BUS  |      | STEP 2: RF CARRIER |      | STEP 3: MODULATION |      |  STEP 4: CARD LOAD |
|  - Verify SCLK/CS | ===> | - Probe 13.56 MHz  | ===> | - Verify 100% ASK  | ===> |    MODULATION      |
|  - Read Reg 0x37  |      | - Sine Vpp 10-20V  |      | - Pause t1: 2-3 us |      | - Probe 848 kHz    |
|    (Chip Version) |      | - Check harmonics  |      | - Check overshoot  |      |   sidebands on spy |
+-------------------+      +--------------------+      +--------------------+      +--------------------+
```

### Step 1: SPI Bus Verification
- Attach logic analyzer channels to `SCLK`, `MOSI`, `MISO`, `CS#`, and `IRQ`.
- Issue a read of the silicon version register (Address `0x37` on MFRC522 $\rightarrow$ Expected value: `0x92` for v2.0 or `0x91` for v1.0).
- If MISO returns `0x00` or `0xFF`: Check clock polarity (CPOL=0), chip select assertion, and verify power rails.

### Step 2: RF Carrier Verification
- Attach a high-impedance 10:1 passive oscilloscope probe across `TX1` and `TX2` (or across the antenna coil).
- Verify continuous **13.560 MHz ($\pm 7\text{ kHz}$)** sinusoidal oscillation.
- Confirm differential amplitude: $V_{pp}$ across the coil should be between **$10\text{V}$ and $20\text{V}$** (or $3.3\text{V}$ single-ended).

### Step 3: Modulation Envelope Verification
- Capture the RF carrier while transmitting a REQA command (`0x26`).
- Measure the carrier pause width: must fall strictly within **$2.0\ \mu\text{s} \le t_1 \le 3.0\ \mu\text{s}$**.
- If excessive ringing or overshoot is observed after the pause, the antenna $Q$-factor is too high; increase the value of series damping resistors ($R_Q$).

### Step 4: Tag Load Modulation Verification
- Place a 2-turn pickup coil ("spy coil") connected to an oscilloscope near the antenna.
- Approach the reader with an NTAG213 or MIFARE card.
- Zoom in on the RF envelope after the REQA pause. Look for the card's **848 kHz subcarrier burst** ($12.712\text{ MHz} / 14.408\text{ MHz}$ sideband modulation) exhibiting Manchester transitions.

---

## 5. Troubleshooting & Root Cause Analysis (RCA) Matrix

| Symptom | Probable Root Cause | Diagnostic Check | Verified Engineering Fix |
| :--- | :--- | :--- | :--- |
| **Transceiver unresponsive; reads return 0x00 or 0xFF** | SPI mode mismatch or floating reset pin | Check MISO on scope; probe $\overline{\text{RSTPD}}$ pin | Configure SPI Controller for Mode 0 (CPOL=0, CPHA=0). Ensure $\overline{\text{RSTPD}}$ is driven HIGH ($3.3\text{V}$). |
| **PN532 commands return no ACK or garbled response** | **Bit order mismatch (LSB-First trap)** | Inspect MOSI data on logic analyzer | PN532 hardware SPI requires **LSB-first** transmission. Reverse bit order in software or enable LSB-first in MCU SPI hardware. |
| **Card only detected at zero distance (< 3 mm)** | Antenna detuning or mismatched $Q$-factor | Measure antenna inductance $L_{ant}$ with LCR meter | Adjust matching capacitors ($C_{series}, C_{parallel}$) to center resonance at 13.56 MHz; ensure $Q \approx 20\text{--}30$. |
| **RF carrier turns on, but tags never respond to REQA** | **Omission of $5.0\text{ ms}$ guard delay ($T_{guard}$)** | Scope probe RF carrier vs REQA burst | Insert `delay_ms(5)` immediately after enabling `TX_CONTROL` before sending REQA to allow tag reservoir capacitors to charge. |
| **Microcontroller crashes or resets when RF field enables** | Inrush current causing VDD rail sag | Monitor $3.3\text{V}$ power rail with scope trigger during RF turn-on | Add bulk decoupling capacitor ($10\ \mu\text{F}$ tantalum or low-ESR ceramic) adjacent to transceiver `TVDD` and `AVDD` pins. |
| **Card detected, but anti-collision fails (`CollErr` asserted)** | High RF noise or receiver gain saturated | Read `RFCfgReg` and `CollReg` | Lower the internal receiver gain setting (e.g. from $48\text{ dB}$ to $38\text{ dB}$); adjust `RxThreshold` register. |
| **Tags completely undetected when mounted on metal/battery** | Eddy currents in metal canceling magnetic flux | Probe $H$-field strength near metal surface | Apply a sintered ferrite shielding sheet ($\mu_r' \ge 100$) between the PCB loop antenna and the metal surface. |
| **CRC errors during high-speed transfers (424 / 848 kbps)** | Antenna bandwidth too narrow ($Q$ too high) | Calculate $BW = f_c / Q$ | Increase damping resistor $R_Q$ to reduce $Q$ to $10\text{--}15$, widening RF bandwidth to $> 1\text{ MHz}$. |
