# FPGA UART Implementation

This project contains the Verilog implementation of a UART (Universal Asynchronous Receiver/Transmitter) protocol for FPGAs.

## Modules

*   **`uart_tx.v`**: The UART transmitter module. This module takes parallel data and transmits it serially.
*   **`uart_rx.v`**: The UART receiver module. This module receives serial data and converts it to parallel data.
*   **`uart.v`**: A top-level module that instantiates both the `uart_tx` and `uart_rx` modules.

## Parameters

The modules are parameterized to allow for easy configuration of the UART protocol. The key parameters are:

*   **`CLKS_PER_BIT`**: The number of clock cycles per bit. This is determined by the clock frequency and the desired baud rate.

## Usage

To use these modules, instantiate the `uart` module in your top-level FPGA design and connect the `rx` and `tx` ports to the appropriate pins on your FPGA.

## Algorithm

### UART Protocol

The UART protocol is a method of sending serial data. The data is framed with a start bit and a stop bit. The start bit is always a logic '0', and the stop bit is always a logic '1'. The data bits are sent between the start and stop bits, typically LSB first.

A typical UART frame looks like this:

```
           +---+---+---+---+---+---+---+---+---+---+
           |   | D | D | D | D | D | D | D | D |   |
Idle ~~~~~~| S | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | S |~~~~~~ Idle
           | T |   |   |   |   |   |   |   |   | T |
           | A |   |   |   |   |   |   |   |   | O |
           | R |   |   |   |   |   |   |   |   | P |
           | T |   |   |   |   |   |   |   |   |   |
           +---+---+---+---+---+---+---+---+---+---+
```

### Transmitter (TX) Algorithm

The UART transmitter is implemented as a state machine with the following states:

*   **Idle (0)**: The transmitter is waiting for the `tx_start` signal. When `tx_start` is asserted, the transmitter loads the `tx_data` into a data register and moves to the Start Bit state.
*   **Start Bit (1)**: The transmitter sends the start bit (logic '0') for one bit period.
*   **Data Bits (2)**: The transmitter sends the 8 data bits, one at a time, for one bit period each.
*   **Stop Bit (3)**: The transmitter sends the stop bit (logic '1') for one bit period and then returns to the Idle state.

### Receiver (RX) Algorithm

The UART receiver is also implemented as a state machine:

*   **Idle (0)**: The receiver is waiting for a start bit. When it detects a logic '0' on the `rx` line, it moves to the Start Bit state.
*   **Start Bit (1)**: The receiver waits for half a bit period and then checks the `rx` line again. If it is still '0', the receiver confirms a valid start bit and moves to the Data Bits state. Otherwise, it returns to the Idle state.
*   **Data Bits (2)**: The receiver samples the `rx` line in the middle of each bit period to read the 8 data bits.
*   **Stop Bit (3)**: The receiver waits for a stop bit (logic '1'). Once the stop bit is received, it sets the `rx_done` flag and returns to the Idle state.

## Block Diagram

```
+-----------------------------------------------------------------+
|                                                                 |
|                              uart                               |
|                                                                 |
|  +-----------------+                     +-----------------+    |
|  |                 |     tx_start,     |                 |    |
|  |     uart_tx     |------ tx_data ---->|     uart_rx     |    |
|  |                 |                     |                 |    |
|  |   tx_busy, tx   |<--------------------|   rx_data, rx   |    |
|  |                 |                     |                 |    |
|  +-----------------+                     +-----------------+    |
|                                                                 |
+-----------------------------------------------------------------+
```