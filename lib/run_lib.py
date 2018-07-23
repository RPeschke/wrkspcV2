#!/usr/bin/env python
import sys, os, time, csv, numpy as np
from time import strftime
sys.path.append( os.getcwd() )
import linkEth, cmd_lib, FileHandshake
sys.path.append('/home/testbench2/root_6_08/lib')
import ROOT
ROOT.gROOT.LoadMacro("root/TTreeMgmt/MakeMBeventTTree.cxx")
ROOT.gROOT.LoadMacro("root/TTreeMgmt/PlotPedestalStatistics.cxx")
ROOT.gROOT.LoadMacro("root/TTreeMgmt/MakePedestalTTree.cxx")

NORM       =  "\033[m"
BOLD       =  "\033[1m"
FAINT      =  "\033[2m"
SOFT       =  "\033[95m"
OKBLUE     =  "\033[94m"
OKGREEN    =  "\033[92m"
WARNING    =  "\033[93m"
FATAL      =  "\033[1;91m"
UNDERLINE  =  "\033[4m"
BCYAN      =  "\033[1;96m"
BROWN      =  "\033[33m"
def Print(c,s):
    print"%s%s%s"%(c,str(s),NORM)

class CmdLineArgHandler:
    def __init__(self, sys):
        #self.Pedestals = self.pedestals()
        usageMSG=FATAL+"Usage:\n"+\
        "./ExampleSteeringScript.py <S/N> <HV>\n"+OKBLUE +\
        "Where:\n"+\
            "<S/N>          = KLMS_0XXX\n"+\
            "<HV>           = (e.g.) 74p52\n"
        if (len(sys.argv)!=3):
            Print(FATAL, usageMSG)
            exit(-1)
        self.t0                = time.time()
        self.SN                = str(sys.argv[1])
        self.strHV             = str(sys.argv[2])
        self.rawHV             = float(self.strHV.replace("p","."))
        self.date              = strftime("%Y%m%d", time.localtime())
        self.datetime          = strftime("%Y%m%d_%H%M%S%Z", time.localtime())
        self.binDatafile       = "temp/data.dat"
        self.tfile             = "data/%s/%s_%s.root" % (self.SN,self.SN,self.date)
        self.pedfile           = "data/%s/pedestals.root" % (self.SN)
        #self.tfile             = "data/%s/%s_%s.root" % (self.SN,self.SN,self.datetime)
        self.NumEvts           = 0
        self.NumSoftwareEvtsPerWin = 0
        self.ASICmask          = "0000000001"  # e.g. 0000000111 for enabling ASICs 0, 1, and 2
        self.HVmask            = "0100000000000001" #16-ch mask: 0= 255 trim DAC counts, 1= HV DAC from file
        self.TrigMask          = "0000000000000001" #16-ch mask: 0= 4095 trig DAC counts, 1= trig DAC from file
        self.HVDAC_offset      = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        self.ThDAC_offset      = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        self.FWpedSubType      = 3 # 1 for FW pedSub, 2 for peds only, 3 for raw data
        self.ASIClookbackParam = 3
        self.FWoutMode         = 0 # 0 for waveforms, 1 for feat. ext. data only
        self.Config = ""
        if not (os.path.isdir("data/"+self.SN)):
            os.system("mkdir -p data/" + self.SN + "/plots")

    def Get_ASIC_Th_from_file(self, ASIC, opt=""):
        calib_file = "data/%s/calib/HVandTH/%s_HV%s_ASIC%d.txt" % (self.SN, self.SN, self.strHV, ASIC)
        if not (os.path.isfile(calib_file)):  #infile.mode == 'r':
            Print(FATAL, "Could not find calibration file %s! Exiting . . ." % (calib_file))
            exit(-1)
        num_lines = int(os.popen("sed -n '$=' "+calib_file).read())
        if (num_lines == 15):
            infile = open(calib_file, 'r')
        else:
            Print(FATAL, "Calibration file %s has wrong number of lines. Exiting!" % (calib_file))
            Print(FATAL, "Remove faulty calibration file and rerun script" )
            quit()
        csvFile = csv.reader(infile, delimiter='\t')
        fileLines= []
        for line in csvFile:
            fileLines.append(line)
        infile.close()
        thBase = [int(line[0]) for line in fileLines]
        if not (opt=='quiet'):
            Print(SOFT, "Found threshold base values from calibration file" )
            Print(OKGREEN, thBase)
        return thBase

    def Get_ASIC_HV_from_file(self, ASIC, opt=""):
        calib_file = "data/%s/calib/HVandTH/%s_HV%s_ASIC%d.txt" % (self.SN, self.SN, self.strHV, ASIC)
        if not (os.path.isfile(calib_file)):  #infile.mode == 'r':
            Print(FATAL, "Could not find calibration file %s! Exiting . . ." % calib_file)
            exit(-1)
        num_lines = int(os.popen("sed -n '$=' "+calib_file).read())
        if (num_lines == 15):
            infile = open(calib_file, 'r')
        else:
            Print(FATAL, "Calibration file %s has wrong number of lines. Exiting!" % (calib_file))
            Print(FATAL, "Remove faulty calibration file and rerun calibration script")
            quit()
        csvFile = csv.reader(infile, delimiter='\t')
        fileLines= []
        for line in csvFile:
            fileLines.append(line)
        infile.close()
        hvList = [int(line[1]) for line in fileLines]
        if not (opt=='quiet'):
            Print(SOFT,"Found HV starting values and threshold base values from calibration file")
            Print(OKGREEN, hvList)
        return hvList

    def OpenEthLinkAndDataFile(self,ctrl):
        Print(SOFT, "Opening port")
        Print(SOFT, "Opening binary data file for writing")
        ctrl.open()
        f = open(self.binDatafile,'wb') #a=append, w=write, b=binary
        return f

    def CheckTimeSinceLastReprogram(self,tProg):
        return time.time()-tProg > 12600

    def MainDataCollectionLoop(self,ctrl,cmd,f,ASIC):
        Print(SOFT, "Sending run configuration to FPGA")
        ctrl.send(cmd.Generate_ASIC_triggered_run_config_cmd(ASIC))
        tExtra = 0
        evtNum = 0
        tProg = t0 = time.time()
        hs = FileHandshake.FileHandshake()
        Print(SOFT, "\nTaking %s events. . ." % (self.NumEvts))
        for evtNum in range(1, self.NumEvts+1):
            if (self.CheckTimeSinceLastReprogram(tProg)):
                tExtra += self.pauseForReprogram(hs,ctrl,cmd)
                tProg = time.time()
            rcv = ctrl.receive(20000)# rcv is string of Hex
            time.sleep(0.001)
            self.printPseudoStatusBar(self.NumEvts,evtNum)
            rcv = linkEth.hexToBin(rcv)
            f.write(rcv) # write received binary data into file
        self.EvtRate = float(evtNum)/(time.time()-t0-tExtra)
        Print(SOFT, "\nOverall hit rate was %s%.2f Hz" % (OKGREEN,self.EvtRate))

    def SoftwareTriggeredDataCollectionLoop(self,ctrl,cmd,f):
        ctrl.send(cmd.HVoff())
        time.sleep(0.01)
        ctrl.send(cmd.THoff())
        time.sleep(0.01)
        for ASIC in range(10):
            if ((2**ASIC & int(self.ASICmask,2)) > 0):
                Print(SOFT, "Sending run configuration to FPGA")
                ctrl.send(cmd.Generate_Software_triggered_run_config_cmd(ASIC))
                time.sleep(0.01)
                t0 = time.time()
                NumEvts = 128*self.NumSoftwareEvtsPerWin
                Print(SOFT, "Taking %s events for ASIC %d . . ." % (NumEvts, ASIC))
                for evtNum in range(1,128*self.NumSoftwareEvtsPerWin+1):
                    ctrl.send(cmd.Set_Readout_Window(((evtNum-1)*4)%512))
                    time.sleep(0.005)
                    ctrl.send(cmd.forceTrig)
                    rcv = ctrl.receive(20000)# rcv is string of Hex
                    time.sleep(0.005)
                    self.printPseudoStatusBar(NumEvts,evtNum)
                    rcv = linkEth.hexToBin(rcv)
                    f.write(rcv) # write received binary data into file
                self.EvtRate = float(evtNum)/(time.time()-t0)
                Print(SOFT, "\nOverall hit rate was %s%.2f Hz" % (OKGREEN,self.EvtRate))


    def printPseudoStatusBar(self,NumEvts,evtNum):
        if (NumEvts/400.<1.):
            multiplier = 1
        elif (NumEvts/4000.<1.):
            multiplier = 10
        elif (NumEvts/40000.<1.):
            multiplier = 100
        else:
            multiplier = 1000
        if (evtNum%multiplier==0):
            sys.stdout.write('.')
            sys.stdout.flush()
        if ( (evtNum%(80*multiplier)==0) or evtNum==(NumEvts) ):
            sys.stdout.write("<--%d\n" % evtNum)
            sys.stdout.flush()

    def pauseForReprogram(self,hs,ctrl,cmd):
        Print(SOFT, "Pausing data collection\nRaising HV trim DACs")
        Print(BCYAN, "Closing port\nStarting handshake . . .")
        tProgStart = time.time()
        ctrl.send(cmd.HVoff())
        time.sleep(0.1)
        ctrl.close()
        hs.start_handshake()
        Print(BCYAN, "Return-handshake acknowledged\nOpening port")
        ctrl.open()
        time.sleep(0.2)
        Print(SOFT, "Sending run configuration to FPGA")
        ctrl.send(cmd.RunConfig)
        time.sleep(0.2)
        Print(SOFT, "Resuming data collection")
        return(time.time()-tProgStart)

    def TurnOffTrigsAndHV_ClosePortsAndFiles(self,ctrl,cmd,f):
        Print(SOFT, "Disabling ASIC triggering\nRaising HV trim DACs\nClosing port\nClosing data file")
        f.close()
        ctrl.send(cmd.turnOffASICtriggering)
        time.sleep(0.1)
        ctrl.send(cmd.HVoff())
        time.sleep(0.2)
        ctrl.close()
        time.sleep(0.1)

    def ConvertDataToRootFile(self, root_file=""):
        if (root_file==""):
            root_file = self.tfile
        Print(SOFT, "Parsing data . . .")
        os.system("./bin/tx_ethparse1_ck temp/data.dat %s temp/triggerBits.txt 0" %(root_file))
        os.system("echo -n > temp/data.dat") #clean binary file again to save disk space!
        Print(SOFT, "Data Parsed\nWaveform data saved in %s%s" % (OKBLUE,root_file))

    def SaveDataCollectionParameters(self,ASIC):
        Print(SOFT,"Saving data-collection parameters to %s%s\n\n" % (OKBLUE,self.tfile))
        ThDAC_Base    = np.asarray(self.Get_ASIC_Th_from_file(ASIC,'quiet'))
        ThDAC_offset  = np.asarray(self.ThDAC_offset)
        HVDAC         = np.asarray(self.Get_ASIC_HV_from_file(ASIC,'quiet')+self.HVDAC_offset)
        ROOT.WriteParametersToRootFile(self.tfile, self.rawHV, ThDAC_Base, ThDAC_offset, HVDAC, self.EvtRate)


    def CreatePedestalMasterFile(self):
        ROOT.AveragePedestalTTree(self.pedfile,int(self.ASICmask,2),float(self.NumSoftwareEvtsPerWin))
        Print(SOFT, "Averaged pedestal data saved in %s%s" % (OKBLUE,self.pedfile))

    def Plot_Peds_ManyASICs(self):
        ROOT.PlotPedestalStatisticsManyASICs("temp/pedsTemp.root", "data/" + self.SN + "/plots/pedDistManyASICs.pdf")
    def Plot_Peds_OneASIC(self):
        ROOT.PlotPedestalStatisticsOneASIC("temp/pedsTemp.root", "data/" + self.SN + "/plots/pedDistOneASIC.pdf")
    def Plot_Peds_Channel(self,ch):
        ROOT.PlotPedestalStatisticsOneChannel("temp/pedsTemp.root", "data/" + self.SN + "/plots/pedDistCh%d.pdf"%ch,ch)
