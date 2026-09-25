# NFC Protocol & SPI-Based RFID Implementation Knowledge Base

## 1. Executive Overview

**Near Field Communication (NFC)** is a specialized subset of High-Frequency (HF) Radio Frequency Identification (RFID) operating at **13.56 MHz**. While generic RFID was engineered for one-way identification across ranges from centimeters to meters, NFC was standardized by ISO/IEC, ECMA, and the NFC Forum for **secure, bidirectional, short-range (typically $\le 4\text{ cm}$) high-integrity interactions**.

In embedded systems, an NFC subsystem is commonly realized as a **two-tier architecture**:
1. **Host Microcontroller / SoC** (e.g., STM32, ESP32, NXP i.MX, Nordic nRF5340): Executes application logic, NFC Forum protocol stacks, NDEF parsing, cryptographic authentication (Crypto1, AES-128, ECC), and host card emulation (HCE).
2. **NFC Transceiver / Front-End Controller** (e.g., NXP PN532, STMicroelectronics ST25R3916, NXP MFRC522, TI TRF7970A): Bridges the digital host domain to the analog 13.56 MHz electromagnetic field.
3. **SPI Interconnect Bus**: Synchronous, full-duplex serial interface that provides high data throughput, deterministic timing, and low CPU overhead for transferring raw modulation bits, FIFO buffers, and command frames between the Host MCU and the RF front-end.

```text
+-------------------+                      +-------------------------+                     +------------------+
|    Host MCU       |                      |  NFC Transceiver IC     |                     |  Matching & EMC  |
| (Application,     |      SPI Interface   | (Framing, FIFO, Mod/Dem)|   13.56 MHz TX/RX   |     Network      |
|  Protocol Stack,  |======================| (PN532 / ST25R3916 /    |====================>| (Low-pass filter,|==+
|  Crypto Engine)   |  MOSI, MISO, SCLK,   |  MFRC522)               |   TX1, TX2, RX      |  Matching caps,  |  |
|                   |  CS#, IRQ, RST       |                         |                     |  Damping R)      |  |
+-------------------+                      +-------------------------+                     +------------------+  |
                                                                                                                 |
                                                   Inductive Magnetic Coupling (H-field)                         |
                                                   Carrier: 13.56 MHz, d <= 4 cm                                 v
                                              + - - - - - - - - - - - - - - - - - - - - - - +              +----------+
                                              |                                             |              | PCB Loop |
                                              |       +-----------------------------+       |<=============| Antenna  |
                                              |       |   Target NFC Tag / Phone    |       |              +----------+
                                              |       |  (NTAG21x, MIFARE, HCE)     |       |
                                              |       | - Resonant LC Tank (13.56M) |       |
                                              |       | - Power Harvester / Rect    |       |
                                              |       | - Load Modulator (848 kHz)  |       |
                                              + - - - +-----------------------------+ - - - +
```

---

## 2. Directory Structure & Documentation Suite

This knowledge base is organized into focused, mathematically rigorous engineering modules:

