import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
import logging

# Test the 16-bit shift register
@cocotb.test()
async def test_shift_register_16bit(dut):
    """Test for 16-bit SIPO Shift Register"""
    
    # Create a clock on the SC (Shift Clock) signal
    cocotb.start_soon(Clock(dut.SC, 10, units="ns").start())  # 10 ns clock period

    # Initial conditions
    dut.RESET_N.value = 0 
    dut.d_in.value = 0

    # Apply reset
    dut.RESET_N.value = 0  #assert reset
    await Timer(20, units='ns')  # Wait for 10 ns
    dut.RESET_N.value = 1        # Release reset

    # Shift in the 16-bit serial data sequence: 1011011000110101
    data_sequence = [1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1]
    
    for bit in data_sequence:
        dut.d_in.value = bit
        await RisingEdge(dut.SC)  # Wait for the rising edge of the clock

    # Give time for the output to propagate and observe the result
    await Timer(10, units='ns')

    # Expected output (after shifting in the bits)
    expected_output = int("1011011000110101", 2)

    # Check if the output matches the expected value
    assert dut.Q.value == expected_output, f"Reset failed: Q = {dut.Q.value}, expected {expected_output}"

    # Log the successful test completion
    dut._log.info(f"Test Passed: Q = {dut.Q.value}, expected {expected_output}")

