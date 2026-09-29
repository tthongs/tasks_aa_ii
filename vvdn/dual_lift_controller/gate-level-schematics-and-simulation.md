# Gate-Level Schematics, TTL IC Implementation & Simulation Guide

This document provides the hardware implementation details for the **Dual Lift Controller**: standard 7400-series TTL Integrated Circuit (IC) Bill of Materials, detailed pin-to-pin wiring schematics, propagation delay analysis, and complete simulation verification.

---

## 1. Standard TTL 7400-Series IC Implementation & Bill of Materials

The entire dual lift controller can be constructed using readily available off-the-shelf standard 7400-series TTL or 74HCT CMOS digital logic integrated circuits:

| IC Part Number | Function Description | Package | Quantity Required | Subsystem Usage |
| :--- | :--- | :--- | :---: | :--- |
| **74LS148** | 8-to-3 Line Priority Encoder | 16-pin DIP | **1** | Encodes 1-hot floor call pushbuttons ($R_0..R_3$) into 2-bit binary ($R_1, R_0$). |
| **74LS74** | Dual D-Type Positive-Edge-Triggered Flip-Flops | 14-pin DIP | **2** | 2-bit floor position registers for Lift A ($A_1, A_0$) and Lift B ($B_1, B_0$). |
| **74LS86** | Quad 2-Input XOR Gates | 14-pin DIP | **2** | Distance calculation LSBs ($d_0 = X_0 \oplus Y_0$) and bit equivalence logic. |
| **74LS04** | Hex Inverters (NOT Gates) | 14-pin DIP | **2** | Signal inversions ($\overline{R}, \overline{A}, \overline{B}, \overline{SEL}$). |
| **74LS08** | Quad 2-Input AND Gates | 14-pin DIP | **3** | Distance MSB terms, magnitude comparators, and motor enable gates. |
| **74LS32** | Quad 2-Input OR Gates | 14-pin DIP | **2** | Sum-of-Products distance combine and nearest lift arbitration. |
| **74LS85** | 4-Bit Magnitude Comparator | 16-pin DIP | **3** | Optional single-chip replacement for Distance Compare and Direction Comparators. |
| **NE555 / 74LS123**| Precision Timer / Dual Monostable Multivibrator | 8/16-pin DIP | **2** | 5.0-second Door Open monostable delay timer for Lift A and Lift B. |
| **ULN2003A** | High-Voltage High-Current Darlington Transistor Array| 16-pin DIP | **1** | Interfacing 5V logic signals to 12V/24V motor contactor and door solenoid coils. |

---

## 2. Gate-Level Pin-to-Pin Schematic Architecture

### 2.1 Complete 2-Bit Absolute Distance Subtractor (|R - A|)

```text
               74LS86 (XOR)                     74LS04 (NOT)                74LS08 (AND) / 74LS32 (OR)
          ┌─────────────────────┐          ┌─────────────────────┐     ┌──────────────────────────────────┐
  R0 ────►│ Pin 1 (1A)          │          │                     │     │                                  │
          │         Pin 3 (1Y)  ├──────────┼─────────────────────┼─────┼──────────────────────────────────┼────► dA0 (LSB)
  A0 ────►│ Pin 2 (1B)          │          │                     │     │                                  │
          └─────────────────────┘          │                     │     │                                  │
  R1 ────┬─────────────────────────────────┼─────────────────────┼────►│ Pin 1 (1A)                       │
         │                                 │                     │     │         Pin 3 (1Y) ──┐           │
  A1 ────┼─────────────────────────────────┼►Pin 1 (1A)          │     │ Pin 2 (1B)           │           │
         │                                 │   Pin 2 (1Y: ~A1)───┼────►│ (74LS08)             ├──[74LS32]─┼────► dA1 (MSB)
         │                                 │                     │     │                      │   OR Gate │
         │                                 │                     │     │                      │  Pin 3 (1Y)
         │                                 │                     │     │ Pin 4 (2A) ──┐       │           │
         └─────────────────────────────────┴─────────────────────┴────►│ Pin 5 (2B) ──┴───────┘           │
                                                                       └──────────────────────────────────┘
```

---

### 2.2 Nearest Lift Arbitration Unit (dA vs. dB)

