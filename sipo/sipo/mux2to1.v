module bcd_to_seven_segment (
    input [3:0] bcd_data,      // 4-bit BCD input
    output reg [6:0] seg       // 8-bit output for seven-segment display
);

    always @(*) begin
        case (bcd_data)
            4'b0000: seg = 7'b1111110; // 0
            4'b0001: seg = 7'b0110000; // 1
            4'b0010: seg = 7'b1101101; // 2
            4'b0011: seg = 7'b1111001; // 3
            4'b0100: seg = 7'b0110010; // 4
            4'b0101: seg = 7'b1011011; // 5
            4'b0110: seg = 7'b1011111; // 6
            4'b0111: seg = 7'b1110000; // 7
            4'b1000: seg = 7'b1111111; // 8
            4'b1001: seg = 7'b1110011; // 9
            default: seg = 7'b1111111; // Off for invalid BCD
        endcase
    end
endmodule

module mux2to1 (
    input [3:0] Latch_Q_LSB,         // 4-bit input 0
    input [3:0] Latch_Q_MSB,         // 4-bit input 1
    input lsb_sel,                   // Selection line
    output [3:0] bcd_data,           // 4-bit output
    output [6:0] uo_out,
    input wire clk    // 8-bit output for seven-segment display
);
    wire [3:0] y_internal;

    // Generate 4 instances of the 1-bit mux
    genvar i;
    generate
        for (i = 0; i < 4; i = i + 1) begin : mux_loop
            sky130_fd_sc_hd__udp_mux_2to1 mux_instance (
                .X(y_internal[i]),          // Output for the specific bit
                .A0(Latch_Q_LSB[i]),       // i0 for the specific bit
                .A1(Latch_Q_MSB[i]),       // i1 for the specific bit
                .S(lsb_sel)                 // Select line
            );
        end
    endgenerate

    // Assign the internal output to the final output
    assign bcd_data = y_internal;

    // Instantiate the BCD to seven-segment converter
    bcd_to_seven_segment bcd_display (
        .bcd_data(bcd_data), // Connect bcd_data to the converter
        .seg(uo_out)         // Connect the output to uo_out
    );

endmodule
