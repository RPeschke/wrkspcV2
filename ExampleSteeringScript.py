#!/usr/bin/env python
import sys, os, time
sys.path.append( os.getcwd()+'/lib/' )
import linkEth, cmd_lib, FileHandshake, run_lib
################################################################################
##                      KLM Hawaii Steering Script
##
##      This script is meant to simplify data collection for the KLM
##  scintillator testbench.
##      For longer data runs (>3.5hr), it will be necessary to first start
##  py/MicroProcesses/JTAG_reprogramming.py with sudo privileges in a second
##  shell, then launch this script from your original shell
##
##      Author: Chris Ketter
##      email:  cketter@hawaii.edu
##      last modified: 20 July 2018
##
################################################################################

### ----CONTROL PARAMETERS---- ###
run = run_lib.CmdLineArgHandler(sys)
run.NumEvts       = 100
run.ASICmask      = "0000000001"  # e.g. 0000000111 for enabling ASICs 0, 1, and 2
run.HVmask        = "0100000000000001" #16-channel mask: 0=HVoff, 1=HVnom
run.HVDAC_offset  = [ -25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -25]
run.ThDAC_offset  = [-425, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,   0]

# Construct command and linkEth classes for building and sending hex packets to FPGA
cmd = cmd_lib.CMD(run)
ctrl = linkEth.UDP('192.168.20.5', '24576', '192.168.20.1', '28672', "eth4") # (addr_fpga, port_fpga, addr_pc, port_pc, interface):

### Uncomment next 4 lines to TAKE CALIBRATION DATA
#for ASIC in range(10):
# if ((2**ASIC & int(ASICmask,2)) > 0):
#     os.system("./py/ThresholdScan/SingleASIC_Starting_Values.py %s %s %d %s" % (run.SN,run.strHV,ASIC,run.HVmask))
#     time.sleep(0.1)

### Uncomment next line to MEASURE PEDESTAL DISTRIBUTION
#os.system("./py/OfflinePedestals/measurePedDist.py %s %s %d -OneASIC" % (run.SN, run.ASICmask, 1))

### Uncomment next line to SAVE PEDESTALS TO FILE
#os.system("./py/OfflinePedestals/measurePedDist.py %s %s %d -SavePedestals" % (run.SN, run.ASICmask, 64))

### Uncomment next 6 lines to COLLECT DATA
f = run.ConfigureTXandFPGA(ctrl,cmd,0)
run.MainDataCollectionLoop(ctrl,cmd,f)
run.TurnOffTrigsAndHV_ClosePortsAndFiles(ctrl,cmd,f)
run.ConvertDataToRootFile()
run.SaveDataCollectionParameters(0)
