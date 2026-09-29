# UART Frame & Protocol Analysis: Framing, Oversampling, Errors & Buffering

This technical guide provides a deep-dive analysis of the **UART character frame**, **16x oversampling clock synchronization**, **hardware error detection flags**, **9-bit multi-drop addressing**, **hardware auto-flow control**, and **high-throughput DMA circular buffer architectures**.

---

## 1. Bit-Level Frame Anatomy & Signal Transitions

Unlike packetized network buses that include destination headers and CRCs in every packet, UART transmits data as independent **character frames** framed by start and stop transitions:

```text
  Idle (Mark: 1) ──────┐                                                               ┌────── Idle (Mark: 1)
                       │ Start │  D0   │  D1   │  D2   │  D3   │  D4   │  D5   │  D6   │  D7   │Parity │ Stop  │
                       │ Bit(0)│ (LSB) │       │       │       │       │       │       │ (MSB) │ (Opt) │ Bit(1)│
                       └───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘
                       |<--------------------------- 1 Frame (10 to 12 Bit Times) ----------------------------->|
```

### Frame Component Breakdown:
1. **Idle State (Mark / Logic 1)**:
   - When no transmission is active, the line is continuously held at positive supply voltage ($3.3\,\text{V}$ or $5\,\text{V}$). This confirms physical cable continuity. A disconnected or broken wire floating to $0\,\text{V}$ is immediately detectable as a fault condition.
2. **Start Bit (Space / Logic 0, exactly 1 bit period)**:
   - A high-to-low transition ($1 \rightarrow 0$) signals the beginning of a new frame.
   - It resynchronizes the receiver's internal baud rate counter for that character.
3. **Data Bits (Typically 8 bits, configurable 5 to 9 bits)**:
   - Transmitted **LSB (Least Significant Bit, D0) first**, terminating with MSB (D7).
   - In 9-bit mode, the 9th bit (D8) acts as an address/data discriminator in multi-drop networks.
4. **Parity Bit (Optional, 1 bit)**:
   - Evaluated as the exclusive-OR (XOR) sum of all transmitted data bits.
   - **Even Parity**: Parity bit is set to 1 if the count of 1s in the data byte is odd, making the total count of 1s even.
   - **Odd Parity**: Parity bit is set to 1 if the count of 1s in the data byte is even, making the total count of 1s odd.
   - **Mark / Space Parity**: Fixed at 1 or 0 regardless of data (used in legacy protocols).
5. **Stop Bit (Logic 1 / Mark, configurable 1, 1.5, or 2 bits)**:
   - Forces the physical line back to the idle HIGH state.
   - Provides a mandatory processing recovery window for the receiver's shift register and FIFO before the next high-to-low start bit edge arrives.

---

## 2. Receiver Clock Recovery & 16x Oversampling Architecture

Because no shared clock wire connects transmitter and receiver, UART receivers utilize an internal **$16\times$ (or $8\times$) oversampling clock** derived from the local peripheral bus clock to sample incoming bits precisely at their midpoints:

```text
               16x Oversampling Clock Cycles across One Bit Period
       ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
       │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ 10│ 11│ 12│ 13│ 14│ 15│ 16│
       └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
                                   ▲   ▲   ▲
                                   └───┼───┘
                           Majority Voting Window:
                           Samples taken at ticks 7, 8, 9
```

### The Synchronization & Majority Voting Algorithm:
1. **Falling Edge Detection**: The receiver continuously polls the RX line at the $16\times$ clock rate. When a high-to-low transition is detected, a counter starts.
2. **Start Bit Verification**: At clock ticks 7, 8, and 9 (the mathematical center of the expected Start bit), the line state is sampled three times. If at least 2 of the 3 samples are Logic 0, the Start bit is validated. If not, the transition is rejected as a transient noise spike, and the receiver resets to the idle polling state.
3. **Data Bit Sampling**: For each subsequent bit (D0 through Stop), the receiver counts 16 ticks from the center of the previous bit and takes **three consecutive samples at ticks 7, 8, and 9**.
4. **Majority Voting Logic**:
   - $\text{Bit Value} = (\text{Sample}_7 \land \text{Sample}_8) \lor (\text{Sample}_7 \land \text{Sample}_9) \lor (\text{Sample}_8 \land \text{Sample}_9)$
   - If all three samples agree ($0-0-0$ or $1-1-1$), the bit is clean.
   - If samples disagree ($2:1$ split, e.g., $1-0-1$), the majority value is accepted, but the hardware sets the **Noise Error (NE)** flag in the status register.

