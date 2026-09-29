# LIN Protocol: Working Mechanism & Electrical Architecture

## 1. Single-Wire Physical Layer Architecture (ISO 17987-4)

The Local Interconnect Network (LIN) physical layer is engineered for extreme cost efficiency and automotive reliability. It utilizes a **single physical copper signal wire** referenced to the vehicle chassis Ground (GND), completely eliminating the cost, weight, and connector complexity of differential pairs.

---

### 1.1 Voltage Levels & Logic Signaling

The LIN bus operates directly at the vehicle battery potential ($V_{BAT} = 12\,\text{V}$ nominal, with a normal operational envelope of **$9.0\,\text{V} \dots 18.0\,\text{V}$** and extended tolerance down to $6.0\,\text{V}$ during engine cranking).

The physical bus supports two electrical states:
1. **Recessive State (Logic 1)**:
   - The bus line is passively pulled up to battery voltage $V_{BAT}$ through termination resistors and reverse-polarity protection diodes.
   - Any voltage on the bus exceeding **$0.8 \times V_{BAT}$** is guaranteed to be detected as Recessive (Logic 1).
   - In a $12\,\text{V}$ system: $V_{REC} \ge 9.6\,\text{V}$ (typical $12.0\,\text{V}$).
2. **Dominant State (Logic 0)**:
   - Actively driven state. An open-drain/open-collector NMOS transistor pulls the bus line towards Ground (GND).
   - Any voltage below **$0.2 \times V_{BAT}$** is guaranteed to be detected as Dominant (Logic 0).
   - In a $12\,\text{V}$ system: $V_{DOM} \le 2.4\,\text{V}$ (typical $0.7\,\text{V} \dots 1.2\,\text{V}$ across the NMOS saturation and diode drops).
   - **Wired-AND Law**: Just as in I2C and CAN, if any single node activates its pull-down driver, the bus transitions to Dominant, overriding any number of nodes in the Recessive state.

```text
  Voltage (V)
   12V (VBAT) ─────────────┐                                ┌──────── Recessive (Logic 1)
                           │                                │
    9.6V (0.8 VBAT) ───────┼─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┼─ ─ ─ ─  Recessive Threshold
                           │   Indeterminate / Transition   │
    2.4V (0.2 VBAT) ───────┼─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┼─ ─ ─ ─  Dominant Threshold
                           │                                │
    GND (0V) ──────────────┴────────────────────────────────┴──────── Dominant (Logic 0)
                           |<--------- Dominant ----------->|
```

### 1.2 Electrical Parameter Matrix (ISO 17987-4)

| Parameter | Symbol | Min | Typical | Max | Unit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Battery Supply Voltage** | $V_{BAT}$ | $9.0$ | $12.0$ | $18.0$ | V |
| **Recessive Bus Voltage** | $V_{bus\_rec}$ | $0.8 \times V_{BAT}$ | $V_{BAT}$ | $V_{BAT}$ | V |
| **Dominant Bus Voltage** | $V_{bus\_dom}$ | $0.0$ | $0.8$ | $0.2 \times V_{BAT}$ | V |
| **Receiver Threshold Center** | $V_{th\_mid}$ | $0.48 \times V_{BAT}$ | $0.5 \times V_{BAT}$ | $0.52 \times V_{BAT}$ | V |
| **Receiver Hysteresis** | $V_{hys}$ | $0.05 \times V_{BAT}$ | $0.1 \times V_{BAT}$ | $0.175 \times V_{BAT}$ | V |
| **Master Pull-Up Resistor** | $R_{master}$ | $900$ | $1000$ ($1\,\text{k}\Omega$) | $1100$ | $\Omega$ |
| **Slave Pull-Up Resistor** | $R_{slave}$ | $27\,\text{k}$ | $30\,\text{k}\Omega$ | $33\,\text{k}$ | $\Omega$ |
| **Total Bus Capacitance** | $C_{bus}$ | $1.0$ | $4.7$ | $10.0$ | nF |
| **Controlled Slew Rate** | $SR$ | $1.0$ | $2.0$ | $3.0$ | $\text{V}/\mu\text{s}$ |

---

## 2. Asymmetric Termination & Transceiver Architecture

### 2.1 The Asymmetric Termination Scheme

To establish reliable pull-up biasing without requiring active controllers at every node, LIN uses a strictly **asymmetric termination architecture**:

```text
       +12V (VBAT)                              +12V (VBAT)
           │                                        │
          ─┴─ Blocking Diode                       ─┴─ Blocking Diode
          ▲─┬ (1N4148 / BAS21)                     ▲─┬ (1N4148 / BAS21)
            │                                        │
           [ ] R_master (1kΩ, 1%)                   [ ] R_slave (30kΩ, 1%)
            │                                        │
   LIN ─────┴──────────────────────────────┬─────────┴──────────────────────── Bus
            │                              │
         ┌──┴───────────────┐           ┌──┴───────────────┐
         │   Master Node    │           │    Slave Node    │ (Up to 15 Slaves)
         │ (Body Controller)│           │ (Mirror / Door)  │
         └──────────────────┘           └──────────────────┘
```

