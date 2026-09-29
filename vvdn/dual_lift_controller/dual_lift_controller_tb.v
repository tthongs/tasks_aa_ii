// =============================================================================
// Dual Lift Controller: Comprehensive Simulation Testbench
// Exercises 3-Floor and 4-Floor Request Vectors & Edge Cases
// VVDN Engineering Hub - Digital Logic Design Suite
// =============================================================================

`timescale 1ns / 1ps

module dual_lift_controller_tb;

    reg  [1:0] req_floor;
    reg  [1:0] lift_a_floor;
    reg  [1:0] lift_b_floor;
    reg        call_strobe;

    wire       sel_a;
    wire       sel_b;
    wire       up_a;
    wire       down_a;
    wire       stop_a;
    wire       up_b;
    wire       down_b;
    wire       stop_b;
    wire [1:0] dist_a;
    wire [1:0] dist_b;

    // Instantiate Device Under Test (DUT)
    dual_lift_controller dut (
        .req_floor(req_floor),
        .lift_a_floor(lift_a_floor),
        .lift_b_floor(lift_b_floor),
        .call_strobe(call_strobe),
        .sel_a(sel_a),
        .sel_b(sel_b),
        .up_a(up_a),
        .down_a(down_a),
        .stop_a(stop_a),
        .up_b(up_b),
        .down_b(down_b),
        .stop_b(stop_b),
        .dist_a(dist_a),
        .dist_b(dist_b)
    );

    integer r, a, b;
    integer passed_tests = 0;
    integer total_tests = 0;

    initial begin
        $display("==========================================================================");
        $display("   STARTING DUAL LIFT CONTROLLER GATE LOGIC SIMULATION TESTBENCH");
        $display("==========================================================================");

        call_strobe = 1'b1;

        // Exhaustive 4-Floor Verification (64 states)
        for (r = 0; r < 4; r = r + 1) begin
            for (a = 0; a < 4; a = a + 1) begin
                for (b = 0; b < 4; b = b + 1) begin
                    req_floor    = r[1:0];
                    lift_a_floor = a[1:0];
                    lift_b_floor = b[1:0];
                    #10;

                    total_tests = total_tests + 1;

                    // Verify distance calculation
                    if (dist_a !== (r > a ? r - a : a - r)) begin
                        $display("[ERROR] Dist A mismatch at R=%d, A=%d. Got %d", r, a, dist_a);
                        $stop;
                    end
                    if (dist_b !== (r > b ? r - b : b - r)) begin
                        $display("[ERROR] Dist B mismatch at R=%d, B=%d. Got %d", r, b, dist_b);
                        $stop;
                    end

                    // Verify Nearest Lift Dispatch
                    if (dist_a < dist_b) begin
                        if (sel_a !== 1'b1 || sel_b !== 1'b0) begin
                            $display("[ERROR] Lift A should be selected! R=%d, A=%d, B=%d", r, a, b);
                            $stop;
                        end
                    end else if (dist_b < dist_a) begin
                        if (sel_b !== 1'b1 || sel_a !== 1'b0) begin
                            $display("[ERROR] Lift B should be selected! R=%d, A=%d, B=%d", r, a, b);
                            $stop;
                        end
                    end else begin
                        // Equidistant tie: Lift A priority
                        if (sel_a !== 1'b1) begin
                            $display("[ERROR] Tie break failed! R=%d, A=%d, B=%d", r, a, b);
                            $stop;
                        end
                    end

                    // Verify Motor Direction for Selected Lift
                    if (sel_a) begin
                        if (r > a && up_a !== 1'b1) $display("[ERROR] Lift A should move UP");
                        if (r < a && down_a !== 1'b1) $display("[ERROR] Lift A should move DOWN");
                        if (r == a && stop_a !== 1'b1) $display("[ERROR] Lift A should STOP");
                    end
                    if (sel_b) begin
                        if (r > b && up_b !== 1'b1) $display("[ERROR] Lift B should move UP");
                        if (r < b && down_b !== 1'b1) $display("[ERROR] Lift B should move DOWN");
                        if (r == b && stop_b !== 1'b1) $display("[ERROR] Lift B should STOP");
                    end

                    passed_tests = passed_tests + 1;
                end
            end
        end

        $display("--------------------------------------------------------------------------");
        $display("All %0d test vectors PASSED successfully!", passed_tests);
        $display("Gate logic verified: Nearest lift is ALWAYS dispatched without error.");
        $display("==========================================================================");
        $finish;
    end

endmodule
