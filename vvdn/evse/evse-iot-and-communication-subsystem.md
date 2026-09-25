# EVSE IoT & Communication Subsystem: Gateway Architecture, OCPP 1.6J/2.0.1 & Cloud Connectivity

This document provides a comprehensive technical guide to the **IoT Gateway, Networking Interfaces, Cloud Protocols, and Edge Communication** of the EVSE Low Voltage Controller Board. It details the dual-processor safety topology, wireless/wired network interfaces, OCPP 1.6-J and 2.0.1 message flows over Secure WebSockets, Dynamic Load Management (DLM) over RS-485 Modbus, and secure dual-bank Over-the-Air (OTA) firmware updates.

---

## 1. Dual-Processor System Topology (Safety vs. Connectivity)

Industrial and commercial EVSE controller boards split operations between two specialized computing domains:

```text
 ┌────────────────────────────────────────────────────────┐     ┌────────────────────────────────────────────────────────┐
 │       REAL-TIME SAFETY MICROCONTROLLER (MCU)           │     │            IoT APPLICATION PROCESSOR / SoM             │
 │        (e.g., STM32G4 / STM32F4 / LPC5500)             │     │      (e.g., ESP32-S3 / NXP i.MX6ULL / i.MX8M)          │
 │                                                        │     │                                                        │
 │  • IEC 61851-1 Control Pilot PWM generation (1 kHz)    │     │  • Embedded Linux / FreeRTOS Network Stack             │
 │  • Diode check & ADC Pilot Voltage Peak Sampling       │     │  • Wi-Fi 802.11 b/g/n & BLE 5.0 Stack                  │
 │  • Proximity Pilot (PP) cable resistor decoding        │     │  • 4G LTE Cat-1 / NB-IoT PPP Cellular Engine           │
 │  • 6mA DC / 30mA AC RCM hardware trip loop (<10 ms)    │     │  • 10/100 Mbps Ethernet MAC/PHY                        │
 │  • Main Contactor PWM Economizer Drive                 │     │  • OCPP 1.6-J / OCPP 2.0.1 JSON-over-WebSockets Engine │
 │  • Motorized Connector Lock H-Bridge Control           │     │  • TLS 1.3 / X.509 Cryptographic Security Layer        │
 │  • Precision Energy Metering DSP Sampling              │     │  • Local Web Server & Bluetooth BLE Commissioning App  │
 │  • Hardware Watchdog & Fail-Safe E-Stop Loop           │     │  • Dual-Bank A/B Secure OTA Firmware Manager           │
 └───────────────────────────┬────────────────────────────┘     └───────────────────────────┬────────────────────────────┘
                             │                                                              │
                             └────────────── High-Speed Isolated SPI / UART ────────────────┘
                                            (Protected CRC-16 Command Framing)
```

### Why a Dual-Processor Architecture is Mandatory:
1. **Safety Isolation (IEC 61851-1)**: Fault trips (such as $6\,\text{mA}$ DC residual current or pilot disconnect) require contactor de-energization within **$< 10\text{--}40\,\text{ms}$**. A general-purpose OS (such as Linux) or a Wi-Fi/cellular stack undergoing TCP retransmissions or garbage collection can introduce non-deterministic latencies exceeding hundreds of milliseconds.
2. **Cybersecurity Containment**: If the IoT network interface is subjected to an external DDoS attack, buffer overflow, or unauthorized network intrusion, the real-time MCU continues to run its hardware safety state machine independently, preventing hazardous electrical conditions.
3. **Low-Power Standby**: During idle nighttime hours, the high-power application processor can enter deep sleep, leaving the low-power MCU consuming $< 10\,\text{mW}$ while monitoring for a vehicle plug-in event.

---

## 2. Multi-Bearer Physical Connectivity Subsystem

To guarantee seamless connectivity in diverse deployment environments (residential garages, underground parking basements, highway charging hubs), the controller board incorporates four primary network bearers:

