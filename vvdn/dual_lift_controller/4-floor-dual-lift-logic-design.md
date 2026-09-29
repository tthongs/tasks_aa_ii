# 4-Floor Dual Lift Controller: Gate-Level Logic Design

This document details the complete gate-level digital logic design for an intelligent **Dual Lift System serving a 4-Floor Building** (Floors 0, 1, 2, and 3, corresponding to Ground, First, Second, and Third floors). The system implements binary arithmetic distance calculation, magnitude comparison, nearest lift dispatching, and autonomous motor direction control.

---

## 1. System Parameters & Binary Encoding

In a 4-floor building, every floor position and request is represented efficiently using a **2-bit binary code**:

```text
 Floor 3 (Third Floor)  ─── Binary Code: 11
 Floor 2 (Second Floor) ─── Binary Code: 10
 Floor 1 (First Floor)  ─── Binary Code: 01
 Floor 0 (Ground Floor) ─── Binary Code: 00
```

### 1.1 Input & Output Interface

```text
                           DUAL LIFT 4-FLOOR CONTROLLER
                              ┌──────────────────────┐
       Request Floor (R1, R0)─┤►                     ├─► Lift A Select (SEL_A)
      Lift A Floor (A1, A0)  ─┤►                     ├─► Lift B Select (SEL_B)
      Lift B Floor (B1, B0)  ─┤►                     ├─► Motor Up A (UP_A)
      Call Active (STROBE)   ─┤►                     ├─► Motor Down A (DOWN_A)
      Lift A Busy (BUSY_A)   ─┤►                     ├─► Motor Stop A (STOP_A)
      Lift B Busy (BUSY_B)   ─┤►                     ├─► Motor Up B (UP_B)
      Door Sensor A (DC_A)   ─┤►                     ├─► Motor Down B (DOWN_B)
      Door Sensor B (DC_B)   ─┤►                     ├─► Motor Stop B (STOP_B)
                              └──────────────────────┘
```

1. **Request Input**: $R = (R_1, R_0) \in \{00, 01, 10, 11\}$.
2. **Lift A Position**: $A = (A_1, A_0) \in \{00, 01, 10, 11\}$ (Fed by floor limit switch registers).
3. **Lift B Position**: $B = (B_1, B_0) \in \{00, 01, 10, 11\}$.
4. **Distance Outputs**:
   - $d_A = (dA_1, dA_0) = |R - A| \in \{0, 1, 2, 3\}$
   - $d_B = (dB_1, dB_0) = |R - B| \in \{0, 1, 2, 3\}$

---

## 2. Gate-Level Absolute Difference Subtractor ($|X - Y|$)

The mathematical core of the nearest lift dispatch system is calculating the absolute spatial distance $|R - A|$ and $|R - B|$ using digital logic gates.

Let $X = (X_1, X_0)$ and $Y = (Y_1, Y_0)$ be two 2-bit numbers. The absolute difference $D = (D_1, D_0) = |X - Y|$ is derived as follows:

### 2.1 Truth Table for 2-Bit Absolute Difference:

| $X_1 X_0$ | $Y_1 Y_0$ | $X$ (Dec) | $Y$ (Dec) | $D = |X - Y|$ | $D_1$ | $D_0$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 00 | 00 | 0 | 0 | 0 | 0 | 0 |
| 00 | 01 | 0 | 1 | 1 | 0 | 1 |
| 00 | 10 | 0 | 2 | 2 | 1 | 0 |
| 00 | 11 | 0 | 3 | 3 | 1 | 1 |
| 01 | 00 | 1 | 0 | 1 | 0 | 1 |
| 01 | 01 | 1 | 1 | 0 | 0 | 0 |
| 01 | 10 | 1 | 2 | 1 | 0 | 1 |
| 01 | 11 | 1 | 3 | 2 | 1 | 0 |
| 10 | 00 | 2 | 0 | 2 | 1 | 0 |
| 10 | 01 | 2 | 1 | 1 | 0 | 1 |
| 10 | 10 | 2 | 2 | 0 | 0 | 0 |
| 10 | 11 | 2 | 3 | 1 | 0 | 1 |
| 11 | 00 | 3 | 0 | 3 | 1 | 1 |
| 11 | 01 | 3 | 1 | 2 | 1 | 0 |
| 11 | 10 | 3 | 2 | 1 | 0 | 1 |
| 11 | 11 | 3 | 3 | 0 | 0 | 0 |

---

### 2.2 Derivation of Minimal Gate Equations

