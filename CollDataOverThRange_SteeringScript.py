#!/usr/bin/env python
import sys
import time
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
##  the scripts they don't need, then run everything by launching this script.
##
##      Author: Chris Ketter
##      email:  cketter@hawaii.edu
##      last modified: 25 May 2018
##
################################################################################

#---------------- USAGE ----------------#
#e.g./: ./KLM_HI_SteeringScript.py KLMS_0173 74p52
usageMSG="Usage:\n"+\
"./KLM_HI_SteeringScript.py <S/N> <HV>\n"+\
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
tempASCIIdata   = "temp/waveformSamples.txt"
ped_file        = "data/"+SN+"/pedestals.root"
root_file       = "data/"+SN+"/"+SN+".root"
if not (os.path.isdir("data/"+SN)):
    os.system("mkdir -p data/" + SN)
    os.system("chown testbench2:testbench2 data/"+SN)

#########################################
##         LOAD ROOT MACROS            ##
#########################################
ROOT.gROOT.LoadMacro("root/MakeMBeventTTree.cxx")
ROOT.gROOT.LoadMacro("root/PlotSomeWaveforms.cxx")
ROOT.gROOT.LoadMacro("root/MultiGaussFit.cxx")
ROOT.gROOT.LoadMacro("root/PlotPedestalStatisticsOneASIC.cxx")
ROOT.gROOT.LoadMacro("root/PlotPedestalStatisticsManyASICs.cxx")
time.sleep(0.1)

#########################################
###   Measure Pedestal Distribution   ###
#########################################
#numPedEvtsPerWindow = 1
#os.system("echo -n > %s" % tempASCIIdata) #clear ascii file
#time.sleep(0.1)
#for ASIC in range(10):
#    if ((2**ASIC & int(ASICmask,2)) > 0):
#        os.system("sudo ./py/takeSoftwareTriggeredData.py %s %s %s %d %d" % (SN,strRawHV,ASIC,0,numPedEvtsPerWindow*128))
#        time.sleep(0.1)
#os.system("sudo rm temp/pedsTemp.root")
#time.sleep(0.1)
#ROOT.MakeMBeventTTree(tempASCIIdata, "temp/pedsTemp.root", "RECREATE")
#time.sleep(0.1)
#ROOT.PlotPedestalStatisticsManyASICs("temp/pedsTemp.root", "data/" + SN + "/plots/pedDist.pdf")
#time.sleep(0.1)
#print("Pedestal distribution finished")

#########################################
##         TAKE CALIB DATA             ##
#########################################
#for ASIC in range(10):
#    if ((2**ASIC & int(ASICmask,2)) > 0):
#        os.system("sudo ./py/SingleASIC/SingleASIC_Starting_Values.py KLMS_0173 %s %d" % (strRawHV,ASIC))
#        time.sleep(0.1)

os.system("sudo /bin/bash setup_thisMB.sh %s" % ASICmask)
#########################################
#####         Take Data             #####
#########################################
numEvts         = 10000
HVtrimOffset    = 5
trigOffset      = 650                #trigger level (w.r.t. baseline)
CHmask          = "0000000000000001" #16-channel mask: 0=HVoff, 1=HVnom
os.system("echo -n > %s" % tempASCIIdata) #clear ascii file
t0 = tProg = time.time()
for trigOffset in range(200,600,10):
    if ((time.time()-tProg)>12600):
        os.system("sudo /bin/bash setup_thisMB.sh %s" % ASICmask)
        time.sleep(0.1)
        tProg = time.time()
    os.system("sudo ./py/takeSelfTriggeredData.py %s %s %s %s %d %d %d %f" % (SN,strRawHV,ASICmask,CHmask,HVtrimOffset,trigOffset,numEvts,tProg))
time.sleep(0.1)

#########################################
##          Make ROOT TTree            ##
#########################################
####Constructor: MakeMBeventTTree(const char* tempASCIIdata, const char* root_output, const char* TFile_option)
print "writring in %s" % root_file
ROOT.MakeMBeventTTree(tempASCIIdata, root_file, "RECREATE")
time.sleep(0.1)
os.system("echo -n > %s" % tempASCIIdata) #clear ascii file
os.system("chown testbench2:testbench2 " + root_file + " && chmod g+w " + root_file)


#########################################
###           Analyze Data            ###
#########################################

#####PlotSomeWaveforms(const char* root_file, const int argCH)
#ROOT.PlotSomeWaveforms(root_file,15)
#time.sleep(0.1)
#ROOT.PlotSomeWaveforms(root_file,0)

#####PlotPhotoElectronPeaks(char* root_file, int ASIC, int CH, float HV)
#ROOT.MultiGaussFit(root_file, 0, 0, approxHV)

#####PlotPhotoElectronPeaks_vs_HV(SN, root_dir, argASIC, argCH)
#ROOT.PlotPhotoElectronPeaks_vs_HV(SN,    "ch0",       0,     0)


print("END of instructions from KLM_HI_SteeringScript.py\n\n")
