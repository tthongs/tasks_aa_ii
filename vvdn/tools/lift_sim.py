#!/usr/bin/env python3
"""
Dual Lift Controller: Gate-Level Logic Simulation & Verification Tool
VVDN Engineering Hub - Digital Logic Design Toolkit

Simulates and verifies gate-level combinational and sequential logic for
dispatching the nearest lift in 3-floor and 4-floor buildings.

Usage:
    # 1. Simulate specific request scenario:
    python3 tools/lift_sim.py --floors 4 --req 2 --lift-a 0 --lift-b 3

    # 2. Run exhaustive truth table verification for 3-floor system (27 states):
    python3 tools/lift_sim.py --floors 3 --verify

    # 3. Run exhaustive truth table verification for 4-floor system (64 states):
    python3 tools/lift_sim.py --floors 4 --verify
"""

import argparse
import sys

def gate_abs_diff(x1, x0, y1, y0):
    """Gate-level 2-bit absolute difference: |X - Y|"""
    # d0 = x0 ^ y0
    d0 = x0 ^ y0
    # d1 = x1 & ~y1 & (~y0 | x0) | ~x1 & y1 & (~x0 | y0)
    d1 = (x1 and not y1 and (not y0 or x0)) or (not x1 and y1 and (not x0 or y0))
    return int(d1), int(d0)

def gate_comparator(a1, a0, b1, b0):
    """Gate-level 2-bit magnitude comparator"""
    # Equality: EQ = (a1 ~^ b1) & (a0 ~^ b0)
    eq = not (a1 ^ b1) and not (a0 ^ b0)
    # Greater Than: GT = a1 & ~b1 | (a1 ~^ b1) & a0 & ~b0
    gt = (a1 and not b1) or (not (a1 ^ b1) and a0 and not b0)
    # Less Than: LT = ~a1 & b1 | (a1 ~^ b1) & ~a0 & b0
    lt = (not a1 and b1) or (not (a1 ^ b1) and not a0 and b0)
    return int(gt), int(eq), int(lt)

def gate_nearest_lift_dispatch(r_val, a_val, b_val):
    """
    Computes nearest lift selection using pure gate equations.
    r_val, a_val, b_val are integers 0..3
    """
    r1, r0 = (r_val >> 1) & 1, r_val & 1
    a1, a0 = (a_val >> 1) & 1, a_val & 1
    b1, b0 = (b_val >> 1) & 1, b_val & 1

    # Distance dA = |R - A|
    da1, da0 = gate_abs_diff(r1, r0, a1, a0)
    # Distance dB = |R - B|
    db1, db0 = gate_abs_diff(r1, r0, b1, b0)

    # Compare dA and dB
    gt, eq, lt = gate_comparator(da1, da0, db1, db0)

    # Dispatch:
    # If dA < dB (lt=1) -> Lift A
    # If dA > dB (gt=1) -> Lift B
    # If dA == dB (eq=1) -> Default to Lift A (tie-break rule)
    sel_a = lt or eq
    sel_b = gt

    # Direction Logic for Lift A
    gt_a, eq_a, lt_a = gate_comparator(r1, r0, a1, a0)
    up_a = sel_a and gt_a
    down_a = sel_a and lt_a
    stop_a = eq_a or not sel_a

    # Direction Logic for Lift B
    gt_b, eq_b, lt_b = gate_comparator(r1, r0, b1, b0)
    up_b = sel_b and gt_b
    down_b = sel_b and lt_b
    stop_b = eq_b or not sel_b

    return {
        "dA": (da1 << 1) | da0,
        "dB": (db1 << 1) | db0,
        "sel_a": int(sel_a),
        "sel_b": int(sel_b),
        "up_a": int(up_a),
        "down_a": int(down_a),
        "stop_a": int(stop_a),
        "up_b": int(up_b),
        "down_b": int(down_b),
        "stop_b": int(stop_b),
    }

