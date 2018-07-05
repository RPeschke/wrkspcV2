#!/usr/bin/env python
import sys
import time
from time import strftime, gmtime
t0 = time.time()
import os
sys.path.append('/home/testbench2/root_6_08/lib')
import ROOT
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
##      last modified: 04 July 2018
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
floatrawHV = float(strRawHV.replace("p","."))
approxHV = floatrawHV - 5.*169./256. ## fix this later. Should be rawHV - 5*(trimDACvalue)/(256.)

#########################################
##          FILE MANAGEMENT            ##
#########################################
ASICmask        = "0000000001"  # e.g. 0000000111 for enabling ASICs 0, 1, and 2
THmask          = "0000000000000001" #16-channel mask: 0=HVoff, 1=HVnom
HVmask          = "0100000000000001" #16-channel mask: 0=HVoff, 1=HVnom
ped_file        = "data/"+SN+"/pedestals.root"
#UniqueID        = strftime("%Y%m%d_%H%M%S%Z", time.localtime())
UniqueID        = strftime("%Y%m%d", time.localtime())
root_file       = "data/%s/%s_%s.root" % (SN,SN,UniqueID)
if not (os.path.isdir("data/"+SN)):
    os.system("mkdir -p data/" + SN + "/plots")
    os.system("chown -vR testbench2:testbench2 data/"+SN)

#########################################
##         LOAD ROOT MACROS            ##
#########################################
ROOT.gROOT.LoadMacro("root/TTreeMgmt/MakeMBeventTTree.cxx")
ROOT.gROOT.LoadMacro("root/WaveformPlotting/PlotSomeWaveforms.cxx")
ROOT.gROOT.LoadMacro("root/GainStudies/MultiGaussFit.cxx")
ROOT.gROOT.LoadMacro("root/TTreeMgmt/PlotPedestalStatistics.cxx")
time.sleep(0.1)


#########################################
##         TAKE CALIB DATA             ##
#########################################
for ASIC in range(10):
    if ((2**ASIC & int(ASICmask,2)) > 0):
        os.system("sudo ./py/ThresholdScan/SingleASIC_Starting_Values.py %s %s %d %s" % (SN,strRawHV,ASIC,HVmask))
        time.sleep(0.1)
time.sleep(0.1)
print("Threshold scan finished.\n\n")


#########################################
###   Measure Pedestal Distribution   ###
#########################################
print("Measuring pedestal distributions\n")
numPedEvtsPerWindow = 1
time.sleep(0.1)
for ASIC in range(10):
    if ((2**ASIC & int(ASICmask,2)) > 0):
        os.system("sudo ./lib/pedcalc.py eth4 %d" % (ASIC))
        time.sleep(0.1)
        os.system("sudo ./py/takeSoftwareTriggeredData.py %s %s %s %d %d" % (SN,strRawHV,ASIC,0,numPedEvtsPerWindow*128))
        time.sleep(0.1)
os.system("sudo rm temp/pedsTemp.root")
time.sleep(0.1)
ROOT.MakeMBeventTTree("temp/waveformSamples.txt", "temp/pedsTemp.root", "RECREATE")
time.sleep(0.1)
#ROOT.PlotPedestalStatisticsManyASICs("temp/pedsTemp.root", "data/" + SN + "/plots/pedDist.pdf")
#time.sleep(0.1)
ROOT.PlotPedestalStatisticsOneASIC("temp/pedsTemp.root", "data/" + SN + "/plots/pedDist.pdf")
time.sleep(0.1)
print("Pedestal distribution finished\n\n")


#########################################
#####         Take Data             #####
#########################################
print("Collecting data.")
numEvts         = 100
HVtrimOffset    = 25                  # optional offset from 'hv-low' value established in calibration section
trigOffset      = 425                # trigger level w.r.t. baseline (12 bit DAC)
time.sleep(0.1)
tProg=time.time()                    # for longer data runs, FPGA will reprogram roughly every 3.5 hours (due to 4hr limit)
os.system("sudo ./py/takeSelfTriggeredData.py %s %s %s %s %s %d %d %d %f" % (SN,strRawHV,ASICmask,THmask,HVmask,HVtrimOffset,trigOffset,numEvts,tProg))
time.sleep(0.1)
print "writring in %s" % root_file
ROOT.MakeMBeventTTree("temp/waveformSamples.txt", root_file, "RECREATE")
time.sleep(0.1)
os.system("echo -n > temp/waveformSamples.txt") #clear ascii file
os.system("chown testbench2:testbench2 " + root_file + " && chmod g+w " + root_file)
print ("Data collection finished.\n\n")

#########################################
###           Analyze Data            ###
#########################################

#####PlotSomeWaveforms(const char* root_file, const int argCH)
#ROOT.PlotSomeWaveforms(root_file,15)
#time.sleep(0.1)
ROOT.PlotSomeWaveforms(root_file,SN)
time.sleep(0.1)

#####PlotPhotoElectronPeaks(char* root_file, int ASIC, int CH, float HV)
ROOT.MultiGaussFit(root_file,SN, 0, 0, approxHV)

#####PlotPhotoElectronPeaks_vs_HV(SN, root_dir, argASIC, argCH)
#ROOT.PlotPhotoElectronPeaks_vs_HV(SN,    "ch0",       0,     0)


os.system("sudo chown -vR testbench2:testbench2 data/*")
print("END of instructions from KLM_HI_SteeringScript.py\n\n")