- **Master Node Termination**: Features a **$1\,\text{k}\Omega \pm 1\%$** pull-up resistor in series with a silicon blocking diode. The diode prevents the vehicle battery from back-feeding into the master ECU through the bus in the event of an ECU ground disconnection.
- **Slave Node Termination**: Features a high-impedance **$30\,\text{k}\Omega \pm 1\%$** pull-up resistor in series with a blocking diode.
- **Total Bus Equivalent Resistance ($R_{bus}$)**:
  With $N$ slave nodes connected in parallel on the bus, the total effective pull-up resistance is:
  $$R_{bus} = R_{master} \parallel \left(\frac{R_{slave}}{N}\right) = 1000\,\Omega \parallel \left(\frac{30,000\,\Omega}{N}\right)$$
  For a typical 8-slave network:
  $$R_{bus} = 1000 \parallel \left(\frac{30000}{8}\right) = 1000 \parallel 3750 = \frac{1000 \times 3750}{4750} \approx 789.5\,\Omega$$
  The ISO standard mandates that the total combined bus pull-up resistance remain within **$500\,\Omega \le R_{bus} \le 1000\,\Omega$**.

---

### 2.2 Transceiver Architecture & Slew-Rate Shaping

A LIN Transceiver (e.g., NXP `TJA1021`, Microchip `MCP2003`, TI `TLIN1029`) interfaces the digital $3.3\,\text{V}$ or $5\,\text{V}$ UART pins (`TXD`, `RXD`) of a microcontroller to the $12\,\text{V}$ single-wire bus.

```text
                     +12V (VBAT)
                        │
                        ├───────[ 1kΩ / 30kΩ ]───|◀──┐
                        │                            │
             ┌──────────┴────────────────────────────┴─────┐
             │              LIN Transceiver                │
             │                                             │
 MCU TXD ───>│ Slew-Rate Controlled ───┐                   ├──── LIN Bus (12V)
             │ Driver Stage            │                   │
             │                         ▼ [NMOS]            │
             │                         │                   │
             │                        GND                  │
             │                                             │
 MCU RXD <───┤ Receiver with Schmitt Trigger Hysteresis    │
             │                                             │
 MCU INH <───┤ Inhibit / Low-Power Voltage Regulator Control│
             │                                             │
             │ TXD Dominant Timeout Watchdog (> 40ms)      │
             └─────────────────────────────────────────────┘
```

#### Transceiver Subsystems:
1. **Wave-Shaped Slew-Rate Driver**:
   - To eliminate high-frequency radio frequency interference (RFI) without requiring expensive shielded cabling, the output NMOS driver limits the edge transition rates to **$1.0 \dots 3.0\,\text{V}/\mu\text{s}$**.
   - The resulting trapezoidal waveform rounds off sharp square-wave corners, suppressing emissions in the AM/FM broadcast bands.
2. **TXD Dominant Timeout Clamp**:
   - If an MCU crashes or a GPIO shorts to Ground, pulling `TXD` permanently LOW, the bus would be held Dominant indefinitely, completely paralyzing the sub-network.
   - The transceiver contains an internal hardware watchdog ($t_{dom\_to} \approx 40\,\text{ms} \dots 50\,\text{ms}$). If `TXD` remains LOW longer than $t_{dom\_to}$, the NMOS driver is automatically shut off, returning the bus to Recessive.
3. **Schmitt Trigger Receiver**:
   - Filters noise spikes and ensures crisp digital transitions on `RXD` despite high ground shifts between vehicle door panels and the central body controller.

---

## 3. Master-Slave Deterministic Scheduling & State Machine

Unlike CAN (which is event-driven and uses non-destructive bitwise arbitration), LIN is **strictly deterministic**:
- **Single-Master Authority**: Only the Master node is permitted to initiate communication.
- **No Bus Contention**: Slaves never transmit spontaneously. Slaves only transmit data when the Master transmits a header containing their assigned **Protected Identifier (PID)**.
- **Collision-Free Operation**: Because only one node is designated to respond to any given PID, physical data collisions are physically impossible during normal scheduled traffic.

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                       Cyclic Master Schedule Table                          │
 ├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
 │ Time Slot 1     │ Time Slot 2     │ Time Slot 3     │ Time Slot 4           │
 │ (10 ms)         │ (10 ms)         │ (20 ms)         │ (10 ms)               │
 ├─────────────────┼─────────────────┼─────────────────┼───────────────────────┤
 │ PID 0x10        │ PID 0x22        │ PID 0x3C        │ PID 0x15              │
 │ Master -> Door  │ Mirror -> Master│ Master Request  │ Master -> Window      │
 │ (Lock Command)  │ (Position Data) │ (Diagnostics)   │ (Up/Down Command)     │
 └─────────────────┴─────────────────┴─────────────────┴───────────────────────┘
 |<--------------------------- Master Frame Period ---------------------------->|
