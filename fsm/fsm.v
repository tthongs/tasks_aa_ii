// A basic Moore FSM with a single input and single output
// This is a template to get you started.
// We can modify this based on your specific needs.

module fsm (
    input clk,
    input rst,
    input in,
    output out
);

// State declarations
localparam STATE_A = 0;
localparam STATE_B = 1;
localparam STATE_C = 2;

// State register
reg [1:0] state, next_state;

// Next state logic
always @(*) begin
    case (state)
        STATE_A: begin
            if (in)
                next_state = STATE_B;
            else
                next_state = STATE_A;
        end
        STATE_B: begin
            if (in)
                next_state = STATE_C;
            else
                next_state = STATE_A;
        end
        STATE_C: begin
            if (in)
                next_state = STATE_C;
            else
                next_state = STATE_A;
        end
        default: begin
            next_state = STATE_A;
        end
    endcase
end

// Output logic
assign out = (state == STATE_C);

// State transition
always @(posedge clk or posedge rst) begin
    if (rst)
        state <= STATE_A;
    else
        state <= next_state;
end

endmodule
