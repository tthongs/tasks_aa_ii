# 3-Floor Dual Lift Controller: Gate-Level Logic Design

This document details the complete gate-level digital logic design for an intelligent **Dual Lift System serving a 3-Floor Building** (Floors 0, 1, and 2, corresponding to Ground, First, and Second floors). When a passenger initiates a hall call at any floor, the combinational logic dispatches the nearest lift car.

---

## 1. System Specifications & Signal Definitions

```text
 Floor 2 ─── [ R2 Call ] ────────── [ Lift A: A2 ] ────────── [ Lift B: B2 ]
 Floor 1 ─── [ R1 Call ] ────────── [ Lift A: A1 ] ────────── [ Lift B: B1 ]
 Floor 0 ─── [ R0 Call ] ────────── [ Lift A: A0 ] ────────── [ Lift B: B0 ]
```

### 1.1 Input Signals
- **Requested Floor ($R$)**:
  - **1-Hot Inputs**: $R_0$ (Floor 0 Call), $R_1$ (Floor 1 Call), $R_2$ (Floor 2 Call).
  - Only one request is active at an instant ($R_0 + R_1 + R_2 = 1$).
  - **2-Bit Binary Equivalent**: $(R_1, R_0) \in \{00_2, 01_2, 10_2\}$.
- **Lift A Position ($A$)**:
  - **1-Hot Position Sensors**: $A_0, A_1, A_2$ (Limit switches on Floor 0, 1, 2).
  - **2-Bit Binary Equivalent**: $(A_1, A_0) \in \{00_2, 01_2, 10_2\}$.
- **Lift B Position ($B$)**:
  - **1-Hot Position Sensors**: $B_0, B_1, B_2$ (Limit switches on Floor 0, 1, 2).
  - **2-Bit Binary Equivalent**: $(B_1, B_0) \in \{00_2, 01_2, 10_2\}$.

### 1.2 Output Signals
- **Arbitration / Lift Selection**:
  - $SEL_A$: Logic 1 if Lift A is dispatched to answer the call.
  - $SEL_B$: Logic 1 if Lift B is dispatched to answer the call.
- **Motor Control Signals for Lift A**:
  - $UP_A$: Energizes hoisting motor in UP direction.
  - $DOWN_A$: Energizes hoisting motor in DOWN direction.
  - $STOP_A$: Cuts motor power, engages mechanical brake, triggers door opening.
- **Motor Control Signals for Lift B**:
  - $UP_B, DOWN_B, STOP_B$ (Identical control for Lift B).

---

## 2. Exhaustive 27-State Truth Table for Nearest Lift Selection

Because each of the 3 variables ($R, A, B$) can take 3 valid values ($0, 1, 2$), the entire state space consists of exactly $3 \times 3 \times 3 = \mathbf{27 \text{ valid combinations}}$:

- **Distance of Lift A**: $d_A = |R - A|$
- **Distance of Lift B**: $d_B = |R - B|$
- **Tie-Breaker Rule**: When $d_A = d_B$, Lift A is selected by default ($SEL_A = 1, SEL_B = 0$).