| Document | Primary Focus | Key Standards / Topics Covered |
| :--- | :--- | :--- |
| **[spi-rfid-nfc-interaction-guide.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/spi-rfid-nfc-interaction-guide.md)** | **Mentor Briefing & Conceptual Explainer** | **How SPI & RFID interact to create NFC, the 3-tier mental model, step-by-step transaction walkthrough, why SPI over I2C, and mentor Q&A cheat sheet** |
| **[nfc-rf-and-physical-layer.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/nfc-rf-and-physical-layer.md)** | RF Physics, Modulation, Antenna & Matching | 13.56 MHz carrier, inductive coupling, Biot-Savart, 100% vs 10% ASK, Modified Miller, Manchester, 848 kHz subcarrier load modulation, EMC filter design, antenna $Q$-factor, tuning networks |
| **[spi-rfid-transceiver-interface.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/spi-rfid-transceiver-interface.md)** | SPI Hardware Bridge & Controller Architecture | 4-wire SPI + IRQ/RST, Register-driven (MFRC522/ST25R) vs Packet-driven (PN532), CPOL/CPHA modes, LSB-first vs MSB-first bit order trap, FIFO watermark interrupts, timing budgets |
| **[iso14443-framing-and-anticollision.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/iso14443-framing-and-anticollision.md)** | Lower Protocol Stack & Anti-Collision | ISO/IEC 14443 Type A/B, REQA/WUPA 7-bit unaligned short frames, ATQA, Cascade Levels 1/2/3, bit-oriented anti-collision walk, SAK parsing, RATS/ATS, ISO 14443-4 T=CL APDU transport |
| **[ndef-and-card-emulation.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/ndef-and-card-emulation.md)** | High-Level Data & Operating Modes | NFC Forum Tag Types 1–5, Capability Container (CC), NDEF message framing, Record headers (TNF, RTD), URI/Text/MIME, P2P (LLCP/SNEP), Host Card Emulation (HCE) via SPI |
| **[nfc-firmware-and-driver-guide.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/protocols/nfc/nfc-firmware-and-driver-guide.md)** | Embedded Firmware, Linux & Diagnostics | Modular C driver (HAL, register abstraction, anti-collision engine), Linux kernel NFC subsystem (`drivers/nfc`, Device Tree), oscilloscope/logic analyzer debug traces, RCA troubleshooting matrix |
| **[tools/nfc_calc.py](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/tools/nfc_calc.py)** | Engineering CLI Calculator Tool | Loop antenna inductance ($L_{ant}$), resonance frequency, $Q$-factor, matching capacitors ($C_{series}$, $C_{parallel}$), damping resistor ($R_Q$), and NDEF payload encoding |

---

## 3. High-Level Comparison: Generic RFID vs. NFC

RFID encompasses multiple frequency bands and air interface protocols. NFC is specifically an HF technology operating strictly under standardized contactless communication protocols:

| Parameter | Low Frequency (LF) RFID | High Frequency (HF) RFID | Near Field Communication (NFC) | Ultra-High Frequency (UHF) RFID |
| :--- | :--- | :--- | :--- | :--- |
| **Frequency Band** | 125 kHz – 134.2 kHz | 13.56 MHz | **13.56 MHz** | 860 MHz – 960 MHz |
| **Primary Standard** | ISO 11784 / ISO 11785 | ISO/IEC 15693, ISO 14443 | **ISO/IEC 18092, ISO 14443A/B, JIS X 6319-4** | ISO/IEC 18000-6C (EPC Gen2) |
| **Operating Range** | Up to 10 cm | Up to 1 meter (Vicinity) | **Up to 4 – 10 cm (Proximity)** | Up to 10 – 15 meters |
| **Coupling Mechanism**| Inductive (Magnetic $H$-field)| Inductive (Magnetic $H$-field)| **Inductive (Magnetic $H$-field)** | Electromagnetic radiative (Far-field $E$-field) |
| **Data Rates** | ~2 kbps | 26.48 kbps (ISO 15693) | **106, 212, 424, 848 kbps** | 40 – 640 kbps |
| **Operating Modes** | Reader-to-Tag only | Reader-to-Tag only | **1. Reader/Writer<br>2. Card Emulation (PICC)<br>3. Peer-to-Peer (P2P)** | Reader-to-Tag only |
| **Data Format** | Raw ID number | Custom binary / block memory| **Standardized NDEF (Text, URI, MIME)** | EPC data structures |
| **Security / Crypto** | None / basic proprietary | Proprietary (ICODE) | **Hardware Crypto (AES, 3DES, ECC, Crypto1)** | Basic kill/access password |
| **Typical Target** | Animal tagging, car immobilizers | Asset tracking, library books| **Smartphones, contactless payment, IoT pairing** | Logistics pallets, retail apparel |

---

## 4. The Standards Landscape

NFC harmonizes multiple legacy contactless smart card standards into a unified framework governed by the **NFC Forum** and **ISO/IEC**:

