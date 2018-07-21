#!/usr/bin/env python
import sys
import os
import time
sys.path.append( os.getcwd()+'/lib/' )
import linkEth
import cmd_lib
sys.path.append('/home/testbench2/root_6_08/lib')
import ROOT
ROOT.gROOT.LoadMacro("root/TTreeMgmt/MakePedestalTTree.cxx")
ROOT.gROOT.LoadMacro("root/TTreeMgmt/PlotPedestalStatistics.cxx")
################################################################################
##                    Measure Pedestal Distribution
##      This script will collect <NumEvtsPerWin> for all ASICs specified
##  in <ASICmask>. Optional arguments allow the user to specify whether
##  they want to average and save the pedestal data into a .root file
##  or to generate plots to look at the pedestal distributions.
##
##
##
##      Author: Chris Ketter
##      email:  cketter@hawaii.edu
##      last modified: 05 July 2018
##
################################################################################

#---------------- USAGE ----------------#
#e.g./: ./lib/measurePedDist.py
usageMSG="Usage:\n"+\
"./lib/measurePedDist.py <SN> <ASICmask> <NumEvtsPerWin> [...-<Options>...]\n"+\
"\twhere Options are:\n\t-SavePedestals\n\t-ManyASICs\n\t-OneASIC\n\t-ch0 ... -ch15\n"

if (len(sys.argv)<4):
    print usageMSG
    exit(-1)

if (len(sys.argv)>4):
    optList = [str(sys.argv[i]) for i in range(4,len(sys.argv))]

for entry in optList:
    if (entry=='-SavePedestals'):
        opMode = 3 # disable FW pedestal subtraction
    else: opMode = 1

SN              = sys.argv[1]
ASICmask        = sys.argv[2]
NumEvtsPerWin   = int(sys.argv[3])

ctrl = linkEth.UDP('192.168.20.5', '24576', '192.168.20.1', '28672', "eth4") # (addr_fpga, port_fpga, addr_pc, port_pc, interface):
cmd = cmd_lib.CMD(SN, '0p0', ASICmask)
cmdHVoff = cmd.Generate_ASIC_HV_cmd(0, [255 for i in range (15)])
cmdThOff = cmd.Generate_ASIC_TH_cmd(0, [4095 for i in range (15)])


###   Measure Pedestal Distribution   ###
print("\nMeasuring pedestal distributions\n")
time.sleep(0.1)
os.system("echo -n > temp/data.dat") #clean file without removing (prevents ownership change to root in this script)
f = open('temp/data.dat','ab') #a=append, b=binary
time.sleep(0.1)
for ASIC in range(10):
    if ((2**ASIC & int(ASICmask,2)) > 0):
        print "Taking %s events for ASIC %d . . ." % (128*NumEvtsPerWin, ASIC)
        #os.system("./lib/pedcalc.py eth4 %d" % (ASIC))
        #time.sleep(0.1)
        ctrl.open()
        time.sleep(0.1)
        ctrl.send(cmdHVoff)
        time.sleep(0.1)
        cmdRunConfig = cmd.Generate_Software_triggered_run_config_cmd(opMode,0,ASIC)#opmode, outmode, ASIC
        ctrl.send(cmdRunConfig)
        time.sleep(0.1)
        for evt in range(128*NumEvtsPerWin):
            ctrl.send(cmd.Set_Readout_Window((evt*4)%512))
            time.sleep(0.01)
            ctrl.send(cmd.forceTrig)
            rcv = ctrl.receive(20000)# rcv is string of Hex
            time.sleep(0.01)
            if ((i%1)==0):
                sys.stdout.write('.')
                sys.stdout.flush()
            if (i>0 and (i%80)==0) or i==(128*NumEvtsPerWin-1):
                sys.stdout.write("<--%d\n" % i)
                sys.stdout.flush()
            rcv = linkEth.hexToBin(rcv)
            f.write(rcv) # write received binary data into file
        ctrl.close()
f.close()
#---- RUN DATA-PARSING EXECUTABLE ----#
print "\nParsing %s Data" % SN
os.system("./bin/tx_ethparse1_ck temp/data.dat temp/pedsTemp.root temp/triggerBits.txt 0")
time.sleep(0.1)
os.system("echo -n > temp/data.dat") #clean binary file again to save disk space!
time.sleep(0.1)
print "\nData written to temp/pedsTemp.root"
#---- GENERATE PLOTS ----#
for entry in optList:
    if (entry=='-SavePedestals'):
        ped_file = "data/"+SN+"/pedestals.root"
        ROOT.AveragePedestalTTree(ped_file,int(ASICmask,2),float(NumEvtsPerWin))
        print "Pedestal data saved in %s\n" % ped_file
    if (entry=='-ManyASICs'):
        ROOT.PlotPedestalStatisticsManyASICs("temp/pedsTemp.root", "data/" + SN + "/plots/pedDistManyASICs.pdf")
        time.sleep(0.1)
    if (entry=='-OneASIC'):
        ROOT.PlotPedestalStatisticsOneASIC("temp/pedsTemp.root", "data/" + SN + "/plots/pedDistOneASIC.pdf")
        time.sleep(0.1)
    for ch in range(16):
        if (entry=='-ch%d'%ch):
            ROOT.PlotPedestalStatisticsOneChannel("temp/pedsTemp.root", "data/" + SN + "/plots/pedDistCh%d.pdf"%ch,ch)
            time.sleep(0.1)
print("Pedestal measurement finished\n\n")
