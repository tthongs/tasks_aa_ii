# VVDN Engineering Hub & Protocol Knowledge Base

Welcome to your central tracking workspace for embedded systems, hardware protocols, device bring-up, and issue resolution at VVDN.

---

## Workspace Structure

```text
.
├── README.md                          # Central dashboard and quick links
├── templates/
│   ├── issue-template.md              # Standard bug/issue logging format
│   └── device-bringup-checklist.md    # Bring-up checklist for serial interfaces
├── tools/
│   ├── baud_calc.py                   # CLI tool to calculate UART baud rate divisors & error %
│   ├── spi_calc.py                    # CLI tool for SPI timing budgets, round-trip delays & throughput
│   ├── nfc_calc.py                    # CLI tool for antenna inductance, matching network, Q & NDEF
│   └── md_to_docx.py                  # CLI generator to synchronize .md guides into styled .docx files
├── protocols/
│   ├── uart/
│   │   ├── uart-guide.md (.docx)      # Complete guide on UART architecture & debugging
│   │   └── baud-rate-calculations.md  # Detailed baud rate theory, BRG formulas & error analysis
│   ├── spi/
│   │   ├── spi-guide.md (.docx)       # Complete guide on SPI architecture, CPOL/CPHA, Linux spidev & debugging
│   │   ├── spi-timing-and-modes.md    # Detailed SPI modes, AC timing budgets & propagation delay analysis
│   │   └── spi-frame-analysis.md      # Detailed SPI data frames, packet structures, archetypes & CRC
│   ├── nfc/
│   │   ├── README.md (.docx)          # NFC master hub, standards overview & transceiver comparison
│   │   ├── nfc-rf-and-physical-layer.md (.docx) # 13.56 MHz RF physics, ASK modulations, antenna & matching
│   │   ├── spi-rfid-transceiver-interface.md (.docx) # SPI bridge, pinout, register vs packet, LSB trap & FIFO
│   │   ├── iso14443-framing-and-anticollision.md (.docx) # 7-bit REQA, cascade anti-collision walk & T=CL APDUs
│   │   ├── ndef-and-card-emulation.md (.docx) # NFC Forum Types 1-5, NDEF framing, RTD types & HCE
│   │   └── nfc-firmware-and-driver-guide.md (.docx) # Modular C driver, Linux subsystem, bring-up & RCA
│   ├── i2c/
│   │   ├── README.md (.docx)                              # I2C master hub, speed modes & bus comparison
│   │   ├── i2c-working-and-architecture.md (.docx)        # Working mechanism, open-drain, wired-AND, arbitration, clock stretching
│   │   ├── i2c-frame-and-protocol-analysis.md (.docx)     # Frame formats, 7/10-bit addressing, packet archetypes & logic decoding
│   │   └── i2c-timing-calculations-and-hardware.md (.docx)# AC timing specs, pull-up sizing math, bus capacitance & PCB design
│   └── can/                           # (Planned: CAN bus framing & bitrates)
├── evse/
│   ├── README.md (.docx)                              # EVSE master hub, system architecture & standards index
│   ├── evse-low-voltage-controller-working.md (.docx) # LV controller board working, CP/PP, safety, metering & contactor
│   ├── evse-iot-and-communication-subsystem.md (.docx)# IoT gateway, 4G/Wi-Fi/Ethernet, OCPP 1.6J/2.0.1 & DLM
│   └── evse-hardware-schematic-and-interfacing.md (.docx) # Schematics, BOM selection, galvanic isolation & bring-up
├── standards/
│   ├── README.md (.docx)              # Standards hub, lifecycle mapping & comparison matrix
│   ├── rohs/
│   │   └── rohs-guide.md (.docx)      # RoHS 1/2/3 directives, restricted substances, SAC305, exemptions
│   ├── reach/
│   │   └── reach-guide.md (.docx)     # REACH, SVHC Candidate List, O5A rule, SCIP reporting
│   ├── aec/
│   │   └── aec-guide.md (.docx)       # Automotive Electronics Council (AEC-Q100/101/200, grades)
│   └── msl/
│       └── msl-guide.md (.docx)       # Moisture Sensitivity Levels (J-STD-020/033, popcorning, bake)
├── active/                            # In-progress investigations & open device issues
└── resolved/                          # Documented fixes, post-mortems, and RCA
```

---

## Tools & Utilities

- **[tools/baud_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/baud_calc.py)**: Quickly calculate hardware divisor registers (integer & fractional) and error percentage for any MCU clock:
  ```bash
  python3 tools/baud_calc.py --clock 16MHz --baud 115200
  ```
- **[tools/spi_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/spi_calc.py)**: Calculate SPI round-trip propagation delays, safe maximum read clock frequencies, and throughput:
  ```bash
  python3 tools/spi_calc.py --clock 50MHz --trace-cm 5 --tco 7 --tsu 3
  ```
