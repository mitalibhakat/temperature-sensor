// DESIGN

module sipo_with_latch (
    input CS,                   // Chip Select (Active Low)
    input SC,                   // Serial Clock
    input RESET_N,              // Reset (Active Low)
    input D,                    // Serial Data Input
    output [7:0] Latch_Q,        // 8-bit output from the latch
    output reg [3:0] Latch_Q_LSB, // 4-bit LSB output
    output reg [3:0] Latch_Q_MSB  // 4-bit MSB output
);

    wire [15:0] SIPO_Q;         // Output from the SIPO shift register
    wire [7:0] MSB_Q;           // Upper 8 bits of SIPO output
    wire [7:0] shifted_data;    // Left shifted data

    // Instantiate the 16-bit SIPO shift register
    sipo_shift_register sipo_inst (
        .CS(CS),
        .SC(SC),
        .RESET_N(RESET_N),
        .D(D),
        .Q(SIPO_Q)
    );

    // Assign the upper 8 bits of SIPO output
    assign MSB_Q = SIPO_Q[15:8]; // Get the First 8 bit MSBs
    // Left shift the MSBs by 1
    assign shifted_data = {MSB_Q[6:0], 1'b0}; // Left shift by 1

    // Instantiate the 8-bit D latch
    async_active_low_reset_dlatch_8bit latch_inst (
        .Q(Latch_Q),
        .Data_in(shifted_data),  // Connect the shifted data to the latch
        .CS(CS),
        .RESET_N(RESET_N),
        .SC(SC)
    );

    // Separate the Latch_Q into 4-bit LSB and MSB
    always @(Latch_Q) begin
        Latch_Q_LSB = Latch_Q[3:0]; // Lower 4 bits
        Latch_Q_MSB = Latch_Q[7:4]; // Upper 4 bits
    end
//endmodule
//Dump file setup for GTKWAVE
initial begin 
	$dumpfile("sipo_with_latch.vcd");
	$dumpvars(0,sipo_with_latch);
end
endmodule 



// 1. SIPO Shift Register Module
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
            else
            begin
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


// 2. 8-bit D Latch Module
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

