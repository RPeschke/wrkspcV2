#!/usr/bin/env python
import sys
import time
from time import strftime
import os
sys.path.append( os.getcwd()+'/lib/' )
import linkEth
import cmd_lib
sys.path.append('/home/testbench2/root_6_08/lib')
import ROOT
import numpy as np
################################################################################
##                      KLM Hawaii Steering Script
##
##      This script is meant to simplify data collection for the KLM scintillator
##  testbench in Hawaii. Below are sections for Data Collection Parameters,
##  loading of ROOT macros, running targetX ASIC calibration procedures,
##  collecting targetX data, saving the data to a ROOT tree, and analyzing data.
##  The user can uncomment or add in the scripts they want to run, comment out
##  the scripts they don't need, then run everything by launching their own
##  version of this script.
##
##      Author: Chris Ketter
##      email:  cketter@hawaii.edu
##      last modified: 05 July 2018
##
################################################################################

#---------------- USAGE ----------------#
#e.g./: ./MySteeringScript.py KLMS_0173 74p52
usageMSG="Usage:\n"+\
"./ExampleSteeringScript.py <S/N> <HV>\n"+\
"Where:\n"+\
    "<S/N>          = KLMS_0XXX\n"+\
    "<HV>           = (e.g.) 74p52\n"

if (len(sys.argv)!=3):
    print usageMSG
    exit(-1)

SN          = str(sys.argv[1])
strRawHV    = str(sys.argv[2])
floatHV = float(strRawHV.replace("p","."))


#########################################
##          FILE MANAGEMENT            ##
#########################################
ASICmask        = "0000000001"  # e.g. 0000000111 for enabling ASICs 0, 1, and 2
HVmask          = "0100000000000001" #16-channel mask: 0=HVoff, 1=HVnom
ped_file        = "data/"+SN+"/pedestals.root"
#UniqueID        = strftime("%Y%m%d_%H%M%S%Z", time.localtime())
UniqueID        = strftime("%Y%m%d", time.localtime())
root_file       = "data/%s/%s_%s.root" % (SN,SN,UniqueID)
if not (os.path.isdir("data/"+SN)):
    os.system("mkdir -p data/" + SN + "/plots")
    os.system("chown -R testbench2:testbench2 data/"+SN)





#########################################
##         LOAD ROOT MACROS            ##
#########################################
ROOT.gROOT.LoadMacro("root/TTreeMgmt/MakeMBeventTTree.cxx")
ROOT.gROOT.LoadMacro("root/WaveformPlotting/PlotSomeWaveforms.cxx")
ROOT.gROOT.LoadMacro("root/GainStudies/MultiGaussFit.cxx")
ROOT.gROOT.LoadMacro("root/TTreeMgmt/PlotPedestalStatistics.cxx")
time.sleep(0.1)





######################################### Only need to
##         TAKE CALIB DATA             ## do this once
######################################### per raw HV setting
#for ASIC in range(10):
#    if ((2**ASIC & int(ASICmask,2)) > 0):
#        os.system("sudo ./py/ThresholdScan/SingleASIC_Starting_Values.py %s %s %d %s" % (SN,strRawHV,ASIC,HVmask))
#        time.sleep(0.1)
#time.sleep(0.1)
#print("Threshold scan finished.\n\n")
#
ctrl = linkEth.UDP('192.168.20.5', '24576', '192.168.20.1', '28672', "eth4") # (addr_fpga, port_fpga, addr_pc, port_pc, interface):
cmd = cmd_lib.CMD(SN, strRawHV, ASICmask)
cmdHVoff = cmd.Generate_ASIC_HV_cmd(0, [255 for i in range (15)])
cmdThOff = cmd.Generate_ASIC_TH_cmd(0, [4095 for i in range (15)])
thBase = cmd.Get_ASIC_TH_from_file(0)
HV_DAC = cmd.Get_ASIC_HV_from_file(0)





