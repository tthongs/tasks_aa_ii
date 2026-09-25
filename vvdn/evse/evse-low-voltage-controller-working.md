# EVSE Low Voltage Controller Board: Working Mechanism, Electrical Principles & Hardware Subsystems

This document provides a comprehensive, engineering-grade breakdown of the **IoT-based Low Voltage (LV) Controller Board** in modern Electric Vehicle Supply Equipment (EVSE). It covers the physical and electrical working principles of the power management unit, the Control Pilot (CP) and Proximity Pilot (PP) state machines, safety interlocks, contactor actuation, precision energy metering, and fault-trip mechanics.

---

## 1. System Overview & Electrical Domain Boundaries

In an EVSE (Level 2 AC Charger or AC/DC Smart Charging Station), the Low Voltage Controller Board acts as the **central supervisory and control unit**. It operates within the **Safety Extra Low Voltage (SELV / PELV)** regime, physically and galvanically isolated from the high-power AC grid mains ($230\,\text{V} / 400\,\text{V} \text{ AC}$).

```text
  MAINS DOMAIN (CAT III / High Voltage)           ISOLATION BARRIER           SELV CONTROLLER DOMAIN (Low Voltage)
 ┌──────────────────────────────────────┐     ┌──────────────────────┐     ┌───────────────────────────────────────┐
 │                                      │     │                      │     │                                       │
 │  Grid AC In (L1, L2, L3, N)          │     │  Galvanic Clearance  │     │  Real-Time Safety MCU (Cortex-M4)     │
 │       │                              │     │   (Reinforced >=6mm) │     │   • 1 kHz ±12V Control Pilot DAC/PWM  │
 │       ▼                              │     │                      │     │   • Proximity Pilot ADC Sampler       │
 │  Main 4-Pole Power Contactor         │◄────┼── Optocoupler Driver ┼─────┤   • Contactor Gate Control & Economizer│
 │       │                              │     │                      │     │   • Hardware Fault Interlock Engine   │
 │       ▼                              │     │                      │     │                                       │
 │  Residual Current Sensor (Fluxgate)  ├─────┼── Differential Line ─┼────►│   • 6mA DC / 30mA AC Comparator Trip  │
 │       │                              │     │                      │     │                                       │
 │  Current Transformers (L1..L3)       ├─────┼── Magnetic Coupling ─┼────►│  Energy Metering AFE (SPI / UART)     │
 │       │                              │     │                      │     │                                       │
 │  Auxiliary Power SMPS (230V -> 12V)  ├─────┼── Isolated Flyback ──┼────►│  Power Management Unit (PMU)          │
 │       │                              │     │                      │     │   • +12V, +5V, +3.3V, -12V Rails      │
 │       ▼                              │     │                      │     │   • Supercap "Last-Gasp" Backup       │
 │  Type 2 / Type 1 Charging Socket     │     │                      │     │                                       │
 └──────────────────────────────────────┘     └──────────────────────┘     └───────────────────────────────────────┘
```

### Primary Responsibilities of the LV Controller Board:
1. **Pilot Handshaking**: Negotiates charging readiness and current capacity with the On-Board Charger (OBC) of the electric vehicle according to **IEC 61851-1** and **SAE J1772**.
2. **Cable Verification**: Identifies the current rating of the detachable Type 2 charging cable via **IEC 62196-2 Proximity Pilot**.
3. **Safety Protection**: Continuously evaluates DC/AC residual leakage currents, earthing continuity, terminal temperatures, and contactor welding.
4. **Contactor Control**: Powers the contactor coil to connect or disconnect grid power safely at zero-current or under fault conditions.
5. **Revenue Metering**: Measures electrical consumption (kWh) with Class 1.0 or Class 0.5 accuracy for billing.
6. **IoT Cloud Connectivity**: Transmits telemetry, billing data, and station health to cloud servers via **OCPP 1.6-J / 2.0.1**.

---

## 2. Power Management Unit (PMU) & Bipolar Rail Generation

The Low Voltage Controller Board requires multiple regulated DC voltage rails to operate its mixed-signal analog, digital, and communication circuitry:

