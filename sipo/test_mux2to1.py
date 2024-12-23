import cocotb
from cocotb.regression import TestFactory
from cocotb.triggers import Timer

@cocotb.coroutine
def clock_gen(dut):
    """Generates a clock signal."""
    while True:
        dut.clk.value = 0  # Set clock low
        yield Timer(5, units='ns')  # Wait 5 ns
        dut.clk.value = 1  # Set clock high
        yield Timer(5, units='ns')  # Wait 5 ns

@cocotb.coroutine
def test_mux2to1(dut):
    # Start the clock generator
    cocotb.start_soon(clock_gen(dut))

    # Logging initial test setup
    cocotb.log.info("Starting test for 2-to-1 multiplexer with BCD output")

    # Test case 1: Latch_Q_LSB = 2 (0b0010), Latch_Q_MSB = 1 (0b0001), lsb_sel = 0
    dut.Latch_Q_LSB.value = 0b0010  # 2 in binary
    dut.Latch_Q_MSB.value = 0b0001  # 1 in binary
    dut.lsb_sel.value = 0           # Select LSB

    # Wait for some time for signals to propagate
    yield Timer(10, units='ns')     # Wait for 10 ns

    # Logging for LSB selection
    cocotb.log.info("Test Case 1: lsb_sel = 0, Expecting Latch_Q_LSB to be selected.")
    cocotb.log.info(f"Latch_Q_LSB: {dut.Latch_Q_LSB.value}, Latch_Q_MSB: {dut.Latch_Q_MSB.value}, lsb_sel: {dut.lsb_sel.value}")
    cocotb.log.info(f"Expected bcd_data: 0b0010, Actual bcd_data: {dut.bcd_data.value}")
    cocotb.log.info(f"Expected uo_out (seven-segment): 0b1101101, Actual uo_out: {dut.uo_out.value}")

    # Check output for LSB selection
    assert dut.bcd_data.value == 0b0010, "Output mismatch for Input 0"
    assert dut.uo_out.value == 0b1101101, "Seven-segment output mismatch for Input 0"  # Check for BCD 2

    # Test case 2: Change selection to MSB
    dut.lsb_sel.value = 1  # Select MSB

    # Wait for some time for signals to propagate
    yield Timer(10, units='ns')     # Wait for 10 ns

    # Logging for MSB selection
    cocotb.log.info("Test Case 2: lsb_sel = 1, Expecting Latch_Q_MSB to be selected.")
    cocotb.log.info(f"Latch_Q_LSB: {dut.Latch_Q_LSB.value}, Latch_Q_MSB: {dut.Latch_Q_MSB.value}, lsb_sel: {dut.lsb_sel.value}")
    cocotb.log.info(f"Expected bcd_data: 0b0001, Actual bcd_data: {dut.bcd_data.value}")
    cocotb.log.info(f"Expected uo_out (seven-segment): 0b0110000, Actual uo_out: {dut.uo_out.value}")

    # Check output for MSB selection
    assert dut.bcd_data.value == 0b0001, "Output mismatch for Input 1"
    assert dut.uo_out.value == 0b0110000, "Seven-segment output mismatch for Input 1"  # Check for BCD 1

    cocotb.log.info("Test completed successfully.")

# Run the test
factory = TestFactory(test_mux2to1)
factory.generate_tests()
test_mux2to1.py