- **[tools/nfc_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/nfc_calc.py)**: Calculate PCB antenna inductance, resonance capacitors, $Q$-factor, matching network, and NDEF record encodings:
  ```bash
  python3 tools/nfc_calc.py --antenna --width-mm 45 --height-mm 35 --turns 4 --track-mm 0.5
  python3 tools/nfc_calc.py --matching --inductance-uh 1.85 --r-ant 1.1 --q-target 25 --r-load 50
  python3 tools/nfc_calc.py --ndef-uri "https://vvdntech.com"
  ```
- **[tools/i2c_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/i2c_calc.py)**: Calculate I2C pull-up resistor windows ($R_{p(min)}$ and $R_{p(max)}$), bus capacitance budgets, rise time compliance, and 7-bit/8-bit address conversions:
  ```bash
  python3 tools/i2c_calc.py --mode full --vdd 3.3 --cap 180 --rp 2.2k --speed fast --address 0x68
  ```
- **[tools/evse_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/evse_calc.py)**: Calculate EVSE Control Pilot PWM duty cycles, allowable charging currents, grid power, and RCM response times:
  ```bash
  python3 tools/evse_calc.py --mode full --current 32 --phase 3 --voltage-grid 400
  ```
- **[tools/md_to_docx.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/md_to_docx.py)**: Automatically convert/update Markdown documents to styled Microsoft Word (`.docx`) files for mentor sharing and executive reviews:
  ```bash
  python3 tools/md_to_docx.py                 # Syncs all standards/ and protocols/ guides
  python3 tools/md_to_docx.py <path/to/file>  # Converts a specific .md file
  ```

---

## Protocol Guides & Quick Links

- [UART Complete Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/uart-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/uart-guide.docx)): Complete architecture, Linux subsystem, C/Python code, and failure modes.
- [UART Baud Rate Calculations](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/baud-rate-calculations.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/baud-rate-calculations.docx)): In-depth look at baud vs bit rate, hardware BRG divisor formulas, 16x oversampling, error margins, and oscilloscope measurement.
- [SPI Complete Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-guide.docx)): Complete architecture, CPOL/CPHA modes, QSPI/OSPI variants, Linux spidev, C/Python code, and failure modes.
- [SPI Timing & Modes Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-timing-and-modes.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-timing-and-modes.docx)): In-depth look at CPOL/CPHA edge transitions, shift register mechanics, round-trip delay calculations, high-speed signal integrity, and logic analyzer debugging.
- [SPI Data Frame Analysis](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-frame-analysis.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-frame-analysis.docx)): Deep dive on physical vs logical framing, command/address/dummy phases, Flash/IMU/ADC/Safe-SPI archetypes, CRC-8, and multi-segment Linux transfers.
- [NFC Knowledge Base Index](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/README.docx)): Master hub for NFC protocols, ISO/IEC standards map, transceiver comparison (PN532, MFRC522, ST25R3916, TRF7970A), and glossary.
- [NFC & SPI Interaction Guide (Mentor Briefing)](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/spi-rfid-nfc-interaction-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/spi-rfid-nfc-interaction-guide.docx)): Conceptual explainer on how SPI and RFID frontends interact to create NFC, step-by-step transaction walkthrough, why SPI over I2C, and mentor defense Q&A.
- [NFC RF & Physical Layer Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/nfc-rf-and-physical-layer.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/nfc-rf-and-physical-layer.docx)): Near-field inductive coupling physics, Biot-Savart, 100% vs 10% ASK, 848 kHz subcarrier load modulation, antenna $Q$-factor, EMC filters, and ferrite shielding against metal surfaces.
- [NFC SPI Transceiver Interface Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/spi-rfid-transceiver-interface.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/spi-rfid-transceiver-interface.docx)): 4-wire SPI + sideband GPIOs (CS#, IRQ, RSTPD), Register-driven vs Packet-driven frontends, the critical LSB-first bit order trap, FIFO watermark interrupts, and AC timing budgets.
- [ISO/IEC 14443 Protocol & Anti-Collision Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/iso14443-framing-and-anticollision.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/iso14443-framing-and-anticollision.docx)): State machine, 5.0 ms guard delay, 7-bit unaligned REQA/WUPA short frames, ATQA decoding, Cascade Levels 1/2/3 bit-oriented collision walk, SAK resolution, and ISO 14443-4 T=CL APDU transport.
- [NFC NDEF & Card Emulation Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/ndef-and-card-emulation.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/ndef-and-card-emulation.docx)): NFC Forum Tag Types 1–5, Capability Containers (CC), NDEF message framing, Record headers (TNF, RTD URI/Text/MIME), Peer-to-Peer (LLCP/SNEP), and Host Card Emulation (HCE) via SPI.
- [NFC Firmware, Driver & Debugging Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/nfc-firmware-and-driver-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/nfc-firmware-and-driver-guide.docx)): Production-grade modular C driver, Linux kernel NFC subsystem (`drivers/nfc`, Device Tree, `spidev`), 4-step oscilloscope/logic analyzer bring-up, and RCA troubleshooting matrix.
- [I2C Master Architecture & Knowledge Base](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/README.docx)): Master hub for I2C protocol standards, speed modes (100k, 400k, 1M, 3.4M), bus comparison matrix, and hardware quick references.
- [I2C Working Mechanism & Architecture](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-working-and-architecture.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-working-and-architecture.docx)): Physical open-drain layer, wired-AND logic, bidirectional MOSFET level shifters, clock synchronization, clock stretching, multi-master arbitration, spike filters, and stuck SDA bus recovery.
- [I2C Frame & Protocol Analysis](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-frame-and-protocol-analysis.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-frame-and-protocol-analysis.docx)): Bit-level frame anatomy (START, STOP, Repeated START), 9-bit byte units, ACK/NACK signaling, 7-bit vs 8-bit addressing traps, 10-bit addressing frames, reserved addresses, 5 transaction archetypes, and logic analyzer frame decoding.
- [I2C AC Timing, Pull-Up Calculations & Hardware](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-timing-calculations-and-hardware.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-timing-calculations-and-hardware.docx)): AC timing parameter matrix, mathematical derivation of $R_{p(min)}$ and $R_{p(max)}$, bus capacitance budgeting ($C_b$), active bus accelerators, PCB layout & crosstalk shielding, and bench RCA troubleshooting matrix.
- [EVSE Knowledge Base & Systems Hub](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/README.docx)): Master hub for EV charging equipment architecture, high-voltage vs low-voltage domain separation, and international standards.
- [EVSE Low Voltage Controller Working & Architecture](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-low-voltage-controller-working.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-low-voltage-controller-working.docx)): Complete working of the LV controller board, ±12V CP PWM bipolar generation, vehicle state machine (A..F), diode safety check, PP cable rating detection, 6mA DC / 30mA AC RCM leakage trip, welded contactor detection, precision energy metering, and coil economizer.
- [EVSE IoT Gateway & Communication Subsystem](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-iot-and-communication-subsystem.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-iot-and-communication-subsystem.docx)): Dual-processor safety architecture, 4G LTE Cat-1 / Wi-Fi / BLE / Ethernet connectivity, complete OCPP 1.6-J / 2.0.1 transaction message flows, RS-485 Modbus Dynamic Load Management (DLM), RFID authentication, and A/B dual-bank secure OTA.
- [EVSE Hardware Schematics & Bring-Up Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-hardware-schematic-and-interfacing.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-hardware-schematic-and-interfacing.docx)): Component-level schematics (CP op-amp buffer, PP divider, contactor driver, H-bridge lock), reinforced creepage/clearance (>= 6-8mm), GDT/MOV surge protection, and bench RCA troubleshooting matrix.