```text
                  74LS85 4-Bit Magnitude Comparator
                     ┌───────────────────────┐
       dA0 ─────────►│ Pin 10 (A0)           │
       dA1 ─────────►│ Pin 12 (A1)           │
       GND ─────────►│ Pin 13 (A2)           │
       GND ─────────►│ Pin 15 (A3)           │
                     │                       │
       dB0 ─────────►│ Pin 9  (B0)           │
       dB1 ─────────►│ Pin 11 (B1)           │
       GND ─────────►│ Pin 14 (B2)           │
       GND ─────────►│ Pin 1  (B3)           │
                     │                       │
       +5V ─────────►│ Pin 3  (A=B In)       │
       GND ─────────►│ Pin 2  (A<B In)       │
       GND ─────────►│ Pin 4  (A>B In)       │
                     │                       │
                     │        Outputs:       │
                     │ Pin 7  (A<B Out: LT)  ├──────────┐ (74LS32 OR)
                     │ Pin 6  (A=B Out: EQ)  ├──────────┴──[ OR Gate ]───► SEL_A (Lift A Selected)
                     │ Pin 5  (A>B Out: GT)  ├────────────────────────────► SEL_B (Lift B Selected)
                     └───────────────────────┘
```

- **Lift A Dispatch ($SEL_A$)**: Fired when $d_A < d_B$ OR when $d_A = d_B$ (Equidistant tie-break).
- **Lift B Dispatch ($SEL_B$)**: Fired when $d_A > d_B$ ($d_B$ is strictly closer).

---

### 2.3 Motor Power Contactor Driver (ULN2003A Interfacing)

Logic gates operate at $5\,\text{V}$ TTL levels and cannot drive the heavy $12\,\text{V}$ or $24\,\text{V}$ DC coils of the industrial reversing contactors. A **ULN2003A Darlington Transistor Array** bridges the logic to the motor power stage:

```text
       TTL Logic Level (5V)                   ULN2003A Driver                       High-Voltage Contactor (24V)
      ┌──────────────────────┐             ┌─────────────────────┐                 ┌────────────────────────────┐
      │                      │             │                     │                 │  +24V Supply Rail          │
      │  UP_A Gate Output    ├────────────►│ Pin 1 (1B)          │                 │     │                      │
      │                      │             │         Pin 16 (1C) ├─────────────────┼─────┴──[ UP Contactor Coil ]
      │  DOWN_A Gate Output  ├────────────►│ Pin 2 (2B)          │                 │     │                      │
      │                      │             │         Pin 15 (2C) ├─────────────────┼─────┴──[ DOWN Contactor ]    │
      │  DOOR_A Gate Output  ├────────────►│ Pin 3 (3B)          │                 │     │                      │
      │                      │             │         Pin 14 (3C) ├─────────────────┼─────┴──[ Door Motor Relay ]  │
      │                      │             │ Pin 8 (GND)         │                 │                            │
      │                      │             │ Pin 9 (COM Clamp)   ├─────────────────┼────► Tie to +24V Rail      │
      └──────────────────────┘             └─────────────────────┘                 └────────────────────────────┘
```

---

## 3. Propagation Delay & Timing Analysis

In a pure combinational dispatch architecture, speed is governed by the total cumulative propagation delay ($t_{pd}$) through the longest path (critical path):

```text
 Critical Path:
 Floor Call (R) ──► Priority Encoder ──► Abs Difference ──► Magnitude Comp ──► Arbiter ──► Direction Logic ──► Motor Out
                      (74LS148)           (74LS86/08)         (74LS85)        (74LS32)      (74LS85/08)       (ULN2003)
 Delay:                ~ 14 ns              ~ 18 ns            ~ 16 ns         ~ 10 ns        ~ 16 ns          ~ 1.5 µs
```

### Delay Budget Calculation:
$$\text{Total Combinational Gate Delay} = 14\,\text{ns} + 18\,\text{ns} + 16\,\text{ns} + 10\,\text{ns} + 16\,\text{ns} \approx \mathbf{74\,\text{ns}}$$
- The logic gates calculate the nearest lift, resolve ties, and select motor direction in **under $80\,\text{nanoseconds}$**.
- This instantaneous response eliminates human-perceptible latency and prevents contactor race conditions.

---

## 4. Verilog Simulation Waveforms & Verification Scenarios

