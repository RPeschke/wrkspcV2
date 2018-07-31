#!/usr/bin/env python
'''
Overview:
Take pedestal samples 128 times for each window. Add them, cast as floats,
average them, then cast back to int and save in root file
./data/<SN>/pedestals.root
'''
import sys, os, time
sys.path.append( os.getcwd()+'/lib/' )
import linkEth, cmd_lib, FileHandshake, run_lib
run = run_lib.ImportRunControlFunctions(sys)

### ----CONTROL PARAMETERS---- ###
run.NumEvts       = 10
run.ASICmask      = "0000000001"  # e.g. 0000000111 for enabling ASICs 0, 1, and 2
run.HVmask        = "0100000000000001" #16-ch mask: 0= 255 trim DAC counts, 1= HV DAC from file
run.TrigMask      = "0000000000000001" #16-ch mask: 0= 4095 trig DAC counts, 1= trig DAC from file
run.HVDAC_offset  = [ -25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -25]
run.ThDAC_offset  = [-425, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,   0]
run.FWpedSubType = 3 ##  1 for FW pedSub  ##  2 for peds only  ##  3 for raw data  ##
run.ParserPedSubType =  "-NoPedSub"   ##  "-FWpeds"  ##  "-SWpeds"  ##  "-NoPedSub"  ##
### Uncomment block to TAKE CALIBRATION DATA
#for ASIC in range(10):
# if ((2**ASIC & int(run.ASICmask,2)) > 0):
#     os.system("./py/ThresholdScan/SingleASIC_Starting_Values.py %s %s %d %s" % (run.SN,run.strHV,ASIC,run.HVmask))
#     time.sleep(0.1)

# Construct command and linkEth classes for building and sending hex packets to FPGA
cmd = cmd_lib.CMD(run)
ctrl = linkEth.UDP('192.168.20.5', '24576', '192.168.20.1', '28672', "eth4") # (addr_fpga, port_fpga, addr_pc, port_pc, interface):

### Uncomment block to MEASURE PEDESTAL DISTRIBUTION
run.NumSoftwareEvtsPerWin   = 128
f = run.OpenEthLinkAndDataFile(ctrl)
run.SoftwareTriggeredDataCollectionLoop(ctrl,cmd,f)
run.TurnOffTrigsAndHV_ClosePortsAndFiles(ctrl,cmd,f)
run.ConvertDataToRootFile("temp/pedsTemp.root")
run.CreatePedestalMasterFile()
#run.Plot_Peds_OneASIC()

### Uncomment block to COLLECT DATA
#f = run.OpenEthLinkAndDataFile(ctrl)
#run.MainDataCollectionLoop(ctrl,cmd,f,0)
#run.TurnOffTrigsAndHV_ClosePortsAndFiles(ctrl,cmd,f)
#run.ConvertDataToRootFile()
#run.SaveDataCollectionParameters(0)
