module sipo_sr (
    input SC,          // Serial Clock
    input CS,          // Chip Select (active low)
    input RESET_N,     // Reset (active low)
    input SIO,         // Serial data in
    output reg [15:0] sipo_Q  // Parallel output
);

 initial begin
        $dumpfile("dump.vcd");
        $dumpvars(1,sipo_sr);
    end



    always @(negedge SC or posedge RESET_N) begin
        if (!CS)
        begin
            sipo_Q <= {sipo_Q[14:0], SIO};  // Clear all outputs on reset
        end
        else
                if (!RESET_N)
                begin
            sipo_Q <= 16'd0;  // Shift in the SIO data at each negative edge of SC
                end
    end
endmodule
