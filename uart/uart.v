```verilog
module uart #(
    parameter CLKS_PER_BIT = 5208 // 50,000,000 / 9600
) (
    input clk,
    input rst,
    input rx,
    output tx,
    input tx_start,
    input [7:0] tx_data,
    output tx_busy,
    output reg [7:0] rx_data,
    output reg rx_done
);

    wire [7:0] rx_data_wire;
    wire rx_done_wire;

    uart_tx #(.CLKS_PER_BIT(CLKS_PER_BIT)) tx_inst (
        .clk(clk),
        .rst(rst),
        .tx_start(tx_start),
        .tx_data(tx_data),
        .tx(tx),
        .tx_busy(tx_busy)
    );

    uart_rx #(.CLKS_PER_BIT(CLKS_PER_BIT)) rx_inst (
        .clk(clk),
        .rst(rst),
        .rx(rx),
        .rx_data(rx_data_wire),
        .rx_done(rx_done_wire)
    );

    always @(posedge clk) begin
        if (rst) begin
            rx_data <= 0;
            rx_done <= 0;
        end else begin
            rx_data <= rx_data_wire;
            rx_done <= rx_done_wire;
        end
    end

endmodule
```