def main():
    parser = argparse.ArgumentParser(description="Dual Lift Nearest Dispatch Gate Simulation")
    parser.add_argument("--floors", type=int, choices=[3, 4], default=4, help="Number of floors (3 or 4)")
    parser.add_argument("--req", type=int, default=2, help="Requested floor")
    parser.add_argument("--lift-a", type=int, default=0, help="Current floor of Lift A")
    parser.add_argument("--lift-b", type=int, default=3, help="Current floor of Lift B")
    parser.add_argument("--verify", action="store_true", help="Run exhaustive verification across all states")
    args = parser.parse_args()

    max_f = args.floors
    print("=" * 75)
    print(f"   VVDN DUAL LIFT CONTROLLER: GATE-LEVEL SIMULATION REPORT ({max_f}-FLOOR)")
    print("=" * 75)

    if args.verify:
        print(f"Running exhaustive gate-level verification for {max_f}-floor building...")
        total_states = max_f ** 3
        correct = 0
        print("-" * 75)
        print(f"{'Req':^5} | {'Lift A':^6} | {'Lift B':^6} | {'dA':^4} | {'dB':^4} | {'Winner':^8} | {'Act A':^7} | {'Act B':^7}")
        print("-" * 75)
        for r in range(max_f):
            for a in range(max_f):
                for b in range(max_f):
                    res = gate_nearest_lift_dispatch(r, a, b)
                    da_expected = abs(r - a)
                    db_expected = abs(r - b)
                    assert res["dA"] == da_expected and res["dB"] == db_expected

                    winner = "Lift A" if res["sel_a"] else "Lift B"
                    act_a = "UP" if res["up_a"] else ("DOWN" if res["down_a"] else "STOP")
                    act_b = "UP" if res["up_b"] else ("DOWN" if res["down_b"] else "STOP")

                    # Verify nearest selection
                    if da_expected < db_expected:
                        assert res["sel_a"] == 1 and res["sel_b"] == 0
                    elif db_expected < da_expected:
                        assert res["sel_b"] == 1 and res["sel_a"] == 0
                    else: # tie
                        assert res["sel_a"] == 1

                    correct += 1
                    print(f"{r:^5} | {a:^6} | {b:^6} | {res['dA']:^4} | {res['dB']:^4} | {winner:^8} | {act_a:^7} | {act_b:^7}")
        print("-" * 75)
        print(f"✓ Verification Passed: {correct}/{total_states} states strictly verified against distance rule!")
    else:
        r, a, b = args.req, args.lift_a, args.lift_b
        if not (0 <= r < max_f and 0 <= a < max_f and 0 <= b < max_f):
            print(f"Error: Floor inputs must be in range 0 to {max_f - 1}")
            sys.exit(1)

        res = gate_nearest_lift_dispatch(r, a, b)
        print(f"Current State:")
        print(f"  • Floor Request (R) : Floor {r} (Binary: {r:02b})")
        print(f"  • Lift A Position   : Floor {a} (Binary: {a:02b})")
        print(f"  • Lift B Position   : Floor {b} (Binary: {b:02b})")
        print("-" * 75)
        print(f"Gate Distance Calculations:")
        print(f"  • Distance dA = |R - A| : {res['dA']} floors (Binary: {res['dA']:02b})")
        print(f"  • Distance dB = |R - B| : {res['dB']} floors (Binary: {res['dB']:02b})")
        print("-" * 75)
        winner = "LIFT A" if res["sel_a"] else "LIFT B"
        print(f"Arbitration Result:")
        print(f"  • Nearest Lift Selected : {winner} (SEL_A = {res['sel_a']}, SEL_B = {res['sel_b']})")
        if res["dA"] == res["dB"]:
            print(f"  • Note                  : Equidistant tie (dA == dB); resolved to Lift A by default tie-break.")

        print("-" * 75)
        print(f"Motor Actions Generated:")
        act_a = "UP" if res["up_a"] else ("DOWN" if res["down_a"] else "STOP (Door Open)")
        act_b = "UP" if res["up_b"] else ("DOWN" if res["down_b"] else "STOP (Idle / Door Closed)")
        print(f"  • Lift A Motor : {act_a} (UP_A={res['up_a']}, DOWN_A={res['down_a']}, STOP_A={res['stop_a']})")
        print(f"  • Lift B Motor : {act_b} (UP_B={res['up_b']}, DOWN_B={res['down_b']}, STOP_B={res['stop_b']})")
    print("=" * 75)

if __name__ == "__main__":
    main()
