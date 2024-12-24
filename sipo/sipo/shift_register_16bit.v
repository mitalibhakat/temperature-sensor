module shift_register_16bit (
    input SC,
    input RESET_N,
    input d_in,
    output reg [15:0] Q
);
    always @(posedge SC or negedge RESET_N) begin
        if (!RESET_N)
            Q <= 16'b0;
        else
            Q <= {Q[14:0], d_in};
    end
endmodule
/bin/bash: line 1: wq: command not found