```text
                                 COMMUNICATIONS INTERFACE MATRIX
  ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
  │     Wi-Fi & BLE       │  │    4G LTE Cellular    │  │    Wired Ethernet     │  │   RS-485 (Modbus)     │
  │ • 802.11 b/g/n (2.4G) │  │ • Cat-1 / NB-IoT      │  │ • 10/100 Mbps RJ45    │  │ • Half-Duplex Balanced│
  │ • BLE 5.0 Provisioning│  │ • Nano-SIM / eSIM     │  │ • RMII PHY + Magnetics│  │ • Dynamic Load Balance│
  └───────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘
              │                          │                          │                          │
              ▼                          ▼                          ▼                          ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │                           IoT APPLICATION PROCESSOR NETWORK ROUTING LAYER                              │
  └────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Wi-Fi & Bluetooth Low Energy (BLE 5.0)
- **Wi-Fi Station Mode (STA)**: Connects to the site's local $2.4\,\text{GHz}$ WLAN for internet access and OCPP transport.
- **Wi-Fi Soft-AP Mode**: Broadcasts a temporary setup SSID (e.g., `VVDN-EVSE-Setup-9A4F`) for initial unboxing configuration without physical access.
- **BLE 5.0 Commissioning GATT Service**: Allows an electrician or installer to connect via a mobile app to:
  - Configure grid parameters (Maximum panel current limit, Single vs. Three-phase).
  - Push local Wi-Fi SSID and WPA2/WPA3 credentials.
  - Set the Central System URL (`wss://ocpp.operator.com/ocpp16/CP1234`).
  - Read active hardware diagnostic logs and test contactor actuation.

### 2.2 4G LTE Cellular Modem (Cat-1 / NB-IoT / LTE-M)
- **Modem Hardware**: Quectel EC200U / BG95, SIMCom SIM7600, or Telit ME910.
- **Interfacing**: Connected to the application processor via high-speed UART ($921,600\,\text{bps}$) or USB 2.0 High-Speed.
- **Software Integration**: Uses Point-to-Point Protocol (PPP) daemon or internal TCP/IP stack driven via 3GPP AT commands.
- **Fallback Hierarchy**: Automatic failover from Ethernet $\to$ Wi-Fi $\to$ Cellular to maintain constant billing connectivity.

### 2.3 Wired Industrial Ethernet (10/100 Mbps)
- **Hardware**: Dedicated RMII PHY (e.g., Microchip LAN8720A or KSZ8081) coupled to an integrated RJ45 jack with built-in isolation magnetics ($1.5\,\text{kV}$ dielectric isolation).
- Ideal for commercial fleets, multi-story carparks with no cellular reception, and heavy EMI industrial environments.

### 2.4 RS-485 Modbus RTU (Dynamic Load Management)
- **Physical Layer**: Half-duplex differential RS-485 transceiver (e.g., TI SN65HVD72 or MAX485) with TVS surge protection.
- **Purpose**: Communicates with external energy meters (e.g., Eastron SDM630, Schneider iEM3000) installed at the building's main electrical service panel.
- **Dynamic Load Balancing (DLB)**: If total household or building power exceeds the utility supply threshold (e.g., $63\,\text{A}$), the controller polls the smart meter via Modbus RTU every $1.0\,\text{second}$ and throttles the EVSE charging current proportionally to prevent tripping the main utility fuse.
- **Solar Diversion (Zero Grid Export)**: Reads rooftop solar inverter generation and adjusts charging current so the vehicle charges exclusively on surplus PV power.

---

## 3. OCPP (Open Charge Point Protocol) Architecture

**OCPP** is the global de facto open standard for EVSE-to-Cloud communication managed by the Open Charge Alliance (OCA). The LV controller board implements both **OCPP 1.6-J (JSON)** and **OCPP 2.0.1**.

### 3.1 Transport & Security Layer
- **Transport**: JSON framing over **WebSockets** (`ws://` unencrypted or `wss://` encrypted).
- **Security Profile (OCPP Security Whitepaper)**:
  - **Security Profile 1**: Unencrypted HTTP/WebSocket with Basic HTTP Authentication (Username/Password).
  - **Security Profile 2**: TLS 1.2 / TLS 1.3 encryption with HTTP Basic Authentication.
  - **Security Profile 3 (Enterprise)**: Mutual TLS (mTLS) with client and server X.509 cryptographic certificates stored in an onboard secure element (e.g., ATECC608A).

---

### 3.2 Canonical OCPP Message Framing

OCPP messages over WebSockets are formatted as JSON arrays with four fundamental message types:
1. **CALL (`MessageTypeId = 2`)**: `[2, "<UniqueMessageId>", "<ActionName>", {<PayloadJson>}]`
2. **CALLRESULT (`MessageTypeId = 3`)**: `[3, "<UniqueMessageId>", {<PayloadJson>}]`
3. **CALLERROR (`MessageTypeId = 4`)**: `[4, "<UniqueMessageId>", "<ErrorCode>", "<ErrorDescription>", {<Details>}]`

---

### 3.3 End-to-End Charging Session Message Lifecycle