---

## 3. Hardware Error Detection Flags & Diagnosis

Modern UART controllers (e.g., STM32 USART, TI eUSCI, Microchip PIC) monitor signal integrity continuously and report faults via dedicated status register bits:

```text
       Typical UART Status Register (USART_SR / USART_ISR)
   ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
   │ Bit 7   │ Bit 6   │ Bit 5   │ Bit 4   │ Bit 3   │ Bit 2   │ Bit 1   │ Bit 0   │
   ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
   │ TXE     │ TC      │ RXNE    │ IDLE    │ ORE     │ NF / NE │ FE      │ PE      │
   │ Tx Empty│ Complete│ Rx Ready│ IdleLine│ Overrun │ NoiseErr│ Framing │ Parity  │
   └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
```

| Error Flag | Name | Physical Root Cause | Bench Troubleshooting Action |
| :--- | :--- | :--- | :--- |
| **FE** | **Framing Error** | Stop bit sampled as Logic 0 instead of Logic 1 | Baud rate mismatch $> 3\%$, clock jitter, or baud divisor miscalculation |
| **ORE** | **Overrun Error** | New byte arrived before CPU/DMA read previous byte | CPU blocked in long ISR; switch to hardware FIFO or DMA circular buffer |
| **PE** | **Parity Error** | XOR sum of data bits disagrees with received parity bit | Line electrical noise, EMI bursts, or mismatch in parity config (Even vs Odd)|
| **NE / NF**| **Noise Flag** | Majority voting samples (ticks 7, 8, 9) were not unanimous | Ground loop bounce, long unshielded cables, missing pull-up resistors |

---

## 4. BREAK Signaling & Multi-Processor 9-Bit Addressing

### 1. BREAK Signaling (Physical Space Override):
A **BREAK condition** occurs when the TX line is forcefully driven to **Logic 0 (Space) for longer than an entire frame duration** (typically $\ge 11 \dots 13$ bit times):

```text
       Normal 8-N-1 Character                  BREAK Condition (Continuous Space)
  ───┐   ┌───┬───┬───┬───┬───┐   ┌────── ───────────────────────────────────────
     │ S │ D0│ D1│ D2│...│ D7│ P │ Stop  │ Space line held LOW >= 11 to 13 bit periods!
     └───┴───┴───┴───┴───┴───┘   └────── └──────────────────────────────────────
```
- **Primary Uses**:
  - **LIN Bus Synchronization**: In automotive LIN (Local Interconnect Network), the master initiates every frame with a 13-bit minimum BREAK field to wake up slave nodes and reset slave state machines.
  - **DMX512 Stage Lighting**: Lighting consoles precede 512-byte DMX universe frames with an $88\,\mu\text{s}$ BREAK to synchronize LED fixtures.
  - **Modem / Debug Console Reset**: Terminal software sends a BREAK signal (Serial SysRq) to drop Linux into the kernel debugger or reboot a frozen microcontroller.

---

### 2. 9-Bit Addressable Multi-Drop Mode (RS-485 Multi-Processor):
In multi-drop RS-485 networks where multiple slave microcontrollers listen to a single master transmitter, software packet parsing creates excessive CPU interrupt overhead. Hardware **9-bit addressing** eliminates this:

```text
       Master Transmission:
       1. Address Frame: [ 9th Bit = 1 ] -> Data Byte = Target Slave ID (e.g. 0x05)
          ==> All slaves wake up and compare byte to internal Node ID.
       2. Data Frame:    [ 9th Bit = 0 ] -> Payload Byte #1, #2, #3...
          ==> Only Slave 0x05 stays awake; all other slaves re-enter hardware mute!
```

