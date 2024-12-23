import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.result import TestFailure

class LM70:
    """Dummy model for the LM70 temperature sensor"""

    def __init__(self, dut):
        self.dut = dut

    async def drive_temp_data(self, temp_value):
        """Drives 16-bit temperature data to the SIPO"""
        temp_bits = f"{temp_value:016b}"  # Convert the temperature value to a 16-bit binary string
        for bit in temp_bits:
            self.dut.D.value = int(bit)  # Drive each bit serially on D pin
            await Timer(1, units="ns")  # Allow time for signal to settle
            await RisingEdge(self.dut.SC)  # Wait for the rising edge of SC

async def clock_gen(dut):
    """Generates a clock signal for the SC and clk signals."""
    while True:
        dut.SC.value = 0
        await Timer(5, units='ns')
        dut.SC.value = 1
        await Timer(5, units='ns')

# Testbench for the integrated SIPO with latch and MUX design
@cocotb.test()
async def test_sipo_with_latch_mux(dut):
    """Integrated test for SIPO with latch and 2-to-1 MUX"""

    # Start clock generator for SC signal
    cocotb.start_soon(clock_gen(dut))

    # Create an instance of the LM70 model
    lm70 = LM70(dut)

    # Initial reset and CS high to disable SIPO and latch
    dut.RESET_N.value = 0
    dut.CS.value = 1
    dut.D.value = 0  # Data input

    # Apply reset for a few cycles
    await Timer(20, units="ns")

    # Release reset and enable the system (CS = 0)
    dut.RESET_N.value = 1
    await Timer(1, units="ns")  # Small delay before starting the clock

    # Set a specific temperature value for LM70 model (example: 26.75°C in binary)
    temp_value = 0b0010011001111111
    await lm70.drive_temp_data(temp_value)  # Send 16-bit data serially via LM70

    # After shifting all bits, latch the data by setting CS high
    dut.CS.value = 1
    await Timer(10, units="ns")

    # Check latched output (left-shifted MSB) and compare with expected
    sipo_output = dut.SIPO_Q.value.integer
    msbs = (sipo_output >> 8) & 0xFF  # Extract upper 8 bits (MSBs)
    shifted_msbs = (msbs << 1) & 0xFF  # Left shift by 1
    latch_output = dut.Latch_Q.value.integer

    # Log and verify latched data
    dut._log.info(f"Original MSBs = {bin(msbs)}, Shifted MSBs = {bin(shifted_msbs)}, Latched output = {bin(latch_output)}")
    assert latch_output == shifted_msbs, f"Test failed! Latch_Q = {bin(latch_output)}, expected = {bin(shifted_msbs)}"

    # Test case 1: Select Latch_Q_LSB with lsb_sel = 0
    dut.Latch_Q_LSB.value = 0b0010  # LSB in binary
    dut.Latch_Q_MSB.value = 0b0001  # MSB in binary
    dut.lsb_sel.value = 0           # Select LSB
    await Timer(10, units="ns")     # Allow signal propagation

    # Check if BCD and seven-segment outputs match for LSB selection
    assert dut.bcd_data.value == 0b0010, "Output mismatch for Latch_Q_LSB"
    assert dut.uo_out.value == 0b1101101, "Seven-segment mismatch for BCD 2"

    # Test case 2: Select Latch_Q_MSB with lsb_sel = 1
    dut.lsb_sel.value = 1  # Select MSB
    await Timer(10, units="ns")

    # Check if BCD and seven-segment outputs match for MSB selection
    assert dut.bcd_data.value == 0b0001, "Output mismatch for Latch_Q_MSB"
    assert dut.uo_out.value == 0b0110000, "Seven-segment mismatch for BCD 1"

    # Log successful completion
    dut._log.info("Integrated test completed successfully.")

# Run the test using TestFactory
factory = TestFactory(test_sipo_with_latch_mux)
factory.generate_tests()