```text
  Auxiliary SMPS (+12V DC In) ──┬──────────────────────────────────────────► +12V Contactor & Solenoid Rail
                                │
                                ├──► [Inverting Charge Pump / Buck-Boost] ─► -12V Control Pilot Negative Rail
                                │
                                ├──► [High-Efficiency Step-Down Buck] ────► +5V Rail (Relays, RCM, Metering)
                                │                                                  │
                                │                                                  ▼
                                │                                    [Low-Noise LDO / Buck Regulator]
                                │                                                  │
                                │                                                  ▼
                                │                                           +3.3V Rail (MCU, Flash, IoT SoM)
                                │
                                └──► [Supercapacitor Charging & Booster] ──► "Last-Gasp" Power-Fail Backup
```

### 2.1 Voltage Rail Allocation

| Rail | Nominal Voltage | Ripple Limit | Target Subsystems | Typical Current |
| :--- | :--- | :--- | :--- | :--- |
| **$+12\,\text{V}$** | $+12.0\,\text{V} \pm 5\%$ | $< 100\,\text{mV}$ | Main Contactor Coil, Motorized Lock H-Bridge, CP Positive Op-Amp Rail | $1.5\,\text{A}$ (Peak pull-in) / $300\,\text{mA}$ (Hold) |
| **$-12\,\text{V}$** | $-12.0\,\text{V} \pm 5\%$ | $< 50\,\text{mV}$ | CP Negative Op-Amp Rail (Diode Fault Detection) | $50\,\text{mA}$ |
| **$+5\,\text{V}$** | $+5.0\,\text{V} \pm 2\%$ | $< 30\,\text{mV}$ | RCM Leakage Sensor, Energy Metering AFE, Optical Isolators, Pilot Relays | $500\,\text{mA}$ |
| **$+3.3\,\text{V}$** | $+3.3\,\text{V} \pm 1\%$ | $< 15\,\text{mV}$ | Primary Safety MCU, 4G Cellular Modem, Wi-Fi/BLE SoC, SPI Flash, Sensors | $1.2\,\text{A}$ (with cellular burst) |

### 2.2 The Bipolar $\pm 12\,\text{V}$ Rail Generation for Control Pilot
IEC 61851-1 requires the Control Pilot to swing between **$+12\,\text{V}$** (State A) and **$-12\,\text{V}$** (State F / negative PWM envelope). 

Because the auxiliary supply only provides positive $+12\,\text{V}$, the controller board integrates an **Inverting Charge Pump** (e.g., TI LM27762 or Microchip TC7662) or an **Inverting Buck-Boost Converter** (e.g., TI TPS63700):
- Converts $+12\,\text{V}$ input into a regulated, low-noise $-12.0\,\text{V}$ output.
- Powers the negative supply pin ($V_{EE}$) of the rail-to-rail Control Pilot op-amp buffer.

### 2.3 Supercapacitor "Last-Gasp" Circuit
In commercial and public charging networks, if the grid power fails or an upstream circuit breaker trips, the EVSE must immediately report the loss-of-power event to the cloud management platform (CSMS) before dying.
- The LV board incorporates a **$5.5\,\text{V}, 1.0\text{--}1.5\,\text{F}$ supercapacitor** charged continuously via a current-limited diode path from $+5\,\text{V}$.
- A power-fail comparator detects when $+12\,\text{V}$ drops below $10.0\,\text{V}$ and fires an Non-Maskable Interrupt (NMI) to the MCU.
- The MCU halts non-essential peripherals, triggers the boost regulator to power the cellular modem/Wi-Fi from the supercapacitor, sends an **OCPP `StatusNotification(Faulted, PowerLoss)`** message, cleanly saves the active energy meter transaction register to EEPROM/FRAM, and shuts down safely.

---

## 3. Control Pilot (CP) Circuit & State Machine (IEC 61851-1 / SAE J1772)

The **Control Pilot (CP)** line is the primary analog communication channel between the EVSE controller board and the electric vehicle's On-Board Charger (OBC). It operates through a shared single-ended line referenced to Protective Earth (PE).

### 3.1 Equivalent Circuit Topology