```c
// Example STM32 Hardware Multi-Processor Configuration
void UART_MultiProcessor_Init(uint8_t my_node_address) {
    USART1->CR1 |= USART_CR1_M0;            // Configure 9-bit word length
    USART1->CR2 |= (my_node_address << 24); // Set hardware address
    USART1->CR2 |= USART_CR2_ADDM7;         // 7-bit address detection
    USART1->CR1 |= USART_CR1_WAKE;          // Wakeup method: Address Mark (9th bit = 1)
    USART1->CR1 |= USART_CR1_MMM;           // Enter Mute Mode (silent until addressed)
}
```

---

## 5. Hardware Flow Control: RTS / CTS Handshaking

When a high-speed transmitter sends data faster than the receiving microcontroller can process, buffers overflow, causing catastrophic Overrun Errors (**ORE**). **Hardware flow control** (RTS/CTS) provides real-time backpressure:

```text
       DTE (Microcontroller)                                   DCE (Cellular Modem / ESP32)
       ┌──────────────────┐                                    ┌──────────────────┐
       │               TX ├───────────────────────────────────►│ RX               │
       │               RX │◄───────────────────────────────────┤ TX               │
       │              RTS ├───────────────────────────────────►│ CTS              │
       │              CTS │◄───────────────────────────────────┤ RTS              │
       └──────────────────┘                                    └──────────────────┘
```

### Signal Definitions & Active-LOW Polarity:
- **$\overline{\text{RTS}}$ (Request to Send / Ready to Receive)**: Driven by the receiver. When asserted LOW, it signals: *"My internal FIFO has space; you are authorized to send data."* When the receiver FIFO fills to its high-watermark threshold (e.g., $75\%$), it deasserts RTS (pulls it HIGH), forcing the transmitter to immediately pause.
- **$\overline{\text{CTS}}$ (Clear to Send)**: Driven by the transmitter. The transmitter monitors CTS before shifting out each byte. If CTS is HIGH, the transmitter halts immediately between characters.

---

## 6. High-Throughput Buffering: DMA Circular Ring Buffer with IDLE Line Detection

In production firmware, handling high-baud UART (e.g., $921.6\,\text{kbps}$ or $1\,\text{Mbps}$) via byte-by-byte interrupts (`RXNE`) will saturate CPU interrupt bandwidth ($100,000\,\text{ISRs/sec}$). The industry standard architecture combines **Direct Memory Access (DMA)** in **Circular Mode** with **IDLE Line Interrupts**:

```text
       Incoming Serial Bytes (Streamed by DMA directly into SRAM without CPU intervention!)
       ───────────────────────────────────────────────────────────────────────────────────►
                                     Circular Ring Buffer in RAM
                             ┌───────┬───────┬───────┬───────┬───────┐
                             │ Byte 0│ Byte 1│ Byte 2│ Byte 3│ Byte 4│
                             └───────┴───────┴───────┴───────┴───────┘
                                         ▲               ▲
                                         │               │
                                   Tail (CPU Read)  Head (DMA Write)
```

### How IDLE Line Detection Eliminates Fixed Packet Size Limits:
1. **DMA Autonomous Transfer**: DMA channel is mapped directly to `USART_RDR`. Incoming bytes are automatically written into a circular ring buffer in SRAM without generating a single CPU interrupt.
2. **The IDLE Line Event (`USART_IT_IDLE`)**:
   - The hardware UART controller monitors the RX line.
   - When the remote transmitter finishes sending a burst of data, the line remains in the idle HIGH state for **at least 1 full character frame duration** (10 to 11 bit times).
   - The UART hardware instantly triggers a single **IDLE Line Interrupt**.
3. **Variable-Length Packet Processing**:
   - In the IDLE ISR, the CPU reads the remaining DMA counter register (`CNDTR`), calculates exactly how many bytes arrived in the burst:
     $$\text{Bytes Received} = \text{Buffer Size} - \text{DMA\_CNDTR}$$
   - The CPU dispatches the packet to application processing and updates buffer pointers in mere microseconds!
