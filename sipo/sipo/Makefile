# Enable VCD waveform dumping for Icarus Verilog
export COCOTB_SIM = 1

SIM ?= icarus

WAVES=1  # Set this to 1 to enable waveform dumping

TOPLEVEL_LANG ?= verilog

# Set the PDK path where sky180 Verilog models are located
PDK_PATH = /home/saileshmishra164/sky130hd/work_around_yosys/formal_pdk.v

ifeq ($(WAVES),1)
        DUMP_OPTS = -D dump.vcd -fst
endif

# Conditional sources and top levels based on design

ifeq ($(DESIGN),sipo)
     VERILOG_SOURCES = $(PWD)/../sipo/sipo_sr.v  # Path to your Verilog file
     TOPLEVEL = sipo_sr                 # Top-level module name
     MODULE = tb_lm70_sipo              # Python test file (without .py)
endif

ifeq ($(DESIGN),sipo_latch)
     VERILOG_SOURCES = $(PWD)/../sipo/sipo_latch.v \
                       $(PDK_PATH)  # The PDK model file
     TOPLEVEL = sipo_with_latch
     MODULE = test_sipo_with_latch
     
endif


ifeq ($(DESIGN),mux2to1)
     VERILOG_SOURCES = $(PWD)/../sipo/mux2to1.v \
                       $(PDK_PATH)  # The PDK model file
     TOPLEVEL =mux2to1
     MODULE = test_mux2to1

endif

ifeq ($(DESIGN),sipo_with_latch_mux)
     VERILOG_SOURCES = $(PWD)/../sipo/sipo_with_latch_mux.v \
                       $(PDK_PATH)  # The PDK model file
     TOPLEVEL =sipo_with_latch_mux
     MODULE =  test_sipo_with_latch_mux2

endif


#Enable VCD dumping with -fst (faster simulation)
ifeq ($(WAVES),1)
	SIM_ARGS += $(DUMP_OPTS)
endif

#Include Cocotb Makefile rules
include $(shell cocotb-config --makefiles)/Makefile.sim


