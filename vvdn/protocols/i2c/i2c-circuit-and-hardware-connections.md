# I2C Hardware Connection & Circuit Schematic Guide

This engineering guide provides detailed, practical hardware schematics and connection blueprints for the **I2C** (**Inter-Integrated Circuit**) bus across standard multi-target networks, bidirectional bi-voltage level translation, address conflict multiplexing, active rise-time accelerators, and long-distance cable extenders.

---

## 1. Standard Multi-Target I2C Bus Circuit with Master & Peripherals

The standard board-level open-drain architecture interconnecting a microcontroller with sensors, an EEPROM, and a Real-Time Clock (RTC):

```text
                               +3.3V VDD Power Rail
                                     │         │
                                   [ Rp ]    [ Rp ]  Pull-Up Resistors
                                    4.7k      4.7k   (Sized for Bus Capacitance)
                                     │         │
     SDA Line ───────────────────────┼─────────o───────┬──────────────────────┬──────────────────────┐
     SCL Line ───────────────────────o─────────────────┼──────────┬───────────┼──────────┬───────────┤
                                     │                 │          │           │          │           │
     Microcontroller (Master)        │                 │          │           │          │           │
     ┌────────────────────────┐      │                 │          │           │          │           │
     │                   SDA  ├──────┴─────────────────┤          │           │          │           │
     │                        │                        │          │           │          │           │
     │                   SCL  ├────────────────────────┘          │           │          │           │
     │                        │                                   ▼           ▼          ▼           ▼
     │                   GND  ├────┬─────────────────────────►┌───────────────┐  ┌───────────────┐
     └────────────────────────┘    │                          │ SCL       SDA │  │ SCL       SDA │
                                   │                          │               │  │               │
                                   │                          │ 24LC256 EEPROM│  │ BMP280 Sensor │
                                   │                          │ Addr: 0x50    │  │ Addr: 0x76    │
                                   │                          │ A0 A1 A2  GND │  │ CSB SDO   GND │
                                   │                          └──┬──┬──┬───┬──┘  └──┬───┬────┬──┘
                                   │                             │  │  │   │        │   │    │
                                  GND ───────────────────────────┴──┴──┴───┴────────┴───┴────┴────
```

### Critical Hardware Sizing Rules:
1. **Pull-Up Resistor ($R_p$) Sizing Limits**:
   - **Minimum Resistance ($R_{p(min)}$)**: Dictated by driver current sink capability ($I_{OL} = 3\,\text{mA}$ for Standard/Fast mode):
     $$R_{p(min)} = \frac{V_{DD} - V_{OL(max)}}{I_{OL}} = \frac{3.3\,\text{V} - 0.4\,\text{V}}{3\,\text{mA}} \approx 966\,\Omega$$
   - **Maximum Resistance ($R_{p(max)}$)**: Dictated by bus capacitance ($C_b$) and maximum allowed rise-time ($t_r = 1000\,\text{ns}$ for $100\,\text{kbps}$, $300\,\text{ns}$ for $400\,\text{kbps}$):
     $$R_{p(max)} = \frac{t_{r(max)}}{0.8473 \times C_b} = \frac{300\,\text{ns}}{0.8473 \times 100\,\text{pF}} \approx 3.54\,\text{k}\Omega$$
   - **Industry Sweet Spot**: $R_p = 2.2\,\text{k}\Omega \dots 4.7\,\text{k}\Omega$ for $3.3\,\text{V}$ systems running at $400\,\text{kbps}$.
2. **Hardware Address Pin Strapping ($A_0, A_1, A_2$)**:
   - Unconnected address pins float, causing intermittent address detection. Tie address pins directly to Ground or $V_{DD}$.
3. **Decoupling Capacitors**:
   - Every I2C target IC must have its own $0.1\,\mu\text{F}$ ceramic bypass capacitor placed within $3\,\text{mm}$ of its $V_{DD}$ pin.

---

## 2. Bidirectional Bi-Voltage Level-Shifter Circuit (3.3V to 5V)

To bridge a 3.3V microcontroller (STM32/ESP32) with 5V I2C peripherals (legacy 5V sensors, LCDs, Arduino shields):

```text
       +3.3V (LV Domain)                                             +5.0V (HV Domain)
             │                                                             │
            [R1] 4.7k                                                     [R2] 4.7k
             │                                                             │
     SDA_LV ─┴──────────────────┐                     ┌────────────────────┴─ SDA_HV
                                │                     │
                             Source                 Drain
                                │     ┌─────────┐     │
                             ┌──┴──┐  │  Body   │  ┌──┴──┐
                             │     ├──┤  Diode  ├──┤     │  N-Channel MOSFET (BSS138 / 2N7002)
                             │     │  │  ─┤>├── │  │     │
                             └──┬──┘  └─────────┘  └──┬──┘
                                │                     │
                                └─── Gate ────────────┘
                                       │
                                    +3.3V (Low-Voltage Power Rail)
```
*(An identical MOSFET and pull-up pair is replicated for the SCL clock line).*

### Three-State Operating Dynamics:
1. **Idle State (Bus High)**:
   - Gate is tied to $+3.3\,\text{V}$. Source is held at $+3.3\,\text{V}$ by $R_1$.
   - $V_{GS} = 3.3\,\text{V} - 3.3\,\text{V} = 0\,\text{V} < V_{TH}$. MOSFET is OFF.
   - The HV side is independently pulled up to $+5.0\,\text{V}$ by $R_2$. Zero current flows between the two supply domains.