#########################################
###   Measure Pedestal Distribution   ###
#########################################
#print("\nMeasuring pedestal distributions\n")
#numPedEvtsPerWindow = 1
#time.sleep(0.1)
#os.system("echo -n > temp/data.dat") #clean file without removing (prevents ownership change to root in this script)
#f = open('temp/data.dat','ab') #a=append, b=binary
#time.sleep(0.1)
#t1 = time.time()
#for ASIC in range(10):
#    if ((2**ASIC & int(ASICmask,2)) > 0):
#        print "Taking %s events for ASIC %d . . ." % (128*numPedEvtsPerWindow, ASIC)
#        #os.system("sudo ./lib/pedcalc.py eth4 %d" % (ASIC))
#        #time.sleep(0.1)
#        ctrl.open()
#        time.sleep(0.1)
#        ctrl.send(cmdHVoff)
#        time.sleep(0.1)
#        cmdRunConfig = cmd.Generate_Software_triggered_run_config_cmd(1,0,ASIC)
#        ctrl.send(cmdRunConfig)
#        time.sleep(0.1)
#        for evt in range(128*numPedEvtsPerWindow):
#            ctrl.send(cmd.Set_Readout_Window((evt*4)%512))
#            time.sleep(0.01)
#            ctrl.send(cmd.forceTrig)
#            rcv = ctrl.receive(20000)# rcv is string of Hex
#            time.sleep(0.01)
#            if ((i%1)==0):
#                sys.stdout.write('.')
#                sys.stdout.flush()
#            if (i>0 and (i%80)==0) or i==(128*numPedEvtsPerWindow-1):
#                sys.stdout.write("<--%d\n" % i)
#                sys.stdout.flush()
#            rcv = linkEth.hexToBin(rcv)
#            f.write(rcv) # write received binary data into file
#        ctrl.close()
#f.close()
#
##---- RUN DATA-PARSING EXECUTABLE ----#
#print "\nParsing %s Data" % SN
#os.system("echo -n > temp/waveformSamples.txt") #clean file without removing (prevents ownership change to root in this script)
#time.sleep(0.1)
#os.system("./bin/tx_ethparse1_ck temp/data.dat temp/waveformSamples.txt temp/triggerBits.txt 0")
#time.sleep(0.1)
#os.system("echo -n > temp/data.dat") #clean binary file again to save disk space!
#time.sleep(0.1)
#print "\nData parsed."
#
##---- WRITE DATA TO ROOT FILE ----#
#os.system("sudo rm temp/pedsTemp.root")
#time.sleep(0.1)
#ROOT.MakeMBeventTTree("temp/waveformSamples.txt", "temp/pedsTemp.root")
#time.sleep(0.1)
#
##---- GENERATE PLOTS ----#
##ROOT.PlotPedestalStatisticsManyASICs("temp/pedsTemp.root", "data/" + SN + "/plots/pedDist.pdf")
##time.sleep(0.1)
#ROOT.PlotPedestalStatisticsOneASIC("temp/pedsTemp.root", "data/" + SN + "/plots/pedDistOneASIC.pdf")
#time.sleep(0.1)
#ROOT.PlotPedestalStatisticsOneChannel("temp/pedsTemp.root", "data/" + SN + "/plots/pedDistCh0.pdf",0)
#time.sleep(0.1)
#ROOT.PlotPedestalStatisticsOneChannel("temp/pedsTemp.root", "data/" + SN + "/plots/pedDistCh14.pdf",14)
#time.sleep(0.1)
#print("Pedestal distribution finished\n\n")





#########################################
#####         Take Data             #####
#########################################

#---- CONFIGURE TRIGGER THRESHOLDS ----#
trigLevel = [thBase[0]-425,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095]
cmdTh = cmd.Generate_ASIC_TH_cmd(0,trigLevel)

#---- CONFIGURE HV DAC VALUES ----#
HV_DAC[0] -= 25
HV_DAC[14] -= 25
cmdHV = cmd.Generate_ASIC_HV_cmd(0,HV_DAC)

#---- TX CONFIGURATION FOR SELF-TRIGGERING ----#
    # OpMode:  =1 for ped sub data  /  =2 for peds  /  =3 for raw data
    # OutMode: =0 for waveforms  /  =1 for feature extracted data only
    # LookBack: Window lookback parameter in range [0,511]
cmdRunConfig = cmd.Generate_ASIC_triggered_run_config_cmd(1,0,3) #(OpMode, OutMode, LookBack)

#---- SEND COMMANDS TO TX ASIC AND FPGA ----#
ctrl.open()
time.sleep(0.1)
ctrl.send(cmdHV)
time.sleep(0.2)
ctrl.send(cmdTh)
time.sleep(0.2)
ctrl.send(cmdRunConfig)
time.sleep(0.2)