The Verilog testbench [`dual_lift_controller_tb.v`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/dual_lift_controller_tb.v) was executed to verify all operational permutations. Below are three canonical test vector walkthroughs:

### Scenario 1: Request Closer to Lift B
- **State**: Request at **Floor 2** ($R = 10_2$). Lift A is at **Floor 0** ($A = 00_2$). Lift B is at **Floor 3** ($B = 11_2$).
- **Calculated Distances**:
  $$d_A = |2 - 0| = 2 \ (10_2)$$
  $$d_B = |2 - 3| = 1 \ (01_2)$$
- **Comparator Output**: $d_A > d_B$ ($GT = 1, LT = 0, EQ = 0$).
- **Arbiter Output**: $SEL_A = 0, \mathbf{SEL_B = 1}$.
- **Direction Output**: Lift B is at Floor 3, Target is Floor 2 ($R < B \implies \mathbf{DOWN_B = 1}, UP_B = 0, STOP_B = 0$).
- **Result**: Lift B immediately descends to Floor 2 while Lift A remains idle at Floor 0.

```text
Time (ns)   Req   Lift_A   Lift_B   dA   dB   Winner   UP_A  DOWN_A  STOP_A   UP_B  DOWN_B  STOP_B
 120.0       2      0        3       2    1   LIFT B     0      0       1       0      1       0
```

---

### Scenario 2: Equidistant Request (Tie-Breaking Rule)
- **State**: Request at **Floor 1** ($R = 01_2$). Lift A is at **Floor 0** ($A = 00_2$). Lift B is at **Floor 2** ($B = 10_2$).
- **Calculated Distances**:
  $$d_A = |1 - 0| = 1 \ (01_2)$$
  $$d_B = |1 - 2| = 1 \ (01_2)$$
- **Comparator Output**: $d_A == d_B$ ($EQ = 1, LT = 0, GT = 0$).
- **Arbiter Output**: Tie detected; priority goes to **Lift A** ($\mathbf{SEL_A = 1}, SEL_B = 0$).
- **Direction Output**: Lift A is at Floor 0, Target is Floor 1 ($R > A \implies \mathbf{UP_A = 1}$).
- **Result**: Lift A moves UP to Floor 1 while Lift B stays stationed at Floor 2.

```text
Time (ns)   Req   Lift_A   Lift_B   dA   dB   Winner   UP_A  DOWN_A  STOP_A   UP_B  DOWN_B  STOP_B
 250.0       1      0        2       1    1   LIFT A     1      0       0       0      0       1
```

---

### Scenario 3: Request at Floor Where Lift A is Already Parked
- **State**: Request at **Floor 3** ($R = 11_2$). Lift A is at **Floor 3** ($A = 11_2$). Lift B is at **Floor 1** ($B = 01_2$).
- **Calculated Distances**:
  $$d_A = |3 - 3| = 0 \ (00_2)$$
  $$d_B = |3 - 1| = 2 \ (10_2)$$
- **Comparator Output**: $d_A < d_B$ ($LT = 1$).
- **Arbiter Output**: **Lift A** ($\mathbf{SEL_A = 1}, SEL_B = 0$).
- **Direction Output**: Target matches current position ($R == A \implies \mathbf{STOP_A = 1}, UP_A = 0, DOWN_A = 0$).
- **Door Mechanism**: $DOOR\_OPEN_A$ triggers, opening the cabin doors immediately for waiting passengers.

```text
Time (ns)   Req   Lift_A   Lift_B   dA   dB   Winner   UP_A  DOWN_A  STOP_A   UP_B  DOWN_B  STOP_B
 380.0       3      3        1       0    2   LIFT A     0      0       1       0      0       1
```

---

## 5. Summary Verification Checklist

- [x] **Nearest Lift Rule Verified**: Confirmed across all 64 4-floor combinations and all 27 3-floor combinations via Python simulation (`tools/lift_sim.py`) and Verilog testbench (`dual_lift_controller_tb.v`).
- [x] **Zero Conflict**: Interlocking gates ensure $UP$ and $DOWN$ signals can never be asserted concurrently.
- [x] **Fail-Safe Stopping**: Any unselected lift automatically receives $STOP = 1$ to maintain mechanical brakes.
- [x] **Hardware Feasibility**: Designed strictly using standard TTL logic ICs with low component count and sub-$100\,\text{ns}$ latency.
