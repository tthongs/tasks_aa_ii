```verilog
module uart_tx #(
    parameter CLKS_PER_BIT = 5208 // 50,000,000 / 9600
) (
    input clk,
    input rst,
    input tx_start,
    input [7:0] tx_data,
    output tx,
    output tx_busy
);

    reg [3:0] state = 0;
    reg [CLKS_PER_BIT-1:0] clk_counter = 0;
    reg [3:0] bit_counter = 0;
    reg [7:0] data_reg = 0;

    assign tx_busy = (state != 0);

    always @(posedge clk) begin
        if (rst) begin
            state <= 0;
            clk_counter <= 0;
            bit_counter <= 0;
            data_reg <= 0;
        end else begin
            case (state)
                0: begin // Idle
                    if (tx_start) begin
                        state <= 1;
                        data_reg <= tx_data;
                    end
                end
                1: begin // Start bit
                    tx <= 0;
                    if (clk_counter == CLKS_PER_BIT - 1) begin
                        clk_counter <= 0;
                        state <= 2;
                    end else begin
                        clk_counter <= clk_counter + 1;
                    end
                end
                2: begin // Data bits
                    tx <= data_reg[bit_counter];
                    if (clk_counter == CLKS_PER_BIT - 1) begin
                        clk_counter <= 0;
                        if (bit_counter == 7) begin
                            state <= 3;
                        end else begin
                            bit_counter <= bit_counter + 1;
                        end
                    end else begin
                        clk_counter <= clk_counter + 1;
                    end
                end
                3: begin // Stop bit
                    tx <= 1;
                    if (clk_counter == CLKS_PER_BIT - 1) begin
                        clk_counter <= 0;
                        state <= 0;
                    end else begin
                        clk_counter <= clk_counter + 1;
                    end
                end
            endcase
        end
    end

endmodule
```