2. **3.3V Master Pulls Bus LOW ($0\,\text{V}$)**:
   - Source potential drops to $0\,\text{V}$.
   - $V_{GS} = 3.3\,\text{V} - 0\,\text{V} = 3.3\,\text{V} > V_{TH}$. The MOSFET turns fully ON.
   - The conducting channel shorts Drain to Source, discharging the 5V line to Ground.
3. **5V Slave Pulls Bus LOW ($0\,\text{V}$)**:
   - Drain potential drops to $0\,\text{V}$.
   - The intrinsic body diode becomes forward biased, pulling the Source node down to $\approx 0.6\,\text{V}$.
   - Once Source drops, $V_{GS} = 3.3\,\text{V} - 0.6\,\text{V} = 2.7\,\text{V} > V_{TH}$. The channel turns ON, pulling the 3.3V node down to pure Ground.

---

## 3. I2C Bus Multiplexer / Switch Circuit (TI TCA9548A / NXP PCA9548A)

Used to solve **hardware I2C address conflicts** when connecting multiple identical sensors (e.g., four ToF distance sensors all hardcoded to address `0x29`) and to **isolate bus capacitance**:

```text
       Host Microcontroller                                 TCA9548A 8-Channel I2C Switch
       ┌───────────────────┐                                 ┌─────────────────────────────┐
       │               SDA ├────────────────────────────────►│ SDA (Pin 22)                │
       │                   │                                 │                             │
       │               SCL ├────────────────────────────────►│ SCL (Pin 23)     Channel 0  ├────► Sensor #1 (Addr 0x29)
       │                   │                                 │          SD0/SC0 (Pins 4, 5)│
       │             RESET#├────────────────────────────────►│ RESET#           Channel 1  ├────► Sensor #2 (Addr 0x29)
       │                   │                                 │          SD1/SC1 (Pins 6, 7)│
       │         A0, A1, A2├───[ Hardwired Address: 0x70 ]──►│ A0, A1, A2       Channel 2  ├────► Sensor #3 (Addr 0x29)
       └───────────────────┘                                 │          SD2/SC2 (Pins 8, 9)│
                                                             │                  Channel 3  ├────► Sensor #4 (Addr 0x29)
                                                             └─────────────────────────────┘
```

### Key Engineering Benefits:
1. **Dynamic Channel Selection**: The host MCU sends a single byte to the multiplexer address (`0x70`) to enable one or more downstream channels:
   - Write `0x01` $\rightarrow$ Enables Channel 0 only.
   - Write `0x02` $\rightarrow$ Enables Channel 1 only.
2. **Capacitive Bus Segmentation**: Upstream and downstream bus segments are physically disconnected when disabled. If each downstream cable has $150\,\text{pF}$ of capacitance, the master only sees the capacitance of the currently active channel, keeping total bus capacitance safely below the $400\,\text{pF}$ specification.

---

## 4. Long-Distance High-Capacitance I2C Bus Extender (NXP P82B715 / P82B96)

Standard I2C drivers cannot drive cables longer than $1 \dots 2\,\text{meters}$ due to wire capacitance exceeding $400\,\text{pF}$. A dedicated **bidirectional bus buffer** scales drive current by $10\times$, extending range up to **$50\,\text{meters}$**:

```text
   Local 3.3V I2C Bus                                                   Long-Distance Buffered Bus (up to 50m)
   ┌───────────────────────┐                                            ┌───────────────────────────────────┐
   │ Master MCU            │                                            │ Remote Sensor / Actuator          │
   │ SDA ──┬── P82B715     │                                            │ P82B715 ──┬── Remote Target       │
   │       │   ┌─────────┐ │       +12V Industrial Supply               │ ┌─────────┐   │                   │
   │       └───┤ Sx  Lx  ├─┼───────┬────────────────────────────┬───────┼─┤ Lx   Sx ├───┘                   │
   │ SCL ──┬───┤ Sy  Ly  ├─┼───────┼──────┬──────────────┬──────┼───────┼─┤ Ly   Sy ├───┐                   │
   │       │   └─────────┘ │       │      │              │      │       │ └─────────┘   │                   │
   └───────┼───────────────┘     [330Ω] [330Ω]         [330Ω] [330Ω]    └───────────────┼───────────────────┘
          [4.7k] Pull-Ups          │      │              │      │                      [4.7k] Pull-Ups
           │                       │      │              │      │                       │
          +3.3V                    └──────┼──────────────┼──────┘                      +3.3V
                                          ▼              ▼
                                     Buffered Lx    Buffered Ly
                                   (Low-Z: 30mA)  (Low-Z: 30mA)
                                   Over Shielded Twisted Pair Cable (STP)
```

### Operating Principles:
- The **Sx/Sy** pins interface directly with standard $400\,\text{pF}$ logic-level I2C devices.
- The **Lx/Ly** buffered pins feature heavy current sink capability ($I_{OL} \ge 30\,\text{mA}$), allowing pull-up resistors as low as $330\,\Omega$ connected to an industrial $+12\,\text{V}$ rail.
- This slashes RC charge time constants, allowing transmission across multi-nanofarad industrial cables.