The sequence below illustrates a complete user-authenticated charging transaction:

```text
   VEHICLE (OBC)           EVSE CONTROLLER BOARD                     CLOUD CSMS (BACKEND)
        │                            │                                         │
        │                            ├───── [2, "msg01", "BootNotification"] ─►│
        │                            │◄──── [3, "msg01", {status: Accepted}] ──┤
        │                            │                                         │
        │                            ├───── [2, "msg02", "StatusNotification", │
        │                            │       {status: "Available"}] ──────────►│
        │                            │◄──── [3, "msg02", {}] ──────────────────┤
        │                            │                                         │
        │ User taps RFID Card        │                                         │
        │───────────────────────────►│                                         │
        │                            ├───── [2, "msg03", "Authorize",          │
        │                            │       {idTag: "B4A198F0"}] ────────────►│
        │                            │◄──── [3, "msg03", {status: Accepted}] ──┤
        │                            │                                         │
        │ Cable plugged into vehicle │                                         │
        │ (CP transitions to State B)│                                         │
        │ Motorized lock engages     │                                         │
        │ Vehicle asserts State C    │                                         │
        │ (Charging requested)       │                                         │
        │ Contactor snaps CLOSED     │                                         │
        │                            ├───── [2, "msg04", "StartTransaction",   │
        │                            │       {connectorId: 1, idTag: "...",    │
        │                            │        meterStart: 12450, ...}] ───────►│
        │                            │◄──── [3, "msg04", {transactionId: 402}]─┤
        │                            │                                         │
        │◄════ POWER TRANSFER ══════►│                                         │
        │      (32A Active)          │                                         │
        │                            │ (Every 30s Periodic Meter Stream)       │
        │                            ├───── [2, "msg05", "MeterValues",        │
        │                            │       {transactionId: 402, values: [    │
        │                            │        {Power: 21950, Current: 32.0,    │
        │                            │         Energy: 13120}]}] ─────────────►│
        │                            │◄──── [3, "msg05", {}] ──────────────────┤
        │                            │                                         │
        │ Vehicle completes charge   │                                         │
        │ (CP transitions to State B)│                                         │
        │ Contactor opens            │                                         │
        │ Lock disengages            │                                         │
        │                            ├───── [2, "msg06", "StopTransaction",    │
        │                            │       {transactionId: 402,              │
        │                            │        meterStop: 14820,                │
        │                            │        reason: "EVDisconnected"}] ─────►│
        │                            │◄──── [3, "msg06", {}] ──────────────────┤
        │                            │                                         │
        │                            ├───── [2, "msg07", "StatusNotification", │
        │                            │       {status: "Available"}] ──────────►│
        │                            │◄──── [3, "msg07", {}] ──────────────────┤
```

---

### 3.4 Key OCPP Actions & Payload Anatomy

#### 1. `BootNotification`
Sent on initial power-up or reboot to register station identity with the cloud:
```json
[2, "10001", "BootNotification", {
  "chargePointVendor": "VVDN Technologies",
  "chargePointModel": "VVDN-AC-22KW-PRO",
  "chargePointSerialNumber": "VVDN-EVSE-2026-0042",
  "firmwareVersion": "v2.4.12-secure",
  "iccid": "89014103211118510720",
  "imsi": "310410123456789",
  "meterType": "ADE7953-MID-Class1"
}]
```

#### 2. `MeterValues`
Streams real-time power, energy, voltage, and SoC telemetry for billing and smart charging algorithms:
```json
[2, "10005", "MeterValues", {
  "connectorId": 1,
  "transactionId": 402,
  "meterValue": [{
    "timestamp": "2026-09-25T12:55:00Z",
    "sampledValue": [
      {"value": "21950", "context": "Sample.Periodic", "measurand": "Power.Active.Import", "unit": "W"},
      {"value": "32.1", "context": "Sample.Periodic", "measurand": "Current.Import", "unit": "A", "phase": "L1"},
      {"value": "31.9", "context": "Sample.Periodic", "measurand": "Current.Import", "unit": "A", "phase": "L2"},
      {"value": "32.0", "context": "Sample.Periodic", "measurand": "Current.Import", "unit": "A", "phase": "L3"},
      {"value": "230.4", "context": "Sample.Periodic", "measurand": "Voltage", "unit": "V", "phase": "L1-N"},
      {"value": "13120", "context": "Sample.Periodic", "measurand": "Energy.Active.Import.Register", "unit": "Wh"}
    ]
  }]
}]
```

---

