# Device Bring-Up Checklist: UART & Serial Interfaces

Use this checklist when connecting, configuring, or validating serial communication with a new device or development board.

---

### Step 1: Electrical & Hardware Verification (Before Powering On)
- [ ] **Operating Voltage Level**: Identify target I/O voltage (1.8V, 2.5V, 3.3V, or 5V TTL).
  - *Warning*: Connecting 5V TTL to a 1.8V/3.3V SoC UART pin can damage the SoC.
  - *Warning*: Connecting RS-232 levels (±12V) directly to TTL pins will destroy the board. Use a MAX232 or MAX3232 transceiver.
- [ ] **Adapter Configuration**: Set jumper on USB-to-UART adapter (FTDI / CP2102 / CH340) to match target voltage (e.g. 3.3V).
- [ ] **Wiring Connection (Null-Modem / Crossover)**:
  - `Host TX` connects to `Target Board RX`
  - `Host RX` connects to `Target Board TX`
  - `Host GND` MUST connect to `Target Board GND` (Common reference point)
  - `VCC`: Only connect if powering the target device from the adapter. **Do NOT connect VCC if the board has its own power supply.**

---

### Step 2: Host Side Interface Verification
- [ ] Plug in the USB-to-UART converter.
- [ ] Identify device path:
  ```bash
  dmesg | grep -i tty
  ls -l /dev/ttyUSB* /dev/ttyACM*
  ```
- [ ] Ensure user has permissions to access serial port:
  ```bash
  sudo usermod -aG dialout $USER  # requires re-login or newgrp dialout
  ```
- [ ] **Loopback Test (Optional but recommended)**:
  - Disconnect from target board.
  - Short `TX` to `RX` on the adapter.
  - Open terminal (`picocom -b 115200 /dev/ttyUSB0`) and type characters.
  - If characters echo back, the USB-to-UART dongle and driver are working properly.

---

### Step 3: Serial Communication Settings
- [ ] Verify standard board parameters (check board documentation or bootloader config):
  - **Baud rate**: Typically `115200` (often `9600` for older gear, `921600` or `1500000` for Rockchip/some modern SoCs).
  - **Data bits**: `8`
  - **Parity**: `None` (N)
  - **Stop bits**: `1`
  - **Flow control**: Typically `None` (disable hardware RTS/CTS unless explicitly wired).

---

### Step 4: Connecting & Capturing Boot Logs
- [ ] Start serial console client:
  ```bash
  picocom -b 115200 /dev/ttyUSB0 --logfile bootlog_$(date +%F_%H%M%S).txt
  # or
  minicom -D /dev/ttyUSB0 -b 115200
  ```
- [ ] Power cycle / Reset the target board.
- [ ] Look for bootloader prompt (U-Boot, UEFI, Little Kernel, or SoC ROM code).

---

### Step 5: Sanity Checks if Communication Fails
| Symptom | Probable Cause | Immediate Test |
| :--- | :--- | :--- |
| **No output at all** | TX/RX swapped, wrong port, no common GND, wrong voltage | Swap TX/RX; measure voltage with multimeter (TX should idle HIGH) |
| **Garbage / gibberish characters** | Baud rate mismatch or noisy signal | Try common baud rates: 115200, 9600, 57600, 38400, 1500000 |
| **Can read boot logs, cannot type** | Flow control enabled, RX pin not connected, or read-only debug port | Disable hardware flow control (`-n` in picocom, turn off Hardware Flow Control in minicom) |
| **Random corruption / framing errors** | Ground loop, high wire capacitance, clock drift | Use shorter wires, ensure tight GND connection |