#### LSB ($D_0$):
Inspecting the column for $D_0$, we observe that $D_0 = 1$ whenever $X_0 \neq Y_0$, and $D_0 = 0$ whenever $X_0 = Y_0$.
$$\mathbf{D_0 = X_0 \oplus Y_0}$$
*A single 2-input XOR gate generates the LSB of the distance!*

#### MSB ($D_1$):
$D_1 = 1$ whenever $|X - Y| \ge 2$.
This occurs when:
1. $X - Y \ge 2 \implies (X=2, Y=0)$, $(X=3, Y=0)$, or $(X=3, Y=1)$
2. $Y - X \ge 2 \implies (Y=2, X=0)$, $(Y=3, X=0)$, or $(Y=3, X=1)$

Using Karnaugh Map grouping:
$$\mathbf{D_1 = X_1 \overline{Y_1} (\overline{Y_0} + X_0) + \overline{X_1} Y_1 (\overline{X_0} + Y_0)}$$

```text
                      GATE-LEVEL ABSOLUTE SUBTRACTOR CIRCUIT
       X0 ───┬─────────────────────────────────┐
       Y0 ───┼──────────┬──────────────────────┼──[ XOR ]─────────────► D0
             │          │                      │
       X1 ───┼──────────┼─────────┐            │
       Y1 ───┼──────────┼─────────┼─────┐      │
             │          │         │     │      │
             │        ┌─┴─┐     ┌─┴─┐   │      │
             │        │NOT│     │NOT│   │      │
             │        └─┬─┘     └─┬─┘   │      │
             │          │ ~Y0     │ ~Y1 │      │
             │          ├──[ OR ]─┼─────┼──────┼──[ AND ]───┐
             └──────────┘         │     │      │            │
                                  └─────┼──────┘            ├──[ OR ]─► D1
                                        │                   │
                                  ┌─────┘                   │
                                  │ (Symmetric Y > X logic) ┘
```

---

## 3. Distance Magnitude Comparator ($d_A$ vs. $d_B$)

Once $d_A = (dA_1, dA_0)$ and $d_B = (dB_1, dB_0)$ are generated, a **2-bit Magnitude Comparator** evaluates which lift is closer:

```text
Bit Equivalence Signals (XNOR):
  EQ_1 = dA1 ⊙ dB1 = ~(dA1 ^ dB1)
  EQ_0 = dA0 ⊙ dB0 = ~(dA0 ^ dB0)
```

1. **Lift A is Strictly Closer ($d_A < d_B$)**:
   $$\mathbf{LT = \overline{dA_1} dB_1 + EQ_1 \cdot \overline{dA_0} dB_0}$$
2. **Equidistant ($d_A = d_B$)**:
   $$\mathbf{EQ = EQ_1 \cdot EQ_0}$$
3. **Lift B is Strictly Closer ($d_B < d_A$)**:
   $$\mathbf{GT = dA_1 \overline{dB_1} + EQ_1 \cdot dA_0 \overline{dB_0}}$$

### 3.1 Nearest Lift Arbitration Gate Logic

```text
                           NEAREST ARBITRATION GATES
      LT (dA < dB) ──┐
                     ├──[ OR ]────────────────────────► SEL_A (Dispatch Lift A)
      EQ (dA == dB) ─┘
                                                      ► SEL_B (Dispatch Lift B)
      GT (dA > dB) ───────────────────────────────────┘
```

- **Lift A Dispatch ($SEL_A$)**: Selected if it is strictly closer ($LT=1$) OR if equidistant ($EQ=1$):
  $$SEL_A = LT + EQ = \overline{GT}$$
- **Lift B Dispatch ($SEL_B$)**: Selected if it is strictly closer ($GT=1$):
  $$SEL_B = GT$$

---

## 4. Direction & Motion Controller Logic

For whichever lift is dispatched, the direction controller compares the requested floor $R = (R_1, R_0)$ with that lift's current floor $(Pos_1, Pos_0)$ using a standard 2-bit comparator:

```text
Bit Equivalence:
  COMP_1 = R1 ⊙ Pos1
  COMP_0 = R0 ⊙ Pos0
```

1. **Target Higher than Current Floor ($R > Pos$)**:
   $$\mathbf{MOVE\_UP = R_1 \overline{Pos_1} + COMP_1 \cdot R_0 \overline{Pos_0}}$$
2. **Target Lower than Current Floor ($R < Pos$)**:
   $$\mathbf{MOVE\_DOWN = \overline{R_1} Pos_1 + COMP_1 \cdot \overline{R_0} Pos_0}$$