```text
            EVSE LOW VOLTAGE CONTROLLER BOARD                      VEHICLE (OBC) ON-BOARD INTERFACE
       ┌────────────────────────────────────────┐             ┌────────────────────────────────────────┐
       │                                        │             │                                        │
       │  Bipolar Buffer (Op-Amp)               │             │             Forward Diode D1           │
       │   +12V Rail                            │             │                 ┌──►|──┐               │
       │     │                                  │             │                 │      │               │
       │   ┌─┴─┐                                │   CP Wire   │                 │     [R2] (2.74 kΩ)   │
PWM ──►│   │   ├───[ R1: 1.0 kΩ ]───────────────┼─────────────┼─────────────────┤      │               │
       │   └─┬─┘       (1% Precision)           │             │                 │      │               │
       │     │                                  │             │                 ├──[S2]┤               │
       │   -12V Rail                            │             │                 │      │               │
       │                                        │             │                 │     [R3] (1.3 kΩ)    │
       │  Analog Peak Detector & ADC            │             │                 │      │               │
       │       ┌────────────────┐               │             │                 ▼      ▼               │
       │  ◄────┤ ADC Sampler    │◄──────────────┤             │             Vehicle Ground (Chassis)   │
       │       └────────────────┘               │             │                                        │
       │                                        │             │                                        │
       │  Protective Earth (PE) ────────────────┼─────────────┼───────────── Vehicle Chassis           │
       └────────────────────────────────────────┘             └────────────────────────────────────────┘
```

1. **EVSE Internal Resistance ($R_1$)**: Exactly $1000\,\Omega \pm 1\%$, connecting the op-amp output to the CP pin.
2. **Vehicle Diode ($D_1$)**: A standard silicon or Schottky diode that allows current to flow only during the positive half-cycle of the PWM signal.
3. **Vehicle Resistors ($R_2$ and $R_3$)**:
   - $R_2 = 2.74\,\text{k}\Omega \pm 1\%$ (Connected continuously inside vehicle).
   - $R_3 = 1.3\,\text{k}\Omega \pm 1\%$ (Switched into parallel with $R_2$ via switch $S_2$ when the vehicle is ready to charge).
   - Equivalent resistance in State C: $R_{eq} = \frac{R_2 \times R_3}{R_2 + R_3} = \frac{2740 \times 1300}{2740 + 1300} \approx 882\,\Omega$.

---

### 3.2 Control Pilot Voltage States

The voltage at the CP pin represents a classic voltage divider between the EVSE's internal $1.0\,\text{k}\Omega$ resistor and the vehicle's internal resistance:
$$V_{CP} = V_{gen} \times \frac{R_{vehicle}}{R_1 + R_{vehicle}}$$

| State | Nominal CP Voltage | Acceptable Voltage Range | Vehicle Status | Contactor Status | PWM Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **State A** | **$+12\,\text{V}$** | $+11.0\,\text{V}$ to $+13.0\,\text{V}$ | **EV Disconnected**: No vehicle plugged into charging socket. | **OPEN** | Constant DC $+12\,\text{V}$ (No PWM) |
| **State B** | **$+9\,\text{V}$** | $+8.2\,\text{V}$ to $+9.8\,\text{V}$ | **EV Connected, Not Ready**: Vehicle detected ($R_2 = 2.74\,\text{k}\Omega$). OBC preparing. | **OPEN** | $1.0\,\text{kHz}$ PWM active |
| **State C** | **$+6\,\text{V}$** | $+5.5\,\text{V}$ to $+6.5\,\text{V}$ | **EV Connected, Ready to Charge**: Switch $S_2$ closed ($R_{eq} = 882\,\Omega$). Cooling normal. | **CLOSED (Charging)** | $1.0\,\text{kHz}$ PWM active |
| **State D** | **$+3\,\text{V}$** | $+2.6\,\text{V}$ to $+3.4\,\text{V}$ | **EV Ready, Ventilation Required**: Lead-acid or high-gassing battery ($R_{eq} = 246\,\Omega$). | **CLOSED (if exhaust fan active)** | $1.0\,\text{kHz}$ PWM active |
| **State E** | **$0\,\text{V}$** | $-1.0\,\text{V}$ to $+1.0\,\text{V}$ | **Error / Ground Short**: CP wire shorted to PE or EVSE unpowered. | **OPEN (Trip)** | Disabled / Tripped |
| **State F** | **$-12\,\text{V}$** | $-11.0\,\text{V}$ to $-13.0\,\text{V}$ | **Critical Fault / Missing Diode**: Vehicle diode $D_1$ missing, shorted, or reversed. | **OPEN (Lockout)** | Tripped |

