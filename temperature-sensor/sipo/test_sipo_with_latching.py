import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
from cocotb.regression import TestFactory





# LM70 module definition
class LM70:
    def __init__(self, dut):
        self.dut = dut
        self.temperature_data = 0b0010011000011111  # Example temperature for 26°C

    async def send_temperature_data(self):
        # Simulate sending the temperature data
        for i in range(15, -1, -1):
            self.dut.D.value = (self.temperature_data >> i) & 1
            await RisingEdge(self.dut.SC)  # Wait for clock edge for data capture


@cocotb.test()
async def test_sipo_with_latch(dut):
    # Start the clock (Serial Clock - SC) with a period of 10 time units (5 ns high, 5 ns low)
    #cocotb.start_soon(Clock(dut.SC, 10, units="ns").start())

    #ensure SC is low before starting the clock
    dut.SC.value = 0


    # Initialize inputs
    dut.CS.value = 1  # Chip select inactive
    dut.RESET_N.value = 0  # Active low reset
    dut.D.value = 0  # Initial data input
     


    #wait for few cycles to apply reset with SC low
    await Timer(20,units="ns")

    # Define input test pattern
    Data_in = 0b0010011000011111  # Example data for 26°C

    # Apply reset
    await Timer(10, units="ns")
    dut.RESET_N.value = 1  # Release reset

    # Activate Chip Select and shift data into the SIPO
    dut.CS.value = 0  # Activate chip select (active low)
    await Timer(5, units="ns")

    # Shift the data bit-by-bit into SIPO (Example: 0010 0110 0001 1111)
    for i in range(15, -1, -1):
        dut.D.value = (Data_in >> i) & 1
        await RisingEdge(dut.SC)  # Wait for clock edge for data capture
        await Timer(5, units="ns")  # Optional small delay before the next bit

    # Wait for a clock edge after shifting all bits to latch data
    await RisingEdge(dut.SC)

    # Deactivate Chip Select and reset
    dut.CS.value = 1
    dut.D.value = 0
    await Timer(20, units="ns")  # Wait to observe final latched output

    # Check final outputs
    SIPO_output = dut.SIPO_Q.value.integer
    expected_output = Data_in

    assert SIPO_output == expected_output, \
        f"SIPO output mismatch: {SIPO_output:#018b} != {expected_output:#018b}"

    # Log the final output values for inspection
    MSBs = (SIPO_output >> 8) & 0xFF
    Left_Shift_Data = (MSBs << 1) & 0xFF
    Latch_Q = dut.Latch_Q.value.integer
    Latch_Q_LSB = Latch_Q & 0x0F
    Latch_Q_MSB = (Latch_Q >> 4) & 0x0F

    # Print outputs to mimic Verilog's $monitor
    cocotb.log.info(f"Final Results:\n"
                    f"Data_in: {Data_in:016b}\n"
                    f"SIPO Output: {SIPO_output:016b}\n"
                    f"8-bit MSBs: {MSBs:08b}\n"
                    f"Left Shifted MSBs: {Left_Shift_Data:08b}\n"
                    f"Latched Data (Latch_Q): {Latch_Q:08b}\n"
                    f"Latched MSB: {Latch_Q_MSB:04b}\n"
                    f"Latched LSB: {Latch_Q_LSB:04b}")

    # Extract temperature from Latch_Q_MSB and Latch_Q_LSB for display
    temperature = f"{Latch_Q_MSB}{Latch_Q_LSB}°C"
    cocotb.log.info(f"TEMPERATURE =>>> {temperature}")

