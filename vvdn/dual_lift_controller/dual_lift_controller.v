// =============================================================================
// Dual Lift Controller: Gate-Level & Structural Verilog Implementation
// Designed for 3-Floor or 4-Floor Buildings with Nearest Lift Dispatch
// VVDN Engineering Hub - Digital Logic Design Suite
// =============================================================================

`timescale 1ns / 1ps

// -----------------------------------------------------------------------------
// Sub-Module 1: 2-Bit Absolute Difference Subtractor (|X - Y|)
// Computes D1, D0 = |X - Y| using minimal logic gates.
// D0 = X0 ^ Y0
// D1 = (X1 & ~Y1 & (~Y0 | X0)) | (~X1 & Y1 & (~X0 | Y0))
// -----------------------------------------------------------------------------
module abs_diff_2bit (
    input  wire x1, x0,
    input  wire y1, y0,
    output wire d1, d0
);
    // Wire declarations for internal gate connections
    wire not_x1, not_x0, not_y1, not_y0;
    wire term1_cond, term2_cond;
    wire term1, term2;

    // Inverters
    not (not_x1, x1);
    not (not_x0, x0);
    not (not_y1, y1);
    not (not_y0, y0);

    // LSB is pure XOR
    xor (d0, x0, y0);

    // MSB Logic
    or  (term1_cond, not_y0, x0);
    and (term1, x1, not_y1, term1_cond);

    or  (term2_cond, not_x0, y0);
    and (term2, not_x1, y1, term2_cond);

    or  (d1, term1, term2);

endmodule


// -----------------------------------------------------------------------------
// Sub-Module 2: 2-Bit Magnitude Comparator
// Compares two 2-bit numbers P and Q.
// Outputs: GT (P > Q), EQ (P == Q), LT (P < Q)
// -----------------------------------------------------------------------------
module comparator_2bit (
    input  wire p1, p0,
    input  wire q1, q0,
    output wire gt,
    output wire eq,
    output wire lt
);
    wire not_p1, not_p0, not_q1, not_q0;
    wire eq1, eq0;
    wire gt_lsb, lt_lsb;

    not (not_p1, p1);
    not (not_p0, p0);
    not (not_q1, q1);
    not_q0_gate: not (not_q0, q0);

    // Bit-wise equivalence using XNOR
    xnor (eq1, p1, q1);
    xnor (eq0, p0, q0);

    // Equality: Both bit 1 and bit 0 are equal
    and  (eq, eq1, eq0);

    // Greater Than: (p1 & ~q1) | (eq1 & p0 & ~q0)
    and  (gt_lsb, eq1, p0, not_q0);
    or   (gt, (p1 & not_q1), gt_lsb);

    // Less Than: (~p1 & q1) | (eq1 & ~p0 & q0)
    and  (lt_lsb, eq1, not_p0, q0);
    or   (lt, (not_p1 & q1), lt_lsb);

endmodule


// -----------------------------------------------------------------------------
// Sub-Module 3: Direction & Motor Drive Gate Unit
// Generates UP, DOWN, and STOP commands for a single lift car.
// -----------------------------------------------------------------------------
module lift_direction_gates (
    input  wire sel,       // Lift Select Enable
    input  wire gt,        // Request > Current Floor
    input  wire eq,        // Request == Current Floor
    input  wire lt,        // Request < Current Floor
    output wire up,
    output wire down,
    output wire stop
);
    wire not_sel;
    not (not_sel, sel);

    // UP only if selected and Request > Current Floor
    and (up, sel, gt);

    // DOWN only if selected and Request < Current Floor
    and (down, sel, lt);

    // STOP if at requested floor OR lift is not selected
    or  (stop, eq, not_sel);

endmodule


// -----------------------------------------------------------------------------
// Top-Level Module: Dual Lift Controller
// Dispatches nearest lift to the requested floor.
// Supports 3-floor (0..2) and 4-floor (0..3) operation.
// -----------------------------------------------------------------------------
module dual_lift_controller (
    input  wire [1:0] req_floor,    // Target Request Floor (2-bit binary: 00, 01, 10, 11)
    input  wire [1:0] lift_a_floor, // Lift A Current Position (2-bit binary)
    input  wire [1:0] lift_b_floor, // Lift B Current Position (2-bit binary)
    input  wire       call_strobe,  // 1 when a call button is pressed
    output wire       sel_a,        // 1 = Lift A Dispatched
    output wire       sel_b,        // 1 = Lift B Dispatched
    output wire       up_a,         // Lift A Move UP
    output wire       down_a,       // Lift A Move DOWN
    output wire       stop_a,       // Lift A STOP / Idle
    output wire       up_b,         // Lift B Move UP
    output wire       down_b,       // Lift B Move DOWN
    output wire       stop_b,       // Lift B STOP / Idle
    output wire [1:0] dist_a,       // Computed Distance |R - A|
    output wire [1:0] dist_b        // Computed Distance |R - B|
);

    // Step 1: Distance Calculation for Lift A: dA = |R - A|
    abs_diff_2bit calc_dist_a (
        .x1(req_floor[1]), .x0(req_floor[0]),
        .y1(lift_a_floor[1]), .y0(lift_a_floor[0]),
        .d1(dist_a[1]), .d0(dist_a[0])
    );

    // Step 2: Distance Calculation for Lift B: dB = |R - B|
    abs_diff_2bit calc_dist_b (
        .x1(req_floor[1]), .x0(req_floor[0]),
        .y1(lift_b_floor[1]), .y0(lift_b_floor[0]),
        .d1(dist_b[1]), .d0(dist_b[0])
    );

    // Step 3: Distance Comparator: Compares dA and dB
    wire dist_gt, dist_eq, dist_lt;
    comparator_2bit comp_distances (
        .p1(dist_a[1]), .p0(dist_a[0]),
        .q1(dist_b[1]), .q0(dist_b[0]),
        .gt(dist_gt), // dA > dB
        .eq(dist_eq), // dA == dB
        .lt(dist_lt)  // dA < dB
    );

    // Step 4: Nearest Lift Arbitration Logic
    // If dA < dB (dist_lt) -> Lift A is strictly closer
    // If dA > dB (dist_gt) -> Lift B is strictly closer
    // If dA == dB (dist_eq) -> Equidistant tie: Default to Lift A
    wire arb_sel_a, arb_sel_b;
    or  (arb_sel_a, dist_lt, dist_eq); // dA <= dB -> Lift A
    assign arb_sel_b = dist_gt;        // dB < dA  -> Lift B

    // Qualify selections with active call strobe
    and (sel_a, arb_sel_a, call_strobe);
    and (sel_b, arb_sel_b, call_strobe);

    // Step 5: Position vs Request Comparators for Direction Control
    wire gt_a, eq_a, lt_a;
    comparator_2bit comp_lift_a (
        .p1(req_floor[1]), .p0(req_floor[0]),
        .q1(lift_a_floor[1]), .q0(lift_a_floor[0]),
        .gt(gt_a), .eq(eq_a), .lt(lt_a)
    );

    wire gt_b, eq_b, lt_b;
    comparator_2bit comp_lift_b (
        .p1(req_floor[1]), .p0(req_floor[0]),
        .q1(lift_b_floor[1]), .q0(lift_b_floor[0]),
        .gt(gt_b), .eq(eq_b), .lt(lt_b)
    );

    // Step 6: Motor Motion Output Gates
    lift_direction_gates dir_a (
        .sel(sel_a), .gt(gt_a), .eq(eq_a), .lt(lt_a),
        .up(up_a), .down(down_a), .stop(stop_a)
    );

    lift_direction_gates dir_b (
        .sel(sel_b), .gt(gt_b), .eq(eq_b), .lt(lt_b),
        .up(up_b), .down(down_b), .stop(stop_b)
    );

endmodule
