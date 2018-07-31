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

        #--- Load Root Macros---#
        ROOT.gROOT.LoadMacro("root/Feature_extraction/ExtractFeatures_ck.cxx")

    def ProcessWaveforms(self, infile="", outfile=""):
        '''const char* root_input, const char* root_output'''
        if not (infile): infile = self.run.root_file
        if not (outfile): outfile = infile.replace('.root','_features.root')
        if (self.DEBUG): print("Infile: %s,  Outfile: %s" % (infile,outfile))
        ROOT.ProcessWaveformData(infile,outfile)
