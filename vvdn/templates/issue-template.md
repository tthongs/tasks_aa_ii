# Issue: [Brief Title of the Issue]

- **ID / Date**: `[YYYY-MM-DD]`
- **Device / Board**: `[e.g., Target Board X, USB-to-UART Adapter FTDI/CH340/CP2102]`
- **Protocol / Interface**: `[e.g., UART (8-N-1, 115200), SPI, I2C]`
- **Status**: `[Open / Investigating / Resolved / Blocked]`
- **Assignee / Reporter**: `[Name]`

---

## 1. Problem Description
- What was the expected behavior?
- What is the actual behavior observed?

## 2. Hardware Setup & Connections
- **Voltage Levels**: `[e.g., 3.3V TTL, 1.8V, RS-232]`
- **Pin Mapping**:
  - TXD (Host) -> RXD (Device)
  - RXD (Host) <- TXD (Device)
  - GND <-> GND (Common ground verified?)
  - Flow control pins (RTS / CTS), if applicable
- **Adapters / Converters Used**: `[e.g., FT232RL, logic analyzer]`

## 3. Software Configuration & Environment
- **Host OS**: `[e.g., Ubuntu 22.04 LTS]`
- **Device Node**: `[e.g., /dev/ttyUSB0, /dev/ttyS0]`
- **Port Settings**:
  - Baud Rate: `[e.g., 115200]`
  - Data Bits: `[e.g., 8]`
  - Parity: `[e.g., None]`
  - Stop Bits: `[e.g., 1]`
  - Flow Control: `[None / Hardware RTS-CTS / Software XON-XOFF]`
- **Tools Used**: `[minicom, picocom, screen, python-serial, logic analyzer]`

## 4. Logs & Error Output
```text
[Paste terminal output, dmesg, error traces, or logic analyzer captures here]
```

## 5. Troubleshooting Steps & Observations
- [ ] Checked common ground connection?
- [ ] Verified TX/RX are not swapped?
- [ ] Checked logic levels (3.3V vs 1.8V vs 5V)?
- [ ] Performed loopback test on host adapter?
- [ ] Verified device baud rate with oscilloscope / logic analyzer?
- [ ] Other tests conducted:
  - *Observation 1...*
  - *Observation 2...*

## 6. Root Cause Analysis (RCA)
- **Root Cause**: `[What caused the problem?]`

## 7. Resolution / Fix
- **Fix Applied**: `[Hardware fix, software configuration change, driver patch]`
- **Verification**: `[How the fix was verified to work reliably]`
