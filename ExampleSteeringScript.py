#!/usr/bin/env python
import sys, os, time
sys.path.append( os.getcwd()+'/lib/' )
import cmd_lib, FileHandshake, run_lib, anal_lib
sys.path.append('/home/testbench2/root_6_08/lib')
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
##      last modified: 23 July 2018
##
################################################################################
run = run_lib.ImportRunControlFunctions(sys)

### ----CONTROL PARAMETERS---- ###
run.NumEvts       = 100
run.ASICmask      = "0000000001"  # e.g. 0000000111 for enabling ASICs 0, 1, and 2
run.HVmask        = "0100000000000001" #16-ch mask: 0= 255 trim DAC counts, 1= HV DAC from file
run.TrigMask      = "0000000000000001" #16-ch mask: 0= 4095 trig DAC counts, 1= trig DAC from file
run.HVDAC_offset  = [ -25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -25]
run.ThDAC_offset  = [-225, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,   0]


#run.MeasureTrigDAC_and_HV_DAC_BaseValues()

#run.CreatePedestalMasterFile() # opt: (# of averages)

#run.MeasurePedestalDistribution() # opt: (# of evts. per win.)
#run.Plot_Peds_OneASIC()

#run.CollectRandomWindowData()

#run.CollectASICtriggeredData()

root = anal_lib.NewAnalysis(run)
root.ProcessWaveforms() # opt: (infile, outfile)
