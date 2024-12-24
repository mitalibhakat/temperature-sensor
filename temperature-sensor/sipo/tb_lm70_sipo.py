import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

# Testbench for the sipo_sr module
@cocotb.test()
async def tb_lm70_sipo(dut):
    # Clock and Reset setup
    clock = Clock(dut.SC, 10, units="ns")  # Clock period is 10 ns (i.e., 100MHz)
    cocotb.fork(clock.start())  # Start clock
    
    # Initialize signals
    dut.CS.value = 1
    dut.RESET_N.value = 0
    dut.SIO.value = 0
    
    lm70_data = 0b0000100101111111  # LM70 data to shift
    
    # Apply reset
    dut.RESET_N.value = 0
    await Timer(9.5, units="ns")  # Simulate for 9.5 ns
    dut.RESET_N.value = 1
    await Timer(2, units="ns")  # Wait for 2 ns
    dut.CS.value = 0  # Start communication
    
    # Bitwise data shifting
    for i in range(15, -1, -1):
        dut.SIO.value = (lm70_data >> i) & 1  # Shift out each bit
        await Timer(10, units="ns")  # Delay between bits

    # End transmission
    dut.CS.value = 1
    dut.RESET_N.value = 0
    await Timer(20, units="ns")

    # Optional: Monitor output
    dut._log.info(f"Shifted data: {bin(lm70_data)}")
    dut._log.info(f"SIPO Output: {dut.sipo_Q.value}")

