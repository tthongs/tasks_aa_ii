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
│   ├── uart_calc.py                   # CLI tool for UART BRG divisors, frame throughput & RS-485 delays
│   ├── spi_calc.py                    # CLI tool for SPI timing budgets, round-trip delays & throughput
│   ├── nfc_calc.py                    # CLI tool for antenna inductance, matching network, Q & NDEF
│   ├── i2c_calc.py                    # CLI tool for I2C pull-up windows, bus capacitance & address decode
│   ├── can_calc.py                    # CLI tool for CAN/CAN-FD bit timing, sample points & arbitration
│   ├── lin_calc.py                    # CLI tool for LIN frame timing, PID parity, checksums & auto-baud
│   ├── ldo_calc.py                    # CLI tool for LDO thermal dissipation, feedback dividers & ESR stability
│   ├── mosfet_calc.py                 # CLI tool for MOSFET conduction/switching loss, gate drive & thermal
│   └── md_to_docx.py                  # CLI generator to synchronize .md guides into styled .docx files
├── protocols/
│   ├── uart/
│   │   ├── README.md (.docx)          # UART master hub, transceiver standards (TTL, RS-232/422/485) & roadmap
│   │   ├── uart-guide.md (.docx)      # Complete guide on UART architecture, Linux subsystem & debugging
│   │   ├── uart-frame-and-protocol-analysis.md (.docx) # Frame anatomy, 16x oversampling, 9-bit mode & DMA ring buffers
│   │   ├── uart-circuit-and-hardware-connections.md (.docx) # Schematics: MCU-to-MCU, USB bridge, RS-232, RS-485, level shifters
│   │   └── baud-rate-calculations.md (.docx) # Detailed baud rate theory, BRG formulas & error analysis
│   ├── spi/
│   │   ├── README.md (.docx)          # SPI master hub, standards overview & 4-mode comparison
│   │   ├── spi-guide.md (.docx)       # Complete guide on SPI architecture, CPOL/CPHA, Linux spidev & debugging
│   │   ├── spi-timing-and-modes.md (.docx) # Detailed SPI modes, AC timing budgets & propagation delay analysis
│   │   ├── spi-frame-analysis.md (.docx) # Detailed SPI data frames, packet structures, archetypes & CRC
│   │   └── spi-circuit-and-hardware-connections.md (.docx) # Schematics: Star/daisy-chain, QSPI Flash, isolation & level shifting
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
│   │   ├── i2c-circuit-and-hardware-connections.md (.docx)# Schematics: Master/Slaves, MOSFET level-shifter, TCA9548A, P82B715
│   │   └── i2c-timing-calculations-and-hardware.md (.docx)# AC timing specs, pull-up sizing math, bus capacitance & PCB design
│   ├── can/
│   │   ├── README.md (.docx)                              # CAN master hub, standard comparisons & roadmap
│   │   ├── can-working-and-architecture.md (.docx)        # Differential physical layer, arbitration, fault confinement & transceivers
│   │   ├── can-frame-and-protocol-analysis.md (.docx)     # Frame formats (2.0A/B, FD), bit stuffing, J1939, CANopen, UDS & SocketCAN
│   │   ├── can-circuit-and-hardware-connections.md (.docx)# Schematics: Transceiver VIO, split termination, CMC, TVS, ISO1042
│   │   └── can-timing-bitrates-and-hardware.md (.docx)    # Bit timing budgets, Time Quanta, SJW, TDC, termination & RCA matrix
│   └── lin/
│       ├── README.md (.docx)                              # LIN master hub, standard comparisons & roadmap
│       ├── lin-working-and-architecture.md (.docx)        # Single-wire 12V physical layer, asymmetric pull-up, scheduling & sleep/wake
│       ├── lin-frame-and-protocol-analysis.md (.docx)     # Frame anatomy (Break, Sync 0x55, PID parity, Classic/Enhanced Checksum)
│       ├── lin-circuit-and-hardware-connections.md (.docx)# Schematics: Master/Slave nodes, ISO 7637-2 surge protection, harness wiring
│       └── lin-timing-synchronization-and-hardware.md (.docx)# Auto-baud sync math, slave RC capture, duty cycles & bench RCA
├── ldo/
│   ├── README.md (.docx)                              # LDO master hub, operating principles & pass element comparison
│   ├── pmos-ldo-working-and-architecture.md (.docx)   # Common-Source topology, stability tunnel & MLCC compensation
│   ├── nmos-ldo-working-and-architecture.md (.docx)   # Source-Follower topology, Vbias rails, charge pumps & fast transient
│   └── ldo-calculations-and-thermal-design.md (.docx) # Thermal networks, heatsinks, feedback dividers, ESR zeros & RCA
├── mosfets/
│   ├── README.md (.docx)                              # MOSFET master hub, taxonomy, physics, math & selection matrix
│   ├── n-channel-enhancement/                         # e-NMOS physics, inversion, low-side switching & flyback clamping
│   ├── p-channel-enhancement/                         # e-PMOS physics, hole mobility, high-side drive & reverse polarity
│   ├── depletion-mode/                                # Normally-ON d-MOSFET, pinch-off, offline startup & current sources
│   ├── power-trench-mosfet/                           # UMOS & SGT shielded trench, low Rdson, sync buck top/bottom FETs
│   ├── power-vdmos/                                   # Vertical planar DMOS, UIS avalanche Eas & linear mode SOA
│   ├── superjunction-mosfet/                          # CoolMOS charge balance, breaking Si limit, PFC & fast diodes
│   ├── sic-mosfet/                                    # 4H-SiC wide-bandgap, 1200V EV traction, EVSE & +18V/-4V drive
│   ├── logic-level-mosfet/                            # Low-Vth logic-level FETs, direct 3.3V/5V MCU GPIO drive & Qg sizing
│   ├── ldmos-rf/                                      # Lateral DMOS, grounded flange, GHz RF power & Doherty amplifiers
│   ├── finfet-and-gaafet/                             # 3D multi-gate, FinFET & GAA nanosheets, SCE & sub-3nm VLSI
│   └── dual-gate-mosfet/                              # Tetrode FET, cascode integration, ultra-low Crss, AGC & RF mixers
├── evse/
│   ├── README.md (.docx)                              # EVSE master hub, system architecture & standards index
│   ├── evse-low-voltage-controller-working.md (.docx) # LV controller board working, CP/PP, safety, metering & contactor
│   ├── evse-iot-and-communication-subsystem.md (.docx)# IoT gateway, 4G/Wi-Fi/Ethernet, OCPP 1.6J/2.0.1 & DLM
│   └── evse-hardware-schematic-and-interfacing.md (.docx) # Schematics, BOM selection, galvanic isolation & bring-up
├── dual_lift_controller/
│   ├── README.md (.docx)                              # Dual lift master hub, architecture & design index
│   ├── 3-floor-dual-lift-logic-design.md (.docx)      # Gate-level design for 3-floor building (27-state truth table, K-maps)
│   ├── 4-floor-dual-lift-logic-design.md (.docx)      # Gate-level design for 4-floor building (64-state truth table, subtractors)
│   ├── gate-level-schematics-and-simulation.md (.docx)# TTL 7400 IC schematics, gate counts & simulation waveforms
│   ├── dual_lift_controller.v                         # Synthesizable gate-level Verilog hardware description module
│   └── dual_lift_controller_tb.v                      # Verilog testbench validating all 64 state combinations
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
- **[tools/uart_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/uart_calc.py)**: Calculate UART baud divisors, frame timing budgets, payload throughput, and RS-485 cable delays:
  ```bash
  python3 tools/uart_calc.py --baud --clock 16MHz --baudrate 115200
  python3 tools/uart_calc.py --frame --baudrate 115200 --data-bits 8 --parity N --stop-bits 1
  python3 tools/uart_calc.py --rs485 --cable-m 100 --baudrate 115200
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
- **[tools/can_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/can_calc.py)**: Calculate CAN and CAN FD bit timing registers, Sample Point %, bit-stuffing overhead, frame duration, and bitwise arbitration simulation:
  ```bash
  python3 tools/can_calc.py --clock 80MHz --baud 500000 --sp 87.5
  python3 tools/can_calc.py --fd --clock 80MHz --baud 500000 --data-baud 2000000
  python3 tools/can_calc.py --arbitrate --id1 0x120 --id2 0x124
  ```
- **[tools/lin_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/lin_calc.py)**: Calculate LIN frame slot durations ($1.4\times$ slot budget), PID parity bits ($P0, P1$), Classic & Enhanced checksums, auto-baud sync capture ticks, and bus RC parameters:
  ```bash
  python3 tools/lin_calc.py --baud 19200 --data-bytes 8 --slaves 8
  python3 tools/lin_calc.py --pid 0x23
  python3 tools/lin_calc.py --checksum --pid 0x23 --data 0x01 0x02 0x03 0x04
  ```
- **[tools/ldo_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/ldo_calc.py)**: Calculate LDO power dissipation, junction temperature ($T_J$), required heatsink thermal resistance, feedback resistor divider sizing (E96 1%), and ESR stability zero frequency:
  ```bash
  python3 tools/ldo_calc.py --thermal --vin 5.0 --vout 3.3 --iload 0.5 --theta-ja 45.0
  python3 tools/ldo_calc.py --feedback --vout 3.3 --vref 1.2
  python3 tools/ldo_calc.py --stability --cout 10.0 --esr 15.0 --cff 47.0 --r1 21.0 --r2 12.0
  python3 tools/ldo_calc.py --compare --vin 3.3 --vout 1.8 --iload 1.0
  ```
- **[tools/mosfet_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/mosfet_calc.py)**: Calculate MOSFET conduction loss, switching loss, gate drive resistor sizing, thermal junction temperatures, and body diode recovery:
  ```bash
  python3 tools/mosfet_calc.py --loss --vds 48 --id 15 --rdson 0.005 --trise 25n --tfall 20n --fsw 150k
  python3 tools/mosfet_calc.py --gate --vdrv 12 --vplat 4.2 --qgd 12n --target-dt 30n
  python3 tools/mosfet_calc.py --diode --vds 400 --iload 20 --vsd 1.2 --tdead 100n --qrr 450n --fsw 100k
  ```
- **[tools/evse_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/evse_calc.py)**: Calculate EVSE Control Pilot PWM duty cycles, allowable charging currents, grid power, and RCM response times:
  ```bash
  python3 tools/evse_calc.py --mode full --current 32 --phase 3 --voltage-grid 400
  ```
- **[tools/lift_sim.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/lift_sim.py)**: Simulate and verify gate-level nearest-lift arbitration and motor direction logic across all floor combinations:
  ```bash
  python3 tools/lift_sim.py --floors 4 --verify
  ```
- **[tools/md_to_docx.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/md_to_docx.py)**: Automatically convert/update Markdown documents to styled Microsoft Word (`.docx`) files for mentor sharing and executive reviews:
  ```bash
  python3 tools/md_to_docx.py                 # Syncs all standards/ and protocols/ guides
  python3 tools/md_to_docx.py <path/to/file>  # Converts a specific .md file
  ```

---

## Protocol Guides & Quick Links

- [UART Master Architecture & Knowledge Base](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/README.docx)): Master hub for UART protocols, transceiver standards (TTL, RS-232, RS-422, RS-485), protocol benchmark matrix, and CLI tools.
- [UART Complete Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/uart-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/uart-guide.docx)): Complete architecture, Linux subsystem, C/Python code, and failure modes.
- [UART Frame & Protocol Analysis](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/uart-frame-and-protocol-analysis.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/uart-frame-and-protocol-analysis.docx)): Bit-level frame anatomy, 16x oversampling clock recovery, majority voting, 9-bit multi-drop addressing, hardware flow control, and DMA circular ring buffers.
- [UART Hardware Connections & Circuit Schematics](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/uart-circuit-and-hardware-connections.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/uart-circuit-and-hardware-connections.docx)): Circuit schematics for MCU cross-over, USB bridge (CP2102/FT232), bipolar RS-232 (MAX3232), half-duplex RS-485 (MAX485), and BSS138 level shifter.
- [UART Baud Rate Calculations](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/baud-rate-calculations.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/uart/baud-rate-calculations.docx)): In-depth look at baud vs bit rate, hardware BRG divisor formulas, 16x oversampling, error margins, and oscilloscope measurement.
- [SPI Master Architecture & Knowledge Base](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/README.docx)): Master hub for SPI protocols, 4-mode truth table, multi-target topologies, Quad/Octal SPI extensions, and benchmark comparison.
- [SPI Complete Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-guide.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-guide.docx)): Complete architecture, CPOL/CPHA modes, QSPI/OSPI variants, Linux spidev, C/Python code, and failure modes.
- [SPI Timing & Modes Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-timing-and-modes.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-timing-and-modes.docx)): In-depth look at CPOL/CPHA edge transitions, shift register mechanics, round-trip delay calculations, high-speed signal integrity, and logic analyzer debugging.
- [SPI Data Frame Analysis](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-frame-analysis.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-frame-analysis.docx)): Deep dive on physical vs logical framing, command/address/dummy phases, Flash/IMU/ADC/Safe-SPI archetypes, CRC-8, and multi-segment Linux transfers.
- [SPI Hardware Connections & Circuit Schematics](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-circuit-and-hardware-connections.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/spi/spi-circuit-and-hardware-connections.docx)): Circuit schematics for single-slave with damping, multi-slave star routing, shift-register daisy-chaining, QSPI Flash (W25Q128JV), and galvanic isolation.
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
- [I2C Hardware Connections & Circuit Schematics](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-circuit-and-hardware-connections.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-circuit-and-hardware-connections.docx)): Circuit schematics for multi-target bus, BSS138 bi-voltage level shifter, TCA9548A multiplexer for address conflicts, and P82B715 long-distance buffer.
- [I2C AC Timing, Pull-Up Calculations & Hardware](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-timing-calculations-and-hardware.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/i2c/i2c-timing-calculations-and-hardware.docx)): AC timing parameter matrix, mathematical derivation of $R_{p(min)}$ and $R_{p(max)}$, bus capacitance budgeting ($C_b$), active bus accelerators, PCB layout & crosstalk shielding, and bench RCA troubleshooting matrix.
- [CAN Master Architecture & Knowledge Base](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/README.docx)): Master hub for CAN/CAN-FD standards, generational comparison matrix (2.0A/B, FD, XL), bus architecture, and CLI tools.
- [CAN Working Mechanism & Physical Layer](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-working-and-architecture.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-working-and-architecture.md)): Physical differential signaling, Recessive/Dominant voltage levels, transceivers, non-destructive bitwise arbitration, error detection, fault confinement state machine (TEC/REC), and acceptance filters.
- [CAN Frame & Protocol Analysis](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-frame-and-protocol-analysis.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-frame-and-protocol-analysis.docx)): Bit-by-bit frame anatomy (Standard 2.0A, Extended 2.0B, CAN FD), bit-stuffing overhead, SAE J1939, CANopen, UDS over CAN-TP (ISO 15765-2), and Linux SocketCAN C driver.
- [CAN Hardware Connections & Circuit Schematics](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-circuit-and-hardware-connections.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-circuit-and-hardware-connections.docx)): Circuit schematics for TJA1051 VIO transceiver, split termination, common-mode choke (51µH), TVS ESD diodes, and ISO1042 galvanically isolated nodes.
- [CAN Timing, Bitrates & Hardware Engineering](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-timing-bitrates-and-hardware.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/can/can-timing-bitrates-and-hardware.docx)): Bit timing theory, Time Quanta, SJW, sample point optimization, CAN FD dual-bitrate timing, Transmitter Delay Compensation (TDC/SSP), bus length trade-offs, split termination, and bench RCA matrix.
- [LIN Master Architecture & Knowledge Base](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/README.docx)): Master hub for LIN protocol standards (LIN 1.3, 2.0, 2.1, 2.2A, ISO 17987), vehicle sub-bus architecture, and comparison matrix.
- [LIN Working Mechanism & Electrical Architecture](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-working-and-architecture.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-working-and-architecture.docx)): Single-wire 12V physical layer, asymmetric termination ($1\text{k}\Omega$ Master, $30\text{k}\Omega$ Slave), transceiver slew-rate control, deterministic schedule tables, sleep/wake-up protocol, and node configuration (NAD).
- [LIN Frame & Protocol Analysis](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-frame-and-protocol-analysis.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-frame-and-protocol-analysis.docx)): Bit-level frame anatomy (Break $\ge 13$ bits, Sync 0x55, PID parity equations P0/P1), Classic vs Enhanced Checksum algorithms, frame types, LIN TP, waveform decoding, and MCU UART driver.
- [LIN Hardware Connections & Circuit Schematics](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-circuit-and-hardware-connections.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-circuit-and-hardware-connections.docx)): Circuit schematics for automotive Master Node (1kΩ + BAS21 diode), Slave Node (internal 30kΩ), ISO 7637-2 surge protection, and vehicle harness wiring.
- [LIN Timing Calculations, Synchronization & Hardware](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-timing-synchronization-and-hardware.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/lin/lin-timing-synchronization-and-hardware.docx)): Bit timing, $1.4\times$ slot budget sizing, slave auto-baud clock synchronization math, timer input capture ISR, duty cycle timing budgets, bus RC capacitance, ISO 7637-2 surge protection, and bench RCA matrix.
- [LDO Master Architecture & Knowledge Base](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/ldo/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/ldo/README.docx)): Master hub for linear regulators, LDO operating principles, PMOS vs. NMOS pass element benchmark, performance metrics, and CLI tools.
- [PMOS LDO Working Mechanism & Architecture](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/ldo/pmos-ldo-working-and-architecture.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/ldo/pmos-ldo-working-and-architecture.docx)): Common-Source topology, gate drive physics ($V_{GATE} < V_{IN}$), two-pole loop dynamics, ESR stability tunnel, MLCC ceramic compensation, and parasitic body diode reverse current protection.
- [NMOS LDO Working Mechanism & Architecture](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/ldo/nmos-ldo-working-and-architecture.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/ldo/nmos-ldo-working-and-architecture.docx)): Source-Follower topology, intrinsic local feedback, gate headroom constraint ($V_{GATE} > V_{IN}$), dual-rail $V_{BIAS}$ vs. internal charge pumps, wideband MLCC stability, and triple-well body effect elimination.
- [LDO Calculations, Feedback Sizing & Thermal Design](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/ldo/ldo-calculations-and-thermal-design.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/ldo/ldo-calculations-and-thermal-design.docx)): Power dissipation math, thermal resistance network ($\theta_{JA}, \theta_{JC}$), heatsink sizing, standard E96 feedback divider design, feedforward capacitor ($C_{FF}$) phase-lead zero, output capacitor dynamic sizing, and bench RCA troubleshooting matrix.
- [MOSFET Master Architecture & Study Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/README.docx)): Master hub covering MOSFET taxonomy, semiconductor physics, mathematical models, switching dynamics, Miller plateau, thermal sizing, and selection matrix.
- [N-Channel Enhancement MOSFET Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/n-channel-enhancement/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/n-channel-enhancement/README.docx)): e-NMOS physics, inversion channel, low-side switching, gate pull-down/damping resistors, and inductive flyback clamping.
- [P-Channel Enhancement MOSFET Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/p-channel-enhancement/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/p-channel-enhancement/README.docx)): e-PMOS hole mobility penalty, high-side power switching, level shifter driver, and millivolt reverse polarity protection circuits.
- [Depletion-Mode MOSFET Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/depletion-mode/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/depletion-mode/README.docx)): Normally-ON d-MOSFET physics, negative pinch-off, lossless high-voltage offline SMPS startup, and two-terminal constant current sources.
- [Power Trench MOSFET Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/power-trench-mosfet/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/power-trench-mosfet/README.docx)): UMOS & Shielded Gate Trench (SGT) architectures, JFET resistance elimination, and synchronous buck top vs bottom FET optimization.
- [Vertical Planar Power VDMOS Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/power-vdmos/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/power-vdmos/README.docx)): Double-diffused planar power physics, high single-pulse avalanche energy ($E_{AS}$), and linear mode SOA immunity to Spirito hotspots.
- [Superjunction (CoolMOS) Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/superjunction-mosfet/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/superjunction-mosfet/README.docx)): Multi-epi charge balance physics, breaking the 1D Silicon limit, non-linear $C_{oss}$, high $dv/dt$ handling, and fast recovery CFD body diodes.
- [Silicon Carbide (SiC) Power MOSFET Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/sic-mosfet/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/sic-mosfet/README.docx)): Wide-bandgap $3.26\,\text{eV}$ physics, $+18\text{V}/-4\text{V}$ asymmetric gate drive, Kelvin Source connection, DESAT protection, and EV traction inverters.
- [Logic-Level MOSFET Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/logic-level-mosfet/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/logic-level-mosfet/README.docx)): Thin-oxide $1-2\,\text{V}$ $V_{TH}$ engineering, direct $3.3\,\text{V}/5\,\text{V}$ MCU GPIO drive, inrush resistor sizing, and gate charge limitations.
- [Lateral DMOS (LDMOS) RF Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/ldmos-rf/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/ldmos-rf/README.docx)): RF power physics, grounded backside flange, ultra-low $C_{rss}$, $65:1$ VSWR survival, and Doherty base station architectures.
- [Advanced Multi-Gate FinFET & GAAFET Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/finfet-and-gaafet/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/finfet-and-gaafet/README.docx)): 3D FinFET tri-gate, Gate-All-Around (GAA) nanosheets, FD-SOI, short-channel effect mitigation, and sub-3nm VLSI scaling.
- [Dual-Gate (Tetrode) MOSFET Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/dual-gate-mosfet/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/mosfets/dual-gate-mosfet/README.docx)): Monolithic cascode integration, independent dual gates, Miller suppression ($C_{rss} < 0.02\,\text{pF}$), AGC amplifiers, and active RF mixers.
- [EVSE Knowledge Base & Systems Hub](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/README.docx)): Master hub for EV charging equipment architecture, high-voltage vs low-voltage domain separation, and international standards.
- [EVSE Low Voltage Controller Working & Architecture](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-low-voltage-controller-working.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-low-voltage-controller-working.docx)): Complete working of the LV controller board, ±12V CP PWM bipolar generation, vehicle state machine (A..F), diode safety check, PP cable rating detection, 6mA DC / 30mA AC RCM leakage trip, welded contactor detection, precision energy metering, and coil economizer.
- [EVSE IoT Gateway & Communication Subsystem](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-iot-and-communication-subsystem.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-iot-and-communication-subsystem.docx)): Dual-processor safety architecture, 4G LTE Cat-1 / Wi-Fi / BLE / Ethernet connectivity, complete OCPP 1.6-J / 2.0.1 transaction message flows, RS-485 Modbus Dynamic Load Management (DLM), RFID authentication, and A/B dual-bank secure OTA.
- [EVSE Hardware Schematics & Bring-Up Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-hardware-schematic-and-interfacing.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/evse/evse-hardware-schematic-and-interfacing.docx)): Component-level schematics (CP op-amp buffer, PP divider, contactor driver, H-bridge lock), reinforced creepage/clearance (>= 6-8mm), GDT/MOV surge protection, and bench RCA troubleshooting matrix.
- [Dual Lift Controller Master Hub](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/README.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/README.docx)): Master hub for 3-floor and 4-floor dual lift dispatch system, architectural block diagrams, and subsystem interface specifications.
- [3-Floor Dual Lift Gate Logic Design](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/3-floor-dual-lift-logic-design.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/3-floor-dual-lift-logic-design.docx)): Gate-level realization for 3 floors (Floors 0, 1, 2), 1-hot distance calculation, exhaustive 27-state truth table, K-maps, and motor direction logic ($UP, DOWN, STOP$).
- [4-Floor Dual Lift Gate Logic Design](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/4-floor-dual-lift-logic-design.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/4-floor-dual-lift-logic-design.docx)): 2-bit binary arithmetic distance subtractors ($|R - A|$, $|R - B|$), 2-bit magnitude comparators, 64-state system analysis, nearest dispatch arbiter, and busy-state priority handling.
- [Gate-Level Schematics & Verilog Simulation](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/gate-level-schematics-and-simulation.md) ([Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/gate-level-schematics-and-simulation.docx)): Standard 7400-series TTL IC Bill of Materials, pin-to-pin schematics, ULN2003 contactor drive, sub-80ns propagation delay analysis, and Verilog simulation test vectors.


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
