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

SOFT       =  "\033[95m"
OKBLUE     =  "\033[94m"
OKGREEN    =  "\033[92m"
FATAL      =  "\033[1;91m"
BCYAN      =  "\033[1;96m"
def Print(s,c):
    print"%s%s\033[m"%(c,str(s))

def CheckCmdLineArgs(sys):
    usageMSG=FATAL+"Usage:\n"+\
    "./SteeringScript.py <S/N> <HV>\n"+OKBLUE +\
    "Where:\n"+\
        "<S/N>          = KLMS_0XXX\n"+\
        "<HV>           = (e.g.) 74p52\n"
    if (len(sys.argv)!=3):
        Print(usageMSG,FATAL)
        exit(-1)


class ImportRunControlFunctions:
    def __init__(self, sys):
        CheckCmdLineArgs(sys)

        ### ----initialize RUN parameters---- ###
        self.t0                = time.time()
        self.SN                = str(sys.argv[1])
        self.strHV             = str(sys.argv[2])
        self.rawHV             = float(self.strHV.replace("p","."))

        ### ----initialize FILE HANDLING variables---- ###
        self.date              = strftime("%Y%m%d", time.localtime())
        self.datetime          = strftime("%Y%m%d_%H%M%S%Z", time.localtime())
        self.binDatafile       = "temp/data.dat"
        self.tfile             = "data/%s/%s_%s.root" % (self.SN,self.SN,self.date)
        self.pedfile           = "data/%s/pedestals.root" % (self.SN)
        #self.tfile             = "data/%s/%s_%s.root" % (self.SN,self.SN,self.datetime)

        ### ----initialize CONTROL PARAMETERS to defaults---- ###
        self.NumEvts           = 0
        self.NumSoftwareEvtsPerWin = 0
        self.ASICmask          = "0000000001"  # e.g. 0000000111 for enabling ASICs 0, 1, and 2
        self.HVmask            = "0100000000000001" #16-ch mask: 0= 255 trim DAC counts, 1= HV DAC from file
        self.TrigMask          = "0000000000000001" #16-ch mask: 0= 4095 trig DAC counts, 1= trig DAC from file
        self.HVDAC_offset      = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        self.ThDAC_offset      = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]

        ### ----HARD-CODED CONTROL PARAMETERS---- ###
        self.FWpedSubType      = 3 # 1 for FW pedSub, 2 for peds only, 3 for raw data
        self.ASIClookbackParam = 3
        self.FWoutMode         = 0 # 0 for waveforms, 1 for feat. ext. data only
        self.ParserPedSubType  = "-SWpeds"
        self.RunConfig = ""
        if not (os.path.isdir("data/"+self.SN)):
            os.system("mkdir -p data/" + self.SN + "/plots")

    def Get_ASIC_Th_from_file(self, ASIC, opt=""):
        calib_file = "data/%s/calib/HVandTH/%s_HV%s_ASIC%d.txt" % (self.SN, self.SN, self.strHV, ASIC)
        if not (os.path.isfile(calib_file)):  #infile.mode == 'r':
            Print("Could not find calibration file %s! Exiting . . ." % (calib_file),FATAL)
            exit(-1)
        num_lines = int(os.popen("sed -n '$=' "+calib_file).read())
        if (num_lines == 15):
            infile = open(calib_file, 'r')
        else:
            Print("Calibration file %s has wrong number of lines. Exiting!" % (calib_file),FATAL)
            Print("Remove faulty calibration file and rerun script" ,FATAL)
            quit()
        csvFile = csv.reader(infile, delimiter='\t')
        fileLines= []
        for line in csvFile:
            fileLines.append(line)
        infile.close()
        thBase = [int(line[0]) for line in fileLines]
        if not (opt=='quiet'):
            Print("Found threshold base values from calibration file", SOFT)
            Print(thBase, OKGREEN)
        return thBase

    def Get_ASIC_HV_from_file(self, ASIC, opt=""):
        calib_file = "data/%s/calib/HVandTH/%s_HV%s_ASIC%d.txt" % (self.SN, self.SN, self.strHV, ASIC)
        if not (os.path.isfile(calib_file)):  #infile.mode == 'r':
            Print("Could not find calibration file %s! Exiting . . ." % calib_file, FATAL)
            exit(-1)
        num_lines = int(os.popen("sed -n '$=' "+calib_file).read())
        if (num_lines == 15):
            infile = open(calib_file, 'r')
        else:
            Print("Calibration file %s has wrong number of lines. Exiting!" % (calib_file), FATAL)
            Print("Remove faulty calibration file and rerun calibration script", FATAL)
            quit()
        csvFile = csv.reader(infile, delimiter='\t')
        fileLines= []
        for line in csvFile:
            fileLines.append(line)
        infile.close()
        hvList = [int(line[1]) for line in fileLines]
        if not (opt=='quiet'):
            Print("Found HV starting values and threshold base values from calibration file", SOFT)
            Print(hvList, OKGREEN)
        return hvList

    def OpenEthLinkAndDataFile(self,ctrl):
        Print("Opening port", SOFT)
        Print("Opening binary data file for writing", SOFT)
        ctrl.open()
        f = open(self.binDatafile,'wb') #a=append, w=write, b=binary
        return f

    def CheckTimeSinceLastReprogram(self,tProg):
        return time.time()-tProg > 12600

    def MainDataCollectionLoop(self,ctrl,cmd,f,ASIC):
        Print("Sending run configuration to FPGA", SOFT)
        self.RunConfig = cmd.Generate_ASIC_triggered_run_config_cmd(ASIC)
        ctrl.send(self.RunConfig)
        tExtra = 0
        evtNum = 0
        tProg = t0 = time.time()
        hs = FileHandshake.FileHandshake()
        Print("\nTaking %s events. . ." % (self.NumEvts), SOFT)
        for evtNum in range(1, self.NumEvts+1):
            if (self.CheckTimeSinceLastReprogram(tProg)):
                tExtra += self.pauseForReprogram(hs,ctrl,cmd)
                tProg = time.time()
            rcv = ctrl.receive(20000)# rcv is string of Hex
            time.sleep(0.001)
            self.printStatusBar(evtNum)
            rcv = linkEth.hexToBin(rcv)
            f.write(rcv) # write received binary data into file
        self.EvtRate = float(evtNum)/(time.time()-t0-tExtra)
        Print("\nOverall hit rate was %s%.2f Hz" % (OKGREEN,self.EvtRate), SOFT)

    def SoftwareTriggeredDataCollectionLoop(self,ctrl,cmd,f):
        ctrl.send(cmd.HVoff())
        cmd.KLMprint(cmd.HVoff(),"cmd.HVoff")
        time.sleep(0.01)
        ctrl.send(cmd.THoff())
        cmd.KLMprint(cmd.THoff(),"cmd.THoff")
        time.sleep(0.01)
        for ASIC in range(10):
            if ((2**ASIC & int(self.ASICmask,2)) > 0):
                Print("Sending run configuration to FPGA", SOFT)
                self.RunConfig = cmd.Generate_Software_triggered_run_config_cmd(ASIC)
                ctrl.send(self.RunConfig)
                cmd.KLMprint(self.RunConfig,"Software_triggered_run_config_cmd")
                time.sleep(0.01)
                t0 = time.time()
                self.NumEvts = 128*self.NumSoftwareEvtsPerWin
                Print("Taking %s events for ASIC %d . . ." % (self.NumEvts, ASIC), SOFT)
                for evtNum in range(1,self.NumEvts+1):
                    ctrl.send(cmd.Set_Readout_Window(((evtNum-1)*4)%512))
                    time.sleep(0.005)
                    ctrl.send(cmd.forceTrig)
                    rcv = ctrl.receive(20000)# rcv is string of Hex
                    time.sleep(0.005)
                    self.printStatusBar(evtNum)
                    rcv = linkEth.hexToBin(rcv)
                    f.write(rcv) # write received binary data into file
                self.EvtRate = float(evtNum)/(time.time()-t0)
                Print("\nOverall hit rate was %s%.2f Hz" % (OKGREEN,self.EvtRate), SOFT)

    def printStatusBar(self,evtNum):
        '''
        [---------------------------------------------------------------->] 100%
                                                                             '''
        status = evtNum/float(self.NumEvts)
        statusBar = BCYAN + "["
        for i  in range(int(72*status)):
            statusBar += "-"
        statusBar += ">"
        for i  in range(int(72*status),72):
            statusBar += " "
        statusBar += "] " + str(int(100*status)) + "%\033[m"
        sys.stdout.write('\r' + statusBar,)
        sys.stdout.flush()

    def pauseForReprogram(self,hs,ctrl,cmd):
        Print("Pausing data collection\nRaising HV trim DACs", SOFT)
        Print("Closing port\nStarting handshake . . .", BCYAN)
        tProgStart = time.time()
        ctrl.send(cmd.HVoff())
        time.sleep(0.1)
        ctrl.close()
        hs.start_handshake()
        Print("Return-handshake acknowledged\nOpening port", BCYAN)
        ctrl.open()
        time.sleep(0.2)
        Print("Sending run configuration to FPGA", SOFT)
        ctrl.send(self.RunConfig)
        time.sleep(0.2)
        Print("Resuming data collection", SOFT)
        return(time.time()-tProgStart)

    def TurnOffTrigsAndHV_ClosePortsAndFiles(self,ctrl,cmd,f):
        Print("Disabling ASIC triggering\nRaising HV trim DACs\nClosing port\nClosing data file", SOFT)
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
        if (self.ParserPedSubType == "-SWpeds"):
            self.ParserPedSubType += (" %s" % self.pedfile)
        Print("Parsing data . . .", SOFT)
        os.system("./bin/tx_ethparse1_ck temp/data.dat %s temp/triggerBits.txt %d %s" % (root_file,self.NumEvts,self.ParserPedSubType))
        os.system("echo -n > temp/data.dat") #clean binary file again to save disk space!
        Print("Data Parsed\nWaveform data saved in %s%s" % (OKBLUE,root_file), SOFT)

    def SaveDataCollectionParameters(self,ASIC):
        Print(SOFT,"Saving data-collection parameters to %s%s\n\n" % (OKBLUE,self.tfile))
        ThDAC_Base    = np.asarray(self.Get_ASIC_Th_from_file(ASIC,'quiet'))
        ThDAC_offset  = np.asarray(self.ThDAC_offset)
        HVDAC         = np.asarray(self.Get_ASIC_HV_from_file(ASIC,'quiet')+self.HVDAC_offset)
        ROOT.WriteParametersToRootFile(self.tfile, self.rawHV, ThDAC_Base, ThDAC_offset, HVDAC, self.EvtRate)

    def CreatePedestalMasterFile(self):
        ROOT.AveragePedestalTTree(self.pedfile,int(self.ASICmask,2),float(self.NumSoftwareEvtsPerWin))
        Print("Averaged pedestal data saved in %s%s" % (OKBLUE,self.pedfile), SOFT)
        os.system("chmod g+w %s" % self.pedfile)

    def Plot_Peds_ManyASICs(self):
        ROOT.PlotPedestalStatisticsManyASICs("temp/pedsTemp.root", "data/" + self.SN + "/plots/pedDistManyASICs.pdf")

    def Plot_Peds_OneASIC(self):
        ROOT.PlotPedestalStatisticsOneASIC("temp/pedsTemp.root", "data/" + self.SN + "/plots/pedDistOneASIC.pdf")

    def Plot_Peds_Channel(self,ch):
        ROOT.PlotPedestalStatisticsOneChannel("temp/pedsTemp.root", "data/" + self.SN + "/plots/pedDistCh%d.pdf"%ch,ch)
