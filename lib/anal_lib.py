#!/usr/bin/env python
import sys, os, time, csv, numpy as np
sys.path.append( os.getcwd() )
import run_lib
sys.path.append('/home/testbench2/root_6_08/lib')
import ROOT

SOFT       =  "\033[95m"
OKBLUE     =  "\033[94m"
OKGREEN    =  "\033[92m"
FATAL      =  "\033[1;91m"
BCYAN      =  "\033[1;96m"
def Print(s,c):
    print"%s%s\033[m"%(c,str(s))


class NewAnalysis:
    def __init__(self, run):
        self.DEBUG = run.DEBUG
        self.run = run
        self.SN                 = str(sys.argv[1])
        self.strHV              = str(sys.argv[2])
        self.rawHV              = float(self.strHV.replace("p","."))
        self.FeatExtd_data = self.run.root_file.replace('.root','_features.root')
        self.HV_DAC = run.Get_ASIC_HV_from_file(0,'quiet')
        self.PlotsDir = run.PlotsDir
        #--- Load Root Macros---#
        ROOT.gROOT.LoadMacro("root/Feature_extraction/ProcessWaveforms.cxx")
        ROOT.gROOT.LoadMacro("root/GainStudies/MultiGaussFit.cxx")
        ROOT.gROOT.LoadMacro("root/WaveformPlotting/StreamAnnotatedSingleChWaveformsToCanvas.cxx")
    def ProcessWaveforms(self, infile=""):
        if not (infile): infile = self.run.root_file
        if (self.DEBUG): print("Infile: %s" % (infile))
        ROOT.ProcessWaveformData(infile)

    def FitSinglePhotonSpectra(self, CH, infile=""):
        approxHV = self.rawHV - 5*(self.HV_DAC[CH] + self.run.HVDAC_offset[CH])/256.
        if not (infile): infile = self.run.root_file
        if (self.DEBUG): print("Infile: %s" % (infile))
        ''' const char* root_file, const char* PlotsDir, const int   argCH, const float approxHV) '''
        ROOT.MultiGaussFit(infile, self.PlotsDir, CH, approxHV)

    def StreamWaveformsToTerminal(self, infile=""):
        if not (infile): infile = self.run.root_file
        if (self.DEBUG): print("Infile: %s, CH: %d, start:%d, stop: %d, dispTime: %d" % (infile))
        ''' const char* root_file, const char* PlotsDir, const int   argCH, const float approxHV) '''
        ROOT.PlotFeatures(infile)