3. **Target Matches Current Floor ($R == Pos$)**:
   $$\mathbf{TARGET\_REACHED = COMP_1 \cdot COMP_0}$$

### 4.1 Lift A Motor Drive Gates:
$$\mathbf{UP_A = SEL_A \cdot MOVE\_UP_A}$$
$$\mathbf{DOWN_A = SEL_A \cdot MOVE\_DOWN_A}$$
$$\mathbf{STOP_A = TARGET\_REACHED_A + \overline{SEL_A}}$$

### 4.2 Lift B Motor Drive Gates:
$$\mathbf{UP_B = SEL_B \cdot MOVE\_UP_B}$$
$$\mathbf{DOWN_B = SEL_B \cdot MOVE\_DOWN_B}$$
$$\mathbf{STOP_B = TARGET\_REACHED_B + \overline{SEL_B}}$$

---

## 5. Busy State Arbitration & Direction-Affinity Logic

In real-world multi-car installations, a lift may already be carrying passengers or moving toward an existing destination.

Let $BUSY_A = 1$ if Lift A is currently in motion, and $BUSY_B = 1$ if Lift B is in motion:

```text
                         DYNAMIC ARBITRATION WITH BUSY FLAGS
                 Idle / Busy Status                         Distance Logic
            ┌───────────────────────────┐             ┌─────────────────────────┐
            │  BUSY_A       BUSY_B      │             │  dA < dB       dB < dA  │
            └─────┬───────────┬─────────┘             └────┬──────────────┬─────┘
                  │           │                            │              │
                  ▼           ▼                            ▼              ▼
     ┌──────────────────────────────────────────────────────────────────────────┐
     │                      PRIORITY ARBITRATION GATES                          │
     └────────────────────────────┬─────────────────────────────┬───────────────┘
                                  │                             │
                                  ▼                             ▼
                            FINAL_SEL_A                   FINAL_SEL_B
```

### Truth Table for Priority Dispatch:

| $BUSY_A$ | $BUSY_B$ | Condition | Dispatched Car | Gate Equation |
| :---: | :---: | :---: | :---: | :--- |
| **0** | **0** | Both Idle | **Nearest Lift** | $\overline{BUSY_A} \cdot \overline{BUSY_B} \cdot (d_A \le d_B \implies L_A, \text{ else } L_B)$ |
| **0** | **1** | Lift B Busy, Lift A Idle | **Lift A** | $\overline{BUSY_A} \cdot BUSY_B \implies SEL_A = 1$ |
| **1** | **0** | Lift A Busy, Lift B Idle | **Lift B** | $BUSY_A \cdot \overline{BUSY_B} \implies SEL_B = 1$ |
| **1** | **1** | Both Busy | **Direction Match or Queue**| Nearest lift moving in the same direction as call |

#### Combined Gate Realization:
$$\mathbf{FINAL\_SEL_A = \overline{BUSY_A} \cdot [BUSY_B + (d_A \le d_B)]}$$
$$\mathbf{FINAL\_SEL_B = \overline{BUSY_B} \cdot [BUSY_A + (d_B < d_A)]}$$

---

## 6. Hardware Safety Interlocks & Emergency Gates

To comply with elevator safety codes (EN 81-20 / ASME A17.1), the gate-level controller incorporates hardwired interlock logic:

```text
                             HARDWARE SAFETY INTERLOCK CIRCUIT
      DOOR_CLOSED_SENSOR_A ──┐
                             ├──[ AND1 ]───┐
      E_STOP_NOT ────────────┘             │
                                           ├──[ AND2 ]───┬──► MOTOR_ENABLE_A
      OVERLOAD_SENSOR_A_NOT ───────────────┘             │
                                                         ▼
                                                [ Coil Contactor Drive ]
```

1. **Door Safety Interlock**:
   - $DOOR\_CLOSED\_SENSOR_A = 1$ only when the door interlock hook is mechanically locked.
   - Motor cannot energize unless the door is confirmed fully closed.
2. **Emergency Stop (E-Stop)**:
   - Active-low signal $\overline{E\_STOP}$. When pressed, all motor outputs are immediately driven to logic 0.
3. **Cabin Overload Interlock**:
   - A strain gauge beneath the lift car floor asserts $OVERLOAD = 1$ if cabin load exceeds rated weight ($> 450\,\text{kg}$).
   - The controller inhibits motor motion and keeps doors open until weight is reduced.