```

### 3.1 Schedule Table Execution Rules
- The Master executes an internal timer defining fixed **Frame Slots** (e.g., $10\,\text{ms}$, $20\,\text{ms}$).
- Each slot must be sized to accommodate the **Maximum Frame Time ($T_{frame\_max}$)** plus an engineer-specified jitter margin.
- If a slave is disconnected or unpowered, the Master sends the header, observes no response, and calmly waits for the slot timer to expire before transmitting the next header. The remaining network continues uninterrupted!

---

## 4. Sleep & Wake-Up Protocol

To prevent parasitic vehicle battery drain when the vehicle ignition is turned off, LIN nodes support an ultra-low-power **Sleep Mode** drawing less than **$10\,\mu\text{A}$**.

```text
           Master Sends Sleep Frame
             (ID 0x3C, Byte 0 = 0x00)
    ACTIVE ─────────────────────────────> SLEEP MODE (< 10µA)
      ▲                                       │
      │                                       │ Any Node Drives Wake-Up Pulse
      │                                       │ (250µs to 5ms Dominant)
      └───────────────────────────────────────┘
```

### 4.1 Going to Sleep
Nodes transition to Sleep Mode under two conditions:
1. **Master Request Sleep Frame**: The Master broadcasts an unconditional Master Request diagnostic frame ($ID = 0x3C$, $DLC = 8$) where **Byte 0 is set to `0x00`** and bytes $1 \dots 7$ are set to `0xFF`. Upon receiving this command, all slaves immediately shut off their internal peripherals and enter deep sleep.
2. **Bus Inactivity Timeout**: If the bus remains constantly Recessive without any transitions for **$T_{bus\_inactivity} \ge 4.0\,\text{seconds}$**, all nodes automatically enter sleep mode.

### 4.2 The Wake-Up Pulse
Any node on the network (either the Master or an event-triggered Slave, such as a user pressing a door-handle button) can wake the bus:
- The waking node pulls the bus **Dominant for $250\,\mu\text{s} \le t_{wake} \le 5.0\,\text{ms}$**.
- Transceivers on all connected sleeping nodes detect the dominant pulse, assert their `INH` pin to power up the microcontroller's low-dropout (LDO) regulator, and wake the CPU.
- **Wake-Up Retry Logic**: If the Master does not begin transmitting frame headers within **$150\,\text{ms} \dots 250\,\text{ms}$** of the wake-up pulse, the slave may issue another wake-up pulse (up to 3 times before pausing for a $1.5\,\text{s}$ backoff period).

---

## 5. Node Configuration & Identification (LIN 2.1 / ISO 17987)

To eliminate the need for hardwired DIP switches or unique firmware builds for identical hardware modules (e.g., Left vs Right mirror actuators), LIN 2.1 introduces standardized **Node Configuration Services**.

```text
 ┌─────────────────────────────────────────────────────────────┐
 │                 Slave Node Identification                   │
 ├─────────────────────────┬─────────────────┬─────────────────┤
 │ Parameter               │ Field Size      │ Description     │
 ├─────────────────────────┼─────────────────┼─────────────────┤
 │ **NAD (Node Address)**  │ 8 bits (1 Byte) │ Unique diagnostic address ($0x01 \dots 0x7E$)│
 │ **Supplier ID**         │ 16 bits (2 Bytes) Assigned by LIN Consortium (e.g., VVDN)│
 │ **Function ID**         │ 16 bits (2 Bytes) Identifies function (e.g., Door Mirror)│
 │ **Variant ID**          │ 8 bits (1 Byte) │ Hardware/firmware version identifier│
 └─────────────────────────┴─────────────────┴─────────────────┘
```

### 5.1 Standard Node Configuration Services
The Master configures slaves dynamically during initial vehicle end-of-line (EOL) flash or runtime initialization via diagnostic frames ($0x3C / 0x3D$):
- **Assign NAD ($0xB0$)**: Replaces a temporary or default Node Address with a unique runtime NAD.
- **Assign Frame Identifier ($0xB1$)**: Configures which Protected Identifiers (PIDs) the slave should respond to.
- **Conditional Change NAD ($0xB3$)**: Changes the NAD of a slave only if its Supplier ID and Function ID match specified criteria, allowing auto-addressing of daisy-chained modules.
- **Save Configuration ($0xB6$)**: Instructs the slave to commit its assigned NAD and PID tables into internal non-volatile EEPROM/Flash.
