// Integrated Design File

// Main SIPO with Latch and MUX to 7-Segment Display

module sipo_with_latch_mux (
    input CS,                      // Chip Select (Active Low)
    input SC,                      // Serial Clock
    input RESET_N,                 // Reset (Active Low)
    input D,                       // Serial Data Input
    input lsb_sel,                 // Selection for LSB/MSB
    input clk,                     // Clock for mux2to1
    output [7:0] Latch_Q,          // 8-bit output from the latch
    output [6:0] uo_out,            // Seven-segment display output
    output [15:0] SIPO_Q           //new output port for sipo_q
);

    wire [15:0] SIPO_Q;            // Output from the SIPO shift register
    wire [7:0] MSB_Q;              // Upper 8 bits of SIPO output
    wire [7:0] shifted_data;       // Left shifted data
    wire [3:0] Latch_Q_LSB;        // 4-bit LSB output from latch
    wire [3:0] Latch_Q_MSB;        // 4-bit MSB output from latch
    wire [3:0] bcd_data;           // BCD data for 7-segment display

    // Instantiate the 16-bit SIPO shift register
    sipo_shift_register sipo_inst (
        .CS(CS),
        .SC(SC),
        .RESET_N(RESET_N),
        .D(D),
        .Q(SIPO_Q) //connect to the new output port
    );

    // Assign the upper 8 bits of SIPO output
    assign MSB_Q = SIPO_Q[15:8];  // Get the First 8 bit MSBs
    // Left shift the MSBs by 1
    assign shifted_data = {MSB_Q[6:0], 1'b0}; // Left shift by 1

    // Instantiate the 8-bit D latch
    async_active_low_reset_dlatch_8bit latch_inst (
        .Q(Latch_Q),
        .Data_in(shifted_data),   // Connect the shifted data to the latch
        .CS(CS),
        .RESET_N(RESET_N),
        .SC(SC)
    );

    // Separate the Latch_Q into 4-bit LSB and MSB
    assign Latch_Q_LSB = Latch_Q[3:0]; // Lower 4 bits
    assign Latch_Q_MSB = Latch_Q[7:4]; // Upper 4 bits

    // Instantiate the 2-to-1 MUX and BCD to Seven-Segment converter
    mux2to1 mux_display (
        .Latch_Q_LSB(Latch_Q_LSB), // 4-bit LSB input
        .Latch_Q_MSB(Latch_Q_MSB), // 4-bit MSB input
        .lsb_sel(lsb_sel),         // Selection line
        .bcd_data(bcd_data),       // 4-bit output for BCD
        .uo_out(uo_out),           // Seven-segment display output
        .clk(clk)
    );

endmodule


// SIPO Shift Register Module
module sipo_shift_register (
    input CS,                   // Chip Select (Active Low)
    input SC,                   // Serial Clock
    input RESET_N,              // Reset (Active Low)
    input D,                    // Serial Data Input
    output reg [15:0] Q         // Parallel Output
);

    wire [15:0] dff_q;           // Internal D flip-flop outputs

    // Instantiate 16 active-low reset D flip-flops
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin: dff_inst
            if (i == 0) begin
                sky130_fd_sc_hd__udp_dff$PR dff (
                    .Q(dff_q[i]),
                    .D(D),
                    .CLK(SC),
                    .RESET(~RESET_N)  // RESET_N active-low
                );
            end
            else begin
                sky130_fd_sc_hd__udp_dff$PR dff (
                    .Q(dff_q[i]),
                    .D(dff_q[i-1]),   // Connect to previous DFF's Q
                    .CLK(SC),
                    .RESET(~RESET_N)  // RESET_N active-low
                );
            end
        end
    endgenerate

    // Assign the parallel output Q
    always @(posedge SC or posedge RESET_N) begin
        if (!RESET_N)
            Q <= 16'b0;           // Reset the parallel output on active-low reset
        else if (!CS)             // Only shift if Chip Select is active
            Q <= dff_q;           // Update the parallel output
    end
endmodule


// 8-bit D Latch Module
module async_active_low_reset_dlatch_8bit (
    output [7:0] Q,               // 8-bit output
    input [7:0] Data_in,          // 8-bit data input
    input CS,                     // Chip select (active low)
    input RESET_N,                // Active-low reset
    input SC                      // Serial clock
);
    // Generate 8 instances of the D latch
    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : dlatch_instance
            sky130_fd_sc_hd__udp_dlatch$PR dlatch_inst (
                .Q(Q[i]),
                .D(Data_in[i]),
                .GATE(~CS),
                .RESET(~RESET_N)    // RESET_N active-low
            );
        end
    endgenerate
endmodule


// BCD to Seven Segment Display Converter
module bcd_to_seven_segment (
    input [3:0] bcd_data,        // 4-bit BCD input
    output reg [6:0] seg         // 7-segment display output
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


// 2-to-1 MUX Module with Seven Segment Display
module mux2to1 (
    input [3:0] Latch_Q_LSB,      // 4-bit LSB input
    input [3:0] Latch_Q_MSB,      // 4-bit MSB input
    input lsb_sel,                // Selection line
    output [3:0] bcd_data,        // 4-bit output for BCD
    output [6:0] uo_out,          // Seven-segment display output
    input clk
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
                .S(lsb_sel)                // Select line
            );
        end
    endgenerate

    // Assign the internal output to the final output
    assign bcd_data = y_internal;

    // Instantiate the BCD to seven-segment converter
    bcd_to_seven_segment bcd_display (
        .bcd_data(bcd_data),     // Connect bcd_data to the converter
        .seg(uo_out)             // Connect the output to uo_out
    );

endmodule