```text
CP Voltage Waveform across Charging Lifecycle:
  12V ──┐ State A (12V DC)
        │
   9V ──┼─────────┐ State B (PWM +9V Peak)
        │         │   ┌─┐   ┌─┐   ┌─┐
   6V ──┼─────────┼───┼─┼───┼─┼───┼─┼───┐ State C (Charging +6V Peak)
        │         │   │ │   │ │   │ │   │  ┌─┐  ┌─┐  ┌─┐
   0V ──┼─────────┼───┼─┼───┼─┼───┼─┼───┼──┼─┼──┼─┼──┼─┼───
        │         │   │ │   │ │   │ │   │  │ │  │ │  │ │
 -12V ──┴─────────┴───┘ └───┘ └───┘ └───┴──┘ └──┘ └──┘ └──
                      ▲                 ▲
                   Plugged In       Charging Started
                   (EV Detected)    (S2 Closed, Contactor Closes)
```

---

### 3.3 The Vehicle Diode Check Principle

The presence of the vehicle diode $D_1$ is a mandatory safety check:
1. When the PWM driver outputs $+12\,\text{V}$, diode $D_1$ is forward-biased. Current flows through $R_2$ (or $R_2 \parallel R_3$), creating the $+9\,\text{V}$ or $+6\,\text{V}$ positive peak.
2. When the PWM driver outputs $-12\,\text{V}$, diode $D_1$ is **reverse-biased**.
3. In reverse bias, no current can flow into the vehicle's resistors. The vehicle impedance appears as an infinite open circuit ($R_{vehicle} = \infty$).
4. The voltage at the CP pin must therefore pull down completely to **$-12\,\text{V}$** during the negative portion of the cycle.
5. **The Safety Test**:
   - If an unauthorized load (such as a human body, water ingress, or a simple resistor without a diode) is connected across CP and PE, current flows during the negative half-cycle as well.
   - The negative voltage would measure $\approx -9\,\text{V}$ or $-6\,\text{V}$ instead of $-12\,\text{V}$.
   - The controller board detects this as **State F (Diode Fault)**, inhibits contactor closure, and prevents electrocution or electrical damage.

---

### 3.4 PWM Duty Cycle to Current Capacity Mapping

The controller board communicates the maximum continuous AC current that the EV is permitted to draw by modulating the duty cycle of the $1.0\,\text{kHz}$ square wave:

```text
Duty Cycle (%) = (Pulse High Time / 1.0 ms) * 100%
```

| Duty Cycle Window | Current Range ($I_{max}$) | Governing Mathematical Formula | Operational Description |
| :--- | :--- | :--- | :--- |
| **$< 3.0\%$** | $0\,\text{A}$ | Charging Not Allowed | Error / Emergency Stop activated |
| **$3.0\% \text{ to } 7.0\%$** | Digital Only | ISO 15118 / DIN 70121 | Digital communication required (HomePlug GreenPHY PLC) |
| **$8.0\% \text{ to } 10.0\%$** | $6.0\,\text{A}$ | Minimum continuous current | Clamped minimum charging rate |
| **$10.0\% \le D \le 85.0\%$** | **$6\,\text{A} \text{ to } 51\,\text{A}$** | **$I = \text{Duty (\%)} \times 0.6\,\text{A}$** | Standard Linear AC Charging range |
| **$85.0\% < D \le 96.0\%$** | **$51\,\text{A} \text{ to } 80\,\text{A}$** | **$I = (\text{Duty (\%)} - 64) \times 2.5\,\text{A}$** | High-Current Level 2 AC charging range |
| **$96.0\% < D \le 97.0\%$** | $80.0\,\text{A}$ | Maximum AC current limit | Maximum rating under SAE J1772 |
| **$> 97.0\%$** | $0\,\text{A}$ | Constant High (+12V DC) | Standby / Unplugged State A |

#### Common Industry Duty Cycle Benchmarks:
- **$10.0\%$** $\to 10 \times 0.6 = \mathbf{6.0\,\text{A}}$ (Minimum baseline charge rate)
- **$16.7\%$** $\to 16.7 \times 0.6 = \mathbf{10.0\,\text{A}}$ (Domestic household socket limit)
- **$26.7\%$** $\to 26.7 \times 0.6 = \mathbf{16.0\,\text{A}}$ (Standard single-phase $3.7\,\text{kW}$ or 3-phase $11\,\text{kW}$)
- **$53.3\%$** $\to 53.3 \times 0.6 = \mathbf{32.0\,\text{A}}$ (Standard single-phase $7.4\,\text{kW}$ or 3-phase $22\,\text{kW}$)
- **$80.0\%$** $\to 80.0 \times 0.6 = \mathbf{48.0\,\text{A}}$ (High-power residential single-phase $11.5\,\text{kW}$)

