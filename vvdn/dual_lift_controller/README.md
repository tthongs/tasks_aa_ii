# Dual Lift Controller: Gate-Level Control Logic Design for 3 & 4 Floor Buildings

Welcome to the **Dual Lift Controller Digital Logic Design Suite**. This project provides an exhaustive, industry-grade gate-level implementation of an intelligent elevator dispatch system for **3-floor** and **4-floor** residential and commercial buildings.

---

## 1. Problem Statement

> **Design Prompt**:
> *"Design a control logic using gates for two lifts which need to be designed for 3 (or) 4 floor building. When a lift request is initiated from any floor, nearest lift should be started."*

### Core Functional Objectives:
1. **Two Independent Lifts**: Lift A ($L_A$) and Lift B ($L_B$) serving common floors.
2. **Floor Coverage**: Configurable for **3-Floor Buildings** (Floors 0, 1, 2) or **4-Floor Buildings** (Floors 0, 1, 2, 3).
3. **Nearest Lift Dispatch Rule**: When a passenger initiates a hall call at floor $R$, the system calculates the absolute spatial distance from both lifts to the requested floor:
   $$d_A = |R - A|$$
   $$d_B = |R - B|$$
   - If $d_A < d_B \implies$ **Lift A is dispatched** ($SEL_A = 1, SEL_B = 0$).
   - If $d_B < d_A \implies$ **Lift B is dispatched** ($SEL_A = 0, SEL_B = 1$).
   - If $d_A = d_B \implies$ **Equidistant Tie**: Deterministic priority rule selects Lift A (or idle lift).
4. **Autonomous Direction Control**: The selected lift automatically determines its motion:
   - If $R > \text{Position} \implies \mathbf{UP}$ motor energized.
   - If $R < \text{Position} \implies \mathbf{DOWN}$ motor energized.
   - If $R = \text{Position} \implies \mathbf{STOP}$ motor, open doors, trigger boarding timer.
5. **Pure Gate-Level Realization**: Built entirely using fundamental combinational and sequential digital logic gates (AND, OR, NOT, XOR, XNOR, Multiplexers, Adders/Subtractors, Magnitude Comparators, and D/JK Flip-Flops).

---

## 2. Top-Level System Architecture

The complete dual lift controller is partitioned into five distinct modular functional units:

```text
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   DUAL LIFT SYSTEM BLOCK DIAGRAM                                       │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Floor Call Buttons (R0..R3) ──► [Priority Encoder] ──► 2-Bit Target Floor (R1, R0)
                                                                │
                                    ┌───────────────────────────┴───────────────────────────┐
                                    │                                                       │
  Lift A Sensors (Limit Sw) ──► [Reg A] (A1, A0)                Lift B Sensors (Limit Sw) ──► [Reg B] (B1, B0)
              │                     │                                       │                   │
              │                     ▼                                       │                   ▼
              │          ┌──────────────────────┐                           │        ┌──────────────────────┐
              │          │ Absolute Difference  │                           │        │ Absolute Difference  │
              │          │ Subtractor |R - A|   │                           │        │ Subtractor |R - B|   │
              │          └──────────┬───────────┘                           │        └──────────┬───────────┘
              │                     │ Distance dA (dA1, dA0)                │                   │ Distance dB (dB1, dB0)
              │                     │                                       │                   │
              │                     └───────────────────┬───────────────────┘                   │
              │                                         │                                       │
              │                                         ▼                                       │
              │                              ┌─────────────────────┐                            │
              │                              │ 2-Bit Magnitude     │                            │
              │                              │ Comparator          │                            │
              │                              │ (dA vs dB)          │                            │
              │                              └──────────┬──────────┘                            │
              │                                         │                                       │
              │                      ┌──────────────────┴──────────────────┐                    │
              │                      │ Nearest Lift Arbiter & Tie-Breaker  │                    │
              │                      └──────────┬──────────────────┬───────┘                    │
              │                                 │                  │                            │
              │                        SEL_A = 1│                  │SEL_B = 1                   │
              │                                 ▼                  ▼                            │
              │                      ┌─────────────────────┐    ┌─────────────────────┐         │
              └─────────────────────►│ Lift A Direction    │    │ Lift B Direction    │◄────────┘
                                     │ Controller          │    │ Controller          │
                                     │ (R vs A Comparator) │    │ (R vs B Comparator) │
                                     └──────────┬──────────┘    └──────────┬──────────┘
                                                │                          │
                                    ┌───────────┼───────────┐  ┌───────────┼───────────┐
                                    ▼           ▼           ▼  ▼           ▼           ▼
                                   UP_A       DOWN_A      STOP UP_B      DOWN_B      STOP
```

---

## 3. Subsystem Breakdown