```text
                                 +----------------------------------+
                                 |         NFC Forum LLCP /         |
                                 |        SNEP / NDEF Exchange      |
                                 +----------------------------------+
                                                  |
                     +----------------------------+----------------------------+
                     |                                                         |
        +-------------------------+                               +-------------------------+
        |  NFC Forum Tag Types    |                               | ISO/IEC 18092 (NFCIP-1) |
        |   (Types 1, 2, 3, 4, 5) |                               |     Peer-to-Peer        |
        +-------------------------+                               +-------------------------+
                     |                                                         |
         +-----------+--------------------+---------------------+              |
         |                                |                     |              |
+-----------------+              +-----------------+   +-----------------+     |
| ISO/IEC 14443-4 |              | JIS X 6319-4    |   | ISO/IEC 15693   |     |
| (T=CL Protocols)|              | (Sony FeliCa)   |   | (Vicinity Cards)|     |
+-----------------+              +-----------------+   +-----------------+     |
         |                                |                     |              |
+-----------------+                       |                     |              |
| ISO/IEC 14443-3 |                       |                     |              |
| (Anti-collision)|                       |                     |              |
+-----------------+                       |                     |              |
         |                                |                     |              |
         +--------------------------------+---------------------+--------------+
                                          |
                        +-----------------------------------+
                        | 13.56 MHz Inductive Physical Layer|
                        |      (Modulation, Bit Coding)     |
                        +-----------------------------------+
```

1. **ISO/IEC 14443 (Proximity Cards up to 10 cm)**:
   - **Part 1**: Physical characteristics (dimensions, UV/X-ray tolerance).
   - **Part 2**: Radio frequency power and signal interface (13.56 MHz, 100% vs 10% ASK, Modified Miller vs NRZ-L).
   - **Part 3**: Initialization and anti-collision framing (REQA/WUPA, ATQA, Cascade Levels 1/2/3, UID, SAK).
   - **Part 4**: Transmission protocol (T=CL, half-duplex block protocol, RATS/ATS, APDUs).
2. **ISO/IEC 18092 (NFCIP-1 - Near Field Communication Interface and Protocol-1)**:
   - Defines Peer-to-Peer (P2P) mode between Initiator and Target.
   - Active communication (both devices generate RF carrier) and Passive communication (Target uses load modulation).
3. **ISO/IEC 15693 (Vicinity Cards up to 1 meter)**:
   - Lower field strength requirement, wider reading distance. Adopted by NFC Forum as **Type 5 Tag**.
4. **NFC Forum Tag Types**:
   - **Type 1**: Based on ISO 14443A (Innovision Topaz), 96 to 2048 bytes, read/write.
   - **Type 2**: Based on ISO 14443A (NXP NTAG, MIFARE Ultralight), 48 to 1904 bytes, 4-byte pages.
   - **Type 3**: Based on JIS X 6319-4 (Sony FeliCa), 212/424 kbps.
   - **Type 4**: Based on ISO 14443-4 (NXP MIFARE DESFire, Smart Card ICs), APDU block communication, supports file system (CC and NDEF files).
   - **Type 5**: Based on ISO 15693 (NXP ICODE, ST ST25TV).

---

## 5. NFC Transceiver Chipset Archetypes (SPI Controlled)

When architecting an SPI-based NFC solution, hardware engineers choose between two primary silicon archetypes:

```text
=============================================================================================
ARCHETYPE 1: Direct Register-Driven Analog Front-End (e.g., MFRC522, ST25R3916, CLRC663)
=============================================================================================
  +----------+               SPI Bus                +---------------------------------------+
  | Host MCU |  --------------------------------->  | Transceiver IC                        |
  |          |                                      | - Register Bank (0x00 - 0x3F)         |
  |  Full    |  [SPI Byte 0: Addr|R/W]              | - 64B / 512B FIFO                     |
  | Protocol |  [SPI Byte 1..N: Data]               | - Bit Framing Engine (BitFramingReg)  |
  |  Stack   |  <================================>  | - Analog Modulator / Demodulator      |
  |  in C    |                                      | - Auto CRC16_A Calculation            |
  +----------+         IRQ Pin (Event Wakeup)       +---------------------------------------+

=============================================================================================
ARCHETYPE 2: Packet-Oriented Intelligent NFC Controller (e.g., NXP PN532, PN7160)
=============================================================================================
  +----------+               SPI Bus                +---------------------------------------+
  | Host MCU |  --------------------------------->  | Intelligent Controller IC             |
  |          |                                      | - Embedded 8051 / ARM Core + ROM FW   |
  | High-Lvl |  [Preamble, LEN, LCS, TFI, CMD, DCS] | - Full ISO 14443-3/4 State Machine    |
  | Commands |  [Handshake: Status Byte Polling]    | - Native Card Emulation & P2P Target  |
  |  Only    |  <================================>  | - Auto Polling & Anti-Collision Engine|
  +----------+         IRQ Pin (Ready / Data Avail) +---------------------------------------+
```