---

## 4. Proximity Pilot (PP) & Motorized Cable Lock

In European and international installations using **IEC 62196 Type 2 (Mennekes)** sockets, the charging cable is detachable. The EVSE must detect:
1. Whether a cable is inserted into the charging socket.
2. The current-carrying capacity of the cable assembly.

```text
    EVSE LOW VOLTAGE CONTROLLER                     TYPE 2 DETACHABLE CHARGING CABLE
   ┌────────────────────────────┐                  ┌─────────────────────────────────┐
   │                            │                  │                                 │
   │  +3.3V or +5V Vref         │                  │                                 │
   │        │                   │                  │                                 │
   │       [R_pullup: 330 Ω]    │                  │                                 │
   │        │                   │     PP Pin       │                                 │
   │        ├───────────────────┼──────────────────┼───────┐                         │
   │        │                   │                  │       │                         │
   │        ▼                   │                  │      [Rc] (Resistor inside plug)│
   │   Analog ADC               │                  │       │                         │
   │   Sampling Channel         │                  │       ▼                         │
   │                            │                  │    PE (Protective Earth)        │
   └────────────────────────────┘                  └─────────────────────────────────┘
```

### 4.1 Cable Resistor Sizing Table

| Resistor Value ($R_c$) | Allowable Tolerance | Maximum Cable Current | EVSE Firmware Action |
| :--- | :--- | :--- | :--- |
| **$1.5\,\text{k}\Omega$** | $1350\,\Omega\text{ to }1650\,\Omega$ | **$13\,\text{A}$** | Limits CP PWM duty cycle to $\le 21.6\%$ ($13\,\text{A}$). |
| **$680\,\Omega$** | $612\,\Omega\text{ to }748\,\Omega$ | **$20\,\text{A}$** | Limits CP PWM duty cycle to $\le 33.3\%$ ($20\,\text{A}$). |
| **$220\,\Omega$** | $198\,\Omega\text{ to }242\,\Omega$ | **$32\,\text{A}$** | Limits CP PWM duty cycle to $\le 53.3\%$ ($32\,\text{A}$). |
| **$100\,\Omega$** | $90\,\Omega\text{ to }110\,\Omega$ | **$63\,\text{A}$** | Limits CP PWM duty cycle to $\le 85.0\%$ ($63\,\text{A}$). |
| **Open Circuit ($\infty$)**| $> 2000\,\Omega$ | **$0\,\text{A}$** | Cable disconnected; contactor opening enforced. |

> [!IMPORTANT]
> **Safety Interlock**: Even if the EV requests $32\,\text{A}$ and the grid can supply $32\,\text{A}$, if the user inserts a thin $20\,\text{A}$ cable ($R_c = 680\,\Omega$), the LV controller board **must clamp the CP PWM duty cycle to $33.3\%$ ($20\,\text{A}$)**. This prevents the cable conductors from overheating and catching fire.

### 4.2 Motorized Connector Lock Actuator
To prevent an energized cable from being unplugged under full electrical load (which would draw a high-voltage destructive arc), Type 2 sockets feature an internal motorized solenoid latch:
- **Actuator Hardware**: A small DC permanent-magnet gearmotor with an internal position feedback microswitch.
- **Drive Circuit**: An **H-Bridge Driver** (e.g., TI DRV8871, Allegro A4950, or discrete Dual P/N MOSFETs) powered from $+12\,\text{V}$.
- **Locking Sequence**:
  1. Vehicle transitions to State B (Plug inserted).
  2. MCU pulses H-bridge forward for $300\,\text{ms}$, driving the locking pin into the notch of the Type 2 plug.
  3. Microswitch feedback transitions from Open to Closed, confirming mechanical engagement.
  4. Only after mechanical lock confirmation is the main contactor permitted to close.
- **Emergency Unlocking**: If power fails while locked, an internal capacitor discharge or manual mechanical pull-cord allows emergency release.

---

## 5. Safety, Protection & Interlock Systems

The Low Voltage Controller Board houses dedicated hardware protection loops that operate independently of software to guarantee fail-safe shutdown:

