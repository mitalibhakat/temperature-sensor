import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
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

# Testbench for the sipo_with_latch module
@cocotb.test()
async def test_sipo_with_latch(dut):
    """Test SIPO with latch design"""

    # Create an instance of the LM70 model
    lm70 = LM70(dut)

    # Ensure SC is low before starting the clock
    dut.SC.value = 0

    # Apply initial reset and CS high to disable SIPO and latch
    dut.RESET_N.value = 0
    dut.CS.value = 1
    dut.D.value = 0  # Data input

    # Wait for a few cycles to apply reset with SC low
    await Timer(20, units="ns")

    # Release reset and enable the system (CS = 0) after ensuring SC is low
    dut.RESET_N.value = 1
    await Timer(1, units="ns")  # Small delay before starting the clock

    # Start a 10ns period clock on the SC (Serial Clock) signal
    clock = Clock(dut.SC, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Apply serial data input after enabling CS (CS = 0)
    dut.CS.value = 0

    # Set a specific temperature value for the LM70 model (16-bit example)
    temp_value = 0b0010011001111111  # Example temp value (26.75°C, binary format)
    await lm70.drive_temp_data(temp_value)  # Send 16-bit data serially via LM70

    # Wait for some time to ensure the SIPO has received all bits
    await Timer(20, units="ns")

    # After all data is shifted, CS goes high to latch the data
    dut.CS.value = 1
    await Timer(10, units="ns")

    # Stop the clock and ensure SC is low again
    # cocotb.stop_soon(clock)

    # Read the latched output and check against expected shifted value
    sipo_output = dut.SIPO_Q.value.integer
    msbs = (sipo_output >> 8) & 0xFF  # Extract upper 8 bits (MSBs)
    shifted_msbs = (msbs << 1) & 0xFF  # Left shift by 1
    latch_output = dut.Latch_Q.value.integer

    # Log and check if Latch_Q output matches expected output
    dut._log.info(f"Original MSBs = {bin(msbs)}")
    dut._log.info(f"Shifted MSBs = {bin(shifted_msbs)}")
    dut._log.info(f"Latched output = {bin(latch_output)}")

    # Check if the MSBs match the expected shifted result
    assert latch_output == shifted_msbs, f"Test failed! Latch_Q = {bin(latch_output)}, expected = {bin(shifted_msbs)}"

    # Optionally, test the MSB/LSB split if needed
    latch_q_msb = dut.Latch_Q_MSB.value.integer
    latch_q_lsb = dut.Latch_Q_LSB.value.integer
    expected_msb = shifted_msbs >> 4  # Upper 4 bits
    expected_lsb = shifted_msbs & 0xF  # Lower 4 bits

    if latch_q_msb != expected_msb or latch_q_lsb != expected_lsb:
        raise TestFailure(f"MSB/LSB test failed! MSB = {latch_q_msb}, expected MSB = {expected_msb}, LSB = {latch_q_lsb}, expected LSB = {expected_lsb}")
    else:
        dut._log.info(f"MSB/LSB test passed! MSB = {latch_q_msb}, LSB = {latch_q_lsb}")

    # Log successful test
    dut._log.info("Test passed!")