## 4. User Authentication: RFID / NFC Subsystem

The controller board features an on-board or external **13.56 MHz RFID / NFC Transceiver** (e.g., NXP PN532, MFRC522, or STMicroelectronics ST25R3916):
- **Supported Standards**: ISO/IEC 14443 Type A/B, MIFARE Classic/Ultralight, MIFARE DESFire EV1/EV2/EV3, and ISO 15693.
- **Host Interface**: Interfaced to the controller over SPI or UART.
- **Card Tap Flow**:
  1. Card presence detected via low-power inductive card detection (LPCD) polling every $200\,\text{ms}$.
  2. Transceiver reads the card's 4-byte or 7-byte Unique Identifier (UID / CSN).
  3. Controller formats the hex UID as an OCPP `idTag` (e.g. `04A2B3C4D5E6F7`).
  4. Controller queries the CSMS via `Authorize(idTag)` or checks the local offline whitelist (Local Authorization List).
  5. If valid, an audible confirmation beep sounds, the RGB LED changes to Cyan, and the session begins.

---

## 5. High-Level Communication: ISO 15118 & Plug & Charge (PnC)

For next-generation smart charging and DC fast chargers, the simple analog PWM pilot is augmented with digital communication via **ISO 15118**:

```text
 ┌────────────────────────────────────────────────────────┐
 │           ISO 15118 GREENPHY PLC MODEM                 │
 │            (Qualcomm QCA7000 / QCA7005)                │
 └───────────────────────────┬────────────────────────────┘
                             │ (Tx/Rx HF Signals 2-30 MHz)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │      Passive High-Pass Analog Matching Network         │
 │           (Blocking 1 kHz PWM & ±12V DC)               │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ─────────────────────────[ CP Wire ]───────────────────── (Coupled to Control Pilot)
```

- **HomePlug GreenPHY PLC**: Modulates digital IP traffic (2–30 MHz OFDM) directly onto the existing Control Pilot wire.
- **Plug & Charge (PnC)**:
  - Eliminates RFID cards and smartphone apps.
  - The vehicle and EVSE establish an automated TLS 1.3 cryptographic session.
  - The vehicle transmits its digitally signed contract certificate.
  - The EVSE validates the certificate with the mobility operator clearing house and automatically begins billing.
- **Smart Grid V2G (Vehicle-to-Grid)**: Coordinates dynamic bidirectional power flow, allowing the EV battery to feed energy back into the grid during peak demand.

---

## 6. Secure Dual-Bank Over-The-Air (OTA) Firmware Updates

To prevent field bricking during firmware upgrades across thousands of deployed chargers, the controller board implements a robust **A/B Dual-Bank Partitioning Architecture**:

```text
  Internal / External SPI Flash Memory (32 MB / 64 MB)
 ┌───────────────────────┬───────────────────────┬───────────────────────┬───────────────────────┐
 │   Secure Bootloader   │   Bank A (Active)     │   Bank B (Candidate)  │   Non-Volatile Storage│
 │   (Immutable ROM)     │   Firmware v2.4.12    │   New Firmware v2.5.0 │   • Meter Calibration │
 │   • ECDSA Signature   │   • Verified OK       │   • Pending Validation│   • OCPP Offline Cache│
 │   • Rollback Watchdog │   • Running Now       │   • Written via OTA   │   • Certs & Keys      │
 └───────────────────────┴───────────────────────┴───────────────────────┴───────────────────────┘
```

### OTA Update State Machine:
1. **Download Phase**: The CSMS issues an OCPP `UpdateFirmware(location: "https://...")` command. The controller downloads the cryptographically signed binary image to the inactive Bank (Bank B).
2. **Signature Verification**: The bootloader checks the image against the manufacturer's public key using **ECDSA SHA-256**. If corrupted or tampered with, the update is rejected.
3. **Execution & Trial Boot**: The bootloader sets the boot vector to Bank B and starts a hardware watchdog timer ($180\,\text{seconds}$).
4. **Self-Test & Confirmation**: The new firmware must successfully:
   - Initialize the safety MCU and CP op-amp circuits.
   - Establish network connectivity (Wi-Fi/Cellular).
   - Reconnect to the CSMS and receive an accepted `Heartbeat`.
5. **Commit or Rollback**:
   - If self-tests pass within $180\,\text{s}$, Bank B is permanently marked as `Active`.
   - If the firmware crashes, freezes, or fails to connect, the hardware watchdog resets the processor. The bootloader detects the failed boot counter and **automatically reverts to Bank A**, restoring full operational status.