```text
                                HARDWARE PROTECTION INTERLOCK MATRIX
 ┌───────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
 │ Residual Current Monitor  │      │ Welded Contactor Sense    │      │ Thermal Protection        │
 │  • 6 mA DC Fluxgate Sensor│      │  • Aux Contact Feedback   │      │  • 4x NTC Thermistors     │
 │  • 30 mA AC Leakage Trip  │      │  • Mains Voltage Detect   │      │  • Dynamic Derating Curve │
 └─────────────┬─────────────┘      └─────────────┬─────────────┘      └─────────────┬─────────────┘
               │                                  │                                  │
               ▼                                  ▼                                  ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
 │               HARDWARE SHUTDOWN LOGIC / COMPARATOR INTERRUPT (Latch Circuit)                   │
 └────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                  │
                                                  ▼
                               ┌─────────────────────────────────────┐
                               │ Contactor Driver Low-Side Gate Shut │  (Cuts coil drive in < 10 ms)
                               └─────────────────────────────────────┘
```

### 5.1 Residual Current Monitoring (RCM) - IEC 62955 Compliance
Electric vehicle batteries and on-board chargers can generate **smooth DC leakage currents** (e.g. through insulation breakdown in the DC link).
- Standard household Type A RCDs are blinded and desensitized if DC fault currents exceed $6\,\text{mA}$ because the DC current permanently saturates the toroidal magnetic core.
- The LV Controller Board integrates an active **Type B or RDC-DD sensor** (e.g., Western Automation, LEM, or VAC sensor) using a fluxgate magnetometer.
- **Trip Thresholds**:
  - **$6\,\text{mA}$ DC Leakage**: Must trip in $< 10.0\,\text{s}$ at $6\,\text{mA}$, $< 150\,\text{ms}$ at $60\,\text{mA}$, and $< 40\,\text{ms}$ at $300\,\text{mA}$.
  - **$30\,\text{mA}$ AC Leakage**: Must trip in $< 300\,\text{ms}$.
- The RCM output connects directly to an active-low hardware interrupt on the MCU and an analog gate pull-down transistor, forcing the main contactor to open instantly.

### 5.2 Welded Contactor Contact Detection
Power contactors handling $32\,\text{A}$ across inductive and capacitive EV loads can suffer contact pitting, arc erosion, and eventual contact welding (mechanical sticking).
- If a contact welds shut, the socket pins remain energized with $230\,\text{V}/400\,\text{V}$ AC even after the session terminates. A user pulling the plug could touch live pins.
- **Detection Method 1: Auxiliary Feedback Contact**: A mechanically linked auxiliary microswitch on the contactor body opens when the main poles open. The MCU monitors this via an isolated input.
- **Detection Method 2: AC Mains Voltage Sensing**: High-voltage optocouplers or resistor dividers on the load side of the contactor detect if voltage is present when the coil drive is deactivated.
- **Firmware Action upon Welded Contact**:
  1. The MCU refuses to unlock the motorized cable lock (keeping the plug trapped so live pins cannot be touched).
  2. The RGB status halo flashes rapid RED.
  3. The EVSE enters permanent lockout and transmits an emergency **OCPP `StatusNotification(Faulted, ContactWeld)`** to the cloud.

### 5.3 Open Protective Earth (O-PEN) & Neutral Fault Detection
In TN-C-S earthing systems (common in the UK and Europe), the combined Protective Earth and Neutral (PEN) conductor from the distribution transformer can break.
- If the PEN conductor breaks, all metallic chassis connected to PE can rise to dangerous line voltages ($> 100\text{--}230\,\text{V}$).
- The LV board monitors the voltage difference between Neutral and Earth ($V_{N-PE}$), and monitors phase-to-neutral voltages.
- If $V_{N-PE} > 30\,\text{V}$ or phase voltage exceeds $253\,\text{V}$ or drops below $207\,\text{V}$, the controller opens all poles (including the Neutral pole) within $5\,\text{seconds}$ as mandated by BS 7671 (Amendment 1).

### 5.4 Dynamic Thermal Derating
- Precision NTC thermistors are mounted on the high-current input terminal lugs, the contactor housing, and inside the charging socket.
- When temperature exceeds **$75^\circ\text{C}$**, the MCU dynamically throttles the CP PWM duty cycle, reducing charging current from $32\,\text{A}$ down to $16\,\text{A}$ or $10\,\text{A}$.
- If temperature exceeds **$85^\circ\text{C}$**, the controller trips the main contactor to avoid thermal runaway.

---

## 6. Precision Energy Metering Subsystem

To facilitate commercial billing and smart grid energy management, the LV controller board incorporates an industrial-grade energy metering Analog Front-End (AFE):