---

## Hardware Compliance & Reliability Standards

All guides are maintained simultaneously in **Markdown (`.md`)** for repository tracking and **Microsoft Word (`.docx`)** for sharing with mentors and stakeholders:

- [Standards Knowledge Base Index](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/README.docx)): Master hub comparing RoHS, REACH, AEC, and MSL across the hardware lifecycle.
- [RoHS Complete Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/rohs/rohs-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/rohs/rohs-guide.docx)): 10 restricted substances, homogeneous materials, Annex III exemptions (6c, 7a, 7c-I), lead-free soldering (SAC305), tin whiskers, and CE DoC.
- [REACH Complete Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/reach/reach-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/reach/reach-guide.docx)): Regulation (EC) No 1907/2006, SVHC Candidate List, Article 33 communication, O5A ("Once an Article, Always an Article") rule, Annex XVII restrictions, and SCIP database.
- [AEC Qualification Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/aec/aec-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/aec/aec-guide.docx)): Automotive Electronics Council standards (AEC-Q100/101/102/103/104/200), temperature grades (0 to 4), stress test groups A–G, zero-defect ($c=0$), and PPAP integration.
- [MSL Handling Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/msl/msl-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/standards/msl/msl-guide.docx)): Moisture Sensitivity Levels 1–6 (IPC/JEDEC J-STD-020/033), steam popcorning physics, dry packs, HIC cards, dry cabinet pausing, and baking matrix.

---

## Bringing Up a New Device

When you receive a new board or serial peripheral:
1. Follow the [Device Bring-Up Checklist](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/templates/device-bringup-checklist.md).
2. If communication fails or unexpected behavior occurs, copy [templates/issue-template.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/templates/issue-template.md) into `active/<issue-name>.md` to track and troubleshoot.
3. Once solved, move the file to `resolved/` with the Root Cause Analysis (RCA) and verified fix.