| State | Req ($R$) | Lift A ($A$) | Lift B ($B$) | $d_A$ | $d_B$ | Winner ($SEL_A, SEL_B$) | Lift A Motor | Lift B Motor | Operational Rationale |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | 0 | 0 | 0 | 0 | 0 | **Lift A** (1, 0) | $STOP_A$ | $STOP_B$ | Both at floor 0; Lift A opens door. |
| **1** | 0 | 0 | 1 | 0 | 1 | **Lift A** (1, 0) | $STOP_A$ | $STOP_B$ | Lift A already at floor 0 ($d_A=0$). |
| **2** | 0 | 0 | 2 | 0 | 2 | **Lift A** (1, 0) | $STOP_A$ | $STOP_B$ | Lift A already at floor 0 ($d_A=0$). |
| **3** | 0 | 1 | 0 | 1 | 0 | **Lift B** (0, 1) | $STOP_A$ | $STOP_B$ | Lift B already at floor 0 ($d_B=0$). |
| **4** | 0 | 1 | 1 | 1 | 1 | **Lift A** (1, 0) | $DOWN_A$ | $STOP_B$ | Equidistant ($d=1$); Lift A dispatched DOWN. |
| **5** | 0 | 1 | 2 | 1 | 2 | **Lift A** (1, 0) | $DOWN_A$ | $STOP_B$ | Lift A closer ($d_A=1 < d_B=2$). |
| **6** | 0 | 2 | 0 | 2 | 0 | **Lift B** (0, 1) | $STOP_A$ | $STOP_B$ | Lift B already at floor 0 ($d_B=0$). |
| **7** | 0 | 2 | 1 | 2 | 1 | **Lift B** (0, 1) | $STOP_A$ | $DOWN_B$ | Lift B closer ($d_B=1 < d_A=2$). |
| **8** | 0 | 2 | 2 | 2 | 2 | **Lift A** (1, 0) | $DOWN_A$ | $STOP_B$ | Equidistant ($d=2$); Lift A dispatched DOWN. |
| **9** | 1 | 0 | 0 | 1 | 1 | **Lift A** (1, 0) | $UP_A$ | $STOP_B$ | Equidistant ($d=1$); Lift A dispatched UP. |
| **10**| 1 | 0 | 1 | 1 | 0 | **Lift B** (0, 1) | $STOP_A$ | $STOP_B$ | Lift B already at floor 1 ($d_B=0$). |
| **11**| 1 | 0 | 2 | 1 | 1 | **Lift A** (1, 0) | $UP_A$ | $STOP_B$ | Equidistant ($d=1$); Lift A dispatched UP. |
| **12**| 1 | 1 | 0 | 0 | 1 | **Lift A** (1, 0) | $STOP_A$ | $STOP_B$ | Lift A already at floor 1 ($d_A=0$). |
| **13**| 1 | 1 | 1 | 0 | 0 | **Lift A** (1, 0) | $STOP_A$ | $STOP_B$ | Both at floor 1; Lift A opens door. |
| **14**| 1 | 1 | 2 | 0 | 1 | **Lift A** (1, 0) | $STOP_A$ | $STOP_B$ | Lift A already at floor 1 ($d_A=0$). |
| **15**| 1 | 2 | 0 | 1 | 1 | **Lift A** (1, 0) | $DOWN_A$ | $STOP_B$ | Equidistant ($d=1$); Lift A dispatched DOWN. |
| **16**| 1 | 2 | 1 | 1 | 0 | **Lift B** (0, 1) | $STOP_A$ | $STOP_B$ | Lift B already at floor 1 ($d_B=0$). |
| **17**| 1 | 2 | 2 | 1 | 1 | **Lift A** (1, 0) | $DOWN_A$ | $STOP_B$ | Equidistant ($d=1$); Lift A dispatched DOWN. |
| **18**| 2 | 0 | 0 | 2 | 2 | **Lift A** (1, 0) | $UP_A$ | $STOP_B$ | Equidistant ($d=2$); Lift A dispatched UP. |
| **19**| 2 | 0 | 1 | 2 | 1 | **Lift B** (0, 1) | $STOP_A$ | $UP_B$ | Lift B closer ($d_B=1 < d_A=2$). |
| **20**| 2 | 0 | 2 | 2 | 0 | **Lift B** (0, 1) | $STOP_A$ | $STOP_B$ | Lift B already at floor 2 ($d_B=0$). |
| **21**| 2 | 1 | 0 | 1 | 2 | **Lift A** (1, 0) | $UP_A$ | $STOP_B$ | Lift A closer ($d_A=1 < d_B=2$). |
| **22**| 2 | 1 | 1 | 1 | 1 | **Lift A** (1, 0) | $UP_A$ | $STOP_B$ | Equidistant ($d=1$); Lift A dispatched UP. |
| **23**| 2 | 1 | 2 | 1 | 0 | **Lift B** (0, 1) | $STOP_A$ | $STOP_B$ | Lift B already at floor 2 ($d_B=0$). |
| **24**| 2 | 2 | 0 | 0 | 2 | **Lift A** (1, 0) | $STOP_A$ | $STOP_B$ | Lift A already at floor 2 ($d_A=0$). |
| **25**| 2 | 2 | 1 | 0 | 1 | **Lift A** (1, 0) | $STOP_A$ | $STOP_B$ | Lift A already at floor 2 ($d_A=0$). |
| **26**| 2 | 2 | 2 | 0 | 0 | **Lift A** (1, 0) | $STOP_A$ | $STOP_B$ | Both at floor 2; Lift A opens door. |

---

## 3. Direct 1-Hot Gate Logic Design

In relay and discrete digital logic controllers, 1-hot encoding is widely preferred because it eliminates encoders and decoders, reducing gate propagation delay to a bare minimum.

### 3.1 Distance Generation Gates
For a 3-floor building, the distance between any floor and a lift can only be **0, 1, or 2 floors**.

#### For Lift A:
1. **Distance = 0 ($d_{A0}$)**: Lift A is at the requested floor.
   $$d_{A0} = R_0 A_0 + R_1 A_1 + R_2 A_2$$
2. **Distance = 1 ($d_{A1}$)**: Lift A is 1 floor away.
   $$d_{A1} = R_0 A_1 + R_1 A_0 + R_1 A_2 + R_2 A_1$$
3. **Distance = 2 ($d_{A2}$)**: Lift A is 2 floors away (one at Floor 0, other at Floor 2).
   $$d_{A2} = R_0 A_2 + R_2 A_0$$

#### For Lift B:
1. **Distance = 0 ($d_{B0}$)**:
   $$d_{B0} = R_0 B_0 + R_1 B_1 + R_2 B_2$$
2. **Distance = 1 ($d_{B1}$)**:
   $$d_{B1} = R_0 B_1 + R_1 B_0 + R_1 B_2 + R_2 B_1$$
3. **Distance = 2 ($d_{B2}$)**:
   $$d_{B2} = R_0 B_2 + R_2 B_0$$

