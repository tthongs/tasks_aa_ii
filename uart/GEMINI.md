# Project Overview

This project is a Verilog implementation of a UART (Universal Asynchronous Receiver/Transmitter) for FPGAs. It includes modules for a UART transmitter and receiver, along with a top-level UART module that combines them.

# Building and Running

To use this project, you will need a Verilog simulator or an FPGA development board.

1.  **Simulation:**
    *   Compile the Verilog files (`uart_tx.v`, `uart_rx.v`, and `uart.v`) with your simulator.
    *   Create a testbench to stimulate the `uart` module and verify its functionality.

2.  **FPGA Implementation:**
    *   Add the Verilog files to your FPGA project.
    *   Instantiate the `uart` module in your top-level design.
    *   Connect the `rx` and `tx` ports to the appropriate pins on your FPGA.
    *   Synthesize, place, and route the design.
    *   Program the FPGA and test the UART communication.

# Development Conventions

*   The code follows standard Verilog-2001 syntax.
*   Modules are parameterized for easy configuration of the baud rate.
*   The code is commented to explain the functionality of each module.