#---- DATA COLLECTION ----#
NumEvts = 10
print "Taking %s events . . ." % (NumEvts)
#print "Taking data for %d seconds" % (tTotal)
os.system("echo -n > temp/data.dat") #clean file without removing (prevents ownership change to root in this script)
f = open('temp/data.dat','ab') #a=append, b=binary
time.sleep(0.1)
t0 = tProg = time.time() # for longer data runs, FPGA will reprogram roughly every 3.5 hours (due to 4hr limit)
#while (t2<tTotal):
#    evtNum+=1
tExtra = 0
evtNum = 0
for evtNum in range(0, NumEvts):
    if (time.time()-tProg > 12600):
        tProgStart = time.time()
        ctrl.send(cmdHVoff)
        time.sleep(0.1)
        ctrl.close()
        os.system("sudo /bin/bash setup_thisMB.sh %s" % sys.argv[3])
        time.sleep(0.1)
        ctrl.open()
        time.sleep(0.2)
        ctrl.send(cmdHV)
        time.sleep(0.2)
        ctrl.send(cmdTh)
        time.sleep(0.2)
        ctrl.send(cmdRunConfig)
        time.sleep(0.2)
        tProg = time.time()
        print("Resuming data collection.\n\n")
        tExtra += time.time()-tProgStart
    rcv = ctrl.receive(20000)# rcv is string of Hex
    time.sleep(0.001)
    if (evtNum>0 and (evtNum%100)==0):
        sys.stdout.write('.')
        sys.stdout.flush()
    if ((evtNum>0 and (evtNum%8000)==0) or evtNum==(NumEvts-1)):
        sys.stdout.write("<--%d\n" % evtNum)
        sys.stdout.flush()
    rcv = linkEth.hexToBin(rcv)
    f.write(rcv) # write received binary data into file
    t2 = time.time()-t0
EvtRate = (1+evtNum)/float(t2-tExtra)
print "\nOverall hit rate was %.2f Hz" % EvtRate
ctrl.send(cmd.turnOffASICtriggering)
time.sleep(0.1)
f.close()
ctrl.send(cmdHVoff)  # No sense in leaving it cranked up anymore
time.sleep(0.2)
ctrl.close()
time.sleep(0.1)

#---- WRITE PARAMETERS TO ROOT FILE ----#
thDAC_Base = np.asarray(thBase)
thDAC      = np.asarray(trigLevel)
HV_DAC     = np.asarray(HV_DAC)
ROOT.WriteParametersToRootFile(root_file, floatHV, thDAC_Base, thDAC, HV_DAC, EvtRate)
#---- RUN DATA-PARSING EXECUTABLE ----#
print "\nParsing %s Data" % SN
os.system("echo -n > temp/waveformSamples.txt") #clean file without removing (prevents ownership change to root in this script)
os.system("./bin/tx_ethparse1_ck temp/data.dat temp/waveformSamples.txt temp/triggerBits.txt 0")
os.system("echo -n > temp/data.dat") #clean binary file again to save disk space!
time.sleep(0.1)
print "\nData parsed."

#---- WRITE DATA TO ROOT FILE ----#
print "writring in %s" % root_file
ROOT.MakeMBeventTTree("temp/waveformSamples.txt", root_file)
time.sleep(0.1)
os.system("echo -n > temp/waveformSamples.txt") #clear ascii file
os.system("chown testbench2:testbench2 " + root_file + " && chmod g+w " + root_file)
print ("Data collection finished.\n\n")

#########################################
###           Analyze Data            ###
#########################################

#####PlotSomeWaveforms(const char* root_file, const int argCH)
#ROOT.PlotSomeWaveforms(root_file,SN)
#time.sleep(0.1)

#####PlotPhotoElectronPeaks(char* root_file, int ASIC, int CH, float HV)
#ROOT.MultiGaussFit(root_file,SN, 0, 0, approxHV)

#####PlotPhotoElectronPeaks_vs_HV(SN, root_dir, argASIC, argCH)
#ROOT.PlotPhotoElectronPeaks_vs_HV(SN,    "ch0",       0,     0)


os.system("sudo chown -R testbench2:testbench2 data/*")
print("END of instructions from KLM_HI_SteeringScript.py\n\n")