---

### 3.2 Distance Comparator & Dispatch Arbitration Gates

Lift B is selected **if and only if** it is strictly closer than Lift A ($d_B < d_A$):
$$SEL_B = (d_{B0} \cdot \overline{d_{A0}}) + (d_{B1} \cdot d_{A2})$$

Expanding with the distance definitions:
- When $d_B = 0$ and $d_A \neq 0$: Lift B is already at the requested floor, but Lift A is not:
  $$SEL_B = d_{B0} \cdot (d_{A1} + d_{A2}) + d_{B1} \cdot d_{A2}$$

Lift A is selected for all remaining cases (when $d_A \le d_B$):
$$SEL_A = \overline{SEL_B}$$

```text
                           LIFT ARBITRATION GATES (3-FLOOR)
   dA1 ──┐
         ├──[ OR1 ]───┐
   dA2 ──┘            │
                      ├──[ AND1 ]───┐
   dB0 ───────────────┘             │
                                    ├──[ OR3 ]────────────────► SEL_B (Dispatch Lift B)
   dB1 ───────────────┐             │                               │
                      ├──[ AND2 ]───┘                             ┌─┴─┐
   dA2 ───────────────┘                                           │NOT│
                                                                  └─┬─┘
                                                                    │
                                                                    └─► SEL_A (Dispatch Lift A)
```

---

### 3.3 Direction Control Gates

Once a lift is selected ($SEL_A = 1$ or $SEL_B = 1$), its motor direction is determined by comparing the request with its current floor:

#### Lift A Direction Logic:
1. **Move UP ($UP_A$)**: Requested floor is higher than current floor.
   - Request Floor 1 while Lift A is at Floor 0 ($R_1 A_0$)
   - Request Floor 2 while Lift A is at Floor 0 ($R_2 A_0$)
   - Request Floor 2 while Lift A is at Floor 1 ($R_2 A_1$)
   $$\mathbf{UP_A = SEL_A \cdot [A_0(R_1 + R_2) + A_1 R_2]}$$

2. **Move DOWN ($DOWN_A$)**: Requested floor is lower than current floor.
   - Request Floor 0 while Lift A is at Floor 1 ($R_0 A_1$)
   - Request Floor 0 while Lift A is at Floor 2 ($R_0 A_2$)
   - Request Floor 1 while Lift A is at Floor 2 ($R_1 A_2$)
   $$\mathbf{DOWN_A = SEL_A \cdot [A_2(R_0 + R_1) + A_1 R_0]}$$

3. **STOP ($STOP_A$)**: Lift A is at the requested floor OR Lift A is not selected.
   $$\mathbf{STOP_A = (R_0 A_0 + R_1 A_1 + R_2 A_2) + \overline{SEL_A} = d_{A0} + \overline{SEL_A}}$$

#### Lift B Direction Logic:
$$\mathbf{UP_B = SEL_B \cdot [B_0(R_1 + R_2) + B_1 R_2]}$$
$$\mathbf{DOWN_B = SEL_B \cdot [B_2(R_0 + R_1) + B_1 R_0]}$$
$$\mathbf{STOP_B = (R_0 B_0 + R_1 B_1 + R_2 B_2) + \overline{SEL_B} = d_{B0} + \overline{SEL_B}}$$

```text
                     LIFT A DIRECTION CONTROL GATES
    R1 ──┐
         ├──[ OR ]───┐
    R2 ──┘           ├──[ AND ]───┐
    A0 ──────────────┘            │
                                  ├──[ OR ]───┬──[ AND ]───► UP_A
    R2 ──┐                        │           │
         ├──[ AND ]───────────────┘           │
    A1 ──┘                                    │
                                              │
    SEL_A ────────────────────────────────────┴────────────► (Enable)
```

---

## 4. Door Control & Passenger Boarding Logic

When a lift stops at the requested floor ($STOP = 1$ and $d_0 = 1$), the controller triggers the automatic door mechanism:

```text
          Arrival Pulse               5-Second Monostable Timer (555 / Counter)
    d_A0 ──┐                                  ┌───────────────┐
           ├──[ AND ]───► Trigger (Active-Low)│               ├──► DOOR_OPEN_A (Motor)
    SEL_A ─┘                                  │   Gate Timer  │
                                              │  (t = 5.0 s)  │
    DOOR_OPEN_SENSOR (Photocell / Bump) ─────►│ RESET / PAUSE │
                                              └───────────────┘
```

1. **Door Open Condition**: $DOOR\_OPEN_A = SEL_A \cdot d_{A0} \cdot \overline{UP_A} \cdot \overline{DOWN_A}$.
2. **Door Safety Interlock**: An optical light curtain or edge bumper sensor detects passengers in the doorway, resetting the 5-second timer to hold the door open until the obstruction clears.
3. **Motion Interlock**:
   $$MOTOR\_ENABLE_A = DOOR\_CLOSED\_SWITCH_A$$
   The hoisting motor power relays are hard-interlocked through the physical door-closed limit switch. Power cannot flow to the motor while the door is open.
