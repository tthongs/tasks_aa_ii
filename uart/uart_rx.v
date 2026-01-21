```verilog
module uart_rx #(
    parameter CLKS_PER_BIT = 5208 // 50,000,000 / 9600
) (
    input clk,
    input rst,
    input rx,
    output reg [7:0] rx_data,
    output reg rx_done
);

    reg [3:0] state = 0;
    reg [CLKS_PER_BIT-1:0] clk_counter = 0;
    reg [3:0] bit_counter = 0;
    reg [7:0] data_reg = 0;

    always @(posedge clk) begin
        if (rst) begin
            state <= 0;
            clk_counter <= 0;
            bit_counter <= 0;
            data_reg <= 0;
            rx_done <= 0;
        end else begin
            case (state)
                0: begin // Idle
                    if (rx == 0) begin
                        state <= 1;
                        clk_counter <= 0;
                    end
                end
                1: begin // Start bit
                    if (clk_counter == CLKS_PER_BIT / 2) begin
                        if (rx == 0) begin
                            clk_counter <= 0;
                            state <= 2;
                        end else begin
                            state <= 0;
                        end
                    end else begin
                        clk_counter <= clk_counter + 1;
                    end
                end
                2: begin // Data bits
                    if (clk_counter == CLKS_PER_BIT - 1) begin
                        clk_counter <= 0;
                        data_reg[bit_counter] <= rx;
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
                    if (clk_counter == CLKS_PER_BIT - 1) begin
                        clk_counter <= 0;
                        rx_data <= data_reg;
                        rx_done <= 1;
                        state <= 0;
                    end else begin
                        clk_counter <= clk_counter + 1;
                    end
                end
            endcase
            if (state != 3) begin
                rx_done <= 0;
            end
        end
    end

endmodule
```