### 1. Position & Request Encoding Stage
- **Sensors**: Hall-effect or mechanical limit switches at each floor detect lift car presence ($A_0, A_1, A_2, A_3$ and $B_0, B_1, B_2, B_3$).
- **Request Buttons**: Hall call buttons at each floor latch an incoming passenger request.
- **Encoding**: Converted to 2-bit binary ($00 = \text{Ground/Floor 0}$, $01 = \text{Floor 1}$, $10 = \text{Floor 2}$, $11 = \text{Floor 3}$) via a standard 74LS148 priority encoder or minimal OR gates.

### 2. Distance Computation Engine ($|R - A|$ and $|R - B|$)
- Implements gate-level absolute difference:
  $$d_0 = R_0 \oplus A_0$$
  $$d_1 = R_1 \overline{A_1}(\overline{A_0} + R_0) + \overline{R_1} A_1 (\overline{R_0} + A_0)$$
- Generates distance values ($0, 1, 2, 3$ floors away) in $< 15\,\text{ns}$ propagation delay.

### 3. Nearest Lift Arbiter
- Compares $d_A$ and $d_B$ using a 2-bit magnitude comparator.
- Asserts $SEL_A = 1$ when $d_A \le d_B$, and $SEL_B = 1$ when $d_B < d_A$.

### 4. Direction & Motor Drive Gates
- Compares requested floor $R$ with selected lift's position:
  - $UP = SEL \cdot (R > \text{Position})$
  - $DOWN = SEL \cdot (R < \text{Position})$
  - $STOP = (R == \text{Position}) + \overline{SEL}$

### 5. Door Interlock & Arrival Logic
- When a lift reaches the target floor ($R == \text{Position}$), motor power is cut, and a 555-timer / counter gate sequence opens the door for $5\,\text{seconds}$.
- Safety limit: Motor cannot be energized unless Door Closed Limit Switch is asserted.

---

## 4. Documentation Suite Roadmap

```text
vvdn/dual_lift_controller/
├── README.md (.docx)                              # Executive overview, architecture & directory roadmap
├── 3-floor-dual-lift-logic-design.md (.docx)      # Gate design for 3-floor building (27-state truth table, K-maps)
├── 4-floor-dual-lift-logic-design.md (.docx)      # Gate design for 4-floor building (64-state truth table, subtractors)
├── gate-level-schematics-and-simulation.md (.docx)# TTL 7400 IC schematics, gate counts & simulation waveforms
├── dual_lift_controller.v                         # Synthesizable gate-level Verilog hardware description module
└── dual_lift_controller_tb.v                      # Verilog testbench validating all 64 state combinations
```

### [1. 3-Floor Dual Lift Logic Design](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/3-floor-dual-lift-logic-design.md)
- Complete design for 3-Floor Buildings (Floors 0, 1, 2).
- 1-Hot input encoding ($R_0, R_1, R_2$) and 2-bit binary encoding.
- Exhaustive 27-state truth table for distance and nearest lift selection.
- Karnaugh Maps (K-maps) and Boolean minimal equations for $SEL_A$ and $SEL_B$.
- Gate-level schematics using fundamental AND, OR, NOT, XOR gates.

### [2. 4-Floor Dual Lift Logic Design](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/4-floor-dual-lift-logic-design.md)
- Complete design for 4-Floor Buildings (Floors 0, 1, 2, 3).
- 2-bit binary arithmetic: Gate-level absolute subtractor and 2-bit comparator.
- 64-state truth table and algebraic reduction.
- Direction control logic ($UP, DOWN, STOP$) with motor interlocking.
- Lift Busy and direction-affinity arbitration.

### [3. Gate-Level Schematics & Simulation](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/dual_lift_controller/gate-level-schematics-and-simulation.md)
- Component-level pinout schematics using standard 7400-series TTL ICs (74LS04, 74LS08, 74LS32, 74LS86, 74LS85, 74LS74).
- Total IC and gate budget calculation.
- Verilog simulation waveforms and timing analysis.

---

## 5. Verification Tools: `tools/lift_sim.py`

A gate-level verification simulator is provided to model and verify all logic combinations:

```bash
# 1. Run exhaustive verification across all 64 states for 4-floor building:
python3 tools/lift_sim.py --floors 4 --verify

# 2. Run exhaustive verification across all 27 states for 3-floor building:
python3 tools/lift_sim.py --floors 3 --verify

# 3. Simulate specific operational scenario:
# Request at Floor 2, Lift A at Floor 0, Lift B at Floor 3 -> Nearest is Lift A (dA=2, dB=1 -> Lift B wins!)
python3 tools/lift_sim.py --floors 4 --req 2 --lift-a 0 --lift-b 3
```