```text
  Phase Voltages (L1, L2, L3, N) ──► [Precision Resistor Dividers (1000:1)] ──► Voltage ADC Channels
                                                                                       │
  Phase Currents (CT1, CT2, CT3) ──► [Burden Resistors & Antialiasing Filter]─► Current ADC Channels
                                                                                       │
                                                                                       ▼
                                                                           ┌───────────────────────┐
                                                                           │  Dedicated Metering   │
                                                                           │  IC (ADE7953 / STPM32)│
                                                                           │   • RMS Computation   │
                                                                           │   • Active / Reactive │
                                                                           │   • High-Speed DSP    │
                                                                           └───────────┬───────────┘
                                                                                       │ (Isolated SPI)
                                                                                       ▼
                                                                           Primary Controller MCU
```

### 6.1 Metering IC & Sensor Architecture
- **AFE Solutions**: Cirrus Logic CS5463, Analog Devices ADE7953 (Single-phase) or ADE9000 (Polyphase), or STMicroelectronics STPM32.
- **Current Measurement**: Precision Current Transformers (CTs) with $1000:1$ turns ratio across low-tolerance metal film burden resistors ($10\,\Omega\text{ to }33\,\Omega, 0.1\%, 25\,\text{ppm}/^\circ\text{C}$).
- **Voltage Measurement**: High-impedance matched resistor ladders ($1\,\text{M}\Omega$ series strings consisting of multiple SMD resistors to withstand high-voltage surge transients).

### 6.2 Computed Electrical Metrics
Every $100\text{--}500\,\text{ms}$, the metering IC calculates and exposes registers over isolated SPI:
- **$V_{RMS}$**: Root-Mean-Square Voltage per phase (accuracy $< 0.5\%$).
- **$I_{RMS}$**: Root-Mean-Square Current per phase ($< 0.5\%$).
- **Active Power ($P$)**: True real power in Watts ($W$).
- **Reactive Power ($Q$)**: Power in volt-amperes reactive ($\text{VAR}$).
- **Apparent Power ($S$)**: Power in volt-amperes ($\text{VA}$).
- **Power Factor ($\cos \phi$)**: Phase angle efficiency ($0.00\text{ to }1.00$).
- **Accumulated Active Energy ($E_{active}$)**: Transferred energy in kilowatt-hours ($\text{kWh}$) logged to secure non-volatile FRAM.

---

## 7. Contactor Actuation & Coil Economizer Circuit

The main contactor typically requires a $12\,\text{V}$ or $24\,\text{V}$ DC coil to actuate its 4-pole high-current contacts ($4 \times 40\,\text{A}$).

### 7.1 The Coil Economizer Principle
1. **Pull-In Phase (High Inrush)**: To overcome the internal mechanical spring and close the heavy contacts, the coil requires a large initial pull-in current ($\approx 1.5\,\text{A}\text{ at }12\,\text{V} = 18\,\text{W}$) for the first $100\,\text{ms}$.
2. **Hold Phase (Economizing)**: Once closed, maintaining the magnetic field requires far less current ($\approx 0.3\,\text{A}\text{ at }4\text{--}6\,\text{V} = 1.8\,\text{W}$).
3. Keeping the coil at full $12\,\text{V}$ indefinitely wastes $16\,\text{W}$ of power, turning the inside of the sealed enclosure into a heat trap.

```text
              +12V Coil Supply
                     │
              ┌──────┴──────┐
              │  Contactor  │
              │  Coil (12V) │
              └──────┬──────┘
                     │
                     ├────────────┐
                     │            │
                   ──┴──         [D_flyback: Fast Recovery / TVS Clamp]
              NMOS ──┬──          │
              Driver │            │
                     ├────────────┘
                     │
                    GND
                     ▲
                     │ Gate: 100% PWM for 100 ms (Pull-in)
                     │       40% PWM @ 25 kHz (Hold Phase)
```

- The controller board drives the coil via an N-channel logic-level MOSFET (e.g., AO3400 or Vishay Si2302) using high-frequency ($25\,\text{kHz}$) PWM.
- The MCU applies **$100\%$ duty cycle for $100\,\text{ms}$** to snap the contactor shut.
- The MCU then scales down to **$35\text{--}45\%$ duty cycle**, maintaining contact pressure while slashing power dissipation by **$85\%$**.
- A fast-recovery freewheeling diode (e.g., ES1J) and Zener/TVS clamp suppress inductive kickback voltages when de-energizing.