### Comparative Selection Matrix:

| Feature / Metric | NXP MFRC522 | NXP PN532 | STMicro ST25R3916 | TI TRF7970A |
| :--- | :--- | :--- | :--- | :--- |
| **Silicon Architecture** | Direct Register AFE | Intelligent Controller (8051)| Direct Register High-Perf AFE| Direct Register AFE |
| **SPI Interface Mode** | SPI Mode 0 (CPOL=0, CPHA=0)| SPI Mode 0 (Handshake Protocol)| SPI Mode 1 or Mode 0 | SPI Mode 1 (CPOL=0, CPHA=1)|
| **SPI Bit Order** | **MSB-First** | **LSB-First (Critical Trap!)**| **MSB-First** | **MSB-First** |
| **Max SPI SCLK** | 10 MHz | 5 MHz | 10 MHz (up to 20 MHz streaming)| 10 MHz |
| **Supported Protocols**| ISO 14443A (MIFARE) | ISO 14443A/B, FeliCa, ISO 18092| ISO 14443A/B, FeliCa, ISO 15693| ISO 14443A/B, FeliCa, ISO 15693|
| **Operating Modes** | Reader/Writer only | Reader/Writer, Card Emu, P2P| Reader/Writer, Card Emu, P2P| Reader/Writer, Card Emu, P2P|
| **Max RF Output Power**| ~150 mW | ~200 mW | Up to 1.6 W (Dynamic Power)| ~200 mW |
| **Host Stack Burden** | High (Host runs ISO-3/4) | Low (Chip runs ISO-3/4) | Medium (Host runs ISO-4/NDEF)| High (Host runs ISO-3/4) |
| **Target Applications**| Access control, low-cost tags| Prototyping, P2P, POS terminals| Automotive, EMV payment, NFC POS| Industrial handhelds, asset tracking|

---

## 6. Glossary of Essential NFC Terms

- **PCD (Proximity Coupling Device)**: The NFC reader / writer that generates the 13.56 MHz electromagnetic field and initiates communication.
- **PICC (Proximity Integrated Circuit Card)**: The contactless card, tag, or mobile phone that responds to the PCD via inductive load modulation.
- **VICC (Vicinity Integrated Circuit Card)**: An ISO/IEC 15693 tag capable of communication up to 1 meter from a Vicinity Coupling Device (VCD).
- **H-Field (Magnetic Field Strength)**: Expressed in amperes per meter ($A/m$). ISO 14443 requires the reader to produce between $1.5\text{ A/m}$ and $7.5\text{ A/m}$ across the operating volume.
- **Load Modulation**: The physical process by which a passive tag transmits data back to the reader by modulating its antenna loading impedance, inducing voltage changes on the reader coil.
- **Subcarrier ($f_s$)**: An auxiliary frequency ($f_c / 16 \approx 848\text{ kHz}$) used to separate the card's weak load-modulated uplink signal from the strong 13.56 MHz carrier.
- **REQA / WUPA**: Request Command (7 bits, `0x26`) used to poll for tags in IDLE state; Wake-Up Command (7 bits, `0x52`) used to poll for all tags including those in HALT state.
- **ATQA (Answer to Request Type A)**: 2-byte response from a Type A tag indicating UID size and anti-collision bit framing.
- **UID (Unique Identifier)**: Hardware identifier burned into the tag silicon (Single size = 4 bytes; Double size = 7 bytes; Triple size = 10 bytes).
- **SAK (Select Acknowledge)**: 1-byte response confirming selection of a specific UID and indicating ISO 14443-4 compliance or proprietary memory tag type.
- **RATS / ATS**: Request for Answer to Select / Answer to Select. The activation exchange that transitions an ISO 14443-3 tag into the ISO 14443-4 block protocol (T=CL).
- **NDEF (NFC Data Exchange Format)**: Standardized data container for formatting lightweight records (URLs, vCards, Wi-Fi credentials, text strings) independently of underlying tag silicon.
- **HCE (Host Card Emulation)**: Software-driven card emulation where an application running on the Host MCU acts as a contactless smart card without requiring a hardware Secure Element (SE).